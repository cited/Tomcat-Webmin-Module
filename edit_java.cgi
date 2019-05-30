#!/usr/bin/perl

require './tomcat-lib.pl';
require './java-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection

&ReadParse();

&ui_print_header(undef, $text{'java_title'}, "");

# Show tabs
@tabs = ( [ "install",   $text{'java_tabinstall'}, "edit_java.cgi?mode=install" ],
		  [ "uninstall", $text{'java_tabuninstall'}, "edit_java.cgi?mode=uninstall" ],
			[ "default", $text{'java_tabdefault'}, "edit_java.cgi?mode=default" ]
		);

print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || "install", 1);


print &ui_tabs_start_tab("mode", "install");
print "$text{'java_desc1'}<p>\n";

print &ui_form_start("install_java.cgi", "form-data");
print &ui_table_start($text{'java_install'}, undef, 2);

my %jdk_version = &get_latest_jdk_version();
@opt_avail_jdk = ();
foreach $ver (keys %jdk_version) {
	push(@opt_avail_jdk, [ "$ver=$jdk_version{$ver}", $ver]);
}

my %openjdk_version = &get_openjdk_versions();
@opt_avail_openjdk = ();
foreach $ver (keys %openjdk_version) {
	push(@opt_avail_openjdk, [ "$ver=$openjdk_version{$ver}", $ver]);
}

print &ui_table_row($text{'jdk_installsource'},
	&ui_radio_table("source", 200,
		[ [ 200, $text{'openjdk_latest'},  &ui_select("openjdk_ver", undef, \@opt_avail_openjdk, 1, 0).
																			 '<br>'.
																			 &ui_checkbox("openjdk_headless", 1,undef, 1).$text{'openjdk_headless'}.
																			 &ui_hr()],
			[ 100, $text{'jdk_latest'},  &ui_select("jdk_ver", undef, \@opt_avail_jdk, 1, 0)],
		  [ 0, $text{'source_local'},   &ui_textbox("file", undef, 40)." ". &file_chooser_button("file", 0) ],
		  [ 1, $text{'source_uploaded'},&ui_upload("upload", 40) ],
		  [ 2, $text{'source_ftp'},     &ui_textbox("url", undef, 40) ]
	    ]), 2);
print &ui_table_row($text{'java_def_jdk'},
			&ui_checkbox("def_jdk", 1,undef, 1).$text{'java_def_jdk_desc'}
			,2);


print &ui_table_end();
print &ui_form_end([ [ "", $text{'java_installok'} ] ]);
print &ui_tabs_end_tab();


print &ui_tabs_start_tab("mode", "uninstall");
print "$text{'java_desc2'}<p>\n";

print &ui_form_start("uninstall_java.cgi", "post");
print &ui_table_start($text{'java_uninstall'}, undef, 2);

@jdk_vlist = &get_installed_jdk_versions();
@opts_inst_jdk = ( );
foreach $jdk_ver (@jdk_vlist) {
	push(@opts_inst_jdk, [ $jdk_ver, $jdk_ver ]);
}
print &ui_table_row($text{'java_installed'}, &ui_select("inst_jdk", undef, \@opts_inst_jdk, 1, 0)."<br>\n", 2);
print &ui_table_row($text{'java_rm_def_jdk'}, &ui_checkbox("rm_def_jdk", 1,undef, 1), 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'java_deleteok'} ] ]);
print &ui_tabs_end_tab();

print &ui_tabs_start_tab("mode", "default");
print "$text{'java_desc3'}<p>\n";

print &ui_form_start("default_java.cgi", "post");
print &ui_table_start($text{'java_default'}, undef, 2);

print &ui_table_row($text{'java_installed'}, &ui_select("inst_jdk2", undef, \@opts_inst_jdk, 1, 0)."<br>\n", 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'java_defaultok'} ] ]);
print &ui_tabs_end_tab();

print &ui_tabs_end(1);

&ui_print_footer("", $text{'index_return'});
