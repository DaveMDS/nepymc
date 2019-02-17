#!/usr/bin/env python
#
# usage:
#
# OK:
# python setup.py develop     (run from the build dir, without any install need)
# python setup.py clean       (always run clean --all)
# python setup.py build_i18n
# python setup.py update_po
# python setup.py check_po    (need polib)
# python setup.py test [-a ...]  (run the full test suite, need pytest)
#
# TODO:
# python setup.py install [--prefix=]
# python setup.py uninstall [--prefix=]
# python setup.py build_themes
# python setup.py sdist|bdist
# python setup.py --help
# python setup.py --help-commands
# python setup.py --help uninstall
#
# distutils reference:
#  http://docs.python.org/distutils/
#

import os
import sys
import fnmatch

from distutils.core import setup, Command
from distutils.command.clean import clean
from distutils.command.build import build
from distutils.log import warn, info, error
from distutils.file_util import copy_file
from distutils.dir_util import mkpath
from distutils.dep_util import newer

from nepymc import __version__ as emc_version


class build_i18n(Command):
    description = 'Compile all the po files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        linguas_file = os.path.join('data', 'locale', 'LINGUAS')
        for lang in open(linguas_file).read().split():
            po_file = os.path.join('data', 'locale', lang + '.po')
            mo_file = os.path.join('nepymc', 'locale', lang, 'LC_MESSAGES',
                                   'nepymc.mo')
            mkpath(os.path.dirname(mo_file), verbose=False)
            if newer(po_file, mo_file):
                info('compiling po file: %s -> %s' % (po_file, mo_file))
                cmd = 'msgfmt -o %s -c %s' % (mo_file, po_file)
                os.system(cmd)


class update_po(Command):
    description = 'Prepare all i18n files and update them as needed'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # build the string of all the source files to be translated
        sources = ''
        for dirpath, dirs, files in os.walk('nepymc'):
            for name in fnmatch.filter(files, '*.py'):
                sources += ' ' + os.path.join(dirpath, name)

        # create or update the reference pot file
        pot_file = os.path.join('data', 'locale', 'nepymc.pot')
        info('updating pot file: %s' % pot_file)
        cmd = 'xgettext --from-code=UTF-8 --force-po ' \
              '--output=%s %s' % (pot_file, sources)
        os.system(cmd)

        # create or update all the .po files
        linguas_file = os.path.join('data', 'locale', 'LINGUAS')
        for lang in open(linguas_file).read().split():
            po_file = os.path.join('data', 'locale', lang + '.po')
            if os.path.exists(po_file):
                # update an existing po file
                info('updating po file: %s' % po_file)
                cmd = 'msgmerge -N -U -q %s %s' % (po_file, pot_file)
                os.system(cmd)
            else:
                # create a new po file
                info('creating po file: %s' % po_file)
                mkpath(os.path.dirname(po_file), verbose=False)
                copy_file(pot_file, po_file, verbose=False)


class check_po(Command):
    description = 'Give statistics about translations status'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import polib
        except ImportError:
            error('You need python polib installed')
            return

        # print totals
        po = polib.pofile(os.path.join('data', 'locale', 'nepymc.pot'))
        info('Total strings in nepymc.pot: %d' % len(po.untranslated_entries()))

        # print per-lang statistics
        linguas_file = os.path.join('data', 'locale', 'LINGUAS')
        for lang in sorted(open(linguas_file).read().split()):
            po = polib.pofile(os.path.join('data', 'locale', lang + '.po'))
            bar = '=' * (int(po.percent_translated() / 100 * 30))
            info('%s [%-30s] %3d%% (%d translated, %d fuzzy, '
                 '%d untranslated, %d obsolete)' % (
                    lang, bar, po.percent_translated(),
                    len(po.translated_entries()),
                    len(po.fuzzy_entries()),
                    len(po.untranslated_entries()),
                    len(po.obsolete_entries())))


# noinspection PyAttributeOutsideInit
class CustomCleanCommand(clean):
    description = 'remove ALL build output'

    def finalize_options(self):
        super().finalize_options()
        self.all = True


class CustomBuildCommand(build):
    def run(self):
        # self.run_command("build_themes")
        self.run_command("build_i18n")
        build.run(self)


# noinspection PyAttributeOutsideInit
class DevelopCommand(Command):
    description = 'run in-place from build dir without any install need'
    user_options = [('from-build', 'b',
                     'Run from the build directory'),
                    ('args=', 'a',
                     'Additional arguments for the emc executable')]

    def initialize_options(self):
        self.args = ''
        self.from_build = False

    def finalize_options(self):
        pass

    @staticmethod
    def env_prepend(name, value):
        if name in os.environ:
            os.environ[name] = value + os.pathsep + os.environ[name]
        else:
            os.environ[name] = value

    def run(self):
        self.run_command("clean")

        if self.from_build:
            self.run_command("build")
            bins_path = './build/scripts-{0}.{1}/'.format(*sys.version_info)
            modules_path = os.path.abspath('./build/lib/')

            # modules must be searched in build/lib/
            self.env_prepend('PYTHONPATH', modules_path)
            sys.path.insert(0, modules_path)
        else:
            bins_path = './bin/'

        # PATH for the binaries to be searched in correct place
        self.env_prepend('PATH', os.path.abspath(bins_path))

        # XDG config home in develop/config/
        os.environ['XDG_CONFIG_HOME'] = os.path.abspath('./develop/config/')
        # XDG cache home in develop/cache/
        os.environ['XDG_CACHE_HOME'] = os.path.abspath('./develop/cache/')

        # run emc !
        # os.system('nepymc %s' % self.args)
        del sys.modules['nepymc']
        from nepymc.main import start_emc
        sys.argv = sys.argv[:1]  # TODO FIXME !!
        sys.exit(start_emc())


# noinspection PyAttributeOutsideInit
class TestCommand(Command):
    description = 'Run all the available unit tests'
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        self.pytest_args = ""

    def finalize_options(self):
        pass

    def run(self):
        import shlex
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


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
        'PySide2 (>= 5.12.0)',
        'pyxdg',
        # 'beautifulsoup4',
        'lxml',
        # 'mutagen',
        # 'dbus',
        'pyudev',
        # 'libdiscid',
        'pytest',  # for tests only
    ],

    provides=['emc'],

    packages=[
        'nepymc',
        # 'nepymc.extapi',
        'nepymc.plugins.input_keyb',
        # 'nepymc.plugins.input_lirc',
        # 'nepymc.plugins.input_joy',
        # 'nepymc.plugins.input_webserver',
        # 'nepymc.plugins.input_mpris2',
        # 'nepymc.plugins.screensaver',
        # 'nepymc.plugins.movies',
        # 'nepymc.plugins.tvshows',
        # 'nepymc.plugins.onlinevideo',
        # 'nepymc.plugins.mame',
        # 'nepymc.plugins.music',
        'nepymc.plugins.uitests',
        'nepymc.plugins.calibrator',
        # 'nepymc.plugins.filemanager',
        # 'nepymc.plugins.photos',
        # 'nepymc.plugins.watchdog',
        # 'nepymc.plugins.opticals',
        # 'nepymc.plugins.mp_omxplayer',
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
        'build': CustomBuildCommand,
        'clean': CustomCleanCommand,
        'develop': DevelopCommand,
        'test': TestCommand,
        'build_i18n': build_i18n,
        'update_po': update_po,
        'check_po': check_po,
    },
)
