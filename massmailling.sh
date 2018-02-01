#!/bin/bash
set -x
awk -F"T=\"" '/<=/ {print $2}' /var/log/exim_mainlog | cut -d\" -f1 | sort | uniq -c | sort -n |grep -vf exclude |awk '{$1=""; print}' > /tmp/fisier1
cat /tmp/fisier1|sed 's/^[ \t]*//;s/[ \t]*$//' > /tmp/fisier2
sed 's/^\|$/"/g' /tmp/fisier2 > /tmp/fisier3
IFS='"'
for i in $(cat /tmp/fisier4)
do
grep "$i" /var/log/exim_mainlog | awk '{print $6}' | grep -E -o "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b"|sort|uniq -c|sort -n
done
