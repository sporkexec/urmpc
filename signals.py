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

# Provide access to alarms globally.
def alarm_at(unixtime, callback, user_data=None):
	return _mainloop.set_alarm_at(unixtime, callback, user_data)

def alarm_in(interval, callback, user_data=None):
	return _mainloop.set_alarm_in(interval, callback, user_data)

def alarm_remove(handle):
	return _mainloop.remove_alarm(handle)

def redraw():
	return _mainloop.draw_screen()

