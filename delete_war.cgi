#!/usr/bin/perl

require './tomcat-lib.pl';
use File::Path 'rmtree';

&ReadParse();

&error_setup($text{'delete_err'});
&ui_print_header(undef, $text{'delete_title'}, "");

@mods = split(/\0/, $in{'mod'});
@mods || &error($text{'delete_enone'});

tomcat_service_ctl('stop');

#delete each of the specified directories
my $catalina_home = get_catalina_home();
foreach $d (@mods) {
	print "Removing $catalina_home/$d<br>";
	if(rmtree("$catalina_home/webapps/$d") == 0){
		&error("Failed to remove application");
		&ui_print_footer("", $text{'index_return'});
		exit;
	}

	if($in{'rmwar'}){
		$war = "$catalina_home/webapps/$d.war";
		if( -f $war){
			unlink($war);
			print "<tt>Removed $war</tt><br>";
		}
	}
}
print "Uninstall successful<br>";

tomcat_service_ctl('start');

&ui_print_footer("", $text{'index_return'});

