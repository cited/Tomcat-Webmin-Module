#!/usr/bin/perl
# start.cgi
# Start the tomcat daemon

require './tomcat-lib.pl';
&ReadParse();
&error_setup($text{'start_err'});
$err = &start_tomcat();
&error($err) if ($err);
&webmin_log("start");
&redirect("");
