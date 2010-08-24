#!/usr/bin/env python

#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

"""Rebot -- Robot Framework Report and Log Generator

Version: <VERSION>

Usage:  rebot [options] robot_outputs
  or:   interpreter /path/robot/rebot.py [options] robot_outputs
  or    python -m robot.rebot [options] robot_outputs

Inputs to Rebot are XML output files generated by Robot Framework test runs or
earlier Rebot executions. Rebot can be used to generate logs, reports and
summary reports in HTML format. It can also produce new XML output files which
can be further processed with Rebot or other tools.

When more than one input file is given, a new combined test suite containing
information from given files is created. This allows combining multiple outputs
together to create higher level reports.

For more information about Robot Framework run 'pybot --help' or go to
http://robotframework.org.

Options:

 -N --name name           Set the name of the top level test suite. Underscores
                          in the name are converted to spaces. Default name is
                          created from the name of the executed data source.
 -D --doc documentation   Set the documentation of the top level test suite.
                          Underscores in the documentation are converted to
                          spaces and it may also contain simple HTML formatting
                          (e.g. *bold* and http://url/).
 -M --metadata name:value *  Set metadata of the top level test suite.
                          Underscores in the name and value are converted to
                          spaces. Value can contain same HTML formatting as
                          --doc. Example: '--metadata version:1.2'
 -G --settag tag *        Sets given tag(s) to all executed test cases.
 -t --test name *         Select test cases by name. Name is case and space
                          insensitive and it can also be a simple pattern where
                          '*' matches anything and '?' matches any character.
                          If using '*' and '?' in the console is problematic
                          see --escape and --argumentfile.
 -s --suite name *        Select test suites by name. When this option is used
                          with --test, --include or --exclude, only test cases
                          in matching suites and also matching other filtering
                          criteria are selected. Given name can be a simple
                          pattern similarly as with --test.
 -i --include tag *       Select test cases to run by tag. Similarly as name in
                          --test, tag is case and space insensitive. There are
                          three ways to include test based on tags:
                          1) One tag as a simple pattern. Tests having a tag
                          matching the pattern are included. Example: 'it-*'
                          2) Two or more tags (or patterns) separated by '&' or
                          'AND'. Only tests having all these tags are included.
                          Examples: 'tag1&tag2', 'smokeANDowner-*ANDit-10'
                          3) Two or more tags (or patterns) separated by 'NOT'.
                          Tests having the first tag but not any of the latter
                          ones are included. Example: 'it-10NOTsmoke'
 -e --exclude tag *       Select test cases not to run by tag. These tests are
                          not run even if they are included with --include.
                          Tags are excluded using the rules explained in
                          --include.
 -c --critical tag *      Tests having given tag are considered critical. If no
                          critical tags are set, all tags are critical. Tags
                          can be given as a pattern like e.g. with --test.
                          Resets possible critical tags set earlier.
 -n --noncritical tag *   Tests with given tag are not critical even if they
                          have a tag set with --critical. Tag can be a pattern.
                          Resets possible non critical tags set earlier.
 -d --outputdir dir       Where to create output files. The default is the
                          directory where Rebot is run from and the given path
                          is considered relative to that unless it is absolute.
 -o --output file         XML output file. Not created unless this option is
                          specified. Given path, similarly as paths given to
                          --log, --report and --summary, is relative to
                          --outputdir unless given as an absolute path.
                          Default is 'output.xml'. Example: '--output out.xml'
 -l --log file            HTML log file. Can be disabled by giving a special
                          name 'NONE'. Examples: '--log mylog.html', '-l none'
 -r --report file         HTML report file. Can be disabled with 'NONE'
                          similarly as --log. Default is 'report.html'.
 -S --summary file        HTML summary report. Not created unless this option
                          is specified. Example: '--summary summary.html'
 -T --timestampoutputs    When this option is used, timestamp in a format
                          'YYYYMMDD-hhmmss' is added to all generated output
                          files between their basename and extension. For
                          example '-T -o output.xml -r report.html -l none'
                          creates files like 'output-20070503-154410.xml' and
                          'report-20070503-154410.html'.
    --splitoutputs level  Split output and log files from specified suite
                          level to make them smaller in size. Top level files
                          have links to lower level files for easy navigation.
    --logtitle title      Title for the generated test log. The default title
                          is '<Name Of The Suite> Test Log'. Underscores in
                          the title are converted into spaces in all titles.
    --reporttitle title   Title for the generated test report. The default
                          title is '<Name Of The Suite> Test Report'.
    --summarytitle title  Title for the generated summary report. The default
                          title is '<Name Of The Suite> Summary Report'.
    --reportbackground colors  Background colors to use in report and summary.
                          Either 'all_passed:critical_passed:failed' or
                          'passed:failed'. Both color names and codes work.
                          Examples:  --reportbackground green:yellow:red
                                     --reportbackground #00E:#E00
 -L --loglevel level      Threshold for selecting messages. Available levels:
                          TRACE (default), DEBUG, INFO, WARN, NONE (no msgs)
    --suitestatlevel level  How many levels to show in 'Statistics by Suite'
                          table in outputs. By default all suite levels are
                          shown. If zero (0) is given the whole table is
                          removed. Example: '--suitestatlevel 3'
    --tagstatinclude tag *  Include only these tags in 'Statistics by Tag' and
                          and 'Test Details by Tag' tables in outputs. By
                          default all tags set in test cases are shown. Given
                          'tag' can also be a simple pattern (see e.g. --test).
    --tagstatexclude tag *  Exclude these tags from 'Statistics by Tag' and
                          'Test Details by Tag' tables in outputs. This option
                          can be used with --tagstatinclude similarly as
                          --exclude is used with --include.
    --tagstatcombine tags:name *  Create combined statistics based on tags.
                          These statistics are added into 'Statistics by Tag'
                          table and matching tests into 'Test Details by Tag'
                          table. Unless the optional 'name' is used, name of
                          the added combined tag is got from specified tags.
                          Tags are combined using the rules explained in
                          --include.
    --tagdoc pattern:doc *  Add documentation to tags matching given pattern.
                          Documentation is shown in 'Test Details by Tag'
                          table and also as a tooltip in 'Statistics by Tag'
                          table. Pattern can contain characters '*' (matches
                          anything) and '?' (matches any char). In case of
                          multiple matches, documentations are catenated with
                          spaces. Documentation can contain formatting as with
                          --doc option.
                          Examples:  --tagdoc mytag:My_documentation
                                     --tagdoc regression:*See*_http://info.html
                                     --tagdoc owner-*:Original_author
    --tagstatlink pattern:link:title *  Adds links into 'Statistics by Tag'
                          table in outputs. Pattern can contain characters '*'
                          (matches anything) and '?' (matches any character).
                          Character(s) matching to wildcard expression(s) can
                          be used in the resulting link with syntax %N, where N
                          is the index of the match (starting from 1). In title
                          underscores are automatically converted to spaces.
                          Examples:
                          --tagstatlink mytag:http://my.domain:Link
                          --tagstatlink bug-*:http://tracker/id=%1:Bug_Tracker
    --removekeywords all|passed  Remove keyword data from generated outputs.
                          Keyword data is not needed when creating reports and
                          removing it can make the size of an output file
                          considerably smaller.
                          'all'    - remove data from all keywords
                          'passed' - remove data only from keywords in passed
                                     test cases and suites
    --starttime timestamp  Set starting time of test execution when creating
                          combined reports. Timestamp must be given in format
                          '2007-10-01 15:12:42.268' where all separators are
                          optional (e.g. '20071001151242268' is ok too) and
                          parts from milliseconds to hours can be omitted if
                          they are zero (e.g. '2007-10-01'). If this option is
                          not used, start time of combined reports is 'N/A'.
    --endtime timestamp   Same as --starttime but for ending time. If both
                          options are used, elapsed time is calculated based on
                          them. Otherwise it is calculated by adding elapsed
                          times of combined test suites together.
 -C --monitorcolors on|off|force  Using ANSI colors in console. Normally colors
                          work in unixes but not in Windows. Default is 'on'.
                          'on'    - use colors in unixes but not in Windows
                          'off'   - never use colors
                          'force' - always use colors (also in Windows)
 -E --escape what:with *  Escape characters which are problematic in console.
                          'what' is the name of the character to escape and
                          'with' is the string to escape it with. Note that
                          all given arguments, incl. data sources, are escaped
                          so escape characters ought to be selected carefully.
                          <---------------------ESCAPES----------------------->
                          Examples:
                          --escape space:_ --metadata X:Value_with_spaces
                          -E space:SP -E quot:Q -v var:QhelloSPworldQ
 -A --argumentfile path *  Text file to read more arguments from. File can have
                          both options and data sources one per line. Contents
                          don't need to be escaped but spaces in the beginning
                          and end of lines are removed. Empty lines and lines
                          starting with a hash character (#) are ignored.
                          Example file:
                          |  --include regression
                          |  --name Regression Tests
                          |  # This is a comment line
                          |  my_tests.html
                          |  path/to/test/directory/
 -h -? --help             Print usage instructions.
 --version                Print version information.

Options that are marked with an asterisk (*) can be specified multiple times.
For example '--test first --test third' selects test cases with name 'first'
and 'third'. If other options are given multiple times, the last value is used.

Long option format is case-insensitive. For example --SuiteStatLevel is
equivalent to, but easier to read than, --suitestatlevel. Long options can
also be shortened as long as they are unique. For example '--logti Title' works
while '--lo log.html' does not because the former matches only --logtitle but
latter matches both --log and --logtitle.

Environment Variables:

ROBOT_SYSLOG_FILE         Path to the syslog file. If not specified, or set to
                          special value 'NONE', writing to syslog file is
                          disabled. Path must be absolute.
ROBOT_SYSLOG_LEVEL        Log level to use when writing to the syslog file.
                          Available levels are the same as for --loglevel
                          option to Robot and the default is INFO.

Examples:

# Simple Rebot run that creates log and report with default names.
$ rebot output.xml

# Using options. Note that this is one long command split into multiple lines.
$ rebot --log none --report myreport.html --reporttitle My_Report
        --summary mysummary.html --summarytitle My_Summary
        --SplitOutputs 2 --TagStatCombine smokeANDmytag path/to/myoutput.xml

# Running 'robot/rebot.py' directly and creating combined outputs.
$ python /path/robot/rebot.py -N Project_X -l x.html -r x.html outputs/*.xml
"""

import sys

try:
    import pythonpathsetter
except ImportError:
    # Get here when run as 'python -m robot.rebot' and then importing robot
    # works without this and pythonpathsetter is imported again later.
    pass

import robot


if __name__ == '__main__':
    robot.rebot_from_cli(sys.argv[1:], __doc__)
