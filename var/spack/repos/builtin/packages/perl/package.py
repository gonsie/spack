# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

#
# Author: Milton Woods <milton.woods@bom.gov.au>
# Date: March 22, 2017
# Author: George Hartzell <hartzell@alerce.com>
# Date: July 21, 2016
# Author: Justin Too <justin@doubleotoo.com>
# Date: September 6, 2015
#

import os
import platform
import re
import sys
from contextlib import contextmanager

from llnl.util.lang import match_predicate
from llnl.util.symlink import symlink

from spack import *
from spack.operating_systems.mac_os import macos_version

is_windows = sys.platform == 'win32'


class Perl(Package):  # Perl doesn't use Autotools, it should subclass Package
    """Perl 5 is a highly capable, feature-rich programming language with over
       27 years of development."""

    homepage = "https://www.perl.org"
    # URL must remain http:// so Spack can bootstrap curl
    url = "http://www.cpan.org/src/5.0/perl-5.34.0.tar.gz"

    executables = [r'^perl(-?\d+.*)?$']

    # see https://www.cpan.org/src/README.html for
    # explanation of version numbering scheme

    # Development releases (odd numbers)
    version('5.35.0', sha256='d6c0eb4763d1c73c1d18730664d43fcaf6100c31573c3b81e1504ec8f5b22708')
    version('5.33.3', sha256='4f4ba0aceb932e6cf7c05674d05e51ef759d1c97f0685dee65a8f3d190f737cd')
    version('5.31.7', sha256='d05c4e72128f95ef6ffad42728ecbbd0d9437290bf0f88268b51af011f26b57d')
    version('5.31.4', sha256='418a7e6fe6485cc713a86d1227ef112f0bb3f80322e3b715ffe42851d97804a5')

    # Maintenance releases (even numbers, recommended)
    version('5.34.1', sha256='357951a491b0ba1ce3611263922feec78ccd581dddc24a446b033e25acf242a1', preferred=True)
    version('5.34.0', sha256='551efc818b968b05216024fb0b727ef2ad4c100f8cb6b43fab615fa78ae5be9a', preferred=True)
    version('5.32.1', sha256='03b693901cd8ae807231b1787798cf1f2e0b8a56218d07b7da44f784a7caeb2c', preferred=True)
    version('5.32.0', sha256='efeb1ce1f10824190ad1cadbcccf6fdb8a5d37007d0100d2d9ae5f2b5900c0b4', preferred=True)
    version('5.30.3', sha256='32e04c8bb7b1aecb2742a7f7ac0eabac100f38247352a73ad7fa104e39e7406f', preferred=True)
    version('5.30.2', sha256='66db7df8a91979eb576fac91743644da878244cf8ee152f02cd6f5cd7a731689', preferred=True)
    version('5.30.1', sha256='bf3d25571ff1ee94186177c2cdef87867fd6a14aa5a84f0b1fb7bf798f42f964', preferred=True)
    version('5.30.0', sha256='851213c754d98ccff042caa40ba7a796b2cee88c5325f121be5cbb61bbf975f2', preferred=True)

    # End of life releases
    version('5.28.0', sha256='7e929f64d4cb0e9d1159d4a59fc89394e27fa1f7004d0836ca0d514685406ea8')
    version('5.26.2', sha256='572f9cea625d6062f8a63b5cee9d3ee840800a001d2bb201a41b9a177ab7f70d')
    version('5.24.1', sha256='e6c185c9b09bdb3f1b13f678999050c639859a7ef39c8cad418448075f5918af')
    version('5.22.4', sha256='ba9ef57c2b709f2dad9c5f6acf3111d9dfac309c484801e0152edbca89ed61fa')
    version('5.22.3', sha256='1b351fb4df7e62ec3c8b2a9f516103595b2601291f659fef1bbe3917e8410083')
    version('5.22.2', sha256='81ad196385aa168cb8bd785031850e808c583ed18a7901d33e02d4f70ada83c2')
    version('5.22.1', sha256='2b475d0849d54c4250e9cba4241b7b7291cffb45dfd083b677ca7b5d38118f27')
    version('5.22.0', sha256='0c690807f5426bbd1db038e833a917ff00b988bf03cbf2447fa9ffdb34a2ab3c')
    version('5.20.3', sha256='3524e3a76b71650ab2f794fd68e45c366ec375786d2ad2dca767da424bbb9b4a')
    version('5.18.4', sha256='01a4e11a9a34616396c4a77b3cef51f76a297e1a2c2c490ae6138bf0351eb29f')
    version('5.16.3', sha256='69cf08dca0565cec2c5c6c2f24b87f986220462556376275e5431cc2204dedb6')

    extendable = True

    if not is_windows:
        # Bind us below gdbm-1.20 due to API change: https://github.com/Perl/perl5/issues/18915
        depends_on('gdbm@:1.19')
        # :5.28 needs gdbm@:1:14.1: https://rt-archive.perl.org/perl5/Ticket/Display.html?id=133295
        depends_on('gdbm@:1.14.1', when='@:5.28.0')
        depends_on('berkeley-db')
        depends_on('bzip2')
        depends_on('zlib')
        # :5.24.1 needs zlib@:1.2.8: https://rt.cpan.org/Public/Bug/Display.html?id=120134
        depends_on('zlib@:1.2.8', when='@5.20.3:5.24.1')

    conflicts('@5.34.1:', when='%msvc@:19.29.30136')
    # there has been a long fixed issue with 5.22.0 with regard to the ccflags
    # definition.  It is well documented here:
    # https://rt.perl.org/Public/Bug/Display.html?id=126468
    patch('protect-quotes-in-ccflags.patch', when='@5.22.0')

    # Fix the Time-Local testase http://blogs.perl.org/users/tom_wyant/2020/01/my-y2020-bug.html
    patch('https://rt.cpan.org/Public/Ticket/Attachment/1776857/956088/0001-Fix-Time-Local-tests.patch',
          when='@5.26.0:5.28.9',
          sha256='8cf4302ca8b480c60ccdcaa29ec53d9d50a71d4baf469ac8c6fca00ca31e58a2')
    patch('https://raw.githubusercontent.com/costabel/fink-distributions/master/10.9-libcxx/stable/main/finkinfo/languages/perl5162-timelocal-y2020.patch',
          when='@:5.24.1',
          sha256='3bbd7d6f9933d80b9571533867b444c6f8f5a1ba0575bfba1fba4db9d885a71a')

    # Fix build on Fedora 28
    # https://bugzilla.redhat.com/show_bug.cgi?id=1536752
    patch('https://src.fedoraproject.org/rpms/perl/raw/004cea3a67df42e92ffdf4e9ac36d47a3c6a05a4/f/perl-5.26.1-guard_old_libcrypt_fix.patch', level=1, sha256='0eac10ed90aeb0459ad8851f88081d439a4e41978e586ec743069e8b059370ac', when='@:5.26.2')

    # Fix 'Unexpected product version' error on macOS 11.0 Big Sur
    # https://github.com/Perl/perl5/pull/17946
    patch('macos-11-version-check.patch', when='@5.24.1:5.32.0 platform=darwin')

    # Enable builds with the NVIDIA compiler
    # The Configure script assumes some gcc specific behavior, and use
    # the mini Perl environment to bootstrap installation.
    patch('nvhpc-5.30.patch', when='@5.30.0:5.30 %nvhpc')
    patch('nvhpc-5.32.patch', when='@5.32.0:5.32 %nvhpc')
    conflicts('@5.34.0:', when='%nvhpc')  # todo, add patches...
    conflicts('@5.32.0:', when='%nvhpc@:20.11',
              msg='The NVIDIA compilers are incompatible with version 5.32 and later')

    # Make sure we don't get "recompile with -fPIC" linker errors when using static libs
    conflicts('^zlib~shared~pic', msg='Needs position independent code when using static zlib')
    conflicts('^bzip2~shared~pic', msg='Needs position independent code when using static bzip2')

    # Installing cpanm alongside the core makes it safe and simple for
    # people/projects to install their own sets of perl modules.  Not
    # having it in core increases the "energy of activation" for doing
    # things cleanly.
    variant('cpanm', default=True,
            description='Optionally install cpanm with the core packages.')

    variant('shared', default=True,
            description='Build a shared libperl.so library')

    variant('threads', default=True,
            description='Build perl with threads support')

    resource(
        name="cpanm",
        url="http://search.cpan.org/CPAN/authors/id/M/MI/MIYAGAWA/App-cpanminus-1.7042.tar.gz",
        sha256="9da50e155df72bce55cb69f51f1dbb4b62d23740fb99f6178bb27f22ebdf8a46",
        destination="cpanm",
        placement="cpanm"
    )

    phases = ['configure', 'build', 'install']

    def patch(self):
        # https://github.com/Perl/perl5/issues/15544 long PATH(>1000 chars) fails a test
        os.chmod('lib/perlbug.t', 0o644)
        filter_file('!/$B/', '! (/(?:$B|PATH)/)', 'lib/perlbug.t')

    @classmethod
    def determine_version(cls, exe):
        perl = spack.util.executable.Executable(exe)
        output = perl('--version', output=str, error=str)
        if output:
            match = re.search(r'perl.*\(v([0-9.]+)\)', output)
            if match:
                return match.group(1)
        return None

    @classmethod
    def determine_variants(cls, exes, version):
        for exe in exes:
            perl = spack.util.executable.Executable(exe)
            output = perl('-V', output=str, error=str)
            variants = ''
            if output:
                match = re.search(r'-Duseshrplib', output)
                if match:
                    variants += '+shared'
                else:
                    variants += '~shared'
                match = re.search(r'-Duse.?threads', output)
                if match:
                    variants += '+threads'
                else:
                    variants += '~threads'
            path = os.path.dirname(exe)
            if 'cpanm' in os.listdir(path):
                variants += '+cpanm'
            else:
                variants += '~cpanm'
            return variants

    # On a lustre filesystem, patch may fail when files
    # aren't writeable so make pp.c user writeable
    # before patching. This should probably walk the
    # source and make everything writeable in the future.
    def do_stage(self, mirror_only=False):
        # Do Spack's regular stage
        super(Perl, self).do_stage(mirror_only)
        # Add write permissions on file to be patched
        filename = join_path(self.stage.source_path, 'pp.c')
        perm = os.stat(filename).st_mode
        os.chmod(filename, perm | 0o200)

    @property
    def nmake_arguments(self):
        args = []
        if self.spec.satisfies('%msvc'):
            args.append('CCTYPE=%s' % self.compiler.msvc_version)
        else:
            raise RuntimeError("Perl unsupported for non MSVC compilers on Windows")
        args.append('INST_TOP=%s' % self.prefix.replace('/', '\\'))
        args.append("INST_ARCH=\\$(ARCHNAME)")
        if self.spec.satisfies('~shared'):
            args.append("ALL_STATIC=%s" % "define")
        if self.spec.satisfies('~threads'):
            args.extend(["USE_MULTI=undef", "USE_ITHREADS=undef", "USE_IMP_SYS=undef"])
        if not self.is_64bit():
            args.append("WIN64=undef")
        return args

    def is_64bit(self):
        return platform.machine().endswith('64')

    def configure_args(self):
        spec = self.spec
        prefix = self.prefix

        config_args = [
            '-des',
            '-Dprefix={0}'.format(prefix),
            '-Dlocincpth=' + self.spec['gdbm'].prefix.include,
            '-Dloclibpth=' + self.spec['gdbm'].prefix.lib,
        ]

        # Extensions are installed into their private tree via
        # `INSTALL_BASE`/`--install_base` (see [1]) which results in a
        # "predictable" installation tree that sadly does not match the
        # Perl core's @INC structure.  This means that when activation
        # merges the extension into the extendee[2], the directory tree
        # containing the extensions is not on @INC and the extensions can
        # not be found.
        #
        # This bit prepends @INC with the directory that is used when
        # extensions are activated [3].
        #
        # [1] https://metacpan.org/pod/ExtUtils::MakeMaker#INSTALL_BASE
        # [2] via the activate method in the PackageBase class
        # [3] https://metacpan.org/pod/distribution/perl/INSTALL#APPLLIB_EXP
        config_args.append('-Accflags=-DAPPLLIB_EXP=\\"' +
                           self.prefix.lib.perl5 + '\\"')

        # Discussion of -fPIC for Intel at:
        # https://github.com/spack/spack/pull/3081 and
        # https://github.com/spack/spack/pull/4416
        if spec.satisfies('%intel'):
            config_args.append('-Accflags={0}'.format(
                self.compiler.cc_pic_flag))

        if '+shared' in spec:
            config_args.append('-Duseshrplib')

        if '+threads' in spec:
            config_args.append('-Dusethreads')

        # Development versions have an odd second component
        if spec.version[1] % 2 == 1:
            config_args.append('-Dusedevel')

        return config_args

    def configure(self, spec, prefix):
        if is_windows:
            return
        configure = Executable('./Configure')
        configure(*self.configure_args())

    def build(self, spec, prefix):
        if is_windows:
            pass
        else:
            make()

    @run_after('build')
    @on_package_attributes(run_tests=True)
    def build_test(self):
        if is_windows:
            win32_dir = os.path.join(self.stage.source_path, "win32")
            with working_dir(win32_dir):
                nmake('test', ignore_quotes=True)
        else:
            make('test')

    def install(self, spec, prefix):
        if is_windows:
            win32_dir = os.path.join(self.stage.source_path, "win32")
            with working_dir(win32_dir):
                nmake('install', *self.nmake_arguments,  ignore_quotes=True)
        else:
            make('install')

    @run_after('install')
    def symlink_windows(self):
        if not is_windows:
            return
        win_install_path = os.path.join(self.prefix.bin, "MSWin32")
        if self.is_64bit():
            win_install_path += "-x64"
        else:
            win_install_path += "-x86"
        if self.spec.satisfies("+threads"):
            win_install_path += "-multi-thread"
        else:
            win_install_path += "-perlio"

        for f in os.listdir(os.path.join(self.prefix.bin, win_install_path)):
            lnk_path = os.path.join(self.prefix.bin, f)
            src_path = os.path.join(win_install_path, f)
            if not os.path.exists(lnk_path):
                symlink(src_path, lnk_path)

    @run_after('install')
    def install_cpanm(self):
        spec = self.spec
        maker = make
        cpan_dir = join_path('cpanm', 'cpanm')
        if is_windows:
            maker = nmake
            cpan_dir = join_path(self.stage.source_path, cpan_dir)
        if '+cpanm' in spec:
            with working_dir(cpan_dir):
                perl = spec['perl'].command
                perl('Makefile.PL')
                maker()
                maker('install')

    def _setup_dependent_env(self, env, dependent_spec, deptypes):
        """Set PATH and PERL5LIB to include the extension and
           any other perl extensions it depends on,
           assuming they were installed with INSTALL_BASE defined."""
        perl_lib_dirs = []
        for d in dependent_spec.traverse(deptype=deptypes):
            if d.package.extends(self.spec):
                perl_lib_dirs.append(d.prefix.lib.perl5)
        if perl_lib_dirs:
            perl_lib_path = ':'.join(perl_lib_dirs)
            env.prepend_path('PERL5LIB', perl_lib_path)
        if is_windows:
            env.append_path('PATH', self.prefix.bin)

    def setup_dependent_build_environment(self, env, dependent_spec):
        self._setup_dependent_env(env, dependent_spec,
                                  deptypes=('build', 'run'))

    def setup_dependent_run_environment(self, env, dependent_spec):
        self._setup_dependent_env(env, dependent_spec, deptypes=('run',))

    def setup_dependent_package(self, module, dependent_spec):
        """Called before perl modules' install() methods.
           In most cases, extensions will only need to have one line:
           perl('Makefile.PL','INSTALL_BASE=%s' % self.prefix)
        """

        # If system perl is used through packages.yaml
        # there cannot be extensions.
        if dependent_spec.package.is_extension:

            # perl extension builds can have a global perl
            # executable function
            module.perl = self.spec['perl'].command

            # Add variables for library directory
            module.perl_lib_dir = dependent_spec.prefix.lib.perl5

            # Make the site packages directory for extensions,
            # if it does not exist already.
            mkdirp(module.perl_lib_dir)

    def setup_build_environment(self, env):
        if is_windows:
            env.append_path('PATH', self.prefix.bin)
            return

        spec = self.spec

        if (spec.version <= Version('5.34.0')
            and spec.platform == 'darwin'
            and macos_version() >= Version('10.16')):
            # Older perl versions reject MACOSX_DEPLOYMENT_TARGET=11 or higher
            # as "unexpected"; override the environment variable set by spack's
            # platforms.darwin .
            env.set('MACOSX_DEPLOYMENT_TARGET', '10.16')

        # This is how we tell perl the locations of bzip and zlib.
        env.set('BUILD_BZIP2', 0)
        env.set('BZIP2_INCLUDE', spec['bzip2'].prefix.include)
        env.set('BZIP2_LIB', spec['bzip2'].libs.directories[0])
        env.set('BUILD_ZLIB', 0)
        env.set('ZLIB_INCLUDE', spec['zlib'].prefix.include)
        env.set('ZLIB_LIB', spec['zlib'].libs.directories[0])

    @run_after('install')
    def filter_config_dot_pm(self):
        """Run after install so that Config.pm records the compiler that Spack
        built the package with.  If this isn't done, $Config{cc} will
        be set to Spack's cc wrapper script.  These files are read-only, which
        frustrates filter_file on some filesystems (NFSv4), so make them
        temporarily writable.
        """
        if is_windows:
            return
        kwargs = {'ignore_absent': True, 'backup': False, 'string': False}

        # Find the actual path to the installed Config.pm file.
        perl = self.spec['perl'].command
        config_dot_pm = perl('-MModule::Loaded', '-MConfig', '-e',
                             'print is_loaded(Config)', output=str)

        with self.make_briefly_writable(config_dot_pm):
            match = 'cc *=>.*'
            substitute = "cc => '{cc}',".format(cc=self.compiler.cc)
            filter_file(match, substitute, config_dot_pm, **kwargs)

        # And the path Config_heavy.pl
        d = os.path.dirname(config_dot_pm)
        config_heavy = join_path(d, 'Config_heavy.pl')

        with self.make_briefly_writable(config_heavy):
            match = '^cc=.*'
            substitute = "cc='{cc}'".format(cc=self.compiler.cc)
            filter_file(match, substitute, config_heavy, **kwargs)

            match = '^ld=.*'
            substitute = "ld='{ld}'".format(ld=self.compiler.cc)
            filter_file(match, substitute, config_heavy, **kwargs)

            match = "^ccflags='"
            substitute = "ccflags='%s " % ' '\
                         .join(self.spec.compiler_flags['cflags'])
            filter_file(match, substitute, config_heavy, **kwargs)

    @contextmanager
    def make_briefly_writable(self, path):
        """Temporarily make a file writable, then reset"""
        perm = os.stat(path).st_mode
        os.chmod(path, perm | 0o200)
        yield
        os.chmod(path, perm)

    # ========================================================================
    # Handle specifics of activating and deactivating perl modules.
    # ========================================================================

    def perl_ignore(self, ext_pkg, args):
        """Add some ignore files to activate/deactivate args."""
        ignore_arg = args.get('ignore', lambda f: False)

        # Many perl packages describe themselves in a perllocal.pod file,
        # so the files conflict when multiple packages are activated.
        # We could merge the perllocal.pod files in activated packages,
        # but this is unnecessary for correct operation of perl.
        # For simplicity, we simply ignore all perllocal.pod files:
        patterns = [r'perllocal\.pod$']

        return match_predicate(ignore_arg, patterns)

    def activate(self, ext_pkg, view, **args):
        ignore = self.perl_ignore(ext_pkg, args)
        args.update(ignore=ignore)

        super(Perl, self).activate(ext_pkg, view, **args)

        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.spec)
        exts[ext_pkg.name] = ext_pkg.spec

    def deactivate(self, ext_pkg, view, **args):
        ignore = self.perl_ignore(ext_pkg, args)
        args.update(ignore=ignore)

        super(Perl, self).deactivate(ext_pkg, view, **args)

        extensions_layout = view.extensions_layout
        exts = extensions_layout.extension_map(self.spec)
        # Make deactivate idempotent
        if ext_pkg.name in exts:
            del exts[ext_pkg.name]

    @property
    def command(self):
        """Returns the Perl command, which may vary depending on the version
        of Perl. In general, Perl comes with a ``perl`` command. However,
        development releases have a ``perlX.Y.Z`` command.

        Returns:
            Executable: the Perl command
        """
        for ver in ('', self.spec.version):
            ext = ''
            if is_windows:
                ext = '.exe'
            path = os.path.join(self.prefix.bin, '{0}{1}{2}'.format(
                self.spec.name, ver, ext))
            if os.path.exists(path):
                return Executable(path)
        else:
            msg = 'Unable to locate {0} command in {1}'
            raise RuntimeError(msg.format(self.spec.name, self.prefix.bin))

    def test(self):
        """Smoke tests"""
        exe = self.spec['perl'].command.name

        reason = 'test: checking version is {0}'.format(self.spec.version)
        self.run_test(exe, '--version', ['perl', str(self.spec.version)],
                      installed=True, purpose=reason)

        reason = 'test: ensuring perl runs'
        msg = 'Hello, World!'
        options = ['-e', 'use warnings; use strict;\nprint("%s\n");' % msg]
        self.run_test(exe, options, msg, installed=True, purpose=reason)
