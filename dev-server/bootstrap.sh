#!/usr/bin/env bash

apt-get update

# install packages
apt-get install -y python-dev
apt-get install -y libffi-dev
apt-get install -y pkg-config
apt-get install -y python-protobuf
apt-get install -y python-pip
apt-get install -y iodbc
apt-get install -y unixodbc-dev
pip install virtualenv


mkdir /pathian-logs
chown www-data:www-data /pathian-logs
mkdir /pathian-uploads
chown www-data:www-data /pathian-uploads


#virtualenv configuration
rm -r /pathian
mkdir /pathian
virtualenv /pathian/env
/pathian/env/bin/pip install uwsgi
/pathian/env/bin/pip install --allow-external pyodbc --allow-unverified pyodbc -r /pathian_source_dir/requirements-pinned.txt


#nginx configuration
apt-get install -y nginx
apt-get install -y supervisor
ln -s /pathian_source_dir/dev-server/dev-server-config/supervisor_config.conf /etc/supervisor/conf.d/pathian.conf
mkdir /var/log/supervisor/pathian
service supervisor restart
ln -s /pathian_source_dir/dev-server/dev-server-config/nginx_site_config.conf /etc/nginx/sites-available/pathian.conf
rm /etc/nginx/sites-enabled/*
ln -s /etc/nginx/sites-available/pathian.conf /etc/nginx/sites-enabled/pathian.conf
/etc/init.d/nginx restart