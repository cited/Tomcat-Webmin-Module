#!/usr/bin/perl

require './tomcat-lib.pl';

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
	my  $latest_ver = latest_tomcat_version($install_ver);

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


&ui_print_header(undef, $text{'index_title'}, "", "intro", 1, 1);
&ReadParse();
&error_setup($text{'start_err'});
$err = upgrade_tomcat_from_archive();

&ui_print_footer("", $text{'index_return'});
