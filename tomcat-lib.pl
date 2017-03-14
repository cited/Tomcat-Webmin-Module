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
sub get_tomcat_version
{
	local %version;
	local $out = &backquote_command(
					&quote_path($config{'tomcat_path'})." version 2>&1 </dev/null");
	if ($out =~ /(Server\s+version:\s+([a-zA-Z\s]+)\/([0-9\.]+))/i) {
		# Classic commercial SSH
		$version{'type'} = $2;
		$version{'number'} = $3;
		$version{'full'} = $1;
	}else {
		# Probably Solaris 10 SSHD that didn't display version.  Use it.
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

sub get_tomcat_pid(){
	local $pid = &backquote_command("ps -axww | grep tomcat | grep java | grep -v grep | awk '{print \$1}'");
	return $pid;
}

# Attempts to start the tomcat server, returning undef on success or an error
# message on failure.
sub start_tomcat
{
	if ($config{'start_cmd'}) {
		$out = &backquote_logged("$config{'start_cmd'} 2>&1 </dev/null");
		if ($?) { return "<pre>$out</pre>"; }
		}
	else {
		$out = &backquote_logged("$config{'tomcat_path'} start 2>&1 </dev/null");
		if ($?) { return "<pre>$out</pre>"; }
		}
	return undef;
}

sub stop_tomcat
{
	if ($config{'stop_cmd'}) {
		$out = &backquote_logged("$config{'stop_cmd'} 2>&1 </dev/null");
		if ($?) { return "<pre>$out</pre>"; }
		}
	else {
		$out = &backquote_logged("$config{'tomcat_path'} stop 2>&1 </dev/null");
		if ($?) { return "<pre>$out</pre>"; }
		}
	return undef;
}

sub get_all_war_infos(){
    opendir(DIR, $config{'tomcat_webapps'}) or die $!;
    my @dirs
        = grep {
	    ! /^\./             # Begins with a period
          && -d "$config{'tomcat_webapps'}/$_"   # and is a directory
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
