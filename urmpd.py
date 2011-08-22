import socket
import mpd
import urwid

import signals

# See http://www.musicpd.org/doc/protocol/ch03.html
idle_events = (
	'database', # the song database has been modified after update.
	'playlist', # the current playlist has been modified
	'player', # the player has been started, stopped or seeked
	'mixer', # the volume has been changed
	'output', # an audio output has been enabled or disabled
	'options', # options like repeat, random, crossfade, replay gain
	'sticker', # the sticker database has been modified.
	'subscription', # a client has subscribed or unsubscribed to a channel
	'message', # a message was received on a channel this client is subscribed
	           # to; this event is only emitted when the queue is empty

	'update', # a database update has started or finished. If the database was
	          # modified during the update, the database event is also emitted.

	'stored_playlist', # a stored playlist has been modified, renamed, created
	                   # or deleted
)

class MPDClient(mpd.MPDClient):
	"""Used just like the normal MPDClient. It takes care of reconnecting
	to MPD when the connection drops out."""

	# Holds server address
	_host_port = None, None
	
	def connect(self, host, port):
		"""See mpd.MPDClient.connect(). You only _need_ to call this once."""
		self._host_port = host, port
		self._connect()

	def _connect(self):
		"""Forcefully kills the connection and opens it again."""
		super(MPDClient, self)._reset()
		super(MPDClient, self).connect(*self._host_port)

	def _connect_wrap(self, func):
		"""Wraps an MPDClient function to reconnect if it drops out.
		It should be used on nearly everything, there's no real overhead."""
		def wrap(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except (socket.error, mpd.ConnectionError) as e:
				try:
					self._connect()
					return func(*args, **kwargs)
				except (socket.error, mpd.ConnectionError) as e:
					raise mpd.ConnectionError('Cannot establish connection')
		return wrap

	def __getattr__(self, attr):
		"""Wraps any callable attribute with _connect_wrap."""
		attribute = super(MPDClient, self).__getattr__(attr)
		if not hasattr(attribute, '__call__'):
			return attribute
		return self._connect_wrap(attribute)


	## Utility functions from here on. Call them however you like.

	def playpause(self):
		if self.status()['state'] == 'play':
			self.pause()
		else:
			self.play()

	def toggle(self, name):
		"""Returns a function to toggle the given MPD flag."""
		# Get flag status, flip it, and send it back.
		return lambda: self.__getattr__(name)((1, 0)[int(self.status()[name])])

	def toggle_crossfade(self):
		# Really, 'xfade'? Four characters saved, good job!
		value = int(self.status()['xfade'])
		if value == 0:
			value = 3 #FIXME: This (and other things) should be configurable.
		else:
			value = 0
		# With inconsistency as the cherry on top.
		self.crossfade(value)

	def volume_up(self):
		vdiff = 1
		self.volume_diff(vdiff) #FIXME config
	def volume_down(self):
		vdiff = 1
		self.volume_diff(vdiff * -1) #FIXME config
	def volume_diff(self, diff):
		level = diff + int(self.status()['volume'])
		if diff > 0:
			level = min(level, 100)
		else:
			level = max(level, 0)
		self.setvol(level)

	def urseek(self, diff, absolute=False, percentage=False):
		"""Seek to an absolute or relative position.

		Be aware that we will gladly skip *over* track boundaries.
		For example, if you are at 1:27 in a 1:30 song and ask to jump ahead 5
		seconds, you will end up at 0:01 in the next song.
		This is a feature, not a bug."""
		# Query MPD
		status = self.status()
		try:
			song = int(status['song'])
		except KeyError as e:
			return # No song currently loaded.
		now, total = map(int, self.status()['time'].split(':'))

		if percentage is True:
			diff = diff * 0.01 * total

		if absolute is False:
			target = now + diff
		else:
			target = diff

		if target > total:
			target -= total
			self.next()
			self.seek(target, True, False)
		elif target < 0:
			if song == 0:
				return # No previous song
			self.previous()
			now, total = map(int, self.status()['time'].split(':'))
			self.seek(total+target, False, False)
		else:
			# Typical case
			self.seek(song, target)

class Idler(MPDClient):
	"""Idles for MPD events and reports them."""
	_mainloop = None
	def __init__(self, mainmpc, mainloop):
		"""Steal credentials from main connection and starts idling."""
		super(Idler, self).__init__()
		self._mainloop = mainloop
		self._host_port = mainmpc._host_port
		self.send_idle()

	def __call__(self):
		"""Goes back to idling and emits the MPD events to the system."""
		# Grab events and idle
		events = self.fetch_idle()
		self.send_idle()

		# Emit events, force redraw if necessary
		redraw = False
		for event in events:
			redraw |= signals.emit('idle_'+event)
		if redraw:
			self._mainloop.draw_screen()

