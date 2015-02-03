#!/bin/sh

# hacky launch for MHV led lighting 
/usr/bin/sudo /usr/bin/screen -S leduplighting -dm \
	-c /opt/leduplighting/screenrc 
