#!/usr/bin/perl

require './tomcat-lib.pl';

sub select_tomcat_archive{
	print "$text{'base_desc2'}<p>\n";
	print &ui_form_start("tomcat_upgrade.cgi", "form-data");
	print ui_hidden('mode', 'tomcat_upgrade');
	print &ui_table_start($text{'base_options'}, undef, 2);
	
	my $install_ver = installed_tomcat_version();
    my $install_major = (split /\./, $install_ver)[0];
	
    if($in{'tmver'}){
        $install_major = $in{'tmver'};
	}
	
	my @tmver = &get_tomcat_major_versions();
	my $sel_tmver = $install_major;
	my @tm_opts = ( );
	foreach my $v (@tmver) {
		push(@tm_opts, [ $v, $v ]);
	}

	print <<EOF;
	<script type="text/javascript">
	function update_select(){
		var majorSel = document.getElementById('base_major');
		var major = majorSel.options[majorSel.selectedIndex].value;

		get_pjax_content('/tomcat/tomcat_upgrade.cgi?mode=select_version&tmver='+major);
	}
	</script>
EOF

	print &ui_table_row($text{'base_major'},
		&ui_select("base_major", $sel_tmver, \@tm_opts, 1, 0, undef, undef, 'id="base_major" onchange="update_select()"'));

	my @tver = &major_tomcat_versions($sel_tmver);
	my @tver_opts = ( );
	foreach my $v (reverse @tver) {
		push(@tver_opts, [ $v, $v ]);
	}

	print &ui_table_row($text{'base_installsource'},
		&ui_radio_table("source", 100,
			[ [ 100, $text{'source_archive'},  &ui_select("source_archive", undef, \@tver_opts,1, 0)],
		    ]));

	print &ui_table_end();
	print &ui_form_end([ [ "", $text{'base_upgradeok'} ] ]);
}

sub migrate_settings_and_apps{
	my $old_ver = $_[0];
	my $new_ver = $_[1];
	my $apps_ref = $_[2];

	#Copy Settings
	my @files = ('bin/setenv.sh', 'conf/tomcat-users.xml');
	foreach my $file (@files){
		if( -f "/home/tomcat/apache-tomcat-$old_ver/$file"){
			copy_source_dest("/home/tomcat/apache-tomcat-$old_ver/$file",
							 "/home/tomcat/apache-tomcat-$new_ver/$file");
			print "Copying $file to /home/tomcat/apache-tomcat-$new_ver/$file<br>";
		}
	}

	#make a list of installed apps
	my @exclude_apps = ('docs', 'examples', 'host-manager', 'manager', 'ROOT');

	#move apps
	print "Copying apps ...<br>";
	foreach my $app (@$apps_ref){

		next if grep( /^$app$/, @exclude_apps);

		if(!copy_source_dest(	"/home/tomcat/apache-tomcat-$old_ver/webapps/$app",
							"/home/tomcat/apache-tomcat-$new_ver/webapps/$app")){
			&error("Error: Can't copy $app: $!");
		}else{
			print "$app<br>";
		}

		if(-f "/home/tomcat/apache-tomcat-$old_ver/webapps/$app.war"){
			if(!copy_source_dest(	"/home/tomcat/apache-tomcat-$old_ver/webapps/$app.war",
								"/home/tomcat/apache-tomcat-$new_ver/webapps/$app.war")){
				&error("Error: Can't copy $app.war: $!");
			}else{
				print "$app.war<br>";
			}
		}
	}
}

sub upgrade_tomcat_from_archive{

	my $install_ver = installed_tomcat_version();
	my  $latest_ver = $_[0];

	my @installed_apps = get_all_war_infos();

	#add_tomcat_user();
	download_and_install($latest_ver);

	tomcat_service_ctl('stop');

	setup_catalina_env($latest_ver);
	#setup_tomcat_users($latest_ver);
	setup_tomcat_service($latest_ver);

	migrate_settings_and_apps($install_ver, $latest_ver, \@installed_apps);

	print("Update done, starting new Tomcat ".$latest_ver);
	tomcat_service_ctl('start');
}


&ui_print_header(undef, $text{'index_title_upgrade'}, "", "intro", 1, 1);
if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) {
	&ReadParseMime();
}else {
	&ReadParse(); $no_upload = 1;
}
&error_setup($text{'start_err'});

my $mode = $in{'mode'} || "select_version";

if($mode eq "select_version"){
    select_tomcat_archive();
}elsif($mode eq "tomcat_upgrade"){
    $err = upgrade_tomcat_from_archive($in{'source_archive'});
}

&ui_print_footer("", $text{'index_return'});
