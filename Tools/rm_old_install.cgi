#!/usr/bin/perl
package iB;

#
# Removes all old files created by the tar files
#



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

    print qq~<b><font size=4>Remove old installation</font></b>
             <br><br><font size='3'>This script will remove all unpacked tar files, it won't remove the tar files themselves, just the directories and files created by the installer.
             <br><br>
             <a href='rm_old_install.cgi?act=run'>Run the script now!</a>
            ~;
    print $iB::Q->end_html();
}


sub run {
    my $message;

    rmtree "$iB::PTH/Data";
    rmtree "$iB::PTH/Database";
    rmtree "$iB::PTH/Languages";
    rmtree "$iB::PTH/Sources";
    rmtree "$iB::PTH/Skin";
    rmtree "$iB::INFO->{'HTML_DIR'}non-cgi";

    print $iB::Q->header();
    print $iB::Q->start_html();
    print "All done, you can now reinstall iB3";
    print $iB::Q->end_html();
}
