# Copyright 2008-2010 Nokia Siemens Networks Oyj
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pdb
import sys
import inspect
import traceback
import sha
from StringIO import StringIO
from SimpleXMLRPCServer import SimpleXMLRPCServer
try:
    import signal
except ImportError:
    signal = None


class RobotRemoteServer(SimpleXMLRPCServer):
  
    allow_reuse_address = True

    def __init__(self, host='localhost', port=8270):
        SimpleXMLRPCServer.__init__(self, (host, int(port)), logRequests=False)
        self._libraries = []
        self.register_function(self.get_keyword_names)
        self.register_function(self.run_keyword)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.get_keyword_documentation)
        self.register_function(self.stop_remote_server)
        self.register_function(self.remote_import)
        callback = lambda signum, frame: self.stop_remote_server()
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, callback)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, callback)
        print 'Robot Framework remote library started at %s:%s' % (host, port)
        self.serve_forever()

    def serve_forever(self):
        self._shutdown = False
        while not self._shutdown:
            self.handle_request()

    def stop_remote_server(self):
        self._shutdown = True
        return True

    def remote_import(self, lib_name, code):
        filename = sha.new(code).hexdigest() # create a temporary filename
        open(filename+'.py','w').write(code)
        exec('from %s import %s as m' % (filename, lib_name))
        self._libraries.append(m)
        return True
        

    def get_keyword_names(self):
        names = []
        for library in self._libraries:
            get_kw_names = getattr(library, 'get_keyword_names', None) or \
                           getattr(library, 'getKeywordNames', None)
            if inspect.isroutine(get_kw_names):
                names += get_kw_names()
            else:
                names += [ attr for attr in dir(library) if attr[0] != '_'
                        and inspect.isroutine(getattr(library, attr)) ]
        return names + ['stop_remote_server']

    def run_keyword(self, name, args):
        result = {'status': 'PASS', 'return': '', 'output': '', 
                  'error': '', 'traceback': ''}
        self._intercept_stdout()
        try:
            return_value = self._get_keyword(name)(*args)
        except:
            result['status'] = 'FAIL'
            result['error'], result['traceback'] = self._get_error_details()
        else:
            result['return'] = self._handle_return_value(return_value)
        result['output'] = self._restore_stdout()
        return result

    def get_keyword_arguments(self, name):
        kw = self._get_keyword(name)
        args, varargs, _, defaults = inspect.getargspec(kw)
        if inspect.ismethod(kw):
            args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += [ '%s=%s' % (name, value)
                      for name, value in zip(names, defaults) ]
        if varargs:
            args.append('*%s' % varargs)
        return args

    def get_keyword_documentation(self, name):
        return inspect.getdoc(self._get_keyword(name)) or ''

    def _get_keyword(self, name):
        if name == 'stop_remote_server':
            return self.stop_remote_server
        for library in self._libraries:
            try:
                return getattr(library(), name)
            except:
                pass #TODO Do something here

    def _get_error_details(self):
        exc_type, exc_value, exc_tb = sys.exc_info()
        if exc_type in (SystemExit, KeyboardInterrupt):
            self._restore_stdout()
            raise
        return (self._get_error_message(exc_type, exc_value),
                self._get_error_traceback(exc_tb))

    def _get_error_message(self, exc_type, exc_value):
        name = exc_type.__name__
        message = str(exc_value)
        if not message:
            return name
        if name in ('AssertionError', 'RuntimeError', 'Exception'):
            return message
        return '%s: %s' % (name, message)

    def _get_error_traceback(self, exc_tb):
        # Latest entry originates from this class so it can be removed
        entries = traceback.extract_tb(exc_tb)[1:]
        trace = ''.join(traceback.format_list(entries))
        return 'Traceback (most recent call last):\n' + trace

    def _handle_return_value(self, ret):
        if isinstance(ret, (basestring, int, long, float)):
            return ret
        if isinstance(ret, (tuple, list)):
            return [ self._handle_return_value(item) for item in ret ]
        if isinstance(ret, dict):
            return dict([ (self._str(key), self._handle_return_value(value))
                          for key, value in ret.items() ])
        return self._str(ret)

    def _str(self, item):
        if item is None:
            return ''
        return str(item)

    def _intercept_stdout(self):
        # TODO: What about stderr?
        sys.stdout = StringIO()

    def _restore_stdout(self):
        output = sys.stdout.getvalue()
        sys.stdout.close()
        sys.stdout = sys.__stdout__
        return output

if __name__ == '__main__':
    RobotRemoteServer(*sys.argv[1:])
