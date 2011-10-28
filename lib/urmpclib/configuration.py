import json
from ConfigParser import SafeConfigParser as ConfigParser

def truthiness(value):
	# I'll probably end up regretting this.
	return value.strip().lower() in ('y', 'yes', 't', 'true', '1',)

def extract_palette(config, section):
	section = config[section]
	data = {} # {attribute: {'fg': fg, 'bg': bg}} mapping
	for k, v in section.items():
		if k.endswith('.fg'):
			key = k[:-3]
			subkey = 'fg'
		elif k.endswith('.bg'):
			key = k[:-3]
			subkey = 'bg'
		else:
			continue
		if key not in data:
			data[key] = {}
		data[key][subkey] = v

	palette = []
	for attribute, v in data.items():
		fg = v.get('fg', None)
		bg = v.get('bg', None)
		palette.append((attribute, fg, bg))
	return palette

class KeyMapper(object):
	"""Handles keypress configuration."""
	def __init__(self, actionmap, keymap):
		"""actionmap: {action: callable} where action is a user-visible string.
		keymap: {action: [keylist]}"""
		self._actionmap = {}
		self._keymap = {}
		self.update(actionmap, keymap)

	def update(self, actionmap, keymap):
		self._actionmap.update([(k, v) for (k, v) in actionmap.items()])
		for action, keys in keymap.items():
			if type(keys) in (str, unicode):
				self._keymap[keys] = action
			else:
				for key in keys:
					self._keymap[key] = action

	def __contains__(self, key):
		"""Whether key is set and actually does something."""
		return key in self._keymap and self._keymap[key] in self._actionmap

	def __call__(self, size, key):
		if key in self:
			return self._actionmap[self._keymap[key]](size)
		return key

class ConfigSection(dict):
	"""Holds a section of ConfigParser options.

	Attribute and dictionary syntaxes are supported.
	Supports subsections, i.e. subsection.option keys within main sections.
	Subsections can go to arbitrary depth.
	Returns new ConfigSecion holding subsection when detected."""

	def __getitem__(self, key):
		if key in self:
			ret = super(ConfigSection, self).__getitem__(key)
			try:
				ret = json.loads(ret)
			except ValueError as e:
				pass
			try:
				return ret.encode('utf-8')
			except AttributeError as e:
				return ret

		subsections = []
		for k, v in self.items():
			if k.startswith(str(key)+'.'):
				# Everything after 'key.', v
				subsections.append((k[(len(str(key))+1):], v))
		if subsections != []:
			return self.__class__(subsections)

		raise KeyError(key)

	def __getattr__(self, key):
		try:
			return self.__getitem__(key)
		except KeyError as e:
			raise AttributeError(e.message)

	def sections(self):
		"""Returns all subsection keys, i.e. values before '.' in keys."""
		return tuple(set((k[:k.index('.')] for k in self.keys() if '.' in k)))

	def has_section(self, key):
		return key == 'DEFAULT' or key in self.sections()

class Config(ConfigParser):
	"""ConfigParser that lets you access sections or top-level options.

	Attribute and dictionary syntaxes are supported.
	If a section is found, returns a ConfigSection holding contents."""
	def __getattr__(self, key):
		if self.has_section(key):
			return ConfigSection(self.items(key))
		else:
			section = ConfigSection(self.items('DEFAULT'))
			ret = section.__getattr__(key)
			try:
				ret = json.loads(ret)
			except ValueError as e:
				pass
			try:
				return ret.encode('utf-8')
			except AttributeError as e:
				return ret

	def __getitem__(self, key):
		try:
			return self.__getattr__(key)
		except AttributeError as e:
			raise KeyError(e.message)

config = Config() # Side-effects from importing are bad, be sure __init__ is ok
