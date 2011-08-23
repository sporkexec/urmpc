#!/usr/bin/env python2
import urwid

import urmpd
import signals
from ui_main import MainFrame

palette = [
	('ArtistWalker_main', 'white', 'black'),
	('ArtistWalker_focus', 'light cyan', 'black'),
	('AlbumWalker_main', 'white', 'black'),
	('AlbumWalker_focus', 'light cyan', 'black'),
	('TrackWalker_main', 'white', 'black'),
	('TrackWalker_focus', 'light cyan', 'black'),
	('NowPlayingWalker_main', 'white', 'black'),
	('NowPlayingWalker_focus', 'light cyan', 'black'),
]

mpc = urmpd.MPDClient()
mpc.connect('localhost', 6600)

# Main widget uses mpd
frame = MainFrame(mpc)

# Get urwid set up
event_loop = urwid.SelectEventLoop()
loop = urwid.MainLoop(frame, palette, event_loop=event_loop)

# Idler runs cloned mpc connection, uses MainLoop to force redraw on MPD events
idler = urmpd.Idler(mpc, loop)
event_loop.watch_file(idler, idler)

signals._mainloop = loop
loop.run()

