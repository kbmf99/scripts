#!/bin/bash
export https_proxy=http://192.168.10.254:3128/
killall -9 promtheus
rm -f /etc/init/prometheus.conf
rm -rf ~/prometheus*
unlink /usr/bin/prometheus
cd ~
touch /etc/init/prometheus.conf
cat <<EOT>> /etc/init/prometheus.conf
# Run node_exporter
start on startup
script
/usr/bin/prometheus /usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries
end script
EOT
service node_exporter start
