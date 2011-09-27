import datetime
import urwid
import signals

class timedelta(datetime.timedelta):
	"""Format times in a manner suitable for music.
	If time is over a day it will be indicated by %s day(s).
	Hours will be displayed only if necessary.
	Minutes will always be displayed, even with 0:ss.
	Seconds will always be displayed, even with 0:00."""
	def __str__(self):
		# Large libraries/artists could have days, better account for that.
		if self.days <= 0:
			days = ''
		elif self.days == 1:
			days = '1 day'
		else:
			days = '%s days ' % self.days

		seconds = int(self.seconds)
		minutes = seconds / 60 % 60
		hours = seconds / 60 / 60
		seconds %= 60

		output = []
		mpad = 1
		if hours > 0:
			output.append(str(hours))
			mpad = 2
		output.append(str(minutes).zfill(mpad))
		output.append(str(seconds).zfill(2))

		return days + ':'.join(output)


class VDivider(urwid.BoxWidget):
	def __init__(self, div_char=' ', top=0, bottom=0):
		super(VDivider, self).__init__()
		self._div_char = div_char
		self._top = top
		self._bottom = bottom
		self._selectable = False

	def render(self, size, focus=False):
		height = size[1]
		element = self._top * ' ' + self._div_char + self._bottom * ' '
		text = height * [element]

		return urwid.TextCanvas(text, maxcol=size[0])

	def keypress(self, size, key): return key

class WidgetMux(urwid.WidgetWrap):
	"""Holds several widgets in one place and allows switching between them.
	Similar to GNU screen or a tabbed interface but with no defined UI."""
	def __init__(self, widget_dict, default):
		"""widget_dict: Mapping type (ie dict) of {name: Widget} pairs.
		default: name of Widget to initially use.
		If the same widget is used with multiple keys, you will get ambiguous
		results from self.current(). Avoid this."""
		self.widget_dict = widget_dict
		super(WidgetMux, self).__init__(self.widget_dict[default])

	def switch(self, name):
		target = self.widget_dict[name]
		if self._w is not target:
			self._w = target
		else:
			signals.redraw()

	def current(self):
		"""Gets name of the widget currently being displayed."""
		name = [k for k, v in self.widget_dict.items() if v is self._w] + [None]
		return name[0]

