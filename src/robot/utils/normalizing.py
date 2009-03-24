#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import os
import sys
import re
from UserDict import UserDict


_WHITESPACE_REGEXP = re.compile('\s+')
if os.sep == '\\':
    _CASE_INSENSITIVE_FILESYSTEM = True
else:
    try:
        _CASE_INSENSITIVE_FILESYSTEM = os.listdir('/tmp') == os.listdir('/TMP')
    except OSError:
        _CASE_INSENSITIVE_FILESYSTEM = False


def normalize(string, ignore=[], caseless=True, spaceless=True):
    if spaceless:
        string = _WHITESPACE_REGEXP.sub('', string)
    if caseless:
        string = string.lower()
        ignore = [ ign.lower() for ign in ignore ]
    for ign in ignore:
        string = string.replace(ign, '')
    return string


def normalize_list(list_, ignore=[], caseless=True, spaceless=True):
    """Normalize list, sort it and remove empty values"""
    d = {}
    for item in list_:
        d[normalize(item, ignore, caseless, spaceless)] = 1
    ret = [ k for k in d.keys() if k != '' ]
    ret.sort()
    return ret
    

def normpath(path, normcase=True):
    """Returns path in normalized and absolute format.
    
    On case-insensitive file systems the path is also casenormalized
    (if normcase is True).
    """ 
    if os.sep == '\\' and len(path) == 2 and path[1] == ':':
        path = path + '\\'
    else:
        path = os.path.abspath(path)
    if normcase and _CASE_INSENSITIVE_FILESYSTEM:
        path = path.lower()
    return path


class NormalizedDict(UserDict):
    
    def __init__(self, initial={}, ignore=[], caseless=True, spaceless=True):
        UserDict.__init__(self)
        self._keys = {}
        self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        for key, value in initial.items():
            self[key] = value
    
    def __setitem__(self, key, value):
        nkey = self._normalize(key)
        self._keys.setdefault(nkey, key)
        self.data[nkey] = value

    set = __setitem__

    def __getitem__(self, key):
        return self.data[self._normalize(key)]    

    def __delitem__(self, key):
        nkey = self._normalize(key)
        del self.data[nkey]
        del self._keys[nkey]
    
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def has_key(self, key):
        return self.data.has_key(self._normalize(key))
    
    __contains__ = has_key

    def keys(self):
        return self._keys.values()

    def items(self):
        return [ (key, self[key]) for key in self.keys() ]

    def copy(self):
        copy = UserDict.copy(self)
        copy._keys = self._keys.copy()
        return copy
