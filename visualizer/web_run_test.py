#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

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


# Runs both 'user_script' and 'expect_script' and returns whether the
# test has passed or failed, along with the FULL trace if the test has
# failed (so that the user can debug it)


import cgi
import visualizer.pg_logger

import json
import pprint
import re


EPSILON = 1e-3


output_json = None
user_trace = None # the FULL user trace (without any IDs, though)
answer = None


def tokens_are_equal(x, y):
  # print "tokens_are_equal: {0} versus {1}".format(x, y)
  numeric_const_pattern = r"[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?$"

  res = None

  if re.match(numeric_const_pattern, x):
    try:
      res = abs(float(x) - float(y)) < EPSILON
    except:
      res = False
  else:
    res = x == y
  # print "verdict: {0}".format(res)
  return res


def compare_sequences_of_tokens(seq1, seq2):
  # print "compare_sequences_of_tokens: {0} versus {1}".format(seq1, seq2)
  seq1 = [i for i in seq1.split() if i]
  seq2 = [i for i in seq2.split() if i]
  return len(seq1) == len(seq2) and all(tokens_are_equal(x, y) for x, y in zip(seq1, seq2))


def user_script_finalizer(output_lst):
  # very important!
  global user_trace

  user_trace = output_lst

  really_finalize()


def really_finalize():
  # Procedure for grading test
  # we should compare user_trace[-1]['stdout'] with answer
  global output_json

  if not user_trace:
    ret['status'] = 'error'
    ret['error_msg'] = 'На тестирование отправлена пустая программа'
  else:
    output = user_trace[-1]['stdout']

    ret = {}
    ret['status'] = 'ok'
    ret['passed_test'] = False

    ret['expect_val'] = answer.rstrip()
    ret['test_val'] = output.rstrip()

    # do the actual comparison here!
    if compare_sequences_of_tokens(ret['expect_val'], ret['test_val']):
      ret['passed_test'] = True
    else:
      ret['passed_test'] = False
      ret['status'] = 'error'
    # else:
    #   # branch for the exceptions, not for the WA!
    #   print(86)
    #   ret['status'] = 'error'
    #   # XXX: strange line here
    #   print user_trace
    #   ret['error_msg'] = user_trace_final_entry['exception_msg']

  output_json = json.dumps(ret)


def run_script_on_test_input(user_script, test_input, test_answer):
  global answer

  answer = test_answer

  pg_logger.exec_script_str(user_script, test_input, 
      user_script_finalizer, ignore_id=True)

  return output_json
