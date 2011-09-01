from ConfigParser import SafeConfigParser as ConfigParser

class ConfigSection(dict):
	"""Holds a section of ConfigParser options.

	Attribute and dictionary syntaxes are supported.
	Supports subsections, i.e. subsection.option keys within main sections.
	Subsections can go to arbitrary depth.
	Returns new ConfigSecion holding subsection when detected."""

	#TODO: Add sections(), has_section(key) methods to manage subsections.
	#      Same/similar interface as ConfigParser is ideal.
	def __getitem__(self, key):
		if key in self:
			return super(ConfigSection, self).__getitem__(key)

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

class Config(ConfigParser):
	"""ConfigParser that lets you access sections or top-level options.

	Attribute and dictionary syntaxes are supported.
	If a section is found, returns a ConfigSection holding contents."""
	def __getattr__(self, key):
		if self.has_section(key):
			return ConfigSection(self.items(key))
		else:
			section = ConfigSection(self.items('DEFAULT'))
			return section.__getattr__(key)

	def __getitem__(self, key):
		try:
			return self.__getattr__(key)
		except AttributeError as e:
			raise KeyError(e.message)

config = None
def readfile(filename):
	global config
	config = Config()
	config.read(filename)

