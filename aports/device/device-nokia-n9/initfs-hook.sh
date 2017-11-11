#!/bin/bash

watchdog_kick() {
  while :
  do
    for wd in /dev/watchdog*; do
      if [ -c $wd ]; then
        echo X > $wd
      fi
    done
    if [ -f /bin/sleep ]; then
      /bin/sleep 2s
    else
      return 0
    fi
  done
}

watchdog_kick &
