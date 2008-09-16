import unittest

from robot.output.listeners import _Listener
from robot.utils.asserts import assert_equals


class ListenerWrapper(_Listener):
    
    def __init__(self):
        pass


class TestNameAndArguments(unittest.TestCase):
    
    def setUp(self):
        self.method = ListenerWrapper()._split_args
        
    def test_with_no_args(self):
        assert_equals(self.method('name'), ('name', []))
        
    def test_with_args(self):
        assert_equals(self.method('name:arg'), ('name', ['arg']))
        assert_equals(self.method('listener:v1:v2:v3'), ('listener', ['v1', 'v2', 'v3']))
        assert_equals(self.method('a:b:c'), ('a', ['b', 'c']))
        
    def test_empty_args(self):
        assert_equals(self.method('foo:'), ('foo', ['']))
        assert_equals(self.method('bar:arg1::arg3'), ('bar', ['arg1', '', 'arg3']))
        assert_equals(self.method('L:'), ('L', ['']))
        
    def test_with_windows_path_without_args(self):
        assert_equals(self.method('C:\\name.py'), ('C:\\name.py', []))
        assert_equals(self.method('X:\\APPS\\listener'), ('X:\\APPS\\listener', []))
        assert_equals(self.method('C:/varz.py'), ('C:/varz.py', []))
    
    def test_with_windows_path_with_args(self):
        assert_equals(self.method('C:\\name.py:arg1'), ('C:\\name.py', ['arg1']))
        assert_equals(self.method('D:\\APPS\\listener:v1:b2:z3'), 
                      ('D:\\APPS\\listener', ['v1', 'b2', 'z3']))   
        assert_equals(self.method('C:/varz.py:arg'), ('C:/varz.py', ['arg']))
     
     
if __name__ == '__main__':
    unittest.main()
