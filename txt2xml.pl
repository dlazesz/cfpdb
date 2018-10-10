#!/usr/bin/perl -w

use strict;
use POSIX;

use POSIX "locale_h";
setlocale ( LC_ALL, "hu_HU" );
use locale;

use lib "/home/joker/cvswork/perllib";
require "utils.pm";

use File::Basename;
use Getopt::Std;
my $PROG = basename ( $0 );

my %opt;
getopts ( "hd", \%opt ) or usage();
usage() if $opt{h}; # or ...

my $DEBUG = ( defined $opt{d} ? 1 : 0 );

my ( $name, $begin, $end, $location ) = ( '', '', '' );
my ( $subm, $noti, $came ) = ( '', '', '' );
my ( $url, $remark ) = ( '', '' );

my $file_cnt = 1;

# --- program starts HERE
while (<>) {
  chomp;
  my $s = $_;
  #   ! LingDokKonf 11. (2007-12-06 -- 2007-12-07, Szeged)
  if ( /^  [!ex+-] (.*) \(([0-9]{4}-..-..) -- ([0-9]{4}-..-..), ([^)]*)\)/ ) {
    ( $name, $begin, $end, $location ) = ( $1, $2, $3, $4 );
  }
  elsif ( /^    . subm: (....-..-..)/ ) { $subm = $1; }
  elsif ( /^    . noti: (....-..-..)/ ) { $noti = $1; }
  elsif ( /^    . came: (....-..-..)/ ) { $came = $1; }
  elsif ( /^    (https?:\/\/[^ ]+)/ ) { $url = $1; }
  elsif ( /^$/ ) {
    if ( $name ) {
      my $xml = <<END;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE conf SYSTEM "cfp.dtd">
<?xml-stylesheet type="text/xsl" href="cfp_plain.xsl.xml"?>
<conf>
  <name>$name</name>
  <begin date="$begin"/>
  <end date="$end"/>
  <location>$location</location>
  <submission date="$subm"/>
  <notification date="$noti"/>
  <cameraready date="$came"/>
  <homepage url="$url"/>
  <remark>$remark</remark>
</conf>
END
      my $file_cnt_str = utils::ketjegyure( $file_cnt );
      open F, "> conf.$file_cnt_str.xml";
      print F $xml;
      close F;
      ++$file_cnt;
    }
    ( $name, $begin, $end, $location ) = ( '', '', '' );
    # $name a marker-változó, hogy van-e valami
    ( $subm, $noti, $came ) = ( '', '', '' );
    ( $url, $remark ) = ( '', '' );
  }
  elsif ( $name and /^ *(.+)/ ) { $remark .= $1; }
}

# --- subs

# prints usage info
sub usage {
  print STDERR <<USAGE;
Usage: $PROG [-d] [-h]
Konferencia-infót a szöveges formámból XML-re alakít.
  -d  turns on debugging
  -h  prints this help message & exit
Report bugs to <joker\@nytud.hu>.
USAGE
  exit 1;
}

