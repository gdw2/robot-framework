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

from robot.variables import is_var


class TestCaseFile(object):

    def __init__(self, source=None):
        self.source = source
        self.setting_table = SettingTable()
        self.variable_table = VariableTable()
        self.testcase_table = TestCaseTable()
        self.keyword_table = KeywordTable()

    def __iter__(self):
        for table in [self.setting_table, self.variable_table,
                      self.testcase_table, self.keyword_table]:
            yield table


class DataTable(object):
    pass


class SettingTable(DataTable):

    def __init__(self):
        self.doc = Documentation()
        self.suite_setup = Fixture()
        self.suite_teardown = Fixture()
        self.test_setup = Fixture()
        self.test_teardown = Fixture()
        self.test_timeout = Timeout()
        self.force_tags = Tags()
        self.default_tags = Tags()
        self.metadata = []
        self.imports = []

    def add_metadata(self, name, value):
        self.metadata.append(Metadata(name, value))
        return self.metadata[-1]

    def add_library(self, name, args=None):
        self.imports.append(Library(name, args))
        return self.imports[-1]

    def add_resource(self, name, invalid_args=None):
        self.imports.append(Resource(name, invalid_args))
        return self.imports[-1]

    def add_variables(self, name, args=None):
        self.imports.append(Variables(name, args))
        return self.imports[-1]

    def __iter__(self):
        for setting in [self.doc, self.suite_setup, self.suite_teardown,
                        self.test_setup, self.test_teardown, self.test_timeout,
                        self.force_tags, self.default_tags] \
                        + self.metadata + self.imports:
            yield setting


class VariableTable(DataTable):

    def __init__(self):
        self.variables = []

    def add(self, name, value):
        self.variables.append(Variable(name, value))

    def __iter__(self):
        return iter(self.variables)


class TestCaseTable(DataTable):

    def __init__(self):
        self.tests = []

    def add(self, name):
        self.tests.append(TestCase(name))
        return self.tests[-1]

    def __iter__(self):
        return iter(self.tests)


class KeywordTable(DataTable):

    def __init__(self):
        self.keywords = []

    def add(self, name):
        self.keywords.append(UserKeyword(name))
        return self.keywords[-1]

    def __iter__(self):
        return iter(self.keywords)


class Setting(object):

    def __init__(self):
        self.value = []

    def set(self, value):
        self.value = value

    def _string_value(self, value):
        return value if isinstance(value, basestring) else ' '.join(value)


class Documentation(Setting):

    def __init__(self):
        self.value = ''

    def set(self, value):
        self.value = self._string_value(value)


class Fixture(Setting):

    def __init__(self):
        self.name = None
        self.args = []

    def set(self, value):
        self.name = value[0] if value else ''
        self.args = value[1:]


class Timeout(Setting):

    def __init__(self):
        self.value = None
        self.message = ''

    def set(self, value):
        self.value = value[0] if value else ''
        self.message = ' '.join(value[1:])


class Tags(Setting):
    pass


class Arguments(Setting):
    pass


class Return(Setting):
    pass


class Metadata(Setting):

    def __init__(self, name, value):
        self.name = name
        self.value = self._string_value(value)


class Import(Setting):

    def __init__(self, name, args=None, alias=None):
        self.name = name
        self.args = args or []
        self.alias = alias


class Library(Import):

    def __init__(self, name, args=None, alias=None):
        if args and not alias:
            args, alias = self._split_alias(args)
        Import.__init__(self, name, args, alias)

    def _split_alias(self, args):
        if len(args) >= 2 and args[-2].upper() == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None


class Resource(Import):

    def __init__(self, name, invalid_args=None):
        if invalid_args:
            name += ' ' + ' '.join(invalid_args)
        Import.__init__(self, name)


class Variables(Import):

    def __init__(self, name, args=None):
        Import.__init__(self, name, args)


class Variable(object):

    def __init__(self, name, value):
        self.name = name.rstrip('= ')
        if name.startswith('$') and isinstance(value, basestring):
            value = [value]  # Need to support scalar lists until RF 2.6
        self.value = value


class WithSteps(object):

    def add_step(self, content):
        self.steps.append(Step(content))
        return self.steps[-1]


class TestCase(WithSteps):

    def __init__(self, name):
        self.name = name
        self.doc = Documentation()
        self.tags = Tags()
        self.setup = Fixture()
        self.teardown = Fixture()
        self.timeout = Timeout()
        self.steps = []

    def add_for_loop(self, data):
        self.steps.append(ForLoop(data))
        return self.steps[-1]


class UserKeyword(TestCase):

    def __init__(self, name):
        self.name = name
        self.doc = Documentation()
        self.args = Arguments()
        self.return_ = Return()
        self.timeout = Timeout()
        self.steps = []


class ForLoop(WithSteps):

    def __init__(self, content):
        self.range, index = self._get_range_and_index(content)
        self.vars = content[:index]
        self.values = content[index+1:]
        self.steps = []

    def _get_range_and_index(self, content):
        for index, item in enumerate(content):
            if item.upper() in ['IN', 'IN RANGE']:
                return item.upper() == 'IN RANGE', index
        return False, len(content)


class Step(object):

    def __init__(self, content):
        self.assign = self._get_assigned_vars(content)
        try:
            self.keyword = content[len(self.assign)]
        except IndexError:
            self.keyword = ''
        self.args = content[len(self.assign)+1:]

    def _get_assigned_vars(self, content):
        vars = []
        for item in content:
            item = item.rstrip('= ')
            if not is_var(item):
                break
            vars.append(item)
        return vars
