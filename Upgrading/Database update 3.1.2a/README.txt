########################################################
#                                                      #
#   3.1.3 Atler MySQL Table script                     #
#						       #	
#  This will update your 3.1.2a MySQL to work          #
#  with v3.1.3                                         #
#						       #
#  http://ikonboard.net                                #
########################################################

Open the 313_atlertable.cgi file in a plain text editor
Uncomment line 32 and enter the path to your board.

Example: $iB::PTH = '/home/site/public_html/cgi-bin/';

Save and Upload in ASCII mode to the same directory as the ikonboard.cgi file. 
Set permissions (chmod) to 755.

Run in your browser,

Example: http://www.yoursite.com/cgi-bin/forum/313_atlertable.cgi

You must also decrypt your database password in order for the altertable.cgi 
script to be able to connect to the database. You can do this by opening up 
Boardinfo.cgi and editing the following two lines (Change 'yourpassword' to 
your database password):

'DB_PASS'                      => q!yourpassword!, 

and

'mySQL_DB_PASS'         => q!yourpassword!,

The script will encrypt the password after the upgrade process is complete. 