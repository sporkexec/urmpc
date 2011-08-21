import socket
import mpd

class MPDClient(object):
	_host_port = None, None
	_allow_idle = True
	
	def __init__(self, host, port):
		self._mpc = mpd.MPDClient()
		self._host_port = host, port
		self._connect()

	def allow_idle(self, state=True):
		self._allow_idle = state
		if state is True:
			self._idle()
		else:
			self._noidle()

	def _connect(self):
		self._mpc._reset()
		self._mpc.connect(*self._host_port)

	def _connect_wrap(self, func):
		"""Wrap an MPDClient function to reconnect if it drops out.
		It should be used on nearly everything, there's no real overhead."""
		def wrap(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except (socket.error, mpd.ConnectionError) as e:
				try:
					self._connect()
					#TODO: Should we start idling after reconnecting?
					return func(*args, **kwargs)
				except (socket.error, mpd.ConnectionError) as e:
					raise mpd.ConnectionError('Cannot establish connection')
		return wrap

	def _idle_wrap(self, func):
		"""Wrap an MPDClient function to stop idling while it runs."""
		def wrap(*args, **kwargs):
			if self._allow_idle is False:
				return func(*args, **kwargs)
			else:
				self._noidle()
				ret = func(*args, **kwargs)
				self._idle()
				return ret
		return wrap
	def _idle(self):
		if not self._mpc._pending:
			self._connect_wrap(self._mpc.send_idle)()
	def _noidle(self):
		if not self._mpc._pending:
			return
		self._connect_wrap(self._mpc.send_noidle)()
		try:
			self._connect_wrap(self._mpc.fetch_idle)()
		except mpd.PendingCommandError as e:
			pass # Unnecessary but unharmful.

	def __getattr__(self, attr):
		attribute = self._mpc.__getattr__(attr)
		if not hasattr(attribute, '__call__'):
			return attribute
		function = self._connect_wrap(attribute)
		if attr.find('idle') is -1:
			if attr.startswith('send_') or attr.startswith('fetch_'):
				raise AttributeError("'%s': Do not use pending commands" % attr)
			function = self._idle_wrap(function)
		return function


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

