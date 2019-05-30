#!/usr/bin/perl
# start.cgi
# Start the tomcat daemon

require './tomcat-lib.pl';
&ReadParse();
&error_setup($text{'start_err'});
my ($rc, $err) = tomcat_service_ctl('start');
if ($rc != 0){
	&ui_print_header(undef, $text{'index_title'}, "");
	&error($err);
	&ui_print_footer("", $text{'index_return'});
	exit;
}
&redirect("");
