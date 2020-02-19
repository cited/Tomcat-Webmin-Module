
# Tomcat Webmin Module

[![Documentation Status](https://readthedocs.org/projects/tomcat-webmin-module/badge/?version=latest)](https://tomcat-module.citedcorp.com/en/latest/?badge=latest)
# Info
Apache Tomcat Module for Webmin.  Install and Manage Apache Tomcat or Manage Existing Installations.

# How to install via CDN

Webmin->Webmin Configuration->Webmin Modules->From ftp or http URL

URL: https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat.wbm.gz

md5: https://cdn.acugis.com/apache-tomcat-webmin-plugin/acugis-tomcat-webmin-plugin.txt

Go to Servers->Apache Tomcat (you may need to refresh page)

# How to install from GIT
Archive module

$ git clone https://github.com/AcuGIS/Tomcat-Webmin-Module

$ mv Tomcat-Webmin-Module tomcat

$ tar -cvzf tomcat.wbm.gz tomcat/


Upload from Webmin->Webmin Configuration->Webmin Modules

Go to Servers->Apache Tomcat (you may need to refresh page)

# Notes

## **Ubuntu**
Tested on Ubuntu 14, 16, and 18

## **Readhat/Fedora/CentOS**
Tested on CentOS 6x64 and 7x64

haveged helps Tomcat start much faster.

	yum install epel-release
	yum install haveged
	chkconfig haveged on
  
## **Debian**
Tested on Debian 8 and 9

## **FreeBSD**
tomcat_env doesn't work, because tomcat service(/usr/local/etc/rc.d/tomcat8) is not sourcing the setenv.sh file. Work around is to set tomcat7_java_opts= in service file.

## **Arch**
Install tomcat packages manually and then install module, because Webmin doesn't support pacman. Go to Existing Tomcat Installations below.

	pacman --noconfirm -S tomcat8 tomcat-native jre8-openjdk

## **OpenSuSe**
Install tomcat packages manually and then install module.  Go to Existing Tomcat Installations below.

	zypper -n install tomcat tomcat-webapps tomcat-admin-webapps

## **Slackware**
Install Tomcat using one of our [scripts](https://github.com/AcuGIS)!

## **Existing Tomcat Installations**

The module can also be installed on existing Tomcat installations.  

1.  Install from Webmin->Webmin Configuration->Webmin Modules
2.  Go to Servers > Apache Tomcat
3.  Click config icon in top left corner
4.  Set the paths to those used on your installation

Once you have updated the /etc/webmin/tomcat/config file to your installation paths, you should be able to use all functionality.

## **Issues**
Please report issue here or at hello@acugis.com

# Screen Shots

Tomcat Module:

![tomcat webmin module](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-plugin.gif)

Tomcat Module WAR Manager:

![tomcat webmin module deploy wars](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-war-deploy.gif)

Tomcat Module Configuration Editor:

![tomcat webmin module edit configs](https://cdn.acugis.com/apache-tomcat-webmin-plugin/tomcat-module-edit-configs.gif)


Copyright
---------

* Copyright AcuGIS, 2019
* Copyright Cited, Inc., 2019

