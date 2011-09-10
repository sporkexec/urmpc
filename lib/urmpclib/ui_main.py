# -*- coding: utf-8 -*-
import urwid

import ui_lists
import ui_status
import util
import configuration
from configuration import config

class MainFrame(urwid.Frame):
	def __init__(self, mpc):
		self.mpc = mpc
		seek_diff = int(config.mpd.seek_diff)
		seek_percentage = configuration.truthiness(config.mpd.seek_percentage)
		self.actionmap = {
			'playpause': self.mpc.playpause,
			'next_track': self.mpc.next,
			'previous_track': self.mpc.previous,
			'stop': self.mpc.stop,
			'clear_playlist': self.mpc.clear,
			'shuffle': self.mpc.shuffle,
			'update_database': self.mpc.update,
			'volume_down': self.mpc.volume_down,
			'volume_up': self.mpc.volume_up,
			'seek_back': lambda: self.mpc.urseek(seek_diff * -1, False, seek_percentage),
			'seek_forth': lambda: self.mpc.urseek(seek_diff, False, seek_percentage),
			'toggle_single': self.mpc.toggle('single'),
			'toggle_repeat': self.mpc.toggle('repeat'),
			'toggle_random': self.mpc.toggle('random'),
			'toggle_consume': self.mpc.toggle('consume'),
			'toggle_crossfade': self.mpc.toggle_crossfade,
			'switch_panel': self.toggle_panel,
			'exit': self.quit,
		}

		self.keymap = configuration.KeyMapper(self.actionmap, config.keymap.globals)
		self.librarypanel = LibraryPanel(mpc)
		self.nowplayingpanel = NowPlayingPanel(mpc)
		self.header = ui_status.MainHeader(mpc)
		self.footer = ui_status.MainFooter(mpc)

		super(MainFrame, self).__init__(self.librarypanel, header=self.header,
		                                footer=self.footer)

	def keypress(self, size, key):
		if key in self.keymap:
			return self.keymap(key)
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
			'delete': self.body.delete_current,
			'J': self.body.swap_down,
			'K': self.body.swap_up,
			'n': self.body.swap_down,
			'm': self.body.swap_up,
			'o': self.body.focus_playing,
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

		attr = 'library.vdivider'
		divstr = config.format.library.vdivider
		divlen = len(divstr.decode('utf-8'))
		div1 = urwid.AttrWrap(util.VDivider(divstr), attr, attr)
		div2 = urwid.AttrWrap(util.VDivider(divstr), attr, attr)

		wlist = artists, ('fixed', divlen, div1), albums, ('fixed', divlen, div2), tracks
		super(LibraryPanel, self).__init__(wlist)
