#!/usr/bin/perl
# index.cgi

require './tomcat-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection

# Check if config file exists
if (! -r $config{'tomcat_config'}) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_econfig', "<tt>$config{'tomcat_config'}</tt>",
		    "$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
}

if(-f "$module_root_directory/setup.cgi"){
	&redirect("setup.cgi?mode=checks");
	exit;
}

my %version = get_catalina_version();

&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
	&help_search_link("tomcat", "man", "doc", "google"), undef, undef,
	"Tomcat $version{'number'} / Java $version{'jvm'}");

push(@links, "edit_manual.cgi");
push(@titles, $text{'manual_title'});
push(@icons, "images/edit-file.png");

push(@links, "edit_war.cgi");
push(@titles, $text{'wars_title'});
push(@icons, "images/war.png");

push(@links, "edit_libs.cgi");
push(@titles, $text{'libs_title'});
push(@icons, "images/jar.png");

push(@links, "edit_java.cgi");
push(@titles, $text{'java_title'});
push(@icons, "images/java.png");

push(@links, "edit_proxy.cgi");
push(@titles, $text{'proxy_title'});
push(@icons, "images/mapping.png");

&icons_table(\@links, \@titles, \@icons, 2);

# Check if tomcat is running
print &ui_hr().&ui_buttons_start();
my ($running, $status) = &tomcat_service_ctl('status');
print "$status<br>";
if ($running == 1) {
	# Running .. offer to apply changes and stop
	print &ui_buttons_row("stop.cgi", $text{'index_stop'}, "$text{'index_stopmsg'}");
	print &ui_buttons_row("restart.cgi", $text{'index_restart'}, "$text{'index_restartmsg'}");
}else {
	# Not running .. offer to start
	print &ui_buttons_row("start.cgi", $text{'index_start'}, $text{'index_startmsg'});
}

#Check for an update of tomcat, once a day
#my $latest_ver = upgrade_available();
#if($latest_ver){
#	print &ui_buttons_row("tomcat_upgrade.cgi", $text{'index_upgrade'}, "Tomcat will be updated to  $latest_ver. All WARs will be moved and config will be copied to new install!");
#}
#print &ui_buttons_end();

&ui_print_footer("/", $text{"index"});
