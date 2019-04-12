#!/usr/bin/perl -w
package iB;

#
# Updates the Sql tables for 3.0.1 and up to 3.1.2
#


##########################################################
#| Ikonboard 3 by the Ikonboard Team
#|
#| No parts of this script can be used outside Ikonboard
#| without prior consent.
#| You must keep this header intact and all copyright
#| links visible.
#| For support, visit http://forums.ikonboard.com
#|
#| (c)2006 PitBOSS Entertainment
#| Web: <http://www.ikonboard.com>
#| Please read the license for more information.
#| http://www.ikonboard.com/terms.htm
#########################################################

use strict;

BEGIN {

    $iB::PTH = '.';
    
    #### Getting errors? Enter your path below!
    # Remeber to remove the comment first (# is a comment)
    
    
    $iB::PTH = '/home/dakota2/public_html/cgi-bin/ib312';
    
    
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
#require 'Sources/Lib/FUNC.pm';
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
             <a href='alter_tablenew.cgi?act=run'>Run the upgrader</a>
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
  #####################################################################
  
  print "<br>Updating Table: ".$pre."templates...<br><br>";
  
  my $obj = shift;
  
      # Get the boardinfo file..
  
      require 'Data/Boardinfo.cgi' or &iB::install_error( "Cannot locate /Data/Boardinfo.cgi to require" );
  
      $iB::INFO = Boardinfo->new();
  
      # Get the iDatabase driver.
      require 'Sources/iDatabase/SQL.pm' or iB::install_error( "Cannot locate the needed iDatabase driver to require" );
  
  
  
      my $db    = iDatabase::SQL->new( DATABASE  => $iB::INFO->{'DB_NAME'},
                                       DB_DIR    => $iB::INFO->{'DB_DIR'},
                                       IP        => $iB::INFO->{'DB_IP'},
                                       PORT      => $iB::INFO->{'DB_PORT'},
                                       USERNAME  => $iB::INFO->{'DB_USER'},
                                       PASSWORD  => $iB::INFO->{'DB_PASS'},
                                       DB_PREFIX => $iB::INFO->{'DB_PREFIX'},
                                       DB_DRIVER => $iB::INFO->{'DB_DRIVER'},
                                       ATTR      => { allow_create => 0,
                                                      allow_drop   => 0,
                                                    },
                                   );
  
  
  my $template;
  my $limit;

       $template = open (FILE, "$iB::INFO->{'IKON_DIR'}INSTALL_DATA/global_template.html");
              unless($template) 
                    { die "The global_template.html could not be opened"};
                    
     my @news = <FILE>;
    close FILE;

    my $text = join '', @news;               
                    
         if ($limit) {
        $text = substr($text, 0, $limit);
    }     
          
          $db->update( TABLE  => 'templates',
	                   KEY    => 'global',
	                   VALUES => { TEMPLATE => $template }
	                 );

          
          
          
          
     # $dbh->update( TABLE => 'templates',
     #                   ID    => 'global',
     #                   TEMPLATE => { $text } );
                                          
                                       
                    
                    
  #$dbh->do(" UPDATE ".$pre."templates SET TEMPLATE = '$template' WHERE ID = 'global'");
  #&errors("mySQL error: $DBI::errstr") if $DBI::errstr;
  #print " Updated templates column<br>";
  
 # UPDATE `ib_templates` SET `TEMPLATE` = '<html>',
#`NAME` = NULL WHERE `ID` = 'global' LIMIT 1 ;
  
  
  
  
  
  
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
  