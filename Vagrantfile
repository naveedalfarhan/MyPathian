# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
	# All Vagrant configuration is done here. The most common configuration
	# options are documented and commented below. For a complete reference,
	# please see the online documentation at vagrantup.com.

	# Every Vagrant virtual environment requires a box to build off of.
	config.vm.box = "ubuntu/trusty64"

	# Create a forwarded port mapping which allows access to a specific port
	# within the machine from a port on the host machine. In the example below,
	# accessing "localhost:8080" will access port 80 on the guest machine.
	config.vm.network :forwarded_port, guest: 8080, host: 1234
	config.vm.network :forwarded_port, guest: 8081, host: 8081
	config.vm.network :forwarded_port, guest: 28015, host: 28015
	config.vm.network :forwarded_port, guest: 29015, host: 29015

	# Create a private network, which allows host-only access to the machine
	# using a specific IP.

	config.vm.provider "virtualbox" do |v|
		v.name = "RethinkDB-Dev"
	end

	config.vm.provision :chef_solo do |chef|
		chef.cookbooks_path = ["cookbooks", "my_cookbooks"]
		chef.add_recipe "apt"
		chef.add_recipe "build-essential"
		chef.add_recipe "rethinkdb"
	end

	config.vm.provision :shell, :path => "provision.sh"
end
