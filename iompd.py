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

