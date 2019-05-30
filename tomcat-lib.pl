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
			&inst_error($text{'source_err0'});
		}

	}elsif (($in{'source'} == 1) && ($in{'upload_filename'} ne "")) {	# from uploaded file
		&error_setup($text{'source_err1'});
		$need_unlink = 1;
		if ($no_upload) {
			&inst_error($text{'source_err1.2'});
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
			&inst_error($text{'source_err3'});
		}
		&inst_error($error) if ($error);
	}
	return $file;
}
