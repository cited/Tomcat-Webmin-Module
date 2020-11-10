#!/usr/bin/perl

require './tomcat-lib.pl';
foreign_require('apache', 'apache-lib.pl');

sub get_proxy_file{
	my $domain_user = $_[0];
	my $proxy_file = '';

	if( -d '/etc/httpd/conf.d' ){
		$proxy_file = '/etc/httpd/conf.d/tomcat.conf';
	}elsif( -d '/etc/apache2/conf-enabled/'){	#ubuntu or debian
		$proxy_file = '/etc/apache2/conf-enabled/tomcat.conf';
	}
	return $proxy_file;
}

sub load_proxy_maps{
	my $proxy_file = $_[0];

	my %maps;
	open(my $fh, '<', $proxy_file) or return %maps;
	while(my $line = <$fh>){
		if($line =~ /^ProxyPass ([\/a-z0-9_\-\.]+) ([a-z:\/0-9\.\-]+)/i){
			$maps{$2} = $1;
		}
	}
	close $fh;

	return %maps;
}

sub add_proxy{
	my $proxy_file = $_[0];
	my $app_name   = $_[1];
	my $default    = $_[2];
	my $ssl_port   = $_[3];
	my $wildcard   = $_[4];

	my %idata = ('port_http'=>'8080', 'port_https'=>'8443');

	my $app_path = '/';
	if($default == 0){	#if app is not default
		$app_path .= $app_name;
	}

	if($wildcard == 1){
		$app_name = '';
	}

	my $lref = &read_file_lines($proxy_file);
	my $lnum = 0;
	my $proxy_header_section = 0;
	my $user_domain = 'localhost';
	foreach my $line (@$lref) {
		if($line =~ /^ProxyPass \/ |^ProxyPassReverse \/ /){		#another default app
			if($default == 1){							#if new app is default
				delete @{$lref}[$lnum];					#remove old default app
			}
		}elsif($line =~ /^ProxyPass.*\/$app_name$/){	#if its a line with our app
			delete @{$lref}[$lnum];
		}elsif($line =~ /^ProxyRequests Off$/){
			$proxy_header_section = 1;	#proxy settings are found
		}elsif($line =~ /^ServerName (.*)$/){
			$user_domain = $1;
		}
		$lnum++;
	}


	my $conf_tail;
	if(@$lref[$lnum] eq '</VirtualHost>'){
		$conf_tail = pop @{$lref};
	}
	if($proxy_header_section == 0){
		my $line = "ProxyRequests Off
ProxyPreserveHost On
<Proxy *>
	Order allow,deny
	Allow from all
</Proxy>";
		push(@$lref, $line);
	}

	my $proto = '';
	if($ssl_port == 1){
		$proto = 's';
	}

	push(@$lref, "ProxyPass $app_path http".$proto."://$user_domain:".$idata{'port_http'.$proto}."/$app_name");
	push(@$lref, "ProxyPassReverse $app_path http".$proto."://$user_domain:".$idata{'port_http'.$proto}."/$app_name");
	if($conf_tail){
		push(@$lref, $conf_tail);	#Restore conf end
	}

	flush_file_lines($proxy_file);
}

sub remove_proxy{
	my ($proxy_file, $app_path) = @_;

	my $lref = &read_file_lines($proxy_file);
	my $lnum = 0;
	foreach my $line (@$lref) {
		if($line =~ /^ProxyPass $app_path |^ProxyPassReverse $app_path /){	#if its a line with our app
			delete @{$lref}[$lnum];
		}
		$lnum++;
	}
	flush_file_lines($proxy_file);
}

&ReadParse();

my $form_submit = 0;
if ($in{'submit_flag'}) {
	$form_submit = 1;
}

&ui_print_header(undef, $text{'proxy_title'}, "");


my $proxy_file = get_proxy_file($remote_user);
if($proxy_file eq ''){
	print "Error: Failed to find proxy file for user $remote_user</b>"
}

if($form_submit == 1){
	if($in{'app_path'}){
		remove_proxy($proxy_file, $in{'app_path'});
	}else{
		add_proxy($proxy_file, $in{'app_name'}, $in{'app_default'}, $in{'proxy_ssl'}, $in{'app_wildcard'});
	}
	apache::restart_apache();
}

my %maps = load_proxy_maps($proxy_file);
my @tds = ();
print &ui_columns_start(['Path','URL'], undef, 0, \@tds, 'Apps with proxy ('.$proxy_file.')');
foreach my $url (keys %maps) {

	my @cols;
	push(@cols, $maps{$url});
	push(@cols, "<a href=\"$url\">$url</a>");

	print &ui_columns_row(\@cols, \@tds);
}
print &ui_columns_end();


print &ui_form_start("edit_proxy.cgi", "post");
print &ui_hidden('submit_flag', 1);
print &ui_table_start($text{'proxy_add_options'}, undef, 2);

my @apps = get_all_war_infos();
@opt_apps = ( );
foreach $app (@apps) {
	push(@opt_apps, [ $app, $app ]);
}
print &ui_table_row($text{'proxy_wildcard'},
						&ui_checkbox("app_wildcard", 1, $text{'proxy_wildcard_info'}, 0), 2);
print &ui_table_hr();
print &ui_table_row($text{'wars_installed'}, &ui_select("app_name", undef, \@opt_apps, 10, 1), 2);
print &ui_table_row($text{'proxy_default_app'},
						&ui_checkbox("app_default", 1, $text{'proxy_app_default_warning'}, 0), 2);
print &ui_table_row($text{'proxy_ssl'},
						&ui_checkbox("proxy_ssl", 1, $text{'proxy_ssl_info'}, 0), 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'proxy_installok'} ] ]);


print &ui_form_start("edit_proxy.cgi", "post");
print &ui_hidden('submit_flag', 1);
print &ui_table_start($text{'proxy_remove_options'}, undef, 2);


@opt_paths = ( );
foreach $path (keys %maps) {
	my $val = $maps{$path};
	push(@opt_paths, [ $val, $val ]);
}
print &ui_table_row($text{'proxy_list'}, &ui_select("app_path", undef, \@opt_paths, 10, 1), 2);

print &ui_table_end();
print &ui_form_end([ [ "", $text{'proxy_removeok'} ] ]);

&ui_print_footer("", $text{'index_return'});
