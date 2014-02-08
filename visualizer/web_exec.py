#!/usr/bin/python2.6

# Online Python Tutor
# https://github.com/pgbovine/OnlinePythonTutor/
# 
# Copyright (C) 2010-2012 Philip J. Guo (philip@pgbovine.net)
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# Executes the Online Python Tutor back-end as a CGI script, which
# accepts one POST parameter, 'user_script', containing the string
# contents of the Python script that the user wants to execute.
#
# Returns a complete JSON execution trace to the front-end.
#
# This version uses Python 2.6 on the MIT CSAIL servers.
# (note that Python 2.4 doesn't work on CSAIL, but Python 2.6 does)
#
# If you want to run this script, then you'll need to change the
# shebang line at the top of this file to point to your system's Python.
#
# Also, check CGI execute permission in your script directory.
# You might need to create an .htaccess file like the following:
#
#   Options +ExecCGI
#   AddHandler cgi-script .py


import json
from visualizer.pg_logger import exec_script_str


def web_finalizer(output_lst):
  global output_json

  # use compactly=False to produce human-readable JSON,
  # except at the expense of being a LARGER download

  output_json = json.dumps(output_lst)



def exec_script_on_input(user_script, input_data):
  # pg_logger.set_max_executed_lines(max_instructions)
  exec_script_str(user_script, input_data, web_finalizer)

  return output_json