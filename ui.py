import urwid

def sends_signal(*signals):
	def classmaker(cls):
		urwid.register_signal(cls, signals)
		return cls
	return classmaker


class IOWalker(urwid.ListWalker):
	def __init__(self):
		self.focus = 0
		self.items = []
		self._reload()
	def get_focus(self):
		return self._get_at_pos(self.focus)
	def set_focus(self, focus):
		self.focus = focus
		self._modified()
	def get_next(self, pos):
		return self._get_at_pos(pos + 1)
	def get_prev(self, pos):
		return self._get_at_pos(pos - 1)
	def _get_at_pos(self, pos):
		if pos < 0:
			return None, None
		try:
			ret = self.items[pos]
		except IndexError as e:
			return None, None
		return ret, pos
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

@sends_signal('change')
class ArtistWalker(IOWalker):
	def __init__(self, io):
		self.io = io
		super(ArtistWalker, self).__init__()
	def set_focus(self, focus):
		super(ArtistWalker, self).set_focus(focus)
		urwid.emit_signal(self, 'change', self.items[focus])
	def _get_items(self):
		return sorted(self.io.list('artist'))
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'ArtistWalker_main', 'ArtistWalker_focus')
	def _get_at_pos(self, pos):
		item, pos = super(ArtistWalker, self)._get_at_pos(pos)
		if item is None or pos is None:
			return item, pos
		if item == '':
			item = '[None]'
		item = urwid.Text(item)
		item.set_wrap_mode('clip')
		return self._attrmap(item), pos

@sends_signal('change')
class AlbumWalker(IOWalker):
	def __init__(self, io, artist):
		self.io = io
		self.artist = artist
		super(AlbumWalker, self).__init__()
	def set_focus(self, focus):
		super(AlbumWalker, self).set_focus(focus)
		urwid.emit_signal(self, 'change', (self.artist, self.items[focus]))
	def _get_items(self):
		return sorted(self.io.list('album', 'artist', self.artist))
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'AlbumWalker_main', 'AlbumWalker_focus')
	def change_artist(self, value):
		self.artist = value
		self._reload()
		self.set_focus(self.focus)
	def _get_at_pos(self, pos):
		item, pos = super(AlbumWalker, self)._get_at_pos(pos)
		if item is None or pos is None:
			return item, pos
		if item == '':
			item = '[None]'
		item = urwid.Text(item)
		item.set_wrap_mode('clip')
		return self._attrmap(item), pos

class TrackWalker(IOWalker):
	def __init__(self, io, artist, album):
		self.io = io
		self.artist = artist
		self.album = album
		super(TrackWalker, self).__init__()
	def _get_items(self):
		#TODO: Make sure this sorts like it should.
		return self.io.find('artist', self.artist, 'album', self.album)
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'TrackWalker_main', 'TrackWalker_focus')
	def change_album(self, artist_album):
		self.artist, self.album = artist_album
		self._reload()

	def _get_at_pos(self, pos):
		item, pos = super(TrackWalker, self)._get_at_pos(pos)
		if item is None or pos is None:
			return item, pos
		try:
			text = item['title']
		except KeyError as e:
			text = item['file']
		if text == '':
			text = '[None]'
		text = urwid.Text(text)
		text.set_wrap_mode('clip')
		return self._attrmap(text), pos


class TreeList(urwid.ListBox):
	def __init__(self, *args, **kwargs):
		self.keyremap = {
			'h': 'left',
			'j': 'down',
			'k': 'up',
			'l': 'right',
			'g': 'home',
			'G': 'end',
		}
		self.keymap = {
			'home': self._scroll_top,
			'end': self._scroll_bottom,
		}
		return super(TreeList, self).__init__(*args, **kwargs)

	def keypress(self, size, key):
		if key in self.keyremap:
			key = self.keyremap[key]
		if key in self.keymap:
			return self.keymap[key]()
		else:
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

	def _scroll_top(self):
		self.set_focus(0)
	def _scroll_bottom(self):
		self.set_focus(len(self.body.items)-1)

class MainFrame(urwid.Frame):
	def __init__(self, mpc, *args, **kwargs):
		self.mpc = mpc
		self.keymap = {
			'p': self.mpc.playpause,
			'>': self.mpc.next,
			'<': self.mpc.previous,

			's': self.mpc.stop,
			'c': self.mpc.clear,
			'Z': self.mpc.shuffle,
			'u': self.mpc.update,
			'-': self.mpc.volume_down,
			'+': self.mpc.volume_up,
			'b': lambda: self.mpc.urseek(-5, False, False), #FIXME config
			'f': lambda: self.mpc.urseek(5, False, False), #FIXME config

			'y': self.mpc.toggle('single'),
			'r': self.mpc.toggle('repeat'),
			'z': self.mpc.toggle('random'),
			'R': self.mpc.toggle('consume'),
			'x': self.mpc.toggle_crossfade,

			'q': self.quit,
			'Q': self.quit,
		}
		super(MainFrame, self).__init__(*args, **kwargs)

	def keypress(self, size, key):
		if key in self.keymap:
			return self.keymap[key]()
		else:
			return super(MainFrame, self).keypress(size, key)

	def quit(self):
		raise urwid.ExitMainLoop()


