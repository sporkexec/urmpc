import socket
import mpd

class MPDClient(object):
	"""Wraps mpd.MPDClient to handle connection stupidity.

	You can use it exactly like mpd.MPDClient. It will attempt to reopen the
	connection if it drops out, raising mpd.ConnectionError if it fails."""

	_connect_config = ((), {}) # so __getattr__ can't infinitely recurse.

	def __init__(self):
		super(MPDClient, self).__init__()
		self._mpc = mpd.MPDClient()

	def connect(self, *args, **kwargs):
		"""Connect to the MPD server. Only call this once."""
		self._connect_config = (args, kwargs)
		self._mpc.connect(*args, **kwargs)

	def __getattr__(self, attr):
		"""Tries to make sure a connection is established.

		This may be trickier than it seems since python-mpd apparently has no
		way to gracefully recover from a dropped connection. Thus we end up
		constantly poking it in the spleen just to keep it alive."""
		try:
			self._mpc.ping()
		except (AttributeError, socket.error, mpd.ConnectionError) as e:
			self._mpc._sock = None # used by connect()
			self._mpc._rfile = None # actually transfers data
			args, kwargs = self._connect_config
			try:
				self._mpc.connect(*args, **kwargs)
				self._mpc.ping()
			except (AttributeError, TypeError, socket.error,
					mpd.ConnectionError) as e:
				raise mpd.ConnectionError('Cannot establish connection')
		return self._mpc.__getattr__(attr)

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

