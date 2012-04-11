"""
A Python library for elastic tabstops.

This file contains the unit tests.

See http://nickgravgaard.com/elastictabstops/

Copyright (c) 2012 Tommie Gannert
Distributed under the MIT license
"""
import json
import os.path
import unittest

import elastictabstops as et


class TabStopsTest(unittest.TestCase):
    def setUp(self):
        self.tab_stops = et.TabStops()

    def tearDown(self):
        del self.tab_stops

    def test_get_tab_size(self):
        self.assertEquals(
            self.tab_stops.get_tab_size(10),
            10 + 1)

    def test_get_tab_size_type(self):
        self.assert_(isinstance(self.tab_stops.get_tab_size(10), int))

class IgnoreLastTest(unittest.TestCase):
    def test_empty(self):
        self.assertEquals(
            list(et._ignore_last([])),
            [])

    def test_one(self):
        self.assertEquals(
            list(et._ignore_last([ 'Hello' ])),
            [])

    def test_two(self):
        self.assertEquals(
            list(et._ignore_last([ 'Hello', 'world!' ])),
            [ 'Hello' ])

class ElasticTabstopsTest(unittest.TestCase):
    pass

def _add_test_cases(cls):
    _ITER_TAB_STOPS_KEYS = {
        'startTabSizes': 'start_tab_sizes',
        'endTabSizes': 'end_tab_sizes',
    }

    def _translate_iter_tab_stops(params):
        return dict((_ITER_TAB_STOPS_KEYS[k], v) for (k, v) in params.iteritems())

    _TAB_STOPS_KEYS = {
        'margin': 'margin',
        'minSize': 'min_size',
        'stepSize': 'step_size',
    }

    def _translate_tab_stops(params):
        return dict((_TAB_STOPS_KEYS[k], v) for (k, v) in params.iteritems())

    def create_test_case(name, data):
        def func(self):
            self.assertEquals(
                list(et.iter_tab_sizes(
                    data['textBlock'],
                    et.TabStops(**_translate_tab_stops(data.get('tabStops', {}))),
                    **_translate_iter_tab_stops(data.get('params', {})))),
                data['tabSizes'])

        func.__name__ = name
        func.__doc__ = name + ': ' + json.dumps(data)

        return func

    test_path = os.path.join(os.path.dirname(__file__), '..', 'test')

    for filename in os.listdir(test_path):
        if not filename.endswith('.json'):
            continue

        with open(os.path.join(test_path, filename), 'rt') as f:
            data = json.load(f)

        func = create_test_case('test_' + filename[:-5].replace('-', '_'), data)
        setattr(cls, func.__name__, func)

_add_test_cases(ElasticTabstopsTest)

class TextBlockTest(unittest.TestCase):
    def setUp(self):
        self.tb = et.TextBlock(
            [
                [ 'it', 'is', 'a' ],
                [ 'small', 'world' ],
            ],
            et.TabStops())

    def tearDown(self):
        del self.tb

    def test_create(self):
        pass

    def test_len(self):
        self.assertEquals(len(self.tb), 2)

    def test_delitem(self):
        del self.tb[0]
        self.assertEquals(len(self.tb), 1)

    def test_delslice(self):
        del self.tb[0:1]
        self.assertEquals(len(self.tb), 1)

    def test_getitem(self):
        self.assertEquals(self.tb[0], [ 'it', 'is', 'a' ])

    def test_getslice(self):
        self.assertEquals(self.tb[0:1], [ [ 'it', 'is', 'a' ] ])

    def test_setitem(self):
        self.tb[1] = [ 'abc', 'def' ]
        self.assertEquals(len(self.tb), 2)
        self.assertEquals(self.tb[1], [ 'abc', 'def' ])
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 4, 3 ], [ 4 ] ])

    def test_setslice(self):
        self.tb[1:2] = [ [ 'abc', 'def' ] ]
        self.assertEquals(len(self.tb), 2)
        self.assertEquals(self.tb[1], [ 'abc', 'def' ])
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 4, 3 ], [ 4 ] ])

    def test_append(self):
        self.tb.append([ 'abcdef', 'ghi' ])
        self.assertEquals(len(self.tb), 3)
        self.assertEquals(self.tb[-1], [ 'abcdef', 'ghi' ])
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 7, 3 ], [ 7 ], [ 7 ] ])

    def test_extend(self):
        self.tb.extend([ [ 'abcdef', 'ghi' ] ])
        self.assertEquals(len(self.tb), 3)
        self.assertEquals(self.tb[-1], [ 'abcdef', 'ghi' ])
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 7, 3 ], [ 7 ], [ 7 ] ])

    def test_insert_block(self):
        self.tb.insert(1, [])
        self.assertEquals(len(self.tb), 3)
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 3, 3 ], [], [ 6 ] ])

    def test_insert_block2(self):
        self.tb[1:1] = [ [ 'abcdef', 'ghi' ], [ 'a' ], [ 'mr', 'pink' ] ]
        self.assertEquals(len(self.tb), 5)
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 7, 3 ], [ 7 ], [], [ 6 ], [ 6 ] ])

    def test_insert_block_first(self):
        self.tb.insert(0, [])
        self.assertEquals(len(self.tb), 3)
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [], [ 6, 3 ], [ 6 ] ])

    def test_iter_tab_sizes(self):
        self.assertEquals(list(self.tb.iter_tab_sizes()), [ [ 6, 3 ], [ 6 ] ])

    def test_iter_tab_sizes_range(self):
        self.assertEquals(list(self.tb.iter_tab_sizes(0, 1)), [ [ 6, 3 ] ])
        self.assertEquals(list(self.tb.iter_tab_sizes(1, 2)), [ [ 6 ] ])

if __name__ == '__main__':
    unittest.main()
