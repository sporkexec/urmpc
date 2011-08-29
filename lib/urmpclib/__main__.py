import urwid

import urmpd
import signals
from ui_main import MainFrame

palette = [
	('header.flags', 'light cyan', 'default'),
	('header.border', 'dark gray', 'default'),

	('library.column', 'default', 'black'),
	('library.column.focus', 'dark cyan,standout', 'black'),
	('library.divider', 'dark gray', 'default'),

	('playlist.time', 'dark cyan', 'default'),
	('playlist.artist', 'dark magenta', 'default'),
	('playlist.title', 'dark green', 'default'),
	('playlist.album', 'dark red', 'default'),
	('playlist.time.focus', 'dark cyan,standout', 'default'),
	('playlist.artist.focus', 'dark magenta,standout', 'default'),
	('playlist.title.focus', 'dark green,standout', 'default'),
	('playlist.album.focus', 'dark red,standout', 'default'),

	('footer.progress', 'white', 'black'),
	('footer.progress.elapsed', 'white', 'dark green'),
	('footer.progress.smoothed', 'dark green', 'black'),
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