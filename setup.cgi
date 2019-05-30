#!/usr/bin/perl

require './tomcat-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection
foreign_require('software', 'software-lib.pl');

sub latest_tomcat_version(){
	#get latest version from Apache Tomcat webpage
	my %version;
	if(-f "$module_config_directory/version"){
		read_file_cached("$module_config_directory/version", \%version);

		if(	$version{'updated'} >= (time() - 86400)){	#if last update was less than a day ago
			return $version{'latest'} if ($version{'latest'} ne '0.0.0');
		}
	}

	my $url = 'http://archive.apache.org/dist/tomcat/tomcat-8/';
	&error_setup(&text('install_err3', $url));
	my $error = '';
	my $tmpfile = &transname('tomcat.html');


	&http_download('archive.apache.org', 80, '/dist/tomcat/tomcat-8/', $tmpfile, \$error);
	if($error){
		print &html_escape($error);
		die "Error: Failed to get Apache Tomcat webpage";
	}

	my @latest_versions;
	open(my $fh, '<', $tmpfile) or die "open:$!";
	while(my $line = <$fh>){
		if($line =~ /<a\s+href="v(8\.[0-9\.]+)\/">v[0-9\.]+\/<\/a>/){
			push(@latest_versions, $1);
		}
	}
	close $fh;

	my @result = sort sort_version @latest_versions;
	my $latest_ver = $result[$#result];

	#renew the updated timestamp and latest version
	$version{'updated'} = time();
	$version{'latest'} = $latest_ver;
	&write_file("$module_config_directory/version", \%version);

	return $latest_ver;
}

sub add_tomcat_user{
	#check if tomcat user exists
	if(read_file_contents('/etc/passwd') !~ /\ntomcat:/){
		#add tomcat user
		local $out = &backquote_command('useradd -m tomcat', 0);
	}elsif(! -d '/home/tomcat'){
		&make_dir("/home/tomcat", 0755, 1);
		&set_ownership_permissions('tomcat','tomcat', undef, '/home/tomcat');
	}
}

sub get_tomcat_major_versions(){
	my @majors = ('8', '7','6', '9');
	return @majors;
}

sub major_tomcat_versions{
	my $major = $_[0];	#Tomcat major version 6,7,8

	my $url = "http://archive.apache.org/dist/tomcat/tomcat-$major/";
	&error_setup(&text('install_err3', $url));
	my $error = '';
	my $tmpfile = &transname('tomcat.html');


	&http_download('archive.apache.org', 80, "/dist/tomcat/tomcat-$major/", $tmpfile, \$error);
	if($error){
		error($error);
	}

	my @latest_versions;
	open(my $fh, '<', $tmpfile) or die "open:$!";
	while(my $line = <$fh>){
		if($line =~ /<a\s+href="v($major\.[0-9\.]+)\/">v[0-9\.]+\/<\/a>/){
			push(@latest_versions, $1);
		}
	}
	close $fh;

	return sort sort_version @latest_versions;
}

sub download_and_install{
	my $tomcat_ver;
	my $major;

	#download tomcat archive
	if($in{'source'} == 100){
			$tomcat_ver = $in{'source_archive'};
			$major = substr($tomcat_ver, 0,1);
			$in{'url'} = "http://archive.apache.org/dist/tomcat/tomcat-$major/v$tomcat_ver/bin/apache-tomcat-$tomcat_ver.tar.gz";
			$in{'source'} = 2;
	}
	my $tmpfile = process_file_source();

	if($tmpfile =~ /.*apache-tomcat-([0-9\.]+).tar.gz$/i){
		$tomcat_ver = $1;
	}else{
		&error("Failed to match Tomcat version from archive");
	}
	$major = substr($tomcat_ver, 0,1);

	#extract tomcat archive
	my $cmd_out='';
	my $cmd_err='';
	print "<hr>Extracting to /home/tomcat/apache-tomcat-$tomcat_ver/ ...<br>";
	local $out = &execute_command("tar -x --overwrite -f \"$tmpfile\" -C/home/tomcat/", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err ne ""){
		&error("Error: tar: $cmd_err");
	}else{
		$cmd_out = s/\r\n/<br>/g;
		print &html_escape($cmd_out);
		print "Done<br>";
	}

	#folder is created after tomcat is started, but we need it now
	&make_dir("/home/tomcat/apache-tomcat-$tomcat_ver/conf/Catalina/localhost/", 0755, 1);

	open(my $fh, '>', "/home/tomcat/apache-tomcat-$tomcat_ver/conf/Catalina/localhost/manager.xml") or die "open:$!";
	print $fh <<EOF;
<Context privileged="true" antiResourceLocking="false" docBase="\${catalina.home}/webapps/manager">
	<Valve className="org.apache.catalina.valves.RemoteAddrValve" allow="^.*\$" />
</Context>
EOF
	close $fh;

	#&set_ownership_permissions('tomcat','tomcat', undef, "/home/tomcat/apache-tomcat-$tomcat_ver/");
	&execute_command("chown -R tomcat:tomcat /home/tomcat/apache-tomcat-$tomcat_ver");

	return $tomcat_ver;
}

sub setup_catalina_env{
	my $tomcat_ver = $_[0];

	my %os_env;

	print "<hr>Setting CATALINA environment...";

	read_env_file('/etc/environment', \%os_env);
	$os_env{'CATALINA_HOME'} = "/home/tomcat/apache-tomcat-$tomcat_ver/";
	$os_env{'CATALINA_BASE'} = "/home/tomcat/apache-tomcat-$tomcat_ver/";
	write_env_file('/etc/environment', \%os_env, 0);
}

sub setup_tomcat_users{
	my $tomcat_ver = $_[0];
	my @pw_chars = ("A".."Z", "a".."z", "0".."9", "_", "-");
	my $manager_pass;
	my $admin_pass;

	$manager_pass .= $pw_chars[rand @pw_chars] for 1..32;
	$admin_pass   .= $pw_chars[rand @pw_chars] for 1..32;

	#Save tomcat-users.xml
	open(my $fh, '>', "/home/tomcat/apache-tomcat-$tomcat_ver/conf/tomcat-users.xml") or die "open:$!";
	print $fh <<EOF;
<?xml version='1.0' encoding='utf-8'?>
<tomcat-users>
<role rolename="manager-gui" />
<user username="manager" password="$manager_pass" roles="manager-gui" />

<role rolename="admin-gui" />
<user username="admin" password="$admin_pass" roles="manager-gui,admin-gui" />
</tomcat-users>
EOF
	close $fh;
	print "<hr>Setting Tomcat users...";
}

sub setup_tomcat_service{
	my $tomcat_ver = $_[0];
	copy_source_dest("$module_root_directory/tomcat.service", '/etc/init.d/tomcat');
	&set_ownership_permissions('root','root', 0555, "/etc/init.d/tomcat");
	print "<hr>Setting Tomcat service ...";
}

sub install_tomcat_from_archive{

	add_tomcat_user();
	my $tomcat_ver = download_and_install();

	setup_catalina_env($tomcat_ver);
	setup_tomcat_users($tomcat_ver);
	setup_tomcat_service($tomcat_ver);
}

sub migrate_settings_and_apps{
	my $old_ver = $_[0];
	my $new_ver = $_[1];
	my $apps_ref = $_[2];

	#copy settings
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
	print "Moving apps ...<br>";
	foreach my $app (@$apps_ref){
		next if (grep(/^$app$/, @exclude_apps));

		#move
		if(!move(	"/home/tomcat/apache-tomcat-$old_ver/webapps/$app",
					"/home/tomcat/apache-tomcat-$old_ver/webapps/$app")){
			&error("Error: Can't move $app: $!");
		}else{
			print "$app moved<br>";
		}
	}
}

sub get_apache_proxy_file(){
	my $proxy_file;
	my %osinfo = &detect_operating_system();
	if(	( $osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
		($osinfo{'real_os_type'} =~ /fedora/i)	){	#Fedora
		if( ! -d '/etc/httpd/'){
			return 0;
		}
		$proxy_file = '/etc/httpd/conf.d/tomcat.conf';

	}elsif( ($osinfo{'real_os_type'} =~ /ubuntu/i) or
			($osinfo{'real_os_type'} =~ /debian/i) 	){	#ubuntu or debian
		if( ! -d '/etc/apache2/'){
			return 0;
		}
		$proxy_file = '/etc/apache2/conf-enabled/tomcat.conf';
	}
	return $proxy_file;
}

sub setup_default_apache_proxy(){
	my $proxy_file = get_apache_proxy_file();

	if(-f $proxy_file){
		return 0;
	}

	open(my $fh, '>', $proxy_file) or die "open:$!";

	if(	($osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
		($osinfo{'real_os_type'} =~ /fedora/i)	){	#Fedora

		&execute_command('setsebool httpd_can_network_connect 1');

		print $fh "LoadModule proxy_module 		modules/mod_proxy.so\n";
		print $fh "LoadModule proxy_http_module modules/mod_proxy_http.so\n";
		print $fh "LoadModule rewrite_module  	modules/mod_rewrite.so\n";

	}elsif( $osinfo{'os_type'} =~ /debian/i){	#ubuntu or debian

		print $fh "LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so\n";
		print $fh "LoadModule proxy_http_module  /usr/lib/apache2/modules/mod_proxy_http.so\n";
		print $fh "LoadModule rewrite_module  /usr/lib/apache2/modules/mod_rewrite.so\n";
	}

	print $fh "ProxyRequests Off\n";
	print $fh "ProxyPreserveHost On\n";
	print $fh "    <Proxy *>\n";
	print $fh "       Order allow,deny\n";
	print $fh "       Allow from all\n";
	print $fh "    </Proxy>\n";
	print $fh "ProxyPass / http://localhost:8080/\n";
	print $fh "ProxyPassReverse / http://localhost:8080/\n";

	close $fh;

	print "Added proxy configuration / -> 8080 in $proxy_file\n";
}

sub select_tomcat_archive{
	print "$text{'base_desc1'}<p>\n";
	print &ui_form_start("setup.cgi", "form-data");
	print ui_hidden('mode', 'tomcat_install');
	print &ui_table_start($text{'base_options'}, undef, 2);

	my @tmver = &get_tomcat_major_versions();
	my $sel_tmver = $in{'tmver'} || $tmver[0];
	my @tm_opts = ( );
	foreach my $v (@tmver) {
		push(@tm_opts, [ $v, $v ]);
	}

	print <<EOF;
	<script type="text/javascript">
	function update_select(){
		var majorSel = document.getElementById('base_major');
		var major = majorSel.options[majorSel.selectedIndex].value;

		window.location='setup.cgi?mode=tomcat_install_form&tmver='+major;
	}
	</script>
EOF

	print &ui_table_row($text{'base_major'},
		&ui_select("base_major", $sel_tmver, \@tm_opts, 1, 0, undef, undef, 'id="base_major" onchange="update_select()"'));

	my @tver = &major_tomcat_versions($sel_tmver);
	my @tver_opts = ( );
	foreach my $v (@tver) {
		push(@tver_opts, [ $v, $v ]);
	}

	print &ui_table_row($text{'base_installsource'},
		&ui_radio_table("source", 100,
			[ [ 100, $text{'source_archive'},  &ui_select("source_archive", undef, \@tver_opts,1, 0)],
			  [ 0, $text{'source_local'}, &ui_textbox("file", undef, 40)." ". &file_chooser_button("file", 0) ],
			  [ 1, $text{'source_uploaded'}, &ui_upload("upload", 40) ],
			  [ 2, $text{'source_ftp'},&ui_textbox("url", undef, 40) ]
		    ]));

	print &ui_table_end();
	print &ui_form_end([ [ "", $text{'base_installok'} ] ]);
}

sub setup_checks{

	#Check for commands
	if (!&has_command('java')) {
		print '<p>Warning: Java is not found. Install it manually or from the '.
			  "<a href='./edit_java.cgi?return=%2E%2E%2Ftomcat%2Fsetup.cgi&returndesc=Setup&caller=tomcat'>Java tab</a></p>";
	}

	my @pinfo = software::package_info('haveged', undef, );
	if(!@pinfo){
		my %osinfo = &detect_operating_system();
		if( $osinfo{'real_os_type'} =~ /centos/i){	#CentOS
			@pinfo = software::package_info('epel-release', undef, );
			if(!@pinfo){
				print "<p>Warning: haveged needs epel-release. Install it manually or ".
						"<a href='../package-updates/update.cgi?mode=new&source=3&u=epel-release&redir=%2E%2E%2Ftomcat%2Fsetup.cgi&redirdesc=Tomcat Setup'>click here</a> to have it downloaded and installed.</p>";
			}
		}
		print "<p>Warning: haveged package is not installed. Install it manually or ".
			  "<a href='../package-updates/update.cgi?mode=new&source=3&u=haveged&redir=%2E%2E%2Ftomcat%2Fsetup.cgi&redirdesc=Tomcat Setup'>click here</a> to have it downloaded and installed.</p>";
	}

	my $tomcat_ver = installed_tomcat_version();
	if(!$tomcat_ver){
		print "<p><a href='setup.cgi?mode=tomcat_install_form&return=%2E%2E%2Ftomcat%2Fsetup.cgi&returndesc=Setup&caller=tomcat'>Click here</a> to install Tomcat from Apache site.</p>";
	}

	if (!&has_command('unzip')) {
		print '<p>Warning: unzip command is not found. Install it manually or '.
			  "<a href='../package-updates/update.cgi?mode=new&source=3&u=unzip&redir=%2E%2E%2Ftomcat%2Fsetup.cgi&redirdesc=Tomcat Setup'>click here</a> to have it downloaded and installed.</p>";
	}

	my $proxy_file = get_apache_proxy_file();
	my $www_name = '';
	my %osinfo = &detect_operating_system();
	if(	( $osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
			($osinfo{'real_os_type'} =~ /fedora/i)	){	#Fedora
		$www_name = 'httpd';

	}elsif( ($osinfo{'real_os_type'} =~ /ubuntu/i) or
					($osinfo{'real_os_type'} =~ /debian/i) 	){	#ubuntu or debian
		$www_name = 'apache2';
	}

	@pinfo = software::package_info($www_name, undef, );
	if(!@pinfo){
		print "<p>Warning: $www_name is not installed. Install it manually or ".
				"<a href='../package-updates/update.cgi?mode=new&source=3&u=$www_name&redir=%2E%2E%2Ftomcat%2Fsetup.cgi&redirdesc=Tomcat Setup'>click here</a> to have it downloaded and installed.</p>";
	}

	if(! -f $proxy_file){
		print "<p>Apache default proxy is not configured. ".
			  "<a href='./setup.cgi?mode=setup_apache_proxy&return=%2E%2E%2Ftomcat%2Fsetup.cgi&returndesc=Setup&caller=tomcat'>click here</a></p>";
	}
	print '<p>If you don\'t see any warning above, you can complete setup from '.
		  "<a href='setup.cgi?mode=cleanup&return=%2E%2E%2Ftomcat%2F&returndesc=Apache%20Tomcat&caller=tomcat'>here</a></p>";
}

#Remove all setup files
sub setup_cleanup{
	my $file = $module_root_directory.'/setup.cgi';
	print "Completing Installation\n";
	&unlink_file($file);
}


&ui_print_header(undef, $text{'setup_title'}, "");

if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) {
	&ReadParseMime();
}else {
	&ReadParse(); $no_upload = 1;
}

my $mode = $in{'mode'} || "checks";

if($mode eq "checks"){							setup_checks();
	&ui_print_footer('', $text{'index_return'});
	exit 0;
}elsif($mode eq "cleanup"){						setup_cleanup();
	&ui_print_footer('', $text{'index_return'});
	exit 0;
}elsif($mode eq "tomcat_install_form"){			select_tomcat_archive();
}elsif($mode eq "tomcat_install"){				install_tomcat_from_archive();
}elsif($mode eq "tomcat_upgrade"){				upgrade_tomcat_from_archive();
}elsif($mode eq "setup_apache_proxy"){			setup_default_apache_proxy();
}else{
	print "Error: Invalid setup mode\n";
}

&ui_print_footer('setup.cgi', $text{'setup_title'});
