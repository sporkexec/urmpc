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
	('SongElapsedBar', 'white', 'dark green'),
	('SongRemainingBar', 'white', 'black'),
]

mpc = urmpd.MPDClient()
mpc.connect('localhost', 6600)
event_loop = urwid.SelectEventLoop()


# Get urwid set up
#FIXME: Passing None in here is ugly and will eventually break if urwid decides
#       to be more strict about it.
loop = urwid.MainLoop(None, palette, event_loop=event_loop)
signals._mainloop = loop

# Main widget uses mpd
frame = MainFrame(mpc)
loop.widget = frame

# Idler runs cloned mpc connection, uses MainLoop to force redraw on MPD events
idler = urmpd.Idler(mpc, loop)
event_loop.watch_file(idler, idler)

loop.run()

