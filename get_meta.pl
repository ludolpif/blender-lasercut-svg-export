#!/usr/bin/env perl
use strict;
use warnings;
if ( $#ARGV < 1 ) {
	print STDERR "Usage: $0 <plugin_src_path> <meta_keyname> [meta_keyname]...\n";
	exit(1);
}
my $path = (shift @ARGV) . "/blender_manifest.toml";
open(MANIFEST, "<:encoding(UTF-8)", $path) or die("Can't read $path");

my ($id, $version);
while(<MANIFEST>) {
	$id=$1 if /^id = "([^"]+)"/;
	$version=$1 if /^version = "([^"]+)"/;
}
while(my $arg = shift @ARGV) {
	if ( $arg eq "id" ) { print "$id\n"; }
	if ( $arg eq "version" ) { print "$version\n"; }
	if ( $arg eq "zipglob" ) { print "$id-*.zip\n"; }
	if ( $arg eq "zipname" ) { print "$id-$version.zip\n"; }
}
