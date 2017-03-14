#!/usr/bin/perl

require './tomcat-lib.pl';
use File::Basename;

sub inst_error{
	print "<b>$main::whatfailed : $_[0]</b> <p>\n";
	&ui_print_footer("", $text{'index_return'});
	exit;
}

if ($ENV{REQUEST_METHOD} eq "POST") { &ReadParseMime(); }
else { &ReadParse(); $no_upload = 1; }

$| = 1;
$theme_no_table = 1 if ($in{'source'} == 2 || $in{'source'} == 4);
&ui_print_header(undef, $text{'install_title'}, "");

if ($in{'source'} == 0) {
	# from local file
	&error_setup(&text('install_err1', $in{'file'}));
	$file = $in{'file'};
	if (!(-r $file)) { &inst_error($text{'install_efile'}); }
	}
elsif ($in{'source'} == 1) {
	# from uploaded file
	&error_setup($text{'install_err2'});
	$need_unlink = 1;
	if ($no_upload) {
                &inst_error($text{'install_ebrowser'});
                }
	$file = &transname(&file_basename($in{'upload_filename'}));
	open(MOD, ">$file");
	binmode(MOD);
	print MOD $in{'upload'};
	close(MOD);
	}
elsif ($in{'source'} == 2 ) {
	# from ftp or http url (possible third-party)
	$url = $in{'url'};
	&error_setup(&text('install_err3', $url));
	$file = &transname(&file_basename($url));
	$need_unlink = 1;
	my $error;
	$progress_callback_url = $url;
	if ($url =~ /^(http|https):\/\/([^\/]+)(\/.*)$/) {
		$ssl = $1 eq 'https';
		$host = $2; $page = $3; $port = $ssl ? 443 : 80;
		if ($host =~ /^(.*):(\d+)$/) { $host = $1; $port = $2; }
		&http_download($host, $port, $page, $file, \$error,
			       \&progress_callback, $ssl);
		}
	elsif ($url =~ /^ftp:\/\/([^\/]+)(:21)?\/(.*)$/) {
		$host = $1; $ffile = $3;
		&ftp_download($host, $ffile, $file, \$error, \&progress_callback);
		}
	else { &inst_error($text{'install_eurl'}); }
	&inst_error($error) if ($error);
}

#stop tomcat server
$err = stop_tomcat();
print "Stopping Tomcat server<br>";
&webmin_log("stop");
if ($err){
	&error($err);
	&ui_print_footer("", $text{'index_return'});
	exit;
}

#install war
if(!move($file, "$config{'tomcat_webapps'}/")){
	&error("Error: Can't move file: $!");
}else{
	print "Install successful<br>";
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

&ui_print_footer("", $text{'index_return'});
