#!/usr/bin/env python2

import mpd

import iompd

io = iompd.MPDClient()
io.connect('localhost', 6600)

print io.listall()

