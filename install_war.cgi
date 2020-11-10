#!/usr/bin/perl

require './tomcat-lib.pl';
use File::Basename;
use File::Path 'rmtree';

sub inst_error{
	print "<b>$main::whatfailed : $_[0]</b> <p>\n";
	&ui_print_footer("", $text{'index_return'});
	exit;
}

if($ENV{'CONTENT_TYPE'} =~ /boundary=(.*)$/) { &ReadParseMime(); }
else { &ReadParse(); $no_upload = 1; }

$| = 1;
$theme_no_table = 1 if ($in{'source'} == 2 || $in{'source'} == 4);
&ui_print_header(undef, $text{'install_title'}, "");

my $file = process_file_source();

my @suffixlist = ('\.zip', '\.war');
($file_name,$path,$file_suffix) = fileparse($file,@suffixlist);

my $unzip_dir = '';
my @wars;

#Check if its a .zip or .jar
print "Source: $file<br>";
if($file_suffix eq ".zip"){
	$unzip_dir = unzip_file($file);

	#make a list of extension jars
	opendir(DIR, $unzip_dir) or die $!;
	@wars = grep { $_ = $unzip_dir.'/'.$_ ; -f && /\.war$/ } readdir(DIR);
	closedir(DIR);

}elsif($file_suffix eq ".war"){
	push(@wars, $file);
}else{
	&error("Error: Unsupported file type $file_suffix");
	&ui_print_footer("", $text{'index_return'});
}

$catalina_home = get_catalina_home();

foreach $war (@wars) {
	my $war_name = basename($war);
	if(!move($war, "$catalina_home/webapps/")){
		&error("Error: Can't move file: $!");
	}else{
		print "Install of $war_name is successful<br>";
	}
	&set_ownership_permissions('tomcat','tomcat', 0444, "$catalina_home/webapps/$war_name");
}

if($unzip_dir ne ''){
	&rmtree($unzip_dir);	#remove temp dir
}

#tomcat_service_ctl('restart');

&ui_print_footer("", $text{'index_return'});
