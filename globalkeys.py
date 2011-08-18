import urwid

class GlobalKeys(object):
	def keypress(self, key):
		if key in self.keymap:
			self.keymap[key]()
	def __init__(self, mpc):
		super(GlobalKeys, self).__init__()
		self.mpc = mpc
		self.keymap = {
			'p': self.playpause,
			'>': self.mpc.next,
			'<': self.mpc.previous,

			's': self.mpc.stop,
			'c': self.mpc.clear,
			'Z': self.mpc.shuffle,
			'u': self.mpc.update,
			'-': self.volume_down,
			'+': self.volume_up,
			'b': lambda: self.seek(-5, False, False), #FIXME config
			'f': lambda: self.seek(5, False, False), #FIXME config

			'y': self.toggle('single'),
			'r': self.toggle('repeat'),
			'z': self.toggle('random'),
			'R': self.toggle('consume'),
			'x': self.toggle_crossfade,

			'q': self.quit,
			'Q': self.quit,
		}

	def playpause(self):
		if self.mpc.status()['state'] == 'play':
			self.mpc.pause()
		else:
			self.mpc.play()

	def toggle(self, name):
		"""Returns a function to toggle the given MPD flag."""
		# Get flag status, flip it, and send it back.
		return lambda: self.mpc.__getattr__(name)((1, 0)[int(self.mpc.status()[name])])

	def toggle_crossfade(self):
		# Really, 'xfade'? Four characters saved, good job!
		value = int(self.mpc.status()['xfade'])
		if value == 0:
			value = 3 #FIXME: This (and other things) should be configurable.
		else:
			value = 0
		# With inconsistency as the cherry on top.
		self.mpc.crossfade(value)

	def volume_up(self):
		vdiff = 1
		self.volume_diff(vdiff) #FIXME config
	def volume_down(self):
		vdiff = 1
		self.volume_diff(vdiff * -1) #FIXME config
	def volume_diff(self, diff):
		level = diff + int(self.mpc.status()['volume'])
		if diff > 0:
			level = min(level, 100)
		else:
			level = max(level, 0)
		self.mpc.setvol(level)

	def seek(self, diff, absolute=False, percentage=False):
		"""Seek to an absolute or relative position.

		Be aware that we will gladly skip *over* track boundaries.
		For example, if you are at 1:27 in a 1:30 song and ask to jump ahead 5
		seconds, you will end up at 0:01 in the next song.
		This is a feature, not a bug."""
		# Query MPD
		status = self.mpc.status()
		try:
			song = int(status['song'])
		except KeyError as e:
			return # No song currently loaded.
		now, total = map(int, self.mpc.status()['time'].split(':'))

		if percentage is True:
			diff = diff * 0.01 * total

		if absolute is False:
			target = now + diff
		else:
			target = diff

		if target > total:
			target -= total
			self.mpc.next()
			self.seek(target, True, False)
		elif target < 0:
			if song == 0:
				return # No previous song
			self.mpc.previous()
			now, total = map(int, self.mpc.status()['time'].split(':'))
			self.seek(total+target, False, False)
		else:
			# Typical case
			self.mpc.seek(song, target)

	def quit(self):
		raise urwid.ExitMainLoop()

