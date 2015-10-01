#!/bin/bash

sudo cp /vagrant/rethinkdb-instance.conf /etc/rethinkdb/instances.d/rethinkdb-instance.conf
sudo /etc/init.d/rethinkdb restart
