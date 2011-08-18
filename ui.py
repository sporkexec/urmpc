import urwid

class IOWalker(urwid.ListWalker):
	emptytext = '[None]'
	def __new__(cls, *args, **kwargs):
		urwid.register_signal(cls, ['change'])
		return super(IOWalker, cls).__new__(cls, *args, **kwargs)
	def __init__(self):
		self.focus = 0
		self.items = []
		self._reload()
	def get_focus(self):
		return self._get_at_pos(self.focus)
	def set_focus(self, focus):
		self.focus = focus
		self._modified()
		urwid.emit_signal(self, 'change', self.items[focus])
	def get_next(self, pos):
		return self._get_at_pos(pos + 1)
	def get_prev(self, pos):
		return self._get_at_pos(pos - 1)
	def _get_at_pos(self, pos):
		if pos < 0:
			return None, None
		try:
			text = self.items[pos]
		except IndexError as e:
			return None, None
		if text == '':
			text = self.emptytext
		item = urwid.Text(text)
		item.set_wrap_mode('clip')
		item = self._attrmap(item)
		return item, pos
	def _reload(self):
		"""Grab items from datastore and apply any changes, attempting to
		preserve focus on current item if possible."""
		item, focus = self.get_focus(), self.focus
		self.items[:] = self._get_items()
		try:
			if focus >= len(self.items) or item != self.items[focus]:
				self.focus = self.items.index(item)
		except ValueError as e:
			self.focus = 0
		self._modified()
	def _get_items(self):
		pass
	def _attrmap(self, w):
		return w

class ArtistWalker(IOWalker):
	def __init__(self, io):
		self.io = io
		super(ArtistWalker, self).__init__()
	def _get_items(self):
		return sorted(self.io.list('artist'))
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'ArtistWalker_main', 'ArtistWalker_focus')

class AlbumWalker(IOWalker):
	def __init__(self, io, artist):
		self.io = io
		self.artist = artist
		super(AlbumWalker, self).__init__()
	def _get_items(self):
		return sorted(self.io.list('album', 'artist', self.artist))
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'AlbumWalker_main', 'AlbumWalker_focus')
	def change_artist(self, value):
		self.artist = value
		self._reload()

class TreeList(urwid.ListBox):
	keymap = {
				'h': 'left',
				'j': 'down',
				'k': 'up',
				'l': 'right',
			}

	def keypress(self, size, key):
		if key in self.keymap:
			key = self.keymap[key]
		return super(TreeList, self).keypress(size, key)

	def _keypress_up(self, size):
		middle, top, bottom = self.calculate_visible(size, True)
		if middle is not None and middle[0] == 0:
			return super(TreeList, self)._keypress_up(size)
		w, pos = self.body.get_focus()
		w, pos = self.body.get_prev(pos)
		if w:
			self.set_focus(pos)

	def _keypress_down(self, size):
		middle, top, bottom = self.calculate_visible(size, True)
		if middle is not None and middle[0] + 1 == size[1]:
			return super(TreeList, self)._keypress_down(size)
		w, pos = self.body.get_focus()
		w, pos = self.body.get_next(pos)
		if w:
			self.set_focus(pos)

