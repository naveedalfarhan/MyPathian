#!/usr/bin/env bash

add-apt-repository -y ppa:rethinkdb/ppa
apt-get update

# install packages
apt-get install -y python-dev
apt-get install -y libffi-dev
apt-get install -y pkg-config
apt-get install -y python-protobuf
apt-get install -y python-pip
apt-get install -y libiodbc2
apt-get install -y odbcinst1debian2
apt-get install -y iodbc
apt-get install -y unixodbc
apt-get install -y unixodbc-dev
apt-get install -y rethinkdb
cp /etc/rethinkdb/default.conf.sample /etc/rethinkdb/instances.d/pathian.conf
/etc/init.d/rethinkdb restart

pip install virtualenv

groupadd pathian
usermod -a -G pathian ubuntu
mkdir /pathian
chgrp pathian /pathian
chmod g+rwxs /pathian
mkdir /pathian/uploads
chgrp pathian /pathian/uploads
chmod g+rwxs /pathian/uploads
mkdir /pathian/site
chgrp pathian /pathian/site
chmod g+rwxs /pathian/site
mkdir /var/log/pathian
chgrp pathian /var/log/pathian
chmod g+rwxs /var/log/pathian


#virtualenv configuration
virtualenv /pathian/env
chgrp -R pathian /pathian/env
chmod g+rw -R /pathian/env
/pathian/env/bin/pip install uwsgi


#nginx configuration
apt-get install -y nginx
apt-get install -y supervisor

rm /etc/nginx/sites-enabled/default
cp nginx_site_config.conf /etc/nginx/sites-available/pathian.conf
ln -s /etc/nginx/sites-available/pathian.conf /etc/nginx/sites-enabled/pathian.conf
cp supervisor_config.conf /etc/supervisor/conf.d/pathian.conf
cp pathian.uwsgi /pathian/pathian.uwsgi
chgrp pathian /pathian/pathian.uwsgi
chmod g+rw /pathian/pathian.uwsgi
/etc/init.d/supervisor restart
/etc/init.d/nginx restart