#!/bin/bash
export https_proxy=http://192.168.10.254:3128/
killall -9 telegraf
rm -f /etc/init/telegraf.conf
rm -rf ~/telegraf*
unlink /usr/bin/telegraf
cd ~
touch /etc/init/telegraf.conf
cat <<EOT>> /etc/init/telegraf.conf
# Run node_exporter
start on startup
script
/usr/bin/telegraf --config.file /etc/telegraf/telegraf.yml
end script
EOT
service node_exporter start
