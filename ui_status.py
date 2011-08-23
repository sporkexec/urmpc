import urwid

import signals

class MainFooter(object):
	mpc = None
	_notification = None, None
	_notification_alarm = None

	#FIXME: DRY?
	# Valid widgets we can be rendering
	_components = '_progress_bar', '_notification_bar'
	_progress_bar, _notification_bar = None, None
	_current = None

	def __init__(self, mpc):
		super(MainFooter, self).__init__()
		self.mpc = mpc
		self._notification_bar = urwid.Text('')
		self._progress_bar = urwid.ProgressBar(None, None)
		signals.listen('user_notification', self.notify)
		signals.listen('idle_update', self._notify_update)
		self._change_current()

	def _change_current(self, name=None):
		if name in self._components:
			self._current = getattr(self, name)
		elif name is None:
			# Any logic to automatically determine current goes here.
			self._current = self._progress_bar

	def _get_current(self):
		return self._current

	def __getattr__(self, attr):
		"""Masquerade as our current widget."""
		return getattr(self._get_current(), attr)

	def notify(self, message, interval=1.0): #TODO: Config interval default.
		"""Adds a notification to be displayed in the status bar.
		In addition to the mandatory message to be displayed, you may supply a
		desired duration in the interval parameter. This is a maximum duration,
		as any subsequent notification immediately overrides the current one."""
		#TODO?: Add 'level' param: ('info', 'warn', 'error', 'crit', etc.)
		#      and highlight accordingly, maybe let higher levels get priority.
		if self._notification_alarm:
			signals.alarm_remove(self._notification_alarm)
			self._notification_alarm = None
		self._change_current('_notification_bar')
		self._notification = None, None
		self.set_text(str(message))
		self._notification_alarm = signals.alarm_in(interval, self._clear_notification)
		signals.redraw()

	def _clear_notification(self, *_):
		self._notification = (None, None)
		self._notification_alarm = None
		self._change_current(None)
		signals.redraw()
		return False

	def _notify_update(self):
		if 'updating_db' not in self.mpc.status():
			signals.emit('user_notification', 'Database update finished!')
		# else: update ongoing, ignore

