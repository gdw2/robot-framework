#!/usr/bin/env python

"""Script to generate atest runners based on data files.

Usage:  %s path/to/data.file
"""

from __future__ import with_statement
import sys, os

if len(sys.argv) != 2:
    print __doc__ % os.path.basename(sys.argv[0])
    sys.exit(1)

inpath = os.path.abspath(sys.argv[1])
outpath = inpath.replace(os.path.join('atest', 'testdata'), 
                         os.path.join('atest', 'robot'))

dirname = os.path.dirname(outpath)
if not os.path.exists(dirname):
    os.mkdir(dirname)

with open(inpath) as input:
    tests = []
    process = False
    for line in input.readlines():
        line = line.rstrip()
        if line.startswith('*'):
            name = line.replace('*', '').replace(' ', '').upper()
            process = name in ('TESTCASE', 'TESTCASES')
        elif process and line and line[0] != ' ':
            tests.append(line.split('  ')[0])

with open(outpath, 'w') as output:
    path = inpath.split(os.path.join('atest', 'testdata'))[1][1:]
    output.write("""*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  %s
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

""" % path.replace(os.sep, '/'))
    for test in tests:
        output.write(test + '\n    Check Test Case  ${TESTNAME}\n\n')

print outpath
