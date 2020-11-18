
# Tomcat Webmin Module

[![Documentation Status](https://readthedocs.org/projects/tomcat-webmin-module/badge/?version=latest)](https://tomcat-module.citedcorp.com/en/latest/?badge=latest)
# Info

Apache Tomcat Module for Webmin.  

Install and Manage Apache Tomcat or Manage Existing Installations.

# Install via Webmin

Webmin->Webmin Configuration->Webmin Modules->From ftp or http URL

URL: http://github.com/cited/Tomcat-Webmin-Module/raw/master/scripts/tomcat.wbm.gz

Go to Servers->Apache Tomcat to complete set up using the setup Wizard (you may need to refresh page).

# Install via Script

As Root:

```bash
wget https://raw.githubusercontent.com/cited/Tomcat-Webmin-Module/master/scripts/pre-install.sh
chmod +x pre-install.sh
./pre-install.sh
```

Go to Servers->Apache Tomcat to complete set up using the setup Wizard.

# Install via GIT

As Root:

```bash
git clone https://github.com/cited/Tomcat-Webmin-Module
mv Tomcat-Webmin-Module-master tomcat
tar -cvzf tomcat.wbm.gz tomcat/
```

Upload from Webmin->Webmin Configuration->Webmin Modules

Go to Servers->Apache Tomcat (you may need to refresh page)

# Notes

## **Ubuntu**
Tested on Ubuntu 14, 16, 18, and 20

## **Readhat/Fedora/CentOS**
Tested on CentOS 6, 7, and 8

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

* Copyright AcuGIS, 2020
* Copyright Cited, Inc., 2020

