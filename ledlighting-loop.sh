cd `dirname $0`
while [ 1 ]; do
	/usr/bin/env python dmx.py
	echo "python died, restarting in 5..."
	sleep 5
done


