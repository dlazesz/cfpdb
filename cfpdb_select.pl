#!/usr/bin/perl -w

use strict;
use POSIX;

use POSIX "locale_h";
setlocale ( LC_ALL, "hu_HU" );
use locale;

use lib "/home/joker/cvswork/perllib";
require "dbu.pm";
require "utils.pm";

use DBI;

use File::Basename;
use Getopt::Std;
my $PROG = basename ( $0 );

my %opt;
getopts ( "hd", \%opt ) or usage();
usage() if $opt{h}; # or ...

my $DEBUG = ( defined $opt{d} ? 1 : 0 );

# indexek az adatbázisból kijövõ sorokhoz
my $NAME         = 1; # mert az id a 0. :)
my $BEGIN        = 2;
my $END          = 3;
my $LOCATION     = 4;
my $SUBMISSION   = 5;
my $NOTIFICATION = 6;
my $CAMERAREADY  = 7;
my $HOMEPAGE     = 8;
my $REMARK       = 9;

my $ALERT = '-ALERT'; # XXX gagyi

# --- program starts HERE
my $db = DBI->connect( "dbi:SQLite:cfp.db" )
  || die "Cannot connect to DB: $DBI::errstr";

my $res = $db->selectall_arrayref( q( SELECT * FROM cfp ));

$db->disconnect;

# rendezni kell
my $sorted = sort_nextdate( $res );

if ( $DEBUG ) {
  my $cnt = 1;
  foreach my $r ( @$sorted ) {
    print "$cnt $r->[$NAME] $r->[$SUBMISSION] > $r->[$NOTIFICATION] > $r->[$CAMERAREADY] :: $r->[$BEGIN] -- $r->[$END]\n";
    ++$cnt;
  }
}

# XML-lé alakítás
# rögtön 1 fájlba teszem (bár lehet, hogy ezt külön lépésként kéne XXX)

print <<E;
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE confs SYSTEM "cfps.dtd">
<?xml-stylesheet type="text/xsl" href="cfps_plain.xsl.xml"?>
<confs>
E

print '<separator text="Lesz..."/>';

my $alert = 1; # az elején mindig az alert-esek lesznek...
my $volt = ''; # még nem volt kiírva az, hogy 'Volt...' :)

foreach my $r ( @$sorted ) {
  # 'Volt...' belehekkelese :)
  my $x = join ',', @$r;
  if ( $x !~ m/$ALERT/ ) { $alert = ''; }
  if ( not $alert and not $volt ) {
    print '<separator text="Volt..."/>';
    $volt = 1;
  }
  # kiiratas
  print printxml( $r );
}

print <<E;
</confs>
E

# --- subs
# XML-lé alakítás
# alert dolgot is kezeli :)
# header nélkül, hogy egybe lehessen tenni egy nagyob XML fájlba
sub printxml {
  my $r = shift;

  my %alert = ();
  foreach my $cond ( ( $SUBMISSION,
                       $NOTIFICATION,
                       $CAMERAREADY,
                       $BEGIN,
                       $END ) ) {
    if ( $r->[$cond] =~ s/$ALERT// ) {
      $alert{$cond} = ' alert="yes"';
    } else {
      $alert{$cond} = '';
    }
  }

  my $xml = <<E;
<conf>
  <name>$r->[$NAME]</name>
  <begin date="$r->[$BEGIN]"$alert{$BEGIN}/>
  <end date="$r->[$END]"$alert{$END}/>
  <location>$r->[$LOCATION]</location>
  <submission date="$r->[$SUBMISSION]"$alert{$SUBMISSION}/>
  <notification date="$r->[$NOTIFICATION]"$alert{$NOTIFICATION}/>
  <cameraready date="$r->[$CAMERAREADY]"$alert{$CAMERAREADY}/>
  <homepage url="$r->[$HOMEPAGE]"/>
  <remark>...</remark>
</conf>
E
  return $xml;
}

sub sort_nextdate {
  my $r = shift;

  my @date = localtime( time );
  my $now = ($date[5] + 1900) . '-' .
            utils::ketjegyure( $date[4]+1 ) . '-' .
            utils::ketjegyure( $date[3] );

  my %elmult = ();
  my %lesz = ();

  # biztos nem hatékony, talán jobb lenne csak az indexeket rendezgetni XXX
  foreach my $r ( @$r ) {

    # ami már nem aktuális
print "--- $r->[$NAME]\n" if $DEBUG;
    if ( $r->[$END] lt $now ) {
      if ( exists $elmult{$r->[$END]} ) { # szokásos: tömb a hash-érték
        push @{ $elmult{$r->[$END]} }, $r;
      } else {
        $elmult{$r->[$END]} = [ $r ];
      }

    # ami még aktuális
    } else {
      # azt nézzük, hogy a konf-hoz tartozó MELYIK dátum aktuális most!
      foreach my $cond ( ( $r->[$SUBMISSION],
                           $r->[$NOTIFICATION],
                           $r->[$CAMERAREADY],
                           $r->[$BEGIN],
                           $r->[$END] ) ) {
print "cond=$cond (now=$now)\n" if $DEBUG;
        if ( $cond ge $now ) {
print "ALERTÁLÁS!\n" if $DEBUG;
          $cond .= $ALERT; # fú ez jó így, fogja módosítani $r-t?
                           # úgy néz ki, hogy igen, mert mûködik. :)
          if ( exists $lesz{$cond} ) { # szokásos: tömb a hash-érték
            push @{ $lesz{$cond} }, $r;
          } else {
            $lesz{$cond} = [ $r ];
          }
          last;
        }
      }
    }
  }

  my @ret = ();
  foreach my $r ( ( sort keys %lesz ) ) { push @ret, @{ $lesz{$r} }; }
  foreach my $r ( ( reverse sort keys %elmult ) ) { push @ret, @{ $elmult{$r} }; }
  return \@ret;
}

# prints usage info
sub usage {
  print STDERR <<USAGE;
Usage: $PROG -f FILE [-d] [-h]
cfpdb -- select all conferences in appropriate order.
  -d       turns on debugging
  -h       prints this help message & exit
Report bugs to <joker\@nytud.hu>.
USAGE
  exit 1;
}

