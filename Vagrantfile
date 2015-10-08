# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"
ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.synced_folder ".", "/vagrant", disabled: true

  config.ssh.username = "docker"
  config.ssh.password = "tcuser"
  config.ssh.insert_key = true

  config.vm.provider :docker do |provider|
    provider.vagrant_vagrantfile = "scripts/Vagrantfile.host"
  end

  config.vm.boot_timeout = 60

  config.vm.define "db" do |db|
    db.vm.provider "docker" do |d|
      d.build_dir = "scripts"
      d.dockerfile = "Dockerfile.db"
      d.name = "postgres"
      d.volumes = ["/var/lib/pgsql/data"]
      d.expose = [5432]
    end
  end

  config.vm.define "app" do |app|
    app.vm.synced_folder ".", "/srv/genelist", type: "rsync", rsync__exclude: [".git/", "venv/", "working/"], rsync__auto:true
    app.vm.provider "docker" do |d|
      d.name = "app"
      d.build_dir = "scripts"
      d.dockerfile = "Dockerfile.app"
      d.ports = [ "5000:5000" ]
      d.link("postgres:postgres")
    end
  end

end
