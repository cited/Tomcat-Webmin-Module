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
	
	mkdir -p /etc/webmin/authentic-theme
	cp -r /var/www/html/portal/*  /etc/webmin/authentic-theme
}
