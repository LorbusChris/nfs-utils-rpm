#!/bin/bash

#
# Convert /etc/sysconfig/nfs values in /etc/nfs.conf valuse
#

#
# No file no conversion
#
if [ ! -f /etc/sysconfig/nfs ]; then
	exit 0
fi

# 
# See if the conversion happen already
#
grep "nfs.conf" /etc/sysconfig/nfs > /dev/null
if [ $? -eq 0 ]; then
	exit 0
fi

if [ -f /etc/nfs.conf.rpmnew ]; then
	# See if it is the we want to use 
	grep tag1234 /etc/nfs.conf.rpmnew > /dev/null
	if [ $? -eq 0 ]; then
		cp /etc/nfs.conf /etc/nfs.conf.rpmsave  
		cat /etc/nfs.conf.rpmnew | sed '/tag123/d' > /etc/nfs.conf
		rm /etc/nfs.conf.rpmnew
	fi
else
		cp /etc/nfs.conf /etc/nfs.conf.rpmsave
fi

#
# Do the conversion 
#
/usr/sbin/nfsconvert

