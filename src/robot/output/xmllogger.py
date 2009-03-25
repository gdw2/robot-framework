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


import os.path

from robot import utils
from robot.errors import DataError


class XmlLogger:
    
    def __init__(self, path, split_level=-1, generator='Robot'):
        self._namegen = utils.FileNameGenerator(path)
        attrs = { 'generator': utils.get_full_version(generator),
                  'generated': utils.get_timestamp() }
        self._writer = self._get_writer(path, attrs)
        self._index_writer = None
        self._split_level = split_level
        self._suite_level = 0

    def _get_writer(self, path, attrs={}):
        try:
            writer = utils.XmlWriter(path)
        except:
            raise DataError("Opening output file '%s' for writing failed: %s"
                            % (path, utils.get_error_message()))
        writer.start_element('robot', attrs)
        return writer
        
    def _close_writer(self, writer):
        writer.end_element('robot')
        writer.close()

    def close(self):
        self._close_writer(self._writer)
                
    def message(self, msg):
        html = msg.html and 'yes' or 'no'
        attrs = { 'timestamp': msg.timestamp, 'level': msg.level, 'html': html }
        self._writer.whole_element('msg', msg.message, attrs)

    def start_keyword(self, kw):
        attrs = { 'name': kw.name, 'type': kw.type, 'timeout': kw.timeout }
        self._writer.start_element('kw', attrs)
        self._writer.whole_element('doc', kw.doc)
        self._write_list('arg', [utils.unic(a) for a in kw.args], 'arguments')

    def end_keyword(self, kw):
        self._write_status(kw)
        self._writer.end_element('kw')

    def start_test(self, test):
        attrs = { 'name': test.name, 'critical': test.critical,
                  'timeout': str(test.timeout) }
        self._writer.start_element('test', attrs)
        self._writer.whole_element('doc', test.doc)

    def end_test(self, test):
        self._write_list('tag', test.tags, 'tags')
        self._write_status(test, test.message)
        self._writer.end_element('test')

    def start_suite(self, suite):
        outpath = None
        if self._suite_level == self._split_level:
            self._start_split_output(suite)
            outpath = self._writer.path
        self._start_suite(suite)
        self._suite_level += 1
        return outpath
        
    def _start_split_output(self, suite):
        path =  self._namegen.get_name()
        self._start_suite(suite, {'src': os.path.basename(path)})
        self._index_writer = self._writer
        self._writer = self._get_writer(path)
    
    def _start_suite(self, suite, extra_attrs=None):
        attrs = extra_attrs is not None and extra_attrs or {}
        attrs['name'] = suite.name
        self._writer.start_element('suite', attrs)
        self._writer.whole_element('doc', suite.doc)
        self._writer.start_element('metadata')
        for name, value in suite.get_metadata():        
            self._writer.whole_element('item', value, {'name': name})
        self._writer.end_element('metadata')

    def end_suite(self, suite):
        self._suite_level -= 1
        self._end_suite(suite)
        if self._suite_level == self._split_level:
            return self._end_split_output(suite)

    def _end_split_output(self, suite):
        outpath = self._writer.path
        self._close_writer(self._writer)
        self._writer = self._index_writer
        self._end_suite(suite)
        return outpath
    
    def _end_suite(self, suite):
        # Note that suites statistics message is _not_ written into xml
        self._write_status(suite, suite.message)
        self._writer.end_element('suite')

    def start_statistics(self, stats):
        self._writer.start_element('statistics')

    def end_statistics(self, stats):
        self._writer.end_element('statistics')
        
    def start_total_stats(self, total_stats):
        self._writer.start_element('total')

    def end_total_stats(self, total_stats):
        self._writer.end_element('total')

    def start_tag_stats(self, tag_stats):
        self._writer.start_element('tag')

    def end_tag_stats(self, tag_stats):
        self._writer.end_element('tag')

    def start_suite_stats(self, tag_stats):
        self._writer.start_element('suite')

    def end_suite_stats(self, tag_stats):
        self._writer.end_element('suite')

    def stat(self, stat):
        attrs = { 'pass' : str(stat.passed), 'fail' : str(stat.failed) }
        if stat.type == 'tag':
            attrs['info'] = self._get_tag_stat_info(stat)
        if stat.doc is not None:
            attrs['doc'] = stat.doc
        self._writer.whole_element('stat', stat.name, attrs)

    def _get_tag_stat_info(self, stat):
        if stat.critical is True:
            return 'critical'
        if stat.non_critical is True:
            return 'non-critical'
        if stat.combined is True:
            return 'combined'
        return ''
        
    def start_syslog(self, syslog):
        self._writer.start_element('syslog')
        
    def end_syslog(self, syslog):
        self._writer.end_element('syslog')
        
    def _write_list(self, tag, items, container=None):
        if container is not None:
            self._writer.start_element(container)
        for item in items:
            self._writer.whole_element(tag, item)
        if container is not None:
            self._writer.end_element(container)

    def _write_status(self, item, message=None):
        attrs = { 'status': item.status, 'starttime': item.starttime, 
                  'endtime': item.endtime } 
        self._writer.whole_element('status', message, attrs)
