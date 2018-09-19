#!/bin/bash
export https_proxy=http://192.168.10.254:3128/
killall -9 alertmanager
rm -f /etc/init/alermanager.conf
rm -rf ~/alermanager*
unlink /usr/bin/alertmanager
cd ~
touch /etc/init/alertmanager.conf
cat <<EOT>> /etc/init/alertmanager.conf
# Run node_exporter
start on startup
script
/etc/alertmanager/alertmanager 
end script
EOT
service alertmanager start
