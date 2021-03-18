#!/usr/bin/perl -wT
#  Perl program to play word-find game
#
#  There were several similar free software programs out there, but I didn't
#  like their complexity and/or wasn't familiar with the languages they were
#  written in.  I figured it would be easier to just write a simple Perl
#  script.  Now it is a CGI script, a lot longer than the original but still
#  pretty simple.
#
#  Copyright 2015, 2021 David Breese
#  MIT License

use 5.010;
use CGI;
# TODO: Migrate to templates.
# TODO: Migrate to a different web framework.  See 
#   https://metacpan.org/pod/CGI::Alternatives

use strict;


# CONSTANTS
##############################################

# Where to find the dice files.  Each dice file should be a newline-separated
# list of "dice" (and the number of items in the list should be a square
# number).  Each "die" should be a string of six characters: the six sides of
# that die (though in reality any number of characters per string will work).
my $diceDir = "$ENV{DOCUMENT_ROOT}/boogle-dice";

# Initialize user-configurable board parameters to defaults.
my $big = 1;
my $caps = 0;
my $fontsize = 3;
my $orientStyle = "up";

# Formatting for the grid
my $colspacer = " ";
my $colspacing = 3;
my $rowspacer = "\n";
my $rowspacing = 2;

# List of the different ways a letter can be facing.  This hash translates
# commonsense names to CSS "rotate" arguments.
my %orientations = (
    "up" => "0deg",
    "right" => "90deg",
    "down" => "180deg",
    "left" => "270deg"
);
my @orientationNames = keys %orientations;

# SUBROUTINES
##############################################

# Select an orientation for a letter
#
# Arguments: none
#
# Returns: A string matching a key in %orientations
#
# TODO: Don't read parent scope variables directly; pass them in as arguments.
sub select_orientation {
    if ($orientStyle eq "random") {
        return @orientationNames[int(rand(scalar @orientationNames))];
    } else {
        return "up"
    }
}

# Process parameters received via CGI
#
# Arguments:
#   $q : The CGI object for this web page
#
# Returns:
#   $big: 1 if we want a 5x5 grid, 0 for a 4x4
#   $caps: 1 if we want all capital dice, 0 for lowercase
#   $fontsize: integer indicating what font size to use
#   $orientStyle: string "random" for randomly oriented letters,
#                   "up" for all letters upright
#
# TODO: Replace magic numbers with constants.
sub process_cgi_params {
    my($q) = shift(@_);
    if ( $q->param('big')           =~ /[01]/        ) {
        $big = 
        $q->param('big');
    }
    if ( $q->param('caps')          =~ /[01]/        ) {
        $caps =
        $q->param('caps');
    }
    if ( $q->param('fontsize')      >  0             ) {
        $fontsize =
        $q->param('fontsize');
    }
    if ( $q->param('orientstyle')   =~ /(random|up)/ ) {
        $orientStyle =
        $q->param('orientstyle');
    }
    return ($big, $caps, $fontsize, $orientStyle);
}

# Open the dice file, and read in the dice.
#
# Arguments:
#   $diceDir : Parent directory in which to find the dice file.
#   $big: 1 if we want a 5x5 grid, 0 for a 4x4
#   $caps: 1 if we want all capital dice, 0 for lowercase
#
# Returns: A list of strings, each string represents 1 Boogle die.
sub read_dice {
    my ($diceDir, $big, $caps) = @_;

    my $ndice;
    my $case;
    
    if ($big) { $ndice = "25"; }
        else { $ndice = "16"; }
    if ($caps) { $case = "upper"; }
        else { $case = "lower"; }
    
    my $dicePath = "${diceDir}/${ndice}-${case}case.txt";
    
    open (DICE, $dicePath) or
        die "Error: could not open dice list at $dicePath. Exiting...";
    
    # Read the dice into a Perl list
    my @dice;
    
    while (my $diestring = <DICE>) {
        chomp $diestring;
        push @dice, $diestring;
    }

    return @dice;
}

# Calculate the size of the game board grid
#
# Arguments:
#   @dice : A list of strings, each string represents 1 Boogle die.
#
# Returns: The number of rows/columns in the smallest (square) game board 
#           grid that exactly fits all the listed Boogle dice.
sub calc_grid_size {
    my @dice = @_;

    my $numcols = sqrt($#dice + 1);
    unless ($numcols == int($numcols)) {
      die "Error: non-square number of dice!";
    }

    return $numcols;
}

#  This loop "rolls" the game board and prints results, with formatting to make
#  it a grid.  Note we *remove* each die from @dice after choosing it.  This is
#  our way to avoid re-picking dice we've already used.
#
#  Might consider using a Fisher-Yates shuffle instead (explained in perlfaq4).
#
#  Arguments:
#    @dice : A list of strings, each string represents 1 Boogle die.  Must
#        containe a square number of dice/strings.
#
#  Returns: An nxn array of letters, representing a Boogle game board.
sub roll_game_letters {
    my @dice = @_;

    my $numcols = calc_grid_size(@dice);

    srand (time ^ $$); # get a random seed

    my @gameLetters = ();

    while ($dice[0]) {
        my @row = ();

        # TODO: This is just a for loop
        my $col = 1;
        while ($col <= $numcols) {

            my $diepick = int(rand($#dice + 1));  # Pick a $die at random...
            my $die = splice(@dice, $diepick, 1);  # Take it out of the array...
            # Pick a $side of the die at random.
            my $dieroll = int(rand(length($die)));
            my $side = substr($die, $dieroll, 1);
    
            push @row, $side;

            $col++;

        }

        push @gameLetters, [ @row ];  # push a _reference_ to @row; see perllol
    }

    return @gameLetters;
}

# READING DATA AND ROLLING THE BOARD
##############################################

my $q = CGI->new();

($big, $caps, $fontsize, $orientStyle) = process_cgi_params($q);

my @dice = read_dice($diceDir, $big, $caps);

my @gameLetters = roll_game_letters(@dice);

# PRINTING THE HTML
##############################################

say $q->header(), $q->start_html('Boogle');

say '<style TYPE="text/css"><!--';
say "table, th, td { border:1px solid black; }";
say 'th, td { ';
# TODO: Rethink the fontsize option
say "font-size:${fontsize}em; ";
say 'width:1.8em; ';
say 'height:1.5em; ';
say 'text-align:center; ';
say '}';
# Set up a CSS class for each direction a letter can be oriented
if ( $orientStyle eq "random" ) {
    foreach my $o (@orientationNames) {
        say ".letter-$o { transform: rotate($orientations{$o}); }"
    }
}
say "--></style>";


say "<h1>Boogle</h1>";


# THE BOOGLE GAME BOARD

say '<table>';

foreach my $rowref (@gameLetters) {

    print "<tr>";

    my @row = @$rowref;

    foreach my $letter (@row) {

        if ($letter =~ /[Qq]/) { $letter .= "u"; } # Append a u to any q.

        my $orientationName = select_orientation(); # Pick an orientation.

        print qq|<td><div class="letter-$orientationName">$letter</div></td>|;

    }

    say "</tr>";

}

say "</table>";
say '<p>To play again, hit refresh.</p>';
say '<p>Or <a href="/configure-boogle.html">adjust the options</a>.</p>';

say $q->end_html();
