#!/usr/bin/env python2

import mpd
import urwid

import iompd
import ui
import globalkeys

palette = [
	('ArtistWalker_main', 'white', 'black'),
	('ArtistWalker_focus', 'light cyan', 'black'),
	('AlbumWalker_main', 'white', 'black'),
	('AlbumWalker_focus', 'light cyan', 'black'),
	('TrackWalker_main', 'white', 'black'),
	('TrackWalker_focus', 'light cyan', 'black'),
]

io = iompd.MPDClient()
io.connect('localhost', 6600)

artist_walker = ui.ArtistWalker(io)
artists = ui.TreeList(artist_walker)

album_walker = ui.AlbumWalker(io, None)
albums = ui.TreeList(album_walker)

track_walker = ui.TrackWalker(io, None, None)
tracks = ui.TreeList(track_walker)

urwid.connect_signal(artist_walker, 'change', album_walker.change_artist)
urwid.connect_signal(album_walker, 'change', track_walker.change_album)
artist_walker.set_focus(artist_walker.focus) # Force a change event

#FIXME: Put everything in a frame or something, avoid the global keybindings.
keyhandler = globalkeys.GlobalKeys(io)

main = urwid.Columns((artists, albums, tracks))
loop = urwid.MainLoop(main, palette, unhandled_input=keyhandler.keypress)
loop.run()

