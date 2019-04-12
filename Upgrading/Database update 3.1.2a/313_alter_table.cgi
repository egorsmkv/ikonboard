#!/usr/bin/perl -w
package iB;

#
# Updates the Sql tables for 3.1.2a to 3.13
#


#################################################################################
# Ikonboard v3.1.5 by South West Telephone Inc.
# No parts of this script can be used outside Ikonboard without prior consent.
#
# More information available from <support@southwestcom.us>
# (c)2011 South West Telephone Inc.
#
# http://www.ikonboard.net
#
# Please Read the license for more information
#################################################################################

use strict;

BEGIN {

    $iB::PTH = '.';

    #### Getting errors? Enter your path below!
    # Remeber to remove the comment first (# is a comment)


    #$iB::PTH = '/home/site/public_html/cgi-bin/';


    unshift (@INC, "$iB::PTH");
    unshift (@INC, "$iB::PTH/Data");
    unshift (@INC, "$iB::PTH/Sources");
    unshift (@INC, "$iB::PTH/Skin");
    unshift (@INC, "$iB::PTH/Languages");
    unshift (@INC, "$iB::PTH/Sources/Lib");

}
#+------------------------------------------------------------------------------------------------------
use CGI;
use CGI::Carp "fatalsToBrowser";
$iB::Q = new CGI;
use DBI;
require "Boardinfo.cgi";
$iB::INFO = Boardinfo->new();

### What are we doing?

if ($iB::Q->param('act') eq 'run') {
    iB::run();
} else {
    iB::show();
}




sub show {
    print $iB::Q->header();
    print $iB::Q->start_html();

    print qq~<b><font size=4>Alter Tables</font></b>
             <br><br><font size='3'>This convertor will update your 3.1.2 mySQL tables to the new format.</font>
             <a href='313_alter_table.cgi?act=run'>Run the upgrader</a>
            ~;
    print $iB::Q->end_html();
}


sub run {
    # Get the board info file.
    my $info = Boardinfo->new();

    # Get a DB connection

    my $dsn  = "DBI:mysql:$info->{'DB_NAME'}:$info->{'DB_IP'}";
    $dsn    .= ":$info->{'DB_PORT'}" if $info->{'DB_PORT'};

    my $dbh = DBI->connect($dsn, $info->{'DB_USER'}, $info->{'DB_PASS'});

    if ($DBI::errstr) {
        &errors("mySQL connection error: $DBI::errstr");
    }

    my $pre = $info->{DB_PREFIX};

  print $iB::Q->header();
  print $iB::Q->start_html("Alter Table Output");

  ##############################################################

  print "Altering Table: ".$pre."active_sessions...<br><br>";

  $dbh->do("ALTER TABLE ".$pre."active_sessions CHANGE USER_AGENT USER_AGENT varchar(255) NULL");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(255)from USER_AGENT column<br>";

  ##############################################################
  
  ##############################################################

  print "Altering Table: ".$pre."address_books...<br><br>";

  $dbh->do("ALTER TABLE ".$pre."address_books CHANGE IN_MEMBER_DESC IN_MEMBER_DESC varchar(128) NULL");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128)from IN_MEMBER_DESC  column<br>";

  ##############################################################
  
  ##############################################################

  print "Altering Table: ".$pre."attachments...<br><br>";

  $dbh->do("ALTER TABLE ".$pre."attachments CHANGE FILE_NAME FILE_NAME varchar(255) NULL");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(255)from FILE_NAME column<br>";

  ##############################################################

  print "<br>Altering Table: ".$pre."categories...<br><br>";

  $dbh->do("ALTER TABLE ".$pre."categories ADD DISP_POS tinyint(1)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Added column DISP_POS.<br>";

  $dbh->do("ALTER TABLE ".$pre."categories CHANGE VIEW VIEW varchar(128)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128) from VIEW.<br>";

  ##############################################################

   print "<br>Altering Table: ".$pre."forum_info...<br><br>";

  $dbh->do("ALTER TABLE ".$pre."forum_info CHANGE FORUM_START_THREADS FORUM_START_THREADS varchar(128)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128) from FORUM_START_THREADS.<br>";

  $dbh->do("ALTER TABLE ".$pre."forum_info CHANGE FORUM_VIEW_THREADS FORUM_VIEW_THREADS varchar(128)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128) from FORUM_VIEW_THREADS.<br>";

  $dbh->do("ALTER TABLE ".$pre."forum_info CHANGE FORUM_REPLY_THREADS FORUM_REPLY_THREADS varchar(128)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128) from FORUM_REPLY_THREADS.<br>";


  ##############################################################

  print "<br>Altering Table: ".$pre."member_profiles...<br><br>";
  
  ###Corrected section
  $dbh->do("ALTER TABLE ".$pre."member_profiles CHANGE MEMBER_TITLE MEMBER_TITLE varchar(128) NULL");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "Changed attribute to varchar(128)from MEMBER_TITLE  column<br>";

  $dbh->do("ALTER TABLE ".$pre."member_profiles ADD MEMBER_AVADIR text");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "MEMBER_AVADIR column added to table<br>";

  $dbh->do("ALTER TABLE ".$pre."member_profiles ADD RATINGS text");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "RATINGS column added to table<br>";

  $dbh->do("ALTER TABLE ".$pre."member_profiles ADD POST_PER_DAY int(3)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "  POST_PER_DAY column added to table<br>";

  $dbh->do("ALTER TABLE ".$pre."member_profiles ADD POST_PERIOD int(2)");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "  POST_PERIOD column added to table<br>";
  
  $dbh->do("ALTER TABLE ".$pre."member_profiles ADD RATED text");
    &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  print "  RATED column added to table<br>";

  ##############################################################

  print "<br>Updating Table: ".$pre."templates...<br><br>";

 my (@template, $welcome, $happy) = @_;

 open (FILE, "$iB::INFO->{'IKON_DIR'}INSTALL_DATA/global_template.txt") or
                    { die "The global_template.txt could not be opened"};
      @template = <FILE>;
      close FILE;

  $dbh->do(" UPDATE ".$pre."templates SET TEMPLATE = '@template' WHERE ID = 'global'");
  &errors("mySQL error: $DBI::errstr") if $DBI::errstr;

#       $welcome = "Welcome to Ikonboard";

#  $dbh->do(" INSERT INTO ".$pre."templates SET ID = 'welcome', TEMPLATE = '$welcome', NAME = 'Welcome' ");
#   &errors("mySQL error: $DBI::errstr") if $DBI::errstr;
#    #INSERT INTO `ib_templates` SET ID = 'welcome', TEMPLATE = 'Welcome', NAME = 'Welcome'

#       $happy = "Happy Birthday";

# $dbh->do(" INSERT INTO ".$pre."templates SET ID = 'birthday', TEMPLATE = '$happy', Name = 'Happy Birthday'");
#   &errors("mySQL error: $DBI::errstr") if $DBI::errstr;


  print " Updated templates column<br>";

  #####################################################################

  print "All done, you may now remove this script";

  print $iB::Q->end_html();
  exit;
}


sub errors {
  my $error = shift;
  print $iB::Q->header();
  print $iB::Q->start_html("Fatal Errors");
  print "ERROR: $error";
  print $iB::Q->end_html();
  exit;
}

1