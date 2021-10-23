=head1 tomcat-lib.pl

Functions for managing Tomcat server configuration files.

  foreign_require("tomcat", "tomcat-lib.pl");
  @sites = tomcat::list_tomcat_websites()

=cut

BEGIN { push(@INC, ".."); };
use WebminCore;
use File::Copy;
init_config();

sub get_tomcat_config
{
my $lref = &read_file_lines($config{'foobar_conf'});
my @rv;
my $lnum = 0;
foreach my $line (@$lref) {
    my ($n, $v) = split(/\s+/, $line, 2);
    if ($n) {
      push(@rv, { 'name' => $n, 'value' => $v, 'line' => $lnum });
      }
    $lnum++;
    }
return @rv;
}

# Returns a hash containing the version type, number and full version
sub get_catalina_version
{
	local %version;
	local $catalina_home = get_catalina_home();
	local $out = &backquote_command($catalina_home."/bin/catalina.sh version 2>&1 </dev/null");

	if ($out =~ /(Server\s+version:\s+([a-z\s]+)\/([0-9\.]+))/i) {
		$version{'type'} = $2;
		$version{'number'} = $3;
		$version{'full'} = $1;
	}else {
		$version{'type'} = 'unknown';
		$version{'number'} = 0.0;
		$version{'full'} = 'unknown/0.0';
	}

	if ($out =~ /JVM Version:\s+(.*)/i ){
		$version{'jvm'} = $1;
	}else{
		$version{'jvm'} = 'unknown';
	}
	return %version;
}

sub tomcat_service_ctl{
	my $ctl = $_[0];
	local $out = &execute_command("$config{'tomcat_service'} $ctl", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err ne ""){
		return ($out >> 8, $cmd_err);
	}
	return ($out >> 8, $cmd_out);
}

sub get_all_war_infos(){
	my $catalina_home = get_catalina_home();
    opendir(DIR, $catalina_home.'/webapps') or die $!;
    my @dirs
        = grep {
	    ! /^\./             				 # Doesn't begins with a period
          && -d "$catalina_home/webapps/$_"  # and is a directory
	} readdir(DIR);
    closedir(DIR);

    return sort @dirs;
}

sub file_basename
{
	my $rv = $_[0];
	$rv =~ s/^.*[\/\\]//;
	return $rv;
}

sub sort_version {
	my @A = split(/\./, $a);
	my @B = split(/\./, $b);
	# a sort subroutine, expect $a and $b
	for(my $i=0; $i < 3; $i++){
		if ($A[$i] < $B[$i]) { return -1 } elsif ($A[$i] > $B[$i]) { return 1 }
	}
	return 0;
}

sub latest_tomcat_version{
	my $tomcat_ver = $_[0];
	my %version;
	if(-f "$module_config_directory/version"){
		read_file_cached("$module_config_directory/version", \%version);

		if(	$version{'updated'} >= (time() - 86400)){	#if last update was less than a day ago
			return $version{'latest'} if ($version{'latest'} ne '0.0.0');
		}
	}

  my $major = (split /\./, $tomcat_ver)[0];
  my @all_ver = &major_tomcat_versions($major);
  my $latest_ver = $all_ver[-1];

	#renew the updated timestamp and latest version
	$version{'updated'} = time();
	$version{'latest'} = $latest_ver;
	&write_file("$module_config_directory/version", \%version);

	return $latest_ver;
}

sub installed_tomcat_version(){
	my %os_env;
	read_env_file('/etc/environment', \%os_env);

	if($os_env{'CATALINA_HOME'}){
		$os_env{'CATALINA_HOME'} =~ /\/home\/tomcat\/apache-tomcat-([0-9\.]+)/;
		return $1;
	}else{
		return undef;
	}
}

sub get_catalina_home(){
	my $tomcat_ver = installed_tomcat_version();
	return "/home/tomcat/apache-tomcat-$tomcat_ver";
}

sub download_and_install{
	my $tomcat_ver = $_[0];
	my $major;

	#download tomcat archive
  $major = substr($tomcat_ver, 0,1);
  $in{'url'} = "https://dlcdn.apache.org/dist/tomcat/tomcat-$major/v$tomcat_ver/bin/apache-tomcat-$tomcat_ver.tar.gz";
  $in{'source'} = 2;

	my $tmpfile = process_file_source();

	#extract tomcat archive
	my $cmd_out='';
	my $cmd_err='';
	print "<hr>Extracting to /home/tomcat/apache-tomcat-$tomcat_ver/ ...<br>";
	local $out = &execute_command("tar -x -v --overwrite -f \"$tmpfile\" -C/home/tomcat/", undef, \$cmd_out, \$cmd_err, 0, 0);

	if($cmd_err ne ""){
		&error("Error: tar: $cmd_err");
	}else{
		$cmd_out = s/\n/<br>/g;
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

	open(my $fh, '>>', "/home/tomcat/apache-tomcat-$tomcat_ver/bin/setenv.sh") or die "open:$!";
	print $fh "CATALINA_PID=\"/home/tomcat/apache-tomcat-$tomcat_ver/temp/tomcat.pid\"\n";
	close $fh;
}

sub get_installed_libs{
   opendir(DIR, $module_config_directory) or die $!;
   my @lib_lists
       = grep {
			/^lib_[a-z0-9\.\-_\s]+\.list$/i     #
			&& -f "$module_config_directory/$_"   # and is a file
	} readdir(DIR);
    closedir(DIR);

    return sort @lib_lists;
}

sub process_file_source{
	my $file = '';

	if (($in{'source'} == 0) && ($in{'file'} ne "")) {	# from local file
		&error_setup(&text('source_err0', $in{'file'}));
		$file = $in{'file'};
		if (!(-r $file)){
			&error($text{'source_err0'});
		}

	}elsif (($in{'source'} == 1) && ($in{'upload_filename'} ne "")) {	# from uploaded file
		&error_setup($text{'source_err1'});
		$need_unlink = 1;
		if ($no_upload) {
			&error($text{'source_err1.2'});
		}
		$file = transname(file_basename($in{'upload_filename'}));
		open(MOD, ">$file");
		binmode(MOD);
		print MOD $in{'upload'};
		close(MOD);

	}elsif ($in{'source'} == 2 and $in{'url'} ne '') {	# from ftp or http url (possible third-party)
		$url = $in{'url'};
		&error_setup(&text('source_err2', $url));
		$file = &transname(file_basename($url));
		$need_unlink = 1;
		my $error;
		$progress_callback_url = $url;
		if ($url =~ /^(http|https):\/\/([^\/]+)(\/.*)$/) {
			$ssl = $1 eq 'https';
			$host = $2; $page = $3; $port = $ssl ? 443 : 80;
			if ($host =~ /^(.*):(\d+)$/) { $host = $1; $port = $2; }
			my %cookie_headers = ('Cookie'=>'oraclelicense=accept-securebackup-cookie');
			&http_download($host, $port, $page, $file, \$error,
				       \&progress_callback, $ssl, undef, undef, 0, 0, 1, \%cookie_headers);
		} elsif (
			$url =~ /^ftp:\/\/([^\/]+)(:21)?\/(.*)$/) {
			$host = $1; $ffile = $3;
			&ftp_download($host, $ffile, $file, \$error, \&progress_callback);
		}else {
			&error($text{'source_err3'});
		}
		&error($error) if ($error);
	}
	return $file;
}

sub unzip_file{
	my $file  = $_[0];
	my @suffixlist = ('.zip');
	($lib_name,$path,$lib_suffix) = fileparse($file,@suffixlist);

	my $unzip_dir = "/tmp/.webmin/$lib_name";

	#if old temp extension dir exist, remove it
	#if( -d $unzip_dir and rmtree($unzip_dir) == 0){
	#	&error("Failed to remove temp extension dir");
	#	&ui_print_footer("", $text{'index_return'});
	#	exit;
	#}
	&make_dir($unzip_dir, 0754, 1);

	my $unzip_out;
	my $unzip_err;
	print "<hr>Unzipping to $unzip_dir ...<br>";
	local $out = &execute_command("unzip -u \"$file\" -d \"$unzip_dir\"", undef, \$unzip_out, \$unzip_err, 0, 0);

	if($unzip_err){
		&error("Error: unzip: $unzip_err");
	}else{
		$unzip_out = s/\r\n/<br>/g;
		print &html_escape($unzip_out);
	}
	return $unzip_dir;
}

sub get_tomcat_major_versions(){
	my @majors = ('9','8', '7','6');
	return @majors;
}

sub major_tomcat_versions{
	my $major = $_[0];	#Tomcat major version 6,7,8,9

	my $url = "https://dlcdn.apache.org/dist/tomcat/tomcat-$major/";
	&error_setup(&text('install_err3', $url));
	my $error = '';
	my $tmpfile = &transname('tomcat.html');


	&http_download('dlcdn.apache.org', 80, "/dist/tomcat/tomcat-$major/", $tmpfile, \$error);
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
