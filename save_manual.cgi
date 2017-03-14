#!/usr/bin/perl
# Update a manually edited config file

require './tomcat-lib.pl';
&error_setup($text{'manual_err'});
&ReadParseMime();

# Work out the file
@files = (	 "$config{'tomcat_env'}",
			"$config{'tomcat_etc'}/context.xml",
			"$config{'tomcat_etc'}/server.xml",
			"$config{'tomcat_etc'}/tomcat-users.xml",
			"$config{'tomcat_etc'}/web.xml");
&indexof($in{'file'}, @files) >= 0 || &error($text{'manual_efile'});
$in{'data'} =~ s/\r//g;
$in{'data'} =~ /\S/ || &error($text{'manual_edata'});

# Write to it
&open_lock_tempfile(DATA, ">$in{'file'}");
&print_tempfile(DATA, $in{'data'});
&close_tempfile(DATA);

&webmin_log("manual", undef, $in{'file'});
&redirect("");

