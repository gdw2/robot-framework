import sys
import unittest
from StringIO import StringIO

if __name__ == "__main__":
    sys.path.insert(0, "../../../src")

from robot.parsing.tsvreader import TsvReader
from robot.parsing.model import TestCaseFile
from robot.parsing.datareader import FromFilePopulator
from robot.utils.asserts import *
import robot.parsing.populator


class TestTsvParser(unittest.TestCase):

    def setUp(self):
        self.tcf = TestCaseFile()
        self._orig_curdir = robot.parsing.datareader.PROCESS_CURDIR
        robot.parsing.datareader.PROCESS_CURDIR = False

    def tearDown(self):
        robot.parsing.datareader.PROCESS_CURDIR = self._orig_curdir

    def test_start_table(self):
        tsv = StringIO('''*SettING*\t*  Value  *\t*V*
***Variable

*Not*Table*

Keyword*\tNot a table because doesn't start with '*'

*******************T*e*s*t*********C*a*s*e************\t***********\t******\t*
''')
        TsvReader().read(tsv, FromFilePopulator(self.tcf))
        assert_equals(self.tcf.setting_table.name, 'SettING')
        assert_equals(self.tcf.setting_table.header, ['SettING','Value','V'])

    def test_rows(self):
        tsv = StringIO('''Ignored text before tables...
Mote\tignored\text
*Setting*\t*Value*\t*Value*
Document\tWhatever\t\t\\\t
Default Tags\tt1\tt2\tt3\t\t

*Variable*\tWhatever
\\ \\ 2 escaped spaces before and after \\ \\\t\\ \\ value \\ \\
    
''')
        TsvReader().read(tsv, FromFilePopulator(self.tcf))
        assert_equal(self.tcf.setting_table.doc.value, 'Whatever  ')
        assert_equal(self.tcf.setting_table.default_tags.value, ['t1','t2','t3'])
        assert_equal(self.tcf.variable_table.variables[0].name, '\\ \\ 2 escaped spaces before and after \\ \\')
        assert_equal(self.tcf.variable_table.variables[0].value, ['\\ \\ value \\ \\'])

    
    def test_quotes(self):
        tsv = StringIO('''*Variable*\t*Value*
${v}\tHello
${v}\t"Hello"
${v}\t"""Hello"""
${v}\t"""""Hello"""""
${v}\t"Hel""lo"
${v}\t"""Hel "" """" lo"""""""
${v}\t"Hello
${v}\tHello"
''')
        TsvReader().read(tsv, FromFilePopulator(self.tcf))
        actual = [ variable for variable in self.tcf.variable_table.variables ]
        expected = ['Hello','Hello','"Hello"','""Hello""','Hel"lo',
                    '"Hel " "" lo"""','"Hello','Hello"']
        assert_equals(len(actual), len(expected))
        for act, exp in zip(actual, expected):
            assert_equals(act.name, '${v}')
            assert_equals(act.value, [exp])


if __name__ == '__main__':
    unittest.main()
