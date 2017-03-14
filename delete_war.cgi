#!/usr/bin/perl

require './tomcat-lib.pl';
use File::Path 'rmtree';

&ReadParse();

&error_setup($text{'delete_err'});
&ui_print_header(undef, $text{'delete_title'}, "");

@mods = split(/\0/, $in{'mod'});
@mods || &error($text{'delete_enone'});

#stop tomcat server
$err = stop_tomcat();
print "Stopping Tomcat server<br>";
&webmin_log("stop");
if ($err){
	&error($err);
	&ui_print_footer("", $text{'index_return'});
	exit;
}

#delete each of the specified directories
foreach $d (@mods) {
	print "Removing $config{'tomcat_webapps'}/$d<br>";
	if(rmtree("$config{'tomcat_webapps'}/$d") == 0){
		&error("Failed to remove application");
		&ui_print_footer("", $text{'index_return'});
		exit;
	}

	if($in{'rmwar'}){
		$war = "$config{'tomcat_webapps'}/$d.war";
		if( -f $war){
			unlink($war);
			print "<tt>Removed $war<tt><br>";
		}
	}
}

#start tomcat server
$err = start_tomcat();
print "Starting Tomcat server<br>";
&webmin_log("start");
if ($err){
	&error($err);
	&ui_print_footer("", $text{'index_return'});
	exit;
}
print "Uninstall successful<br>";


&ui_print_footer("", $text{'index_return'});

