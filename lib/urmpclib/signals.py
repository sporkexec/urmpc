"""Provides a few utility function using urwid's signals.

urwid requires emitters to register by class and listeners to specify the
emitter and all kinds of overengineered bullshit. Sometimes we just want to
send a signal from whereever and and have anybody listening receive it. When
that is what you need, use this."""

import urwid
import urwid.signals

class _sender_cls(object): pass
_sender = _sender_cls()
_dict = urwid.signals._signals._supported
_mainloop = None

def _register(obj, signal):
	"""Sidesteps urwid's stupid registration."""
	cls = obj.__class__
	if cls not in _dict:
		_dict[cls] = (signal,)
	elif signal not in _dict[cls]:
		_dict[cls] += (signal,)

def emit(signal, *args):
	_register(_sender, signal)
	return urwid.signals._signals.emit(_sender, signal, *args)

def listen(signal, callback, user_arg=None):
	_register(_sender, signal)
	urwid.connect_signal(_sender, signal, callback, user_arg)

def sends_signal(*signals):
	def classmaker(cls):
		urwid.register_signal(cls, signals)
		return cls
	return classmaker

# Provide access to alarms globally.
def alarm_at(unixtime, callback, user_data=None):
	try:
		return _mainloop.set_alarm_at(unixtime, callback, user_data)
	except AttributeError as e:
		pass # Not fully initialized, no big deal. Might want it on debug log.

def alarm_in(interval, callback, user_data=None):
	try:
		return _mainloop.set_alarm_in(interval, callback, user_data)
	except AttributeError as e:
		pass # Not fully initialized, no big deal. Might want it on debug log.

def alarm_remove(handle):
	try:
		return _mainloop.remove_alarm(handle)
	except AttributeError as e:
		pass # Not fully initialized, no big deal. Might want it on debug log.

def redraw():
	try:
		return _mainloop.draw_screen()
	except AttributeError as e:
		pass # Not fully initialized, no big deal. Might want it on debug log.

