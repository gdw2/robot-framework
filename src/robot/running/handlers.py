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

import sys

from robot import utils
from robot.common import BaseHandler

from runkwregister import RUN_KW_REGISTER
from arguments import PythonKeywordArguments, JavaKeywordArguments, \
    DynamicKeywordArguments, PythonInitArguments, JavaInitArguments


if utils.is_jython:
    from org.python.core import PyReflectedFunction, PyReflectedConstructor

    def _is_java_init(init):
        return isinstance(init, PyReflectedConstructor)
    def _is_java_method(method):
        return hasattr(method, 'im_func') \
               and isinstance(method.im_func, PyReflectedFunction)
else:
    _is_java_init = _is_java_method = lambda item: False


def Handler(library, name, method):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _RunKeywordHandler(library, name, method)
    if _is_java_method(method):
        return _JavaHandler(library, name, method)
    else:
        return _PythonHandler(library, name, method)


def DynamicHandler(library, name, method, doc, argspec):
    if RUN_KW_REGISTER.is_run_keyword(library.orig_name, name):
        return _DynamicRunKeywordHandler(library, name, method, doc, argspec)
    return _DynamicHandler(library, name, method, doc, argspec)


def InitHandler(library, method):
    if method is None:
        method = lambda: None
    Init = _PythonInitHandler if not _is_java_init(method) else _JavaInitHandler
    return Init(library, '__init__', method)


class _BaseHandler(BaseHandler):
    type = 'library'

    def __init__(self, library, handler_name, handler_method):
        self.library = library
        self.name = utils.printable_name(handler_name, code_style=True)
        self.arguments = self._parse_arguments(handler_method)
        self.minargs, self.maxargs = self.arguments.minargs, self.arguments.maxargs

    def _parse_arguments(self, handler_method):
        raise NotImplementedError(self.__class__.__name__)


class _RunnableHandler(_BaseHandler):

    def __init__(self, library, handler_name, handler_method):
        _BaseHandler.__init__(self, library, handler_name, handler_method)
        self._handler_name = handler_name
        self._method = library.scope == 'GLOBAL' and \
                self._get_global_handler(handler_method, handler_name) or None
        self.doc = ''
        self.timeout = ''  # Needed for set_attributes in runner.start_keyword

    def run(self, output, namespace, args):
        """Executes the represented handler with given 'args'.

        Note: This method MUST NOT change this object's internal state.
        """
        posargs, kwargs = self._process_args(args, namespace.variables)
        self._tracelog_args(output, posargs, kwargs)
        self._capture_output()
        try:
            return self._run_handler(self._current_handler(), posargs, kwargs,
                                     output, self._get_timeout(namespace))
        finally:
            self._release_and_log_output(output)

    def _process_args(self, args, variables):
        return self.arguments.resolve(args, variables)

    def _capture_output(self):
        utils.capture_output()

    def _current_handler(self):
        if self._method is not None:
            return self._method
        return self._get_handler(self.library.get_instance(),
                                 self._handler_name)

    def _get_global_handler(self, method, name):
        return method

    def _get_handler(self, lib_instance, handler_name):
        """Overridden by DynamicHandler"""
        return getattr(lib_instance, handler_name)

    def _run_handler(self, handler, posargs, kwargs, output, timeout):
        if timeout is not None and timeout.active():
            return timeout.run(handler, args=posargs, kwargs=kwargs, logger=output)
        return handler(*posargs, **kwargs)

    def _get_timeout(self, namespace):
        timeoutable = self._get_timeoutable_items(namespace)
        if len(timeoutable) > 0 :
            return min([ item.timeout for item in timeoutable ])
        return None

    def _get_timeoutable_items(self, namespace):
        items = namespace.uk_handlers[:]
        if namespace.test is not None and namespace.test.status == 'RUNNING':
            items.append(namespace.test)
        return items

    def _release_and_log_output(self, logger):
        stdout, stderr = utils.release_output()
        logger.log_output(stdout)
        logger.log_output(stderr)
        if stderr.strip() != '':
            sys.stderr.write(stderr+'\n')


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self.doc = utils.get_doc(handler_method)

    def _parse_arguments(self, handler_method):
        return PythonKeywordArguments(handler_method, self.longname)


class _JavaHandler(_RunnableHandler):

    def _parse_arguments(self, handler_method):
        return JavaKeywordArguments(handler_method, self.longname)


class _DynamicHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method, doc='',
                 argspec=None):
        self._argspec = argspec
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self._run_keyword_method_name = handler_method.__name__
        self.doc = doc is not None and utils.unic(doc) or ''

    def _parse_arguments(self, handler_method):
        return DynamicKeywordArguments(self._argspec, self.longname)

    def _get_handler(self, lib_instance, handler_name):
        runner = getattr(lib_instance, self._run_keyword_method_name)
        return self._get_dynamic_handler(runner, handler_name)

    def _get_global_handler(self, method, name):
        return self._get_dynamic_handler(method, name)

    def _get_dynamic_handler(self, runner, name):
        def handler(*args):
            return runner(name, list(args))
        return handler


class _RunKeywordHandler(_PythonHandler):

    def _process_args(self, args, variables):
        index = RUN_KW_REGISTER.get_args_to_process(self.library.orig_name, self.name)
        if index == 0:
            self.arguments.check_arg_limits(args)
            return args, {}
        # There might be @{list} variables and those might have more or less
        # arguments that is needed. Therefore we need to go through arguments
        # one by one.
        processed = []
        while len(processed) < index and args:
            processed += variables.replace_list([args.pop(0)])
        # In case @{list} variable is unpacked, the arguments going further
        # needs to be escaped, otherwise those are unescaped twice.
        processed[index:] = [utils.escape(arg) for arg in processed[index:]]
        args = processed + args
        self.arguments.check_arg_limits(args)
        return args, {}

    def _get_timeout(self, namespace):
        return None


class _DynamicRunKeywordHandler(_DynamicHandler, _RunKeywordHandler):
    _process_args = _RunKeywordHandler._process_args
    _get_timeout = _RunKeywordHandler._get_timeout


class _PythonInitHandler(_BaseHandler):

    def _parse_arguments(self, handler_method):
        return PythonInitArguments(handler_method, self.library.name)


class _JavaInitHandler(_BaseHandler):

    def _parse_arguments(self, handler_method):
        return JavaInitArguments(handler_method, self.library.name)
