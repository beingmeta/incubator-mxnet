# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Debugging help
# http://grapsus.net/blog/post/Low-level-Python-debugging-with-GDB

from __future__ import print_function
import sys
from mxnet.base import _LIB
import mxnet.cython as cy

mxc  = cy.load_cython('mxnet.cython', 'mxcython')
cynd = cy.load_cython('mxnet.ndarray', 'ndarray')

def test_basic_cython():
  print('ENTER test_basic_cython')
  myclass = mxc.CythonTestClass()
  for terms in 5, 9, 23, 177, 1111, 33333, 555555:
    sys.stdout.write('{0:10} terms: '.format(terms))
    mxc.print_pi(terms)
  myclass.print_something('Something')
  print('EXIT test_basic_cython')

  # Test using a C++ class'
  mxc.test_cpp_class()
  mxc.test_perf(10, 1)
  test_perf_bridge(10, 1)


def test_perf(count, make_c_call):
  start = _LIB.TimeInMilliseconds()
  foo = 0
  i = 0
  while i < count:
    foo += i
    if foo > count:
      foo = 0
    if make_c_call != 0:
      _LIB.TrivialCPPCall(0)
    i += 1
  stop = _LIB.TimeInMilliseconds()
  msg = ""
  if make_c_call != 0:
    msg = " WITH API CALL"
  print("PYTHON {}: {} items took {} seconds".format(msg, count, float(stop - start)/1000))


def test_perf_bridge(count, do_cython_call, api_call_count):
  if do_cython_call == 0:
    assert api_call_count == 0  # Sanity on input values
  acc = int(api_call_count)
  start = _LIB.TimeInMilliseconds()
  foo = 0
  i = 0
  while i < count:
    foo += i
    if foo > count:
      foo = 0
    if do_cython_call != 0:
      mxc.bridge_c_call(0, acc)
    i += 1
  stop = _LIB.TimeInMilliseconds()
  msg = ""
  if do_cython_call != 0:
    msg = " WITH CYTHON CALL"
  else:
    msg = " WITHOUT CYTHON CALL"
  print("PYTHON->CYTHON BRIDGE {}, ACC={}: {} items took {} seconds".format(
    msg, acc, count, float(stop - start)/1000))


if __name__ == '__main__':
  # import nose
  # nose.runmodule()

  iter_count = 100000000
  test_perf(iter_count, 0)
  mxc.test_perf(iter_count, 0)
  test_perf(iter_count, 1)
  mxc.test_perf(iter_count, 1)
  test_perf_bridge(iter_count, 0, 0)  # Baseline, no cython call
  test_perf_bridge(iter_count, 1, 0)  # Cython call, but no C API call
  test_perf_bridge(iter_count, 1, 1)  # Cython call with one C API call
  test_perf_bridge(iter_count, 1, 10) # Cython call with multiple C API call

#  test_basic_cython()
