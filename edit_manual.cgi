#!/usr/bin/perl
# Show a page for manually editing an Tomcat server.xml config file

require './tomcat-lib.pl';
&ReadParse();
&ui_print_header(undef, $text{'manual_title'}, "");

my $catalina_home = get_catalina_home();

# Work out and show the files
@files = (	"$catalina_home/bin/setenv.sh",
			"$catalina_home/conf/context.xml",
			"$catalina_home/conf/server.xml",
			"$catalina_home/conf/tomcat-users.xml",
			"$catalina_home/conf/web.xml");
$in{'file'} ||= $files[0];
&indexof($in{'file'}, @files) >= 0 || &error($text{'manual_efile'});

print &ui_form_start("edit_manual.cgi");
print "<b>$text{'manual_file'}</b>\n";
print &ui_select("file", $in{'file'}, [ map { [ $_ ] } @files ], 1, 0);
print &ui_submit($text{'manual_ok'});
print &ui_form_end();

# Show the file contents
print &ui_form_start("save_manual.cgi", "form-data");
print &ui_hidden("file", $in{'file'}),"\n";
$data = &read_file_contents($in{'file'});
print &ui_textarea("data", $data, 20, 80),"\n";
print &ui_form_end([ [ "save", $text{'save'} ] ]);

&ui_print_footer("", $text{'index_return'});

