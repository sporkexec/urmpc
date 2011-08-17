#!/usr/bin/env python2

import mpd
import urwid

import iompd
import ui

palette = [
	('ArtistWalker_main', 'white', 'black'),
	('ArtistWalker_focus', 'light cyan', 'black'),
]


io = iompd.MPDClient()
io.connect('localhost', 6600)

artist_walker = ui.ArtistWalker(io)
artists = ui.TreeList(artist_walker)

album_walker = ui.AlbumWalker(io, None)
albums = ui.TreeList(album_walker)


urwid.connect_signal(artist_walker, 'change', album_walker.change_artist)


main = urwid.Columns((artists, albums))
loop = urwid.MainLoop(main, palette)#, unhandled_input=artists.unhandled_keypress)
loop.run()

