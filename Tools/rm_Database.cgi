#!/usr/bin/perl
package iB;



use strict;

BEGIN {

    #Get script path

    use Cwd;
    my $cwd = cwd();
    $iB::PTH = $cwd;
}
#+------------------------------------------------------------------------------------------------------
use CGI;
use CGI::Carp "fatalsToBrowser";
$iB::Q = new CGI;

use File::Path;

require "$iB::PTH/Data/Boardinfo.cgi";

$iB::INFO = Boardinfo->new();

    if ($iB::Q->param('act') eq 'run') {

        iB::run();

    } else {

        iB::show();
    }




sub show {
    print $iB::Q->header();
    print $iB::Q->start_html();

    print qq~<b><font size=4>Remove your current Database - **USE THIS WITH CAUTION**</font></b>
             <br><br><font size='3'>This script will remove your current, populated Database - only do this if you want to clobber all of your database data!
             <br><br><font color='red'><b>REMOVE THIS SCRIPT AFTER USE!</b></font><br><br>
             <a href='rm_Database.cgi?act=run'>Run the script now!</a>
            ~;
    print $iB::Q->end_html();
}


sub run {



    rmtree $iB::INFO->{'DB_DIR'};

    mkdir ($iB::INFO->{'DB_DIR'}, 0777);

    print $iB::Q->header();
    print $iB::Q->start_html();
    print "Database Directory Emptied";
    print $iB::Q->end_html();
}
