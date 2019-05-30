#!/usr/bin/perl

use File::Path 'rmtree';

require './tomcat-lib.pl';
&ReadParse();

sub uninstall_lib{
	my $lib_name = $_[0];

	#get extension files
	my $lib_list = "$module_config_directory/lib_$lib_name.list";
	my %lib_files;
	&read_file($lib_list, \%lib_files);

	foreach $j (keys %lib_files){
		if( -e $lib_files{$j} or -l $lib_files{$j}){
			&unlink_file($lib_files{$j});
			print "<tt>$lib_files{$j}</tt><br>";
		}elsif( -d $lib_files{$j}){
			rmtree($lib_files{$j});
		}else{
			print "Listed jar <tt>$j</tt> doesn't exist!<br>";
		}
	}
	&unlink_file($lib_list);

	print "<hr>Uninstall of <tt>$lib_name</tt> is successful<br>";
}

&error_setup($text{'delete_err'});
&ui_print_header(undef, $text{'libs_uninstall_title'}, "");

@libs = split(/\0/, $in{'inst_lib'});
@libs || &error($text{'delete_enone'});

tomcat_service_ctl('stop');

#delete each of the specified directories
my $catalina_home = get_catalina_home();
foreach $lib (@libs) {
	print "Removing $lib<br>";
	uninstall_lib($lib);
}

tomcat_service_ctl('start');

&ui_print_footer("", $text{'index_return'});
