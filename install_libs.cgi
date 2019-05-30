#!/usr/bin/perl

require './tomcat-lib.pl';

use File::Basename;
use File::Path 'rmtree';

sub inst_error{
	print "<b>$main::whatfailed : $_[0]</b> <p>\n";
	&ui_print_footer("", $text{'index_return'});
	exit;
}

sub unzip_lib{
	my $file  = $_[0];
	my @suffixlist = ('\.zip');
	($lib_name,$path,$lib_suffix) = fileparse($file,@suffixlist);

	my $unzip_dir = "/tmp/.webmin/$lib_name";

	#if old temp extension dir exist, remove it
	#if( -d $unzip_dir and rmtree($unzip_dir) == 0){
	#	&error("Failed to remove temp extension dir");
	#	&ui_print_footer("", $text{'index_return'});
	#	exit;
	#}
	&make_dir($unzip_dir, 0754, 1);

	my $unzip_out;
	my $unzip_err;
	print "<hr>Unzipping to $unzip_dir ...<br>";
	local $out = &execute_command("unzip -u \"$file\" -d \"$unzip_dir\"", undef, \$unzip_out, \$unzip_err, 0, 0);

	if($unzip_err){
		&error("Error: unzip: $unzip_err");
	}else{
		$unzip_out = s/\r\n/<br>/g;
		print &html_escape($unzip_out);
	}
	return $unzip_dir;
}

if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) {
	&ReadParseMime();
}else {
	&ReadParse();
	$no_upload = 1;
}

$| = 1;
&ui_print_header(undef, $text{'libs_install_title'}, "");

my $lib_file = process_file_source();
my @suffixlist = ('\.zip', '\.jar');
($lib_name,$path,$lib_suffix) = fileparse($lib_file,@suffixlist);

my $unzip_dir = '';
my @lib_jars;

#Check if its a .zip or .jar
print "Source: $lib_file<br>";
if($lib_suffix eq ".zip"){
	$unzip_dir = unzip_lib($lib_file);

	#make a list of extension jars
	opendir(DIR, $unzip_dir) or die $!;
	@lib_jars = grep { $_ = $unzip_dir.'/'.$_ ; -f && /\.jar$/ } readdir(DIR);
	closedir(DIR);

}elsif($lib_suffix eq ".jar"){
	push(@lib_jars, $lib_file);
}else{
	&error("Error: Unsupported file type $lib_suffix");
	&ui_print_footer("", $text{'index_return'});
}

print "<hr> Installing $lib_name files...<br>";
my $catalina_home = get_catalina_home();

#move jars to Tomcat lib and save list of installed jars to lib file
open(my $fh, '>', "$module_config_directory/lib_$lib_name.list") or die "open:$!";
foreach $j (@lib_jars) {
	#move jars to Tomcat lib
	if(!move("$j", "$catalina_home/lib/")){
		&error("Error: Can't move file: $!");
	}
	my $j_name = basename($j);
	&set_ownership_permissions('tomcat','tomcat', 0444, "$catalina_home/lib/$j_name");

	print "$catalina_home/lib/$j_name<br>";
	print $fh "$j_name=$catalina_home/lib/$j_name\n";
}
close $fh;

print "<hr>Done.<br>";

if($unzip_dir ne ''){
	&rmtree($unzip_dir);	#remove temp dir
}

&ui_print_footer("", $text{'index_return'});
