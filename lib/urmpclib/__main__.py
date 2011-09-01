import urwid

import urmpd
import signals
from ui_main import MainFrame

import configuration
from configuration import config
config.read('urmpclib/urmpc.conf.example')

palette = configuration.extract_palette(config, 'palette')

mpc = urmpd.MPDClient()
mpc.connect(config.mpd.host, int(config.mpd.port))
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
