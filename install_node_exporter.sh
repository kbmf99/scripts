#!/bin/bash
export https_proxy=http://192.168.10.254:3128/
killall -9 node_exporter
rm -f /etc/init/node_exporter.conf
rm -rf ~/node_exporter*
unlink /usr/bin/node_exporter
cd ~
wget https://github.com/prometheus/node_exporter/releases/download/v0.15.2/node_exporter-0.15.2.linux-amd64.tar.gz
tar -xzvf ~/node_exporter-0.15.2.linux-amd64.tar.gz
mkdir ~/node_exporter
mv ~/node_exporter-0.15.2.linux-amd64/node_exporter ~/node_exporter
ln -s ~/node_exporter/node_exporter /usr/bin
touch /etc/init/node_exporter.conf
cat <<EOT>> /etc/init/node_exporter.conf
# Run node_exporter

start on startup

script
   /usr/bin/node_exporter  --collector.meminfo --web.listen-address=":9100" --collector.runit.servicedir="/etc/service" --collector.bonding --collector.bcache  --collector.arp --collector.conntrack --collector.cpu --collector.diskstats --collector.drbd --collector.edac --collector.entropy --collector.filefd --collector.filesystem --collector.hwmon --collector.infiniband --collector.interrupts --collector.ipvs --collector.ksmd --collector.loadavg --collector.logind --collector.mdadm  --collector.mountstats --collector.netdev --collector.netstat --collector.nfs --collector.qdisc --collector.sockstat --collector.stat --collector.tcpstat --collector.textfile --collector.time --collector.uname --collector.vmstat --collector.xfs --collector.zfs --collector.timex
end script
EOT
service node_exporter start
