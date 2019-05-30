#!/usr/bin/perl

require './tomcat-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'libs_title'}, "");

# Show tabs
@tabs = ( [ "install",   $text{'libs_tabinstall'}, "edit_libs.cgi?mode=install" ],
		  [ "uninstall", $text{'libs_tabuninstall'}, "edit_libs.cgi?mode=uninstall" ]
		);

print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || "install", 1);

# Display installation form
print &ui_tabs_start_tab("mode", "install");
print "$text{'libs_desc1'}<p>\n";

print &ui_form_start("install_libs.cgi", "form-data");
print &ui_table_start($text{'libs_install'}, undef, 2);

print &ui_table_row($text{'libs_installsource'},
	&ui_radio_table("source", 0,
		[ [ 0, $text{'source_local'},   &ui_textbox("file", undef, 40)." ". &file_chooser_button("file", 0) ],
		  [ 1, $text{'source_uploaded'},&ui_upload("upload", 40) ],
		  [ 2, $text{'source_ftp'},     &ui_textbox("url", undef, 40) ]
	    ]));

print &ui_table_end();
print &ui_form_end([ [ "", $text{'libs_installok'} ] ]);
print &ui_tabs_end_tab();


# Display deletion form
print &ui_tabs_start_tab("mode", "uninstall");
print "$text{'libs_desc2'}<p>\n";

print &ui_form_start("uninstall_libs.cgi", "post");
print &ui_table_start($text{'libs_delete'}, undef, 2);

@libs_lists = &get_installed_libs();
@opts_inst_libs = ( );
foreach $lib_file (@libs_lists) {
	$lib_file =~ /^lib_([a-z0-9\.\-_\s]+)\.list$/i;
	push(@opts_inst_libs, [ $1, $1 ]);
}
print &ui_table_row($text{'libs_installed'}, &ui_select("inst_lib", undef, \@opts_inst_libs, 10, 1), 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'libs_deleteok'} ] ]);
print &ui_tabs_end_tab();


print &ui_tabs_end(1);

&ui_print_footer("", $text{'index_return'});
