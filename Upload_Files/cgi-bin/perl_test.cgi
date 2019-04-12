#!/usr/bin/perl -w

# Change the above line to reflect your server's path to perl

##############################################################################
# This script checks your paths, prints them and also any environment
# variables.  Useful for troubleshooting purposes.
#
# Copyright 2018 Implux Designs Inc.
#
##############################################################################

use CGI::Carp "fatalsToBrowser";

use strict;
no strict "vars";

require CGI;


$style = "BODY          {font: 10pt arial}
#red          {font: 10pt arial;color:red;font-weight:bold}
#bold         {font: 10pt arial;font-weight:bold}
#version      {font: 10pt arial;color:blue;font-weight:bold}
TABLE, TR, TD {font: 10pt arial;font-weight:bold}
#error        {font: 10pt arial;background:#EEEEEE;border:1px solid black; padding-top: 8px; padding-right: 8px; padding-bottom: 8px; padding-left: 8px; text-indent: 8pt}
#plain        {font: 10pt arial}";

#---------------------------------
# Variables
#---------------------------------

$path = $0;
if (eval{require Cwd;}){
use Cwd;
$path = cwd();
}

if ($path eq ''){
$path = "Unobtainable - contact your server administrator";
}

if ($^O eq "MSWin32"){
$platform = "WINDOWS";
} elsif ($^O eq "UNIX"){
  $platform = "UNIX";
  } elsif ($^O eq "linux"){
    $platform = "Linux";
    } else{
      $platform = "Unknown";
      }

$cgiver = $CGI::VERSION;

$test_version = '3.1.5a';

#----------------------------------
# Checking for various perl modules
#----------------------------------

eval { require DB_File };
$db_file  = $@ ? 'No' : 'Yes';

eval { require CGI };
$cgi      = $@ ? 'No' : 'Yes';

eval { require DBI };
$dbi      = $@ ? 'No' : 'Yes';

eval { require Mysql };
$mysql    = $@ ? 'No' : 'Yes';

eval { require Image::Magick };
$magick  = $@ ? 'No' : 'Yes';

#----------------------------------
# Printing the results out
#----------------------------------

print "Content-type: text/html\n\n";
print qq~
<html>
<head>
<title>Ikonboard Path and Environment Test</title>
<style>
$style
</style>
</head>
<body>
<center><h4>Ikonboard Path and Environment Test</h4></center>
<p>This script checks your paths and environment variables and prints the results based on its best information available.

<hr noshade>
<br><br><a id="bold">The absolute path to this script is: </a><a id="red">$path</a>, on a <a id=red>$platform</a> based platform.
<br><a id="bold">This server is running perl version: </a><a id="version">$]</a>.
<br><a id="bold">DOCUMENT_ROOT: </a><a id="red">$ENV{'DOCUMENT_ROOT'}</a>.
<br><a id="bold">CGI Version: </a><a id="version">$cgiver</a>
<br><br>
~;

if ($] < 5){ # check to see if the server is running Perl 5 or higher
print "\n<br><br><a id=\"red\">Note: You're server is running lower than Perl 5.  You will have to
update it to 5 or higher to run Ikonboard.</a>\n\n";
$ver_true = undef;
} else{
  $ver_true = 1;
  }

print qq~
<table>
<tr><td>Has DB_File Perl module installed?</td><td>$db_file</td></tr>
<tr><td>Has CGI Perl module installed?</td><td>$cgi</td></tr>
<tr><td>Has DBI Perl module installed?</td><td>$dbi</td></tr>
<tr><td>Has DBD-Mysql Perl module installed?</td><td>$mysql</td></tr>
<tr><td>Has Image Magick Perl module installed?</td><td>$magick</td></tr>
</table>

~;

print '<br><div id="error"><b>Results:</b>
<br><br>';

#----Suggest possible databases----

if ($ver_true eq undef){
print '<a id="red">Your server is not running a high enough version of Perl to run iB</a>';
} elsif ($db_file eq 'No'){
  print '<a id="red">You do not have the db_file perl module installed on this server. You will not be able to run Ikonboard.</a>';
  } elsif (($db_file eq 'Yes') && ($mysql eq 'No') && ($dbi eq 'No')){
    print '<a id="red">Your server meets the requirements for a DBM database; but you will be unable to install an SQL version of the board, as the DBD-Mysql and DBI packages need to be installed</a>';
    } elsif(($db_file eq 'Yes') && ($mysql eq 'Yes') && ($dbi eq 'no')){
      print '<a id="red">You meet requirements for DBM database, but to use a SQL database you will need to install the DBI Perl Module</a>';
      } elsif (($db_file eq 'Yes') && ($dbi eq 'Yes') && ($mysql eq 'Yes')){
       print '<a id="red">You can run either a DBM or SQL database as all required perl modules are installed. You will need to contact your server administrator for SQL usage information.</a>';
        }
  if ($magick eq 'No'){
       print '<br><a id="red">You cannot use the HRI Registration Secure key as the required ImageMagick module is not installed.</a>';
}

#----------------------------------

print "</div>";

print "<br><br><b>Environment:</b>\n<br><br>
<table>\n";

foreach $key (keys(%ENV)){
print "<tr><td>\$ENV{$key}:</td><td id=\"plain\">$ENV{$key}</td></tr>\n";
}

print "</table><br>
<b>Include Path:\n</b>
<br><ul>";

  foreach $path (@INC){
  print "<li>$path</li>\n";
  }

        print qq~
<br><br><center><font size=1>Version $test_version \n<br>&copy; 2018 <a href="http://impluxdesigns.com">Implux Designs Inc.</a></font></center>
</body>
</html>
~;