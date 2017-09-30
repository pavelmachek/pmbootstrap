#!/bin/sh

### BEGIN INIT INFO
# Provides:          fixtime
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# X-Interactive:     true
# Short-Description: Fix time to be monotonic
# Description:       On machines that forget time when battery is removed,
#                    at least make sure time is monotonic.
### END INIT INFO

F=/etc/fixtime.time

case "$1" in
    start)
	SAVED=$(cat $F)
	if [ $(date +%s) -lt $SAVED ];
	then
	    date -s @$SAVED
	fi
	date +%s > $F
	;;
    stop)
	date +%s > $F
	;;
    esac

