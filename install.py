#!/usr/bin/env python

# Copyright 2008-2010 Nokia Siemens Networks Oyj
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Install script for Robot Framework source distributions.

Usage:  python install.py [ in(stall) | un(install) | re(install) ]

Using 'python install.py install' simply runs 'python setup.py install'
internally. You need to use 'setup.py' directly, if you want to alter the
default installation somehow.

See 'INSTALL.txt' or Robot Framework User Guide for more information.
"""

import glob
import os
import shutil
import sys


def install():
    _remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'))
    print 'Installing Robot Framework...'
    setup = os.path.join(os.path.dirname(sys.argv[0]), 'setup.py')
    rc = os.system('"%s" %s install' % (sys.executable, setup))
    if rc != 0:
        print 'Installation failed.'
        sys.exit(rc)
    print 'Installation was successful.'

def uninstall():
    print 'Uninstalling Robot Framework...'
    try:
        instdir = _get_installation_directory()
    except Exception:
        print 'Robot Framework is not installed or the installation is corrupted.'
        sys.exit(1)
    _remove(instdir)
    if not 'robotframework' in instdir:
        _remove_egg_info(instdir)
    _remove_runners()
    print 'Uninstallation was successful.'

def reinstall():
    uninstall()
    install()


def _get_installation_directory():
    import robot
    # Ensure we got correct robot module
    if 'Robot' not in robot.pythonpathsetter.__doc__:
        raise TypeError
    robot_dir = os.path.dirname(robot.__file__)
    parent_dir = os.path.dirname(robot_dir)
    if 'robotframework' in os.path.basename(parent_dir):
        return parent_dir
    return robot_dir

def _remove_runners():
    runners = ['pybot', 'jybot', 'rebot']
    if os.name == 'java':
        runners.remove('pybot')
    if os.sep == '\\':
        runners = [r + '.bat' for r in runners]
    for name in runners:
        if os.name == 'java':
            _remove(os.path.join(sys.prefix, 'bin', name))
        elif os.sep == '\\':
            _remove(os.path.join(sys.prefix, 'Scripts', name))
        else:
            for dirpath in ['/bin', '/usr/bin/', '/usr/local/bin']:
                 _remove(os.path.join(dirpath, name))

def _remove_egg_info(instdir):
    pattern = os.path.join(os.path.dirname(instdir), 'robotframework-*.egg-info')
    for path in glob.glob(pattern):
        _remove(path)

def _remove(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception, err:
        print "Removing '%s' failed: %s" % (path, err)
    else:
        print "Removed '%s'" % path


if __name__ == '__main__':
    actions = { 'install': install, 'in': install,
                'uninstall': uninstall, 'un': uninstall,
                'reinstall': reinstall, 're': reinstall }
    try:
        actions[sys.argv[1]]()
    except (KeyError, IndexError):
        print __doc__
