# !/bin/bash -e
# Tomcat Module Script for CentOS and Ubuntu
# For use on clean CentOS or Ubuntu box only
# Usage:
# wget https://raw.githubusercontent.com/cited/Tomcat-Webmin-Module/master/scripts/pre-install.sh
# chmod +x pre-installer
# ./pre-installer.sh

function get_repo(){
	if [ -f /etc/centos-release ]; then
		REPO='rpm'
 
	elif [ -f /etc/debian_version ]; then
		REPO='apt'
fi
}

function install_webmin(){

	if [ "${REPO}" == 'apt' ]; then

	echo "deb http://download.webmin.com/download/repository sarge contrib" > /etc/apt/sources.list.d/webmin.list
	wget -qO - http://www.webmin.com/jcameron-key.asc | apt-key add -
	apt-get -y update
	apt-get -y install webmin

	elif [ "${REPO}" == 'rpm' ]; then

cat >/etc/yum.repos.d/webmin.repo <<EOF
		[Webmin]
		name=Webmin Distribution Neutral
		#baseurl=https://download.webmin.com/download/yum
		mirrorlist=https://download.webmin.com/download/yum/mirrorlist
		enabled=1
		gpgkey=https://download.webmin.com/jcameron-key.asc
		gpgcheck=1
EOF
		yum -y install webmin

	fi
}	


function download_tomcat_module(){
pushd /tmp/
	wget https://github.com/cited/Tomcat-Webmin-Module/archive/master.zip
	unzip master.zip
	mv Tomcat-Webmin-Module-master tomcat
	tar -czf /opt/tomcat.wbm.gz tomcat
	rm -rf tomcat master.zip
popd
}

function install_tomcat_module(){
pushd /opt/
	if [ "${REPO}" == 'apt' ]; then
	/usr/share/webmin/install-module.pl tomcat.wbm.gz
        elif [ "${REPO}" == 'rpm' ]; then
        /usr/share/webmin/install-module.pl tomcat.wbm.gz
        fi
popd
        echo -e "Tomcat module is now installed. Go to Servers > Tomcat to complete installation"
	
}



function download_certbot_module(){
pushd /tmp/
	wget https://github.com/cited/Certbot-Webmin-Module/archive/master.zip
	unzip master.zip
	mv Certbot-Webmin-Module-master certbot
	tar -czf /opt/certbot.wbm.gz certbot
	rm -rf certbot master.zip
popd
}

function install_apache(){
	if [ "${REPO}" == 'apt' ]; then
		apt-get -y install apache2
	elif [ "${REPO}" == 'rpm' ]; then
		yum -y install httpd
	fi
}

function install_certbot_module(){
pushd /opt/
	if [ "${REPO}" == 'apt' ]; then
	/usr/share/webmin/install-module.pl certbot.wbm.gz
        elif [ "${REPO}" == 'rpm' ]; then
        /usr/libexec/webmin/install-module.pl certbot.wbm.gz
        fi
popd
        echo -e "Certbot is now installed. Go to Servers > Certbot to complete installation"
	
}

function get_deps(){
if [ "${REPO}" == 'apt' ]; then
		apt-get -y install wget unzip
	elif [ "${REPO}" == 'rpm' ]; then
		yum -y install wget unzip bzip2
    fi
}

get_repo;
get_deps;
# Uncomment line(s) below if you wish to install Webmin, Apache HTTP Server, and Certbot as well.
#install_webmin;
#install_apache;
#download_certbot_module;
#install_certbot_module;
download_tomcat_module;
install_tomcat_module;
