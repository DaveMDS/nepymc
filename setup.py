#!/usr/bin/env python
#
# usage:
#
# OK:
# python setup.py develop  (run in place)
# python setup.py clean --all
#
# TODO:
# python setup.py install [--prefix=]
# python setup.py uninstall [--prefix=]
# python setup.py build_themes
# python setup.py build_i18n
# python setup.py update_po
# python setup.py check_po
# python setup.py sdist|bdist
# python setup.py --help
# python setup.py --help-commands
# python setup.py --help uninstall
#
# distutils reference:
#  http://docs.python.org/distutils/
#
# setuptools reference:
#  https://packaging.python.org/
#  https://setuptools.readthedocs.io/en/latest/
#  https://jichu4n.com/posts/how-to-add-custom-build-steps-and-commands-to-setuppy/
#

import sys
import os
from distutils.core import setup, Command

from nepymc import __version__ as emc_version


# noinspection PyAttributeOutsideInit
class DevelopCommand(Command):
    description = 'Run in-place from build dir without any install need'
    user_options = [('args=', 'a',
                     'Additional arguments for the emc executable')]

    def initialize_options(self):
        self.args = ''

    def finalize_options(self):
        pass

    @staticmethod
    def env_prepend(name, value):
        if name in os.environ:
            os.environ[name] = value + os.pathsep + os.environ[name]
        else:
            os.environ[name] = value

    def run(self):
        self.run_command("build")
        # PATH for the binaries to be searched in build/scripts-X.Y/
        self.env_prepend('PATH',
                         './build/scripts-{0}.{1}/'.format(*sys.version_info))
        # PYTHONPATH for the emc modules be searched in build/lib/
        self.env_prepend('PYTHONPATH', './build/lib/')
        # XDG config home in develop/config/
        os.environ['XDG_CONFIG_HOME'] = os.path.abspath('./develop/config/')
        # XDG cache home in develop/cache/
        os.environ['XDG_CACHE_HOME'] = os.path.abspath('./develop/cache/')
        # run emc !
        # os.system('nepymc %s' % self.args)
        from nepymc.main import start_emc
        sys.exit(start_emc())

setup(
    name="nepymc",
    version=emc_version,
    author='Davide <davemds> Andreoli',
    author_email='dave@gurumeditation.it',
    description='NepyMC is a free Media Center Platform written in Python',
    url='http://github.com/DaveMDS/emc',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 6 - Mature',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Natural Language :: German',
        'Natural Language :: Russian',
        'Natural Language :: Finnish',
    ],

    requires=[
        'PySide2 (>= 5.11.2)',
        'pyxdg',
        # 'beautifulsoup4',
        'lxml',
        # 'mutagen',
        # 'dbus',
        # 'pyudev',
        # 'libdiscid',
    ],

    provides=['emc'],

    packages=[
        'nepymc',
        # 'epymc.extapi',
        # 'epymc.plugins.input_keyb',
        # 'epymc.plugins.input_lirc',
        # 'epymc.plugins.input_joy',
        # 'epymc.plugins.input_webserver',
        # 'epymc.plugins.input_mpris2',
        # 'epymc.plugins.screensaver',
        # 'epymc.plugins.movies',
        # 'epymc.plugins.tvshows',
        # 'epymc.plugins.onlinevideo',
        # 'epymc.plugins.mame',
        # 'epymc.plugins.music',
        # 'epymc.plugins.uitests',
        # 'epymc.plugins.calibrator',
        # 'epymc.plugins.filemanager',
        # 'epymc.plugins.photos',
        # 'epymc.plugins.watchdog',
        # 'epymc.plugins.opticals',
        # 'epymc.plugins.mp_omxplayer',
    ],

    package_data={
        'nepymc': ['themes/*/*', 'themes/*/*/*', 'locale/*/LC_MESSAGES/*.mo'],
        # 'epymc.plugins.movies': ['*.png'],
        # 'epymc.plugins.tvshows': ['*.png'],
        # 'epymc.plugins.mame': ['*.png', '*.jpg'],
        # 'epymc.plugins.music': ['*.png'],
        # 'epymc.plugins.uitests': ['*.png', '*.jpg'],
        # 'epymc.plugins.calibrator': ['*.jpg', '*.png'],
        # 'epymc.plugins.onlinevideo': [ '*.png',
        # 'themoviedb/*',
        # 'youtube/*',
        # 'vimeo/*',
        # 'zapiks/*',
        # 'fantasticc/*',
        # 'porncom/*',
        # 'pornhub/*',
        # 'southparkstudios/*',
        # ],
        # 'epymc.plugins.input_webserver': [
        # 'default/*',
        # 'mobile/*',
        # ]
    },

    scripts=[
        'bin/nepymc',
        # 'bin/epymc_standalone',
        # 'bin/epymc_thumbnailer',
        # 'epymc/plugins/watchdog/epymc_watchdog',
    ],

    cmdclass={
        'develop': DevelopCommand,
    },
)
