#!/usr/bin/perl

require './tomcat-lib.pl';
require './java-lib.pl';
require '../webmin/webmin-lib.pl';	#require
foreign_require('software', 'software-lib.pl');

use File::Basename;

sub extract_java_archive{
	my $jdk_archive = $_[0];

	my $java_dir = '/usr/java';
	if( ! -d $java_dir){
		&make_dir($java_dir, 0755, 1);
	}

	$cmd_out='';
	$cmd_err='';
	print "<hr>Extracting $jdk_archive to $java_dir...<br>";
	local $out = &execute_command("tar -x -v --overwrite -f \"$jdk_archive\" -C/usr/java", undef, \$cmd_out, \$cmd_err, 0, 0);

	my $jdk_tar_first_line = ( split /\n/, $cmd_out )[0];
	my $jdk_dir = $java_dir."/".(split /\//, $jdk_tar_first_line)[0];

	if($cmd_err){
		$cmd_err = s/\n/<br>/g;
		&error("Error: tar: $cmd_err");
	}else{
		$cmd_out = s/\n/<br>/g;
		print &html_escape($cmd_out);
	}

	&set_ownership_permissions('root','root', 0755, $jdk_dir);
	&execute_command("chown -R root:root $jdk_dir", undef, \$cmd_out, \$cmd_err, 0, 0);
	if($cmd_err){
		$cmd_err = s/\n/<br>/g;
		&error("Error: chown: $cmd_err");
	}

	return $jdk_dir;
}

#$| = 1;

if ($ENV{REQUEST_METHOD} eq "POST") {
        &ReadParse(\%getin, "GET");
        &ReadParseMime(undef, \&read_parse_mime_callback, [ $getin{'id'} ]);
        }
else {
        &ReadParse();
        $no_upload = 1;
      }
&error_setup($text{'install_err'});
&ui_print_header(undef, $text{'java_title'}, "");

my $jdk_path = '';
if ($in{'source'} == 100) {

	my ($jdk_name, $url) = split /=/, $in{'jdk_ver'};
	$in{'url'} = $url;
	$in{'source'} = 2;

	my $jdk_archive = process_file_source();
	$jdk_path    = extract_java_archive($jdk_archive);

}elsif($in{'source'} == 200){

	my $jdk_name = (split /=/, $in{'openjdk_ver'})[1];
	my $openjdk_pkg = $jdk_name;
	if($in{'openjdk_headless'} == 1){
		$openjdk_pkg .= '-headless';
	}

	software::update_system_install($openjdk_pkg, undef);
	$jdk_path = get_jdk_dir_by_name($jdk_name);
}

if($in{'def_jdk'} == 1){
	set_default_java($jdk_path);
}

print "<hr>Done<br>";
&ui_print_footer("", $text{'index_return'});
