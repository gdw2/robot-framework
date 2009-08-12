#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

import re

from tsvreader import TsvReader


class TxtReader(TsvReader):

    _splitter = re.compile(' {2,}(?:\| {2,})?')
        
    def _split_row(self, row):
        row = row.rstrip()
        if row.startswith('|  '):
            row = row[1:].lstrip()
        if row.endswith('  |'):
            row = row[:-1].rstrip()
        return self._splitter.split(row)
