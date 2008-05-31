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


import sys
import os

from argumentparser import ArgumentParser
from domwrapper import DomWrapper
from escaping import escape, unescape, escape_file_name
from error import get_error_message, get_error_details
from htmlutils import html_escape, html_attr_escape
from htmlwriter import HtmlWriter
from importing import simple_import, import_
from normalizing import normalize, normalize_list, normpath, NormalizedDict
from match import eq, eq_any, any_eq_any, matches, matches_any, any_matches, \
        contains, contains_any
from misc import get_temp_dir, get_not_none, is_url, plural_or_not, get_link_path, \
        get_doc, cygpath, printable_name_from_path, printable_name, download, \
        calc_percents, percents_to_widths, get_directory, seq2str, seq2str2
from outputcapture import capture_output, release_output
from robottime import get_timestamp, get_start_timestamp, format_time, \
        get_time, get_elapsed_time, get_elapsed_millis, \
        elapsed_string_to_millis, elapsed_millis_to_string, \
        timestr_to_secs, secs_to_timestr, get_diff_to_gmt, \
        secs_to_timestamp, timestamp_to_secs
from robottypes import is_list, is_tuple, is_scalar, is_str, is_integer, \
        is_boolean, is_number, is_list_of_str, to_boolean, to_list, \
        type_as_str, unic
from robotversion import get_version, get_java_version, DATE
from text import cut_long_message, cut_long_assign_msg, wrap
from xmlwriter import XmlWriter
from connectioncache import ConnectionCache
from idgenerator import IdGenerator, FileNameGenerator


version    = get_version()          # Robot version as string
version_date = DATE
py_version = sys.version_info[:2]   # Python version in tuple (major,minor)
java_version = get_java_version()   # Java version in tuple (major,minor)
is_jython  = os.name == 'java'
is_windows = os.sep == '\\'         # This works also in Jython on Windows
is_linux   = sys.platform.count('linux') > 0
is_cygwin  = sys.platform.count('cygwin') > 0
platform   = '%sython %s on %s' % (is_jython and 'J' or 'P', 
                                   sys.version.split()[0], sys.platform)

def get_full_version(who):
    return "%s %s (%s)" % (who, version, platform)
