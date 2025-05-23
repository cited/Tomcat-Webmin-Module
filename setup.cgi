#!/usr/bin/perl

require './tomcat-lib.pl';
require '../webmin/webmin-lib.pl';	#for OS detection
foreign_require('software', 'software-lib.pl');

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

sub setup_catalina_env{
	my $tomcat_ver = $_[0];

	my %os_env;

	print "<hr>Setting CATALINA environment...";

	read_env_file('/etc/environment', \%os_env);
	$os_env{'CATALINA_HOME'} = "/home/tomcat/apache-tomcat-$tomcat_ver/";
	$os_env{'CATALINA_BASE'} = "/home/tomcat/apache-tomcat-$tomcat_ver/";
	write_env_file('/etc/environment', \%os_env, 0);

	open(my $fh, '>>', "/home/tomcat/apache-tomcat-$tomcat_ver/bin/setenv.sh") or die "open:$!";
	print $fh "CATALINA_PID=\"/home/tomcat/apache-tomcat-$tomcat_ver/temp/tomcat.pid\"\n";
	close $fh;
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

sub install_tomcat_from_archive{

	add_tomcat_user();
	my $tomcat_ver = download_and_install($in{'source_archive'});

	setup_catalina_env($tomcat_ver);
	setup_tomcat_users($tomcat_ver);
	setup_tomcat_service($tomcat_ver);
}

sub get_apache_proxy_file(){
	my $proxy_file;
	my %osinfo = &detect_operating_system();
	if(	( $osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
			( $osinfo{'real_os_type'} =~ /rocky/i) or	#rocky
			( $osinfo{'real_os_type'} =~ /alma/i) or	#alma
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
	my %osinfo = &detect_operating_system();
	
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

		get_pjax_content('/tomcat/setup.cgi?mode=tomcat_install_form&tmver='+major);
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
			  [ 0, $text{'source_local'}, &ui_textbox("file", undef, 40)." ". &file_chooser_button("file", 0) ],
			  [ 1, $text{'source_uploaded'}, &ui_upload("upload", 40) ],
			  [ 2, $text{'source_ftp'},&ui_textbox("url", undef, 40) ]
		    ]));

	print &ui_table_end();
	print &ui_form_end([ [ "", $text{'base_installok'} ] ]);
}

sub setup_selinux{
	my $tomcat_home = get_catalina_home();
	
	local $out = &execute_command("semanage fcontext -a -t bin_t \"$tomcat_home/bin(/.*)?\"", undef, \$cmd_out, \$cmd_err, 0, 0);
	print &html_escape($cmd_out.$cmd_err);
	
	local $out = &execute_command("restorecon -r -v \"$tomcat_home/bin\"", undef, \$cmd_out, \$cmd_err, 0, 0);
	print &html_escape($cmd_out.$cmd_err);
}

sub setup_checks{

	my %osinfo = &detect_operating_system();
	
	#Check for commands
	if (!&has_command('java')) {
		print '<p>Warning: Java is not found. Install it manually or from the '.
			  "<a href='./edit_java.cgi?return=%2E%2E%2Ftomcat%2Fsetup.cgi&returndesc=Setup&caller=tomcat'>Java tab</a></p>";
	}

	my @pinfo = software::package_info('haveged', undef, );
	if(!@pinfo){
		if( ($osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
				($osinfo{'real_os_type'} =~ /alma/i) or	#Alma
				($osinfo{'real_os_type'} =~ /rocky/i) ){	#Rocky
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
	
	if(	( $osinfo{'real_os_type'} =~ /centos/i) or	#CentOS
			( $osinfo{'real_os_type'} =~ /rocky/i) or	#Rocky
			( $osinfo{'real_os_type'} =~ /alma/i) or	#Alma
			($osinfo{'real_os_type'} =~  /fedora/i)	){	#Fedora
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
	
	if(@pinfo){
		if( ($osinfo{'real_os_type'} =~ /alma/i) or	#Alma
				($osinfo{'real_os_type'} =~ /rocky/i) ){	#Rocky
			
			local $out = &execute_command("sestatus", undef, \$cmd_out, \$cmd_err, 0, 0);
			if($cmd_out =~ /SELinux status:\s+enabled/i){
				my $se_utils_pkg = 'policycoreutils-python-utils';
				@pinfo = software::package_info($se_utils_pkg, undef, );
				if(!@pinfo){
					print "<p>Warning: $se_utils_pkg is not installed. Install it manually or ".
							"<a href='../package-updates/update.cgi?mode=new&source=3&u=$se_utils_pkg&redir=%2E%2E%2Ftomcat%2Fsetup.cgi&redirdesc=Tomcat Setup'>click here</a> to have it downloaded and installed.</p>";
				}else{
					my $tomcat_home = get_catalina_home();
					local $out = &execute_command("ls -lZ $tomcat_home/bin/startup.sh", undef, \$cmd_out, \$cmd_err, 0, 0);
					if($cmd_out !~ /:bin_t:/i){
						printf "<p>SELinux is enabled. Configured it from ".
										"<a href='./setup.cgi?mode=setup_selinux&return=%2E%2E%2Ftomcat%2Fsetup.cgi&returndesc=Setup&caller=tomcat'>here</a>.</p>";
					}
				}
			}
		}
	}
	print '<p>If you don\'t see any warning above, you can complete setup from '.
		  "<a href='setup.cgi?mode=cleanup&return=%2E%2E%2Ftomcat%2F&returndesc=Apache%20Tomcat&caller=tomcat'>here</a></p>";
}

#Remove all setup files
sub setup_cleanup{
	my $file = $module_root_directory.'/setup.cgi';
	print "Completing Installation</br>";
	&unlink_file($file);
	print &js_redirect("index.cgi");
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
}elsif($mode eq "setup_apache_proxy"){			setup_default_apache_proxy();
}elsif($mode eq "setup_selinux"){						setup_selinux();
}else{
	print "Error: Invalid setup mode\n";
}

&ui_print_footer('setup.cgi', $text{'setup_title'});
