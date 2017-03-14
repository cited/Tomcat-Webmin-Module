#!/usr/bin/perl
# index.cgi

require './tomcat-lib.pl';


# Check if config file exists
if (! -r $config{'tomcat_config'}) {
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_econfig', "<tt>$config{'tomcat_config'}</tt>",
		    "$gconfig{'webprefix'}/config.cgi?$module_name"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
}

# Check if tomcat exists
if (!&has_command($config{'tomcat_path'})) {
        &ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
        print "The Tomcat server executable <tt>$config{'tomcat_path'}</tt> does not exist";
        print &ui_config_link("If you have Tomcat installed, adjust the module configuration to use the correct path.", "module configuration");
        print "The Apache Tomcat package can be automatically installed by Webmin.";
        $escaped_pkg = &quote_escape($config{'tomcat_pkg'});
        print "<a href='../software/install_pack.cgi?source=3&update=$escaped_pkg&return=%2E%2E%2Ftomcat%2F&returndesc=Tomcat%20Server&caller=tomcat'>Click here</a> to have it downloaded and installed.";
        &ui_print_footer("/", $text{"index"});
        exit;
}


# Check if tomcat is the right version
%version = &get_tomcat_version();
if (!%version) {
	# Unknown version
	&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
	print &text('index_eversion', "<tt>$config{'tomcat_path'}</tt>",
		    "$gconfig{'webprefix'}/config.cgi?$module_name",
		    "<tt>$config{'tomcat_path'} -h</tt>",
		    "<pre>$out</pre>"),"<p>\n";
	&ui_print_footer("/", $text{"index"});
	exit;
}
&write_file("$module_config_directory/version", \%version);

&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1, 0,
	&help_search_link("tomcat", "man", "doc", "google"), undef, undef,
	"$version{'number'} / $version{'jvm'}");


#push(@links, "edit_users.cgi");
#push(@titles, $text{'users_title'});
#push(@icons, "images/users.gif");

push(@links, "edit_manual.cgi");
push(@titles, $text{'manual_title'});
push(@icons, "images/manual.gif");

push(@links, "edit_war.cgi");
push(@titles, $text{'wars_title'});
push(@icons, "images/war.png");

&icons_table(\@links, \@titles, \@icons, 2);

# Check if tomcat is running
$pid = &get_tomcat_pid();
print &ui_hr();
print &ui_buttons_start();

if ($pid) {
	# Running .. offer to apply changes and stop
	print &ui_buttons_row("stop.cgi", $text{'index_stop'}, "$text{'index_stopmsg'}, running with PID $pid");
}else {
	# Not running .. offer to start
	print &ui_buttons_row("start.cgi", $text{'index_start'}, $text{'index_startmsg'});
}
print &ui_buttons_end();

&ui_print_footer("/", $text{"index"});
