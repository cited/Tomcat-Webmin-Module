# !/bin/bash -e
# Tomcat Module Script for Rocky Linux
# Usage:
# wget https://raw.githubusercontent.com/cited/Tomcat-Webmin-Module/master/scripts/rocky-linux.sh
# chmod +x pre-installer
# ./pre-installer.sh

function get_deps(){

	yum -y install wget unzip bzip2

}

function setup_selinux(){
	
  #allow apache port for django app
  semanage port -a -t http_port_t -p tcp 7800
  semanage port -m -t http_port_t -p tcp 9000

  setsebool -P httpd_can_network_connect 1
}


function install_apache(){
	
		yum -y install httpd
	
}

function install_webmin(){
	wget -P/tmp 'https://download.webmin.com/developers-key.asc'
	rpm --import /tmp/developers-key.asc || true
	cp -f /tmp/developers-key.asc /etc/pki/rpm-gpg/RPM-GPG-KEY-webmin-developers

  cat >/etc/yum.repos.d/webmin.repo <<EOF
[Webmin]
name=Webmin Distribution Neutral
baseurl=https://download.webmin.com/download/newkey/yum
enabled=1
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-webmin-developers
EOF

  dnf --nogpgcheck install -y webmin tar rsync
	
	
}


function install_certbot_module(){

	dnf install epel-release mod_ssl -y
 	dnf install certbot python3-certbot-apache -y
	
	systemctl restart httpd

  pushd /opt/
    wget --quiet https://github.com/cited/Certbot-Webmin-Module/archive/master.zip
    unzip master.zip
    mv Certbot-Webmin-Module-master certbot
    tar -czf /opt/certbot.wbm.gz certbot
    rm -rf certbot master.zip

    /usr/libexec/webmin/install-module.pl certbot.wbm.gz
  popd
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

	/usr/libexec/webmin/install-module.pl tomcat.wbm.gz
       
popd
        echo -e "Tomcat module is now installed. Go to Servers > Tomcat to complete installation"
	
}

get_deps;
#install_apache;
#install_webmin;
#download_certbot_module;
setup_selinux;
#install_certbot_module;
download_tomcat_module;
install_tomcat_module;
