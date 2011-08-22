import urwid

import signals

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
		return True
	def _get_items(self):
		pass
	def _attrmap(self, w):
		return w

@sends_signal('change')
class ArtistWalker(IOWalker):
	def __init__(self, mpc):
		self.mpc = mpc
		super(ArtistWalker, self).__init__()
		signals.listen('idle_database', self._reload)
	def set_focus(self, focus):
		super(ArtistWalker, self).set_focus(focus)
		urwid.emit_signal(self, 'change', self.items[focus])
	def _get_items(self):
		return sorted(self.mpc.list('artist'))
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

	def play_current(self):
		song_id = self.queue_current()
		if song_id is not None:
			self.mpc.playid(song_id)
	def queue_current(self):
		item, pos = super(ArtistWalker, self)._get_at_pos(self.focus)
		if item is None or pos is None:
			return None
		song_id = None
		for song in self.mpc.find('artist', item):
			sid = self.mpc.addid(song['file'])
			if song_id is None:
				song_id = sid
		return song_id

@sends_signal('change')
class AlbumWalker(IOWalker):
	def __init__(self, mpc, artist):
		self.mpc = mpc
		self.artist = artist
		super(AlbumWalker, self).__init__()
	def set_focus(self, focus):
		super(AlbumWalker, self).set_focus(focus)
		urwid.emit_signal(self, 'change', (self.artist, self.items[focus]))
	def _get_items(self):
		return sorted(self.mpc.list('album', 'artist', self.artist))
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

	def play_current(self):
		song_id = self.queue_current()
		if song_id is not None:
			self.mpc.playid(song_id)
	def queue_current(self):
		item, pos = super(AlbumWalker, self)._get_at_pos(self.focus)
		if item is None or pos is None:
			return None
		song_id = None
		for song in self.mpc.find('artist', self.artist, 'album', item):
			sid = self.mpc.addid(song['file'])
			if song_id is None:
				song_id = sid
		return song_id


class TrackWalker(IOWalker):
	def __init__(self, mpc, artist, album):
		self.mpc = mpc
		self.artist = artist
		self.album = album
		super(TrackWalker, self).__init__()
	def _get_items(self):
		#TODO: Make sure this sorts like it should.
		return self.mpc.find('artist', self.artist, 'album', self.album)
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

	def play_current(self):
		song_id = self.queue_current()
		if song_id is not None:
			self.mpc.playid(song_id)
	def queue_current(self):
		item, pos = super(TrackWalker, self)._get_at_pos(self.focus)
		if item is None or pos is None:
			return None
		song_id = None
		for song in self.mpc.find('file', item['file']):
			sid = self.mpc.addid(song['file'])
			if song_id is None:
				song_id = sid
		return song_id

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


class PlayableList(TreeList):
	def __init__(self, *args, **kwargs):
		super(PlayableList, self).__init__(*args, **kwargs)
		self.keyremap.update({
		})
		self.keymap.update({
			'enter': self.body.play_current,
			' ': self.body.queue_current,
		})

class NowPlayingWalker(IOWalker):
	def __init__(self, mpc):
		self.mpc = mpc
		super(NowPlayingWalker, self).__init__()
		signals.listen('idle_playlist', self._reload)
	def set_focus(self, focus):
		super(NowPlayingWalker, self).set_focus(focus)
		urwid.emit_signal(self, 'change', self.items[focus])
	def _get_items(self):
		return self.mpc.playlistinfo()
	def _attrmap(self, w):
		return urwid.AttrMap(w, 'NowPlayingWalker_main', 'NowPlayingWalker_focus')
	def _get_at_pos(self, pos):
		item, pos = super(NowPlayingWalker, self)._get_at_pos(pos)
		if item is None or pos is None:
			return item, pos

		text = "Artist: %s, Album: %s, Title: %s, Length: %s" % (item['artist'], item['album'], item['title'], item['time'])

		item = urwid.Text(text)
		item.set_wrap_mode('clip')
		return self._attrmap(item), pos

	def play_current(self):
		item, pos = super(NowPlayingWalker, self)._get_at_pos(self.focus)
		if item is None or pos is None:
			return
		self.mpc.playid(item['id'])

	def delete_current(self):
		item, pos = super(NowPlayingWalker, self)._get_at_pos(self.focus)
		if item is None or pos is None:
			return
		self.mpc.deleteid(item['id'])

