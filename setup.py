#!/usr/bin/env python2

from distutils.core import setup

setup(name='urmpc',
	version='0.1.0',
	description='MPD client using urwid',
	author='Jacob Courtneay',
	author_email='jacob@sporkexec.com',
	url='http://github.com/sporkexec/urmpc',
	packages=['urmpclib'],
	package_dir={'': 'lib'},
	scripts=['bin/urmpc'],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console :: Curses',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Topic :: Multimedia :: Sound/Audio :: Players',
		'Operating System :: POSIX :: Linux', #TODO: More testing, BSD & beyond.
	],
)
