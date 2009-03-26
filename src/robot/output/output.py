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


from robot.common.statistics import Statistics
import re

from robot import utils
import robot

from levels import LEVELS
from abstractlogger import AbstractLogger
from systemlogger import SYSLOG
from xmllogger import XmlLogger
from listeners import Listeners
from debugfile import DebugFile


class Output(AbstractLogger):
    
    def __init__(self, settings):
        AbstractLogger.__init__(self, settings['LogLevel'])
        self.xmllogger = XmlLogger(settings['Output'], settings['SplitOutputs'])
        listeners = Listeners(settings['Listeners'])
        SYSLOG.register_logger(self.xmllogger, listeners)
        SYSLOG.disable_message_cache()
        self._debugfile = DebugFile(settings['DebugFile'])
        self._namegen = self._get_log_name_generator(settings['Log'])
        self._settings = settings
        robot.output.OUTPUT = self
        
    def _get_log_name_generator(self, log):
        return log != 'NONE' and utils.FileNameGenerator(log) or None
        
    def close1(self, suite):
        stats = Statistics(suite, self._settings['SuiteStatLevel'], 
                           self._settings['TagStatInclude'], 
                           self._settings['TagStatExclude'], 
                           self._settings['TagStatCombine'],
                           self._settings['TagDoc'],
                           self._settings['TagStatLink'])
        stats.serialize(self.xmllogger)
        self.xmllogger.close(serialize_errors=True)
        SYSLOG.output_file('Output', self._settings['Output'])
        if self._debugfile is not None:
            SYSLOG.output_file('Debug', self._debugfile.path)
            self._debugfile.close()
            
    def close2(self):
        SYSLOG.close()  # TODO: move!
    
    def start_suite(self, suite):
        SYSLOG.info("Running test suite '%s'" % suite.longname)  # TODO: move!
        SYSLOG.start_suite(suite)
        if self.xmllogger.started_output:
            suite.namespace.variables.set_global('${OUTPUT_FILE}',
                                                 self.xmllogger.started_output)
            if self._namegen:
                suite.namespace.variables.set_global('${LOG_FILE}', 
                                                     self._namegen.get_name())
        if self._debugfile is not None:
            self._debugfile.start_suite(suite)
        
    def end_suite(self, suite):
        SYSLOG.end_suite(suite)
        if self.xmllogger.ended_output:
            SYSLOG.output_file('Output', self.xmllogger.ended_output)
            orig_outpath = self._settings['Output']
            suite.namespace.variables.set_global('${OUTPUT_FILE}', orig_outpath)
            self._create_split_log(self.xmllogger.ended_output, suite)
        if self._debugfile is not None:
            self._debugfile.end_suite(suite)

    def _create_split_log(self, outpath, suite):
        if self._namegen is None:
            return
        logpath = self._namegen.get_prev()
        output = robot.serializing.SplitSubTestOutput(outpath)
        output.serialize_log(logpath)
        suite.namespace.variables.set_global('${LOG_FILE}', self._namegen.get_base())
        
    def start_test(self, test):
        SYSLOG.info("Running test case '%s'" % test.name)
        SYSLOG.start_test(test)
        if self._debugfile is not None:
            self._debugfile.start_test(test)
        
    def end_test(self, test):
        SYSLOG.end_test(test)
        if self._debugfile is not None:
            self._debugfile.end_test(test)
        
    def start_keyword(self, kw):
        SYSLOG.start_keyword(kw)
        if self._debugfile is not None:
            self._debugfile.start_keyword(kw)
        
    def end_keyword(self, kw):
        SYSLOG.end_keyword(kw)
        if self._debugfile is not None:
            self._debugfile.end_keyword(kw)
     
    def write(self, msg='', level='INFO', html=False):
        # TODO: remove
        if self._debugfile is not None and self._is_logged(level, 'DEBUG'):
            self._debugfile.message(msg)
        if level.upper() == 'WARN':
            SYSLOG.warn(msg)
        AbstractLogger.write(self, msg, level, html)
        
    def _write(self, msg):
        self.xmllogger.message(msg)
    
    def log_output(self, output):
        """Splits given output to levels and messages and logs them"""
        for msg, level, html in _OutputSplitter(output).messages:
            self.write(msg, level, html)
            

class _OutputSplitter:
    
    _split_output_regexp = re.compile('^(\*(?:%s|HTML)\*)' % '|'.join(LEVELS),
                                      re.MULTILINE)
    
    def __init__(self, output):
        self.messages = self._get_messages(output.strip())

    def _get_messages(self, output):
        if not output:
            return []
        tokens = self._split_output_regexp.split(output)
        if len(tokens) == 1:
            return [ (output, 'INFO', False) ]
        return self._split_messages(tokens)
            
    def _split_messages(self, tokens):
        # Output started with a level
        if tokens[0] == '':
            tokens = tokens[1:]
        # No level in the beginning, default first msg to INFO
        else:
            tokens.insert(0, '*INFO*')
        messages = []
        for i in range(0, len(tokens), 2):
            level, html = self._get_level_and_html(tokens[i][1:-1])
            msg = tokens[i+1].strip()  
            messages.append((msg,level, html))
        return messages

    def _get_level_and_html(self, token):
        if token == 'HTML':
            return 'INFO', True
        return token, False
