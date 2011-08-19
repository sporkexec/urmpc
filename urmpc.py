#!/usr/bin/env python2

from urwid import MainLoop

from urmpd import MPDClient
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

mpc = MPDClient()
mpc.connect('localhost', 6600)

frame = MainFrame(mpc)

loop = MainLoop(frame, palette)
loop.run()

