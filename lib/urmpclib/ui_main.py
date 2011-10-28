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
			'playpause': lambda _: self.mpc.playpause(),
			'next_track': lambda _: self.mpc.next(),
			'previous_track': lambda _: self.mpc.previous(),
			'stop': lambda _: self.mpc.stop(),
			'clear_playlist': lambda _: self.mpc.clear(),
			'shuffle': lambda _: self.mpc.shuffle(),
			'update_database': lambda _: self.mpc.update(),
			'volume_down': lambda _: self.mpc.volume_down(),
			'volume_up': lambda _: self.mpc.volume_up(),
			'seek_back': lambda _: self.mpc.urseek(seek_diff * -1, False, seek_percentage),
			'seek_forth': lambda _: self.mpc.urseek(seek_diff, False, seek_percentage),
			'toggle_single': lambda _: self.mpc.toggle('single')(),
			'toggle_repeat': lambda _: self.mpc.toggle('repeat')(),
			'toggle_random': lambda _: self.mpc.toggle('random')(),
			'toggle_consume': lambda _: self.mpc.toggle('consume')(),
			'toggle_crossfade': lambda _: self.mpc.toggle_crossfade(),
			'library_panel': lambda _: self.get_body().switch('library'),
			'playlist_panel': lambda _: self.get_body().switch('playlist'),
			'help_panel': lambda _: self.get_body().switch('help'),
			'toggle_panels': lambda _: self.toggle_panel(),
			'exit': lambda _: self.quit(),
		}

		self.keymap = configuration.KeyMapper(self.actionmap, config.keymap.globals)

		self.librarypanel = LibraryPanel(mpc)
		self.nowplayingpanel = NowPlayingPanel(mpc)
		self.helppanel = HelpPanel()
		self.panel_dict = {
			'library': self.librarypanel,
			'playlist': self.nowplayingpanel,
			'help': self.helppanel,
		}

		body = util.WidgetMux(self.panel_dict, 'library')
		header = ui_status.MainHeader(mpc)
		footer = ui_status.MainFooter(mpc)

		super(MainFrame, self).__init__(body, header=header, footer=footer)

	def keypress(self, size, key):
		key = super(MainFrame, self).keypress(size, key)
		if key is not None:
			key = self.keymap(size, key)
		return key

	def toggle_panel(self):
		current = self.get_body().current()
		panels = config.format.toggle_panels_order
		try:
			index = (panels.index(current) + 1) % len(panels)
		except ValueError as e:
			index = 0
		self.get_body().switch(panels[index])

	def quit(self):
		raise urwid.ExitMainLoop()

class NowPlayingPanel(ui_lists.TreeList):
	def __init__(self, mpc):
		super(NowPlayingPanel, self).__init__(ui_lists.NowPlayingWalker(mpc))
		actionmap = {
			'play': lambda _: self.body.play_current(),
			'delete': lambda _: self.body.delete_current(),
			'swap_below': lambda _: self.body.swap_down(),
			'swap_above': lambda _: self.body.swap_up(),
			'focus_current': lambda _: self.body.focus_playing(),
		}
		self.keymap.update(actionmap, config.keymap.now_playing)

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

class HelpPanel(urwid.Frame):
	def __init__(self):
		header = urwid.Text([('help.header', 'Current keybindings'),
		         '\nPlease consult the documentation for further information.'])
		self.list = ui_lists.TreeList(ui_lists.HelpPanelWalker())
		super(HelpPanel, self).__init__(self.list, header=header)

