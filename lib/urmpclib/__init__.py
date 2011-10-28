if __name__ == '__main__':
	import os.path, os, sys
	sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

	import urwid
	import urmpd
	import signals
	from ui_main import MainFrame
	import configuration
	from configuration import config

	config_file = os.path.expanduser('~')
	if config_file != '~':
		config_file = os.path.join(config_file, '.urmpc.conf')
		if not os.path.isfile(config_file):
			config_file = os.path.join(os.environ.get('HOME', ''), '.urmpc.conf')
			if not os.path.isfile(config_file):
				config_file = os.path.join('urmpclib', 'urmpc.conf.example')
				if not os.path.isfile(config_file):
					raise IOError('Configuration file not found.')

	config.read(config_file)
	palette = configuration.extract_palette(config, 'palette')
	mpc = urmpd.MPDClient()
	mpc.connect(config.mpd.host, int(config.mpd.port))
	event_loop = urwid.SelectEventLoop()

	# Get urwid set up
	#FIXME: Passing None in here is ugly and will eventually break if urwid decides
	#       to be more strict about it.
	loop = urwid.MainLoop(None, palette, event_loop=event_loop)
	signals._mainloop = loop

	# Main widget uses mpd
	frame = MainFrame(mpc)
	loop.widget = frame

	# Idler runs cloned mpc connection, uses MainLoop to force redraw on MPD events
	idler = urmpd.Idler(mpc, loop)
	event_loop.watch_file(idler, idler)

	try:
		loop.run()
	except KeyboardInterrupt as e:
		pass

