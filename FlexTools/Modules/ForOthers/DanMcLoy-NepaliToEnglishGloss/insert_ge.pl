# Inserts a \ge field after every \d_nep field that contains
# a word glossed in nep_en_gloss.txt
# WARNING:  ANY EXISTING \ge FIELDS WILL BE DELETED!!!!

use utf8;
use strict;

my $nepFld = 'd_nep';
my $enFld = 'ge';
my $glossFile = 'nep_en_gloss.txt';

# Prepare files for I/O
my $infile = 'Lhomi Dictionary Project-sfm.txt';
my $outfile = 'out.txt';
# my $infile = $ARGV[0];
# my $outfile = $ARGV[1];
# die "usage:\n\tperl $0 INFILE.txt OUTFILE.txt\n" unless $ARGV[1];
open (IN, "<:encoding(UTF-8)", $infile) or die "Can't open $infile\n";
open (OUT, ">:encoding(UTF-8)", $outfile) or die "Can't write to $outfile\n";
open (GLOSS, "<:encoding(UTF-8)", $glossFile) or die "Can't open $glossFile\n";
my (%ge, $ge, $de, $ctGe);
while (<GLOSS>) {
	if (/(.*)\t(.*)/) {
		$ge = $2;
		$de = devEssence($1);
		if (defined $ge{$de}) {
			$ge{$de} = " / $ge";
		} else {
			$ge{$de} = $ge;
			$ctGe++;
		}
	}
}
print "Loaded $ctGe glosses...\n";

# Process and output
my $ct = 0;
my $ctTry = 0;
while (<IN>) {
	if (/^\\$nepFld\s+(\S.*)/) {
		$de = devEssence($1);
		$ctTry++;
		if (defined $ge{$de}) {
			print OUT $_;
			print OUT "\\$enFld $ge{$de}\n";
			$ct++;
		} else {
			print OUT $_;
		}
	} elsif (/^\\$enFld\s+(\S.*)/) {
		warn "Deleting original \\$enFld field: $1\n";
		# don't output original ge field
	} else {
		print OUT $_;
	}
}
close IN;
close OUT;
print "Processed $ctTry \\$nepFld fields.\nMatched and inserted $ct glosses.\n";

sub devEssence {
	$de = $_[0];
	# $de =~ tr/इउकिकुशष/ईऊकीकूसस/;
	$de =~ s/इ/ई/g;
	$de =~ s/उ/ऊ/g;
	$de =~ s/ि/ी/g;
	$de =~ s/ु/ू/g;
	$de =~ s/श/स/g;
	$de =~ s/ष/स/g;
	$de =~ s/[\x{200c}\x{200d} \-]//g;
	return $de;
}