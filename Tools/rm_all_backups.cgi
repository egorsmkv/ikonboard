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

    print qq~<b><font size=4>Remove all Back-ups - **USE THIS WITH CAUTION**</font></b>
             <br><br><font size='3'>This script will remove all old Back-ups. Download any that you want to save before running this script!
             <br><br><font color='red'><b>REMOVE THIS SCRIPT AFTER USE!</b></font><br><br>
             <a href='rm_all_backups.cgi?act=run'>Run the script now!</a>
            ~;
    print $iB::Q->end_html();
}


sub run {


    $iB::INFO->{'BACKUP_DIR'} ||= $iB::INFO->{'IKON_DIR'}."BACK_UP";

    rmtree $iB::INFO->{'BACKUP_DIR'};

    mkdir ($iB::INFO->{'BACKUP_DIR'}, 0777);

    print $iB::Q->header();
    print $iB::Q->start_html();
    print "BACK-UP Directory Emptied";
    print $iB::Q->end_html();
}
