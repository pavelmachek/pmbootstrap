#!/bin/bash
F=/etc/fixtime.time
if [ $(date +%s) -lt $(< $F) ];
    then
    date -s @$(< $F)
    fi
date +%s > $F
