#!/usr/bin/perl

require './tomcat-lib.pl';
require './java-lib.pl';
require '../webmin/webmin-lib.pl';	#require

use File::Basename;

&ReadParse();
&error_setup($text{'install_err'});

&ui_print_header(undef, $text{'java_title'}, "");

my $jdk_name = $in{'inst_jdk2'};
$jdk_name || &error($text{'delete_enone'});

my $jdk_dir = get_jdk_dir_by_name($jdk_name);

if(is_default_jdk($jdk_dir) == 1){
	print "$jdk_dir is already set as default JDK.<br>";
}else{
	set_default_java($jdk_dir);
}

print "<hr>Done<br>";
&ui_print_footer("", $text{'index_return'});
