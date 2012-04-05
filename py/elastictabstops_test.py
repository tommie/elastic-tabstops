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

class TextBlockTest(unittest.TestCase):
    def test_line_count(self):
        self.assertRaises(NotImplementedError, lambda: et.TextBlock().line_count)

    def test_iter_lines(self):
        self.assertRaises(NotImplementedError, et.TextBlock().iter_lines, 0, 0)

class ElasticTabstopsTest(unittest.TestCase):
    pass

def _add_test_cases(cls):
    _ITER_TAB_STOPS_KEYS = {
        'startLineNo': 'start_line_no',
        'endLineNo': 'end_line_no',
        'startTabSizes': 'start_tab_sizes',
        'endTabSizes': 'end_tab_sizes',
    }

    def _translate_iter_tab_stops(params):
        return dict((_ITER_TAB_STOPS_KEYS[k], v) for (k, v) in params.iteritems())

    _TAB_STOPS_KEYS = {
        'minLength': 'min_length',
        'margin': 'margin',
        'stepSize': 'step_size',
    }

    def _translate_tab_stops(params):
        return dict((_TAB_STOPS_KEYS[k], v) for (k, v) in params.iteritems())

    def create_test_case(name, data):
        def func(self):
            self.assertEquals(
                list(et.iter_tab_sizes(
                    et.ListTextBlock(data['textBlock']),
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

if __name__ == '__main__':
    unittest.main()
