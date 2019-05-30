#!/usr/bin/perl

use File::Path 'rmtree';

require './tomcat-lib.pl';
require './java-lib.pl';
require '../webmin/webmin-lib.pl';	#For OS Fetection
&ReadParse();

&error_setup($text{'delete_err'});

my $jdk_name = $in{'inst_jdk'};
$jdk_name || &error($text{'delete_enone'});

my $jdk_dir = get_jdk_dir_by_name($jdk_name);
my $def_jdk = is_default_jdk($jdk_dir);

if(($def_jdk == 1) and ($in{'rm_def_jdk'} == 0)){

	&ui_print_header(undef, $text{'delete_title'}, "");
	print "Uninstall stopped, since $jdk_dir is default JDK.<br>";

}else{

	if($jdk_name =~ /.*openjdk.*/){
		&redirect("/software/search.cgi?search=$jdk_name");
		return;
	}

	&ui_print_header(undef, $text{'delete_title'}, "");
	
	print "Removing $jdk_dir...<br>";

	if($def_jdk == 1){
		unset_default_java($jdk_dir);
	}

	if( -d $jdk_dir){
		rmtree($jdk_dir);
	}

	print "<hr>Uninstall of <tt>$jdk_name</tt> is successful<br>";
}

&ui_print_footer("", $text{'index_return'});
