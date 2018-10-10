#!/usr/bin/perl -w

use strict;
use POSIX;

use POSIX "locale_h";
setlocale ( LC_ALL, "hu_HU" );
use locale;

use lib "/home/joker/cvswork/perllib";
require "dbu.pm";

use DBI;

use File::Basename;
use Getopt::Std;
my $PROG = basename ( $0 );

my %opt;
getopts ( "f:hd", \%opt ) or usage();
usage() if $opt{h} or not $opt{f}; # or ...

my $DEBUG = ( defined $opt{d} ? 1 : 0 );

my $FILE = $opt{f};

open F, "$FILE" or die "Problem opening file: $!\n";

undef $/;
my $cfp = <F>;

# kiszedegetjük az adatokat az XML-bõl kézzel. Hm..
my ( $name )         = $cfp =~ m#<name>(.*?)</name>#;
my ( $begin )        = $cfp =~ m#<begin date="([^"]*)"/>#;
my ( $end )          = $cfp =~ m#<end date="([^"]*)"/>#;
my ( $location )     = $cfp =~ m#<location>(.*?)</location>#;
my ( $submission )   = $cfp =~ m#<submission date="([^"]*)"/>#;
my ( $notification ) = $cfp =~ m#<notification date="([^"]*)"/>#;
my ( $cameraready )  = $cfp =~ m#<cameraready date="([^"]*)"/>#;
my ( $homepage )     = $cfp =~ m#<homepage url="([^"]*)"/>#;
my ( $remark )       = $cfp =~ m#<remark>(.*?)</remark>#;

# kicsit gagyi
$name         = he( $name );
$begin        = he( $begin );
$end          = he( $end );
$location     = he( $location );
$submission   = he( $submission );
$notification = he( $notification );
$cameraready  = he( $cameraready );
$homepage     = he( $homepage );
$remark       = he( $remark );

# --- program starts HERE
my $db = DBI->connect( "dbi:SQLite:cfp.db" )
  || die "Cannot connect to DB: $DBI::errstr";

my $st = $db->do( "INSERT INTO cfp
          ( name, begin, end, location,
            submission, notification, cameraready,
            homepage, remark )
          VALUES
          ( '$name', '$begin', '$end', '$location',
            '$submission', '$notification', '$cameraready',
            '$homepage', '$remark' )" );
#print "$st\n";

$db->disconnect;

# --- subs
sub he { # html encode, hogy ezek a jelek "többé" ne okozzanak gondot
  my $s = shift;
  $s =~ s/</&lt;/g;
  $s =~ s/>/&gt;/g;
  $s =~ s/"/&quot;/g;
  $s =~ s/'/&apos;/g;
  $s =~ s/[&]/&amp;/g;
  return $s;
}

# prints usage info
sub usage {
  print STDERR <<USAGE;
Usage: $PROG -f FILE [-d] [-h]
cfpdb -- insert one XML file to DB.
  -f FILE  the XML file to insert (obligatory)
  -d       turns on debugging
  -h       prints this help message & exit
Report bugs to <joker\@nytud.hu>.
USAGE
  exit 1;
}

