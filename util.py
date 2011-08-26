import datetime

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

