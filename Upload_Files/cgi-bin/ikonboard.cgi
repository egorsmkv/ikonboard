#!/usr/bin/perl -w

package iB;
$| = 1;
use strict;
############################################################################
#| Ikonboard 3.1.5A by Implux Designs
#|
#| No parts of this script can be used outside Ikonboard
#| without prior consent.
#| You must keep this header intact and all copyright links visible.
#| For support, visit http://impluxdesigns.com
#|
#| (c)2018 Implux Designs.
#| Web: <http://www.impluxdesigns.com>
#| #| Please read the license included in this release for more information.
#| 
################################################################

# Not much use in production code
# Uncomment if you want, but we *should* catch
# most errors in our eval block
#BEGIN { use CGI::Carp "fatalsToBrowser"; }
# Uncomment this line if you want perl to expand
# on it's cryptic error messages
#use diagnostics;

######################################################
# Lets set the script location and append the INC
#
# USER DEFINABLE 1:
# If you cannot seem to move about the board (everytime
# you click on a link you are returned to the forum/cat
# listings), then make the following value to 1

my $use_ampersands = 0;

# USER DEFINABLE 2:

# mod_perl doesn't seem to like manual unshifting of
# the @INC because it *has* to go in a BEGIN {} block
# as mod_perl only see's this once, things get out of
# whack. "use lib" is a more elegant solution. It's just
# as efficient as it only loads 'lib.pm' from disk once
# but it will prepend the array on every invocation.
# If you get funky errors about not being able to find
# 'somename.pm' in the @INC, add in your full path to
# the ikonboard directorys below.
# EXAMPLE:
# Swop    './Data'   ,
# to      '/home/ikonboard/path/ikonboard/Data',
# Don't forget the single quotes, and the commas!

use lib ( './Data'   ,
          './Sources',
          './Skin'   ,
          './Languages',
          './',
        );

# Use the Benchmark module for our STAT times
use Benchmark;

######################################################
# Lets play nicely with mod_perl
# Even though we use strict, $iB is a global package
# and as mod_perl compiles once and runs, all the
# values are carried over. We don't want that.

$iB::COOKIES_OUT = $iB::COOKIES_OUT = [];    #These double declerations and others like them are
$iB::SESSION     = $iB::SESSION     = undef; #neccessary in order to quiet interpretor warnings due
%iB::IN          = ();                       #to the use of packages across multiple files.
@iB::TEMP_COOKIE = ();
$iB::COOKIES     = {};
$iB::MEMBER      = undef;
$iB::ACTIVE      = undef;

# Calling exit() is a 'very bad thing' for mod_perl, so
# lets use Apache->exit() instead, it wont terminate the
# process. We use this 'hack' for efficiency. mod_cgi
# doesn't care, but mod_perl will only have to do this
# once.

use constant IS_MODPERL => $ENV{MOD_PERL};
use subs qw(exit);
*iB::exit = IS_MODPERL ? \&Apache::exit : sub { CORE::exit };

# End Mod Perl Cleanup
######################################################

######################################################
# Lets create our own warn handler.
# This lets us filter out the 'useless' warns.

$SIG{__WARN__} = sub {
   my $wn = shift;
   return if $wn =~ /Use of uninitialized value/i;    #Most annoying
   return if $wn =~ /name "(?:.+?)" used only once/i; #Very annoying
   return if $wn =~ /Subroutine .+? redefined at/i;   #Very Very annoying mod_perl warnings
   warn $wn;
};

$SIG{__DIE__} = \&catch_die;

# If you want ikonboard to write to a warning log file
# if the process lasts for longer than 30 seconds, uncomment
# this line here, and the alarm( x ); lines (where x is, an
# integer is).

#$SIG{ALRM} = \&write_report;

# End of Warn handler
######################################################

# Get the config file

require "Boardinfo.cgi";
$iB::INFO = Boardinfo->new();
# Ensure a directory is specified for the public uploads
unless ($iB::INFO->{'PUBLIC_UPLOAD'}) {
    $iB::INFO->{'PUBLIC_UPLOAD'} = $iB::INFO->{'HTML_DIR'};
    $iB::INFO->{'PUBLIC_UPLOAD'} =~ s/non-cgi/uploads/;
}

######################################################
# Before we go any further, lets make sure the installer
# has deleted itself

if (  (-e $iB::INFO->{'IKON_DIR'}."installer.cgi")
   && (!(-e $iB::INFO->{'IKON_DIR'}."install.lock")) ) {
   &catch_die("FATAL ERROR:<br>The installer (installer.cgi) is still present in the root ikonboard ".
              "directory. Ikonboard will not run until this file is removed!<br>".
              "Please remove it. You may continue when removed by <a href='$ENV{HTTP_REFERER}'>clicking here</a>");
}

######################################################
# Lets get CGI.pm and do some set-up
# We'll be using CGI.pm until iCGI.pm
# is mod_perl compatible

use CGI;

# We need to configure a few things.

# Are we using an up to date version of CGI.pm?

if ( ($CGI::VERSION < '2.4') or ($use_ampersands == 1) ) {
    # If we are using an old version of CGI.pm
    # then we need to swop all semi-colons to
    # ampersands to ensure that everthing will
    # work right...
    $ENV{'QUERY_STRING'} =~ s:;:&:g;
}

$CGI::USE_PARAM_SEMICOLONS = 1;
$CGI::PRIVATE_TEMPFILES    = 1;
$CGI::HEADERS_ONCE         = 1;
$CGI::POST_MAX             = 500*1024;

# CGI upload temp files. You may want to uncomment this
# if you are getting CGITemp file errors

#$TempFile::TMPDIRECTORY    = $iB::INFO->{'DB_DIR'}.'Temp';

$iB::CGI = new CGI;

# Grab the incoming data

%iB::IN = map { &iB::_clean_key($_) => &iB::_clean_value($iB::CGI->param($_)) } $iB::CGI->param;


# Synchronise the AD value

$iB::IN{AD} ||= $iB::IN{CP};

# Read the stored cookies
# Due to the way we had cookies stored in
# iCGI.pm, we'll need a hash ref from CGI.pm

@iB::TEMP_COOKIE = $iB::CGI->cookie();
for my $c (@iB::TEMP_COOKIE) {
   # Only get 'our' cookies
   next unless $c =~ /^$iB::INFO->{'COOKIE_ID'}/;

   # Add it to our hash
   $iB::COOKIES->{$c} = $iB::CGI->cookie($c);
}

# End CGI set-up
######################################################
# Pre execution set-up
# Load up the needed libraries

require Lib::FUNC;
require Sessions;
require iDatabase::SQL;

# Get a Database connection
# Since we don't want to drop
# and create tables..
# creating the crypt key for db pass
    require 'Sources/ARC4.pm' or die "Cannot open ARC4";
    require 'Sources/MIME/Base64.pm' or die "Cannot open Base64";
    opendir (DIR, $iB::INFO->{'IKON_DIR'}.'Data');
    my @list = grep { !/\A\.{1,2}\Z/ } readdir(DIR);
    closedir(DIR);
    my @key  = grep { /.+?(\.pwd)\Z/ } @list;
    unless (scalar @key > 0) {
        my $file = &iB::my_gen_key();
        my $file_name = $iB::INFO->{'IKON_DIR'}.'/Data/' . $file . '.pwd';
        open (KEYF, ">" . $file_name ) or die "Cannot write to $file_name ($!)";
        print KEYF $file_name;
        close KEYF;
        chmod ( 0644, $file_name );
        $file = $file . '.pwd';
        my $ark4 = Crypt::ARC4->new($file); #preparing the crypting module
        my $OLD = Boardinfo->new();
        if ($iB::INFO->{'DB_PASS'}) {
            $OLD->{'DB_PASS'} = MIME::Base64::encode_base64($ark4->ARC4( $iB::INFO->{'DB_PASS'} )); # crypting the password
            $OLD->{'DB_PASS'} =~ s!\n\Z!!;
        }
        if ($iB::INFO->{'mySQL_DB_PASS'}) {
            $ark4 = Crypt::ARC4->new($file);
            $OLD->{'mySQL_DB_PASS'} = MIME::Base64::encode_base64($ark4->ARC4( $iB::INFO->{'mySQL_DB_PASS'} ));
            $OLD->{'mySQL_DB_PASS'} =~ s!\n\Z!!;
        }
        if ($iB::INFO->{'pgSQL_DB_PASS'}) {
            $ark4 = Crypt::ARC4->new($file);
            $OLD->{'pgSQL_DB_PASS'} = MIME::Base64::encode_base64($ark4->ARC4( $iB::INFO->{'pgSQL_DB_PASS'} ));
            $OLD->{'pgSQL_DB_PASS'} =~ s!\n\Z!!;
        }
        if ($iB::INFO->{'Oracle_DB_PASS'}) {
            $ark4 = Crypt::ARC4->new($file);
            $OLD->{'Oracle_DB_PASS'} = MIME::Base64::encode_base64($ark4->ARC4( $iB::INFO->{'Oracle_DB_PASS'} ));
            $OLD->{'Oracle_DB_PASS'} =~ s!\n\Z!!;
        }
        if ($iB::INFO->{'DBM_DB_PASS'}) {
            $ark4 = Crypt::ARC4->new($file);
            $OLD->{'DBM_DB_PASS'} = MIME::Base64::encode_base64($ark4->ARC4( $iB::INFO->{'DBM_DB_PASS'} ));
            $OLD->{'DBM_DB_PASS'} =~ s!\n\Z!!;
        }
        if ($^O eq 'MacOS' && ($^O eq 'MSWin32' || !Win32::IsWin95())) {
            $OLD->{'FLOCK'} = 0;
        }

        require 'Lib/ADMIN.pm';
        my $ADMIN = FUNC::ADMIN->new();
        $ADMIN->make_module( FILE     => "Boardinfo.cgi",
                             PKG_NAME => 'Boardinfo',
                             VALUES   => $OLD
                           );
    }
    unless ($iB::INFO->{'DB_DRIVER'} eq 'DBM') {
    for my $f (@key) {
        my $ark4 = Crypt::ARC4->new($f);
        $iB::INFO->{'DB_PASS'} = $ark4->ARC4( MIME::Base64::decode_base64($iB::INFO->{'DB_PASS'}) );# decrypting the pass
    }
    }

sub my_gen_key {
    my $obj = shift;
    my @Chars = (
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"
        );
  srand (time ^ $$ ^ unpack "%L*", `ps axww | gzip`);
  my $Password;
  for (my $i = 0; $i < 16; $i++) {
    $Password .= $Chars[ int ( rand ( $#Chars + 1 ) ) ];
  }
  return $Password;
}

my $create = $iB::INFO->{DB_DRIVER} eq 'DBM' ? 1 : 0;
my $drop   = $iB::INFO->{DB_DRIVER} eq 'DBM' ? 1 : 0;

my $db    = iDatabase::SQL->new( DATABASE  => $iB::INFO->{'DB_NAME'},
                                 DB_DIR    => $iB::INFO->{'DB_DIR'},
                                 IP        => $iB::INFO->{'DB_IP'},
                                 PORT      => $iB::INFO->{'DB_PORT'},
                                 USERNAME  => $iB::INFO->{'DB_USER'},
                                 PASSWORD  => $iB::INFO->{'DB_PASS'},
                                 DB_PREFIX => $iB::INFO->{'DB_PREFIX'},
                                 DB_DRIVER => $iB::INFO->{'DB_DRIVER'},
                                 ATTR      => { allow_create => $create,
                                                allow_drop   => $drop,
                                              },
                               );

# Check for errors
&catch_die( $db->error ) if $db->error;

# Set up module interfaces

my $std   = FUNC::STD->new();
my $sess  = Sessions->new();

# Start the Benchmark clock

$iB::TT0  = new Benchmark;
warn "Benchmark initialization error in ikonboard.cgi: $!\n" unless ($iB::TT0);

# We can't always rely on REMOTE_ADDR for the IP
# address of the user accessing the script

$iB::IN{'IP_ADDRESS'} = $ENV{'HTTP_X_FORWARDED_FOR'} || $ENV{'REMOTE_ADDR'};

# 99% of the time, the HTTP_X_FORWARDED_FOR comes from a proxy server, like the
# squid accelerator used on some apache servers that wish to deliver cached content
# This means that the IP address can be multiple, like: 212.12.12.12, 212.12.12.14
# So...

($iB::IN{'IP_ADDRESS'}) = $iB::IN{IP_ADDRESS} =~ /^(.+?)(,|$)/;


# A few small pieces of set-up

$iB::VERSION     = '3.1.5A';
$iB::CONTENT     = $iB::CONTENT = {'HTTP' => '0'};

# Check the POST referrer and check the
# server load (if applicable)

$std->ValidateEntry($db);

# Load the users skin
$iB::SKIN   = $std->LoadSkin();
# Grab the standard skin file
do $iB::SKIN->{'DIR'} . '/Universal.pm';

# ( ADDED HERE BY KEVaholic00 FOR BUG FIX #168, COMMENTED OUT BELOW )
# Lets add on the skin name for ease of use.
my $images_url                   = $iB::INFO->{'IMAGES_URL'};

$iB::INFO->{'IMAGES_URL'}       .= '/' . $iB::SKIN->{'FULL_DIR'};
# ( END ADDITION )

# Load the member, and load the Active user stats
# if applicable

$iB::MEMBER = $sess->authenticate($db) unless $iB::IN{'act'} eq 'Reg';
$iB::ACTIVE = $sess->active_users($db);

# Configure some URL's

$iB::INFO->{'TEAM_ICON_URL'}     = $images_url . '/team_icons';
$iB::INFO->{'AVATARS_URL'}       = $images_url . '/avatars';
$iB::INFO->{'EMOTICONS_URL'}     = $images_url . '/emoticons';
$iB::INFO->{'MIME_IMG'}          = $images_url . '/mime_types';

# Configure some Paths

$iB::INFO->{'PRIVATE_UPLOAD'}    = $iB::INFO->{'DB_DIR'}.'Temp';

# ( COMMENTED OUT BY KEVaholic00 FOR BUG FIX #168 AND PASTED ABOVE )
## Now we've read in all the data that needs the 'raw' IMAGES_URL
## Lets add on the skin name for ease of use.
#$iB::INFO->{'IMAGES_URL'}       .= '/' . $iB::SKIN->{'FULL_DIR'};
# ( END COMMENT )

# End set up

catch_die($@) unless (defined(eval { iB::Action($db) }));
iB::exit();

#+------------------------------------------------------------------------------------------------------

sub Action {
    my $db = shift;

    # Uncomment the following line to write an error for processes over
    # 30 seconds.
    #alarm(30);
    # As the admin link has "AD=1" in it, some firewalls/banner blockers
    # will produce a blank page, not what we want.
    # As Ikonboard 3 has used AD=1 since day 1, I don't want to have to weed
    # through the code looking for every single instance it's been used, so
    # we merely use perls' excellent reg-ex to turn AD into CP. For those who
    # have bookmarked their adminCP link, we allow AD=1 to be used also.

    if ($iB::IN{'AD'} or $iB::IN{CP}) {
        require Admin::Functions;
        my $ad = Admin::Functions->new();
        $ad->process($db);
        return "0 but true";
    }

    $iB::MEMBER_GROUP->{'ACCESS_OFFLINE'} = $iB::MEMBER_GROUP->{'ACCESS_OFFLINE'}; #Another time to quiet warnings.
    unless ($iB::INFO->{'B_ONLINE'}) {
        unless ($iB::MEMBER_GROUP->{'ACCESS_OFFLINE'}) {
            my $output = FUNC::Output->new();
            $output->board_offline( DB  => $db);
            return "0 but true";
        }
    }

    # Are we forcing log ins?
    if ( !$iB::MEMBER->{'MEMBER_ID'} and $iB::INFO->{'FORCE_LOGIN'} ) {
        unless ($iB::IN{act} eq 'Reg' or $iB::IN{act} eq 'LostPass') {
            $sess->do_log_in( DB    => $db,
                              MSG   => 'force_login',
                              OR    => 1,
                            );              # No need to remove cookies and set up the SKIN path
            return "0 but true";
        }
    }

    my %Mode = (  ST        => ['Topic'              , 'ShowTopic'   ],
                  SF        => ['Forum'              , 'ShowForum'   ],
                  SR        => ['Forum'              , 'ShowRules'   ],
                  SC        => ['Boards'             , 'ShowStart'   ],
                  Search    => ['Search::api'        , 'Process'     ],
                  Online    => ['Online'             , 'Process'     ],
                  Legends   => ['Legends'            , 'Process'     ],
                  Help      => ['Help'               , 'Process'     ],
                  Members   => ['Memberlist'         , 'Process'     ],
                  Reg       => ['Register'           , 'Process'     ],
                  Post      => ['Post'               , 'Process'     ],
                  Login     => ['LogInOut'           , 'Process'     ],
                  Profile   => ['Profile'            , 'Process'     ],
                  UserCP    => ['UserCP::Menu'       , 'Process'     ],
                  Mod       => ['Moderate'           , 'Process'     ],
                  Poll      => ['iPoll'              , 'Process'     ],
                  Print     => ['PrintPage'          , 'Process'     ],
                  Invite    => ['Misc::Invite'       , 'Process'     ],
                  Mail      => ['Misc::MailMember'   , 'Process'     ],
                  Cookies   => ['Misc::Cookies'      , 'Process'     ],
                  PMarkers  => ['Misc::PMarkers'     , 'Process'     ],
                  Forward   => ['Misc::Forward'      , 'Process'     ],
                  AOL       => ['Misc::AOL'          , 'Process'     ],
                  ICQ       => ['Misc::ICQ'          , 'Process'     ],
                  MSN       => ['Misc::MSN'          , 'Process'     ],
                  Attach    => ['Misc::Attachments'  , 'Process'     ],
                  Msg       => ['UserCP::Messenger'  , 'Process'     ],
                  MSV       => ['UserCP::Messview'   , 'Process'     ],
                  MSS       => ['UserCP::Messsend'   , 'Process'     ],
                  MSM       => ['Massmsend'  ,         'Process'     ],
                  Subs      => ['Misc::Track'        , 'Process'     ],
                  LostPass  => ['UserCP::Lostpass'   , 'Process'     ],
                  BoardIdx  => ['Boards'             , 'ShowStart'   ],
                  ModCP     => ['ModCP'              , 'Process'     ],
                  Calendar  => ['Calendar'           , 'Process'     ],
                  Report    => ['Misc::Report'       , 'Process'     ],
                  Warn      => ['Warn'               , 'Process'     ],
                  NotePad   => ['NotePad'            , 'Process'     ],
                  NW        => ['Newest'             , 'shownewest'  ],
                  ModSet    => ['ModSet'             , 'Process'     ],
                 # Welcome   => ['Welcome'            , 'Process'     ],
                  Posters   => ['Posters'            , 'showposter'  ],
                 # Happybd   => ['Happybd'            , 'Process'     ],
                  Tsearch   => ['Tsearch'            , 'Process'     ],
                  Team      => ['Team'               , 'Process'     ],
                  Statistics => ['Statistics'            , 'Process'     ],
               );


    $iB::IN{'act'} = 'BoardIdx' if $iB::IN{'act'} eq '';
    $iB::IN{'act'} = 'BoardIdx' unless exists $Mode{ $iB::IN{'act'} };

    # Nice little hack to save writing loads of subroutines for each action.
    # It builds the code from the %Mode hash, depending on the contents of 'act'
    # For example, the eval'd code may look like:

    #      use Topic;
    #      my $idx = Topic->new();
    #         $idx->ShowTopic($db);

    my $code = 'require '.$Mode{ $iB::IN{'act'} }[0].';'.
               'my $idx = '.$Mode{ $iB::IN{'act'} }[0].'->new();'.
                  '$idx->' .$Mode{ $iB::IN{'act'} }[1].'($db);';


    eval $code;

    # Uncomment the following line to write an error for processes over
    # 30 seconds.
    #alarm(0);

    # Because we wrap this subroutine in an eval statement, with the XOR (||)
    # operator that prints our error message, we need to return a true value
    # or mod_perl will print out an empty error message on each page.

    return "0 but true";
}

# A few sanitization routines

sub _clean_key {
    my $key = shift;
    return '' unless defined $key;
    $key =~ s!\.\.!!g;
    $key =~ s!\_\_(.+?)\_\_!!g;
    &iB::_trim($key);
    $key =~ m!^([\w\.-\_]+)$!;
    return $1;
}

sub _clean_value {
    my $Tmp = shift;
    return '' unless defined $Tmp;
    $Tmp =~ s|&|&amp;|g;
    $Tmp =~ s|<!--|&#60;&#33;--|g; $Tmp =~ s|-->|--&#62;|g;
    $Tmp =~ s|<script|&#60;script|ig;
    $Tmp =~ s|>|&gt;|g;
    $Tmp =~ s|<|&lt;|g;
    $Tmp =~ s|"|&quot;|g;
    $Tmp =~ s!^\s+!!;
    $Tmp =~ s!\s+$!!;
    $Tmp =~ s|  | &nbsp;|g;
    $Tmp =~ s!\|!&#124;!g;
    $Tmp =~ s|\n|<br>|g;
    $Tmp =~ s|\$|&#036;|g;
    $Tmp =~ s|\r||g;
    $Tmp =~ s|\_\_(.+?)\_\_||g;
    $Tmp =~ s|\\|&#92;|g;
    $Tmp =~ s|!|&#33;|g;
    $Tmp =~ s|\'|&#39;|g;
    return $Tmp;
}

sub _trim {
  my @tr = @_;
  return unless @_;
  for (@tr) { s!^\s+!!; s!\s+$!!; }
  return wantarray ? @tr : $tr[0];
}

sub catch_die {
    my $error = shift;
    return if $error =~ m!Simple.pm!;
    # Sun solaris bug when used with DB_file.
    # I truly long for the day when universal acutally means universal.
    return if $error =~ m!Magick.pm!;
    return if $error =~ m#Can't locate XSLoader.pm#;


    $error =~ s!$ENV{'DOCUMENT_ROOT'}!/your/path/to!i;

    my ($msg, $path) = split " at ",$error;

    print "Content-type: text/html\n\n";
    print qq~
    <html>
    <head><title>Ikonboard CGI Error</title></head>
    <body bgcolor='#FFFFFF'>
    <font face='Trebuchet MS, Verdana, Arial' size='6' color='#333366'>Ikonboard CGI Error</font>
    <hr size='1' color='#000000' noshade>
    <font face='arial, verdana' size='3' color='#00000'>
    Ikonboard has exited with the following error:
    <br><br><b>$msg</b><br><br>This error was reported at: <font color='#000099' face='Courier, Courier New, Verdana, Arial'>$path</font>
    <br><br><font size='3' color='#990000'><b>Please note that your 'real' paths have been removed to protect your information.</b></font>
    </font>
    </body>
    </html>
    ~;

    iB::exit();
}

sub write_report {

    open LOG, ">>$iB::INFO->{DB_DIR}"."timeout_log";
    print LOG "[Warning] Process ID ($$) ran for longer than 30 seconds:\nAct: $iB::IN{act}\nQuery String: $ENV{QUERY_STRING}\nMember: $iB::MEMBER->{MEMBER_NAME}\nReferer: $ENV{HTTP_REFERER}\n----------------------\n";
    close LOG;
    alarm(0); #Reset the alarm
    return;
}

1;
