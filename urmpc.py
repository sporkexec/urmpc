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

mpc = MPDClient('localhost', 6600)

frame = MainFrame(mpc)

loop = MainLoop(frame, palette)

# We need to turn off idling in order to handle normal MPD commands.
# Rapidly toggling it on/off whenever we do something is _very_ slow.
# So we monkeypatch urwid to leave idle off for 0.1s after each event.
# This way, tight loops (like scrolling by holding the down key) run at a
# tolerable speed. This has the downside of leaving us unable to detect changes
# while the user is doing things.
# We must do one of:
#  - Explicitly check for changes often (before idle goes on?) Probably stupid.
#  - Cache lots of things and try to reduce synchronous MPD commands to the
#    point where we can leave idle on and use send_* commands to communicate.
#    I've kind of tried this, it looks painful.
#  - Introduce another connection to the mix:
#    - Set up another connection idling, toss into the select() loop. Pick me!
#    - Set up another connection with synchronous idling in another thread
#      or process, and send events to another fd or pipe, respectively, which
#      we toss into the select() loop. Sounds too complicated, I think I'm just
#      dick-swinging with this one.
# Looks like we can remove a lot of complexity at the low, low, cost of another
# connection to MPD. Too bad it makes this entire commit pointless...

class UpdateWrap:
	def __init__(self, fun, mpc, interval):
		self.fun = fun
		self.alarm = None
		self.mpc = mpc
		self.interval = interval
	def __call__(self, *args, **kwargs):
		loop.remove_alarm(self.alarm)
		self.mpc.allow_idle(False)
		ret = self.fun(*args, **kwargs)
		self.alarm = loop.set_alarm_in(self.interval, self.callback)
		return ret
	def callback(self, loop, data):
		self.mpc.allow_idle(True)

# If you doubt the performance issue, comment this out and see for yourself.
loop._update = UpdateWrap(loop._update, mpc, 0.1)

loop.run()

