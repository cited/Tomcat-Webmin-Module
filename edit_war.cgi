#!/usr/bin/perl

require './tomcat-lib.pl';
&ReadParse();

&ui_print_header(undef, $text{'wars_title'}, "");

# Show tabs
@tabs = ( [ "install", $text{'wars_tabinstall'}, "edit_wars.cgi?mode=install" ],
		  [ "delete", $text{'wars_tabdelete'}, "edit_wars.cgi?mode=delete" ]
		);

print &ui_tabs_start(\@tabs, "mode", $in{'mode'} || "install", 1);

# Display installation form
print &ui_tabs_start_tab("mode", "install");
print "$text{'wars_desc1'}<p>\n";

print &ui_form_start("install_war.cgi", "form-data");
print &ui_table_start($text{'war_install'}, undef, 2);

print &ui_table_row($text{'war_installsource'},
	&ui_radio_table("source", 0,
		[ [ 0, $text{'source_local'}, &ui_textbox("file", undef, 40)." ". &file_chooser_button("file", 0) ],
		  [ 1, $text{'source_uploaded'}, &ui_upload("upload", 40) ],
		  [ 2, $text{'source_ftp'},&ui_textbox("url", undef, 40) ]
	    ]));

print &ui_table_end();
print &ui_form_end([ [ "", $text{'war_installok'} ] ]);
print &ui_tabs_end_tab();


# Display deletion form
print &ui_tabs_start_tab("mode", "delete");
print "$text{'wars_desc2'}<p>\n";

print &ui_form_start("delete_war.cgi", "post");
print &ui_table_start($text{'wars_delete'}, undef, 2);

@wlist = &get_all_war_infos();
@opts = ( );
foreach $d (@wlist) {
	push(@opts, [ $d, $d ]);
}
print &ui_table_row($text{'wars_installed'},
	&ui_select("mod", undef, \@opts, 10, 1)."<br>\n".
	&ui_checkbox("rmwar", 1, $text{'wars_rmwar'}, 0), 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'wars_deleteok'} ] ]);
print &ui_tabs_end_tab();


print &ui_tabs_end(1);

&ui_print_footer("", $text{'index_return'});
