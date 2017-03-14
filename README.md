
# Tomcat Webmin Module

# Info
Apache Tomcat Module for Webmin.  Install and Manage Apache Tomcat or Manage Existing Installations.

# How to install via CDN

Webmin->Webmin Configuration->Webmin Modules->From ftp or http URL

https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat.wbm.gz

md5: https://cdn.acugis.com/apache-tomcat-webmin-plugin/acugis-tomcat-webmin-plugin.txt

# How to install from GIT
Archive module

$ git clone https://github.com/AcuGIS/Tomcat-Webmin-Plugin

$ mv Tomcat-Webmin-Plugin tomcat

$ tar -cvzf tomcat.wbm.gz /tomcat


Upload from Webmin->Webmin Configuration->Webmin Modules

# Notes

## **Ubuntu**
Tested on Ubuntu 12, 14, and 16

## **Readhat/Fedora/CentOS**
Tested on CentOS 6x64 and 7x64

haveged helps Tomcat start much faster.

	yum install epel-release
	yum install haveged
	chkconfig haveged on
  
## **Debian**
Tested on Debian 7 and 8

## **FreeBSD**
tomcat_env doesn't work, because tomcat service(/usr/local/etc/rc.d/tomcat8) is not sourcing the setenv.sh file. Work around is to set tomcat7_java_opts= in service file.

## **Arch**
Install tomcat packages manually and then install module, because Webmin doesn't support pacman

	pacman --noconfirm -S tomcat8 tomcat-native jre8-openjdk

## **OpenSuSe**
Install tomcat packages manually and then install module

	zypper -n install tomcat tomcat-webapps tomcat-admin-webapps

## **Slackware**
Install Tomcat using one of our [scripts](https://github.com/AcuGIS)!

## **Existing Tomcat Installations**

The module can also be installed on existing Tomcat installations.  Update the /etc/webmin/tomcat/config file to your installation paths.

## **Issues**
Please report issue here or at hello@acugis.com

# Screen Shots

Tomcat Module:

![tomcat webmin module](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-plugin.gif)

Tomcat Module WAR Manager:

![tomcat webmin module deploy wars](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-war-deploy.gif)

Tomcat Module Configuration Editor:

![tomcat webmin module edit configs](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-edit-configs.gif)
