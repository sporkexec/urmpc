import urwid

import ui_lists

class MainFrame(urwid.Frame):
	def __init__(self, mpc):
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

			'tab': self.toggle_panel,

			'q': self.quit,
			'Q': self.quit,
		}

		self.librarypanel = LibraryPanel(mpc)
		self.nowplayingpanel = NowPlayingPanel(mpc)

		super(MainFrame, self).__init__(self.librarypanel)

	def keypress(self, size, key):
		if key in self.keymap:
			return self.keymap[key]()
		else:
			return super(MainFrame, self).keypress(size, key)

	def toggle_panel(self):
		if self.get_body() is self.librarypanel:
			self.set_body(self.nowplayingpanel)
		elif self.get_body() is self.nowplayingpanel:
			self.set_body(self.librarypanel)

	def quit(self):
		raise urwid.ExitMainLoop()

class NowPlayingPanel(ui_lists.TreeList):
	def __init__(self, mpc):
		super(NowPlayingPanel, self).__init__(ui_lists.NowPlayingWalker(mpc))
		self.keyremap.update({
		})
		self.keymap.update({
			'enter': self.body.play_current,
			'd': self.body.delete_current,
		})

class LibraryPanel(urwid.Columns):
	def __init__(self, mpc):
		self.mpc = mpc

		artist_walker = ui_lists.ArtistWalker(mpc)
		artists = ui_lists.PlayableList(artist_walker)

		album_walker = ui_lists.AlbumWalker(mpc, None)
		albums = ui_lists.PlayableList(album_walker)

		track_walker = ui_lists.TrackWalker(mpc, None, None)
		tracks = ui_lists.PlayableList(track_walker)

		urwid.connect_signal(artist_walker, 'change', album_walker.change_artist)
		urwid.connect_signal(album_walker, 'change', track_walker.change_album)
		artist_walker.set_focus(artist_walker.focus) # Force a change event

		self.artists = artists
		self.albums = albums
		self.tracks = tracks

		super(LibraryPanel, self).__init__((artists, albums, tracks))
