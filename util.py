import datetime
import urwid

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
