#!/usr/bin/perl -w

use strict;
use POSIX;

use POSIX "locale_h";
setlocale ( LC_ALL, "hu_HU" );
use locale;

use DBI;

use File::Basename;
use Getopt::Std;
my $PROG = basename ( $0 );

my %opt;
getopts ( "hd", \%opt ) or usage();
usage() if $opt{h}; # or ...

my $DEBUG = ( defined $opt{d} ? 1 : 0 );

# --- program starts HERE
my $db = DBI->connect( "dbi:SQLite:cfp.db" )
  || die "Cannot connect to DB: $DBI::errstr";

$db->do( "CREATE TABLE cfp (
  id            INTEGER PRIMARY KEY,
  name          VARCHAR(100),
  begin         DATE,
  end           DATE,
  location      VARCHAR(100),
  submission    DATE,
  notification  DATE,
  cameraready   DATE,
  homepage      VARCHAR(200),
  remark        VARCHAR(2000)
)" );

$db->disconnect;

# --- subs

# prints usage info
sub usage {
  print STDERR <<USAGE;
Usage: $PROG [-d] [-h]
cfp -- database creation.
  -d  turns on debugging
  -h  prints this help message & exit
Report bugs to <joker\@nytud.hu>.
USAGE
  exit 1;
}

