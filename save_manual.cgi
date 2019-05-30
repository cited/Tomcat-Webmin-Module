#!/usr/bin/perl
# Update a manually edited config file

require './tomcat-lib.pl';
&error_setup($text{'manual_err'});
&ReadParseMime();

my $catalina_home = get_catalina_home();

# Work out the file
@files = (	"$catalina_home/bin/setenv.sh",
			"$catalina_home/conf/context.xml",
			"$catalina_home/conf/server.xml",
			"$catalina_home/conf/tomcat-users.xml",
			"$catalina_home/conf/web.xml");
&indexof($in{'file'}, @files) >= 0 || &error($text{'manual_efile'});
$in{'data'} =~ s/\r//g;
$in{'data'} =~ /\S/ || &error($text{'manual_edata'});

# Write to it
&open_lock_tempfile(DATA, ">$in{'file'}");
&print_tempfile(DATA, $in{'data'});
&close_tempfile(DATA);

&webmin_log("manual", undef, $in{'file'});
&redirect("");

