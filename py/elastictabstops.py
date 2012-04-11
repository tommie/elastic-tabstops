"""
A Python library for elastic tabstops.

See http://nickgravgaard.com/elastictabstops/

For an example usage, see py/examples/eltab.

Copyright (c) 2012 Tommie Gannert
Distributed under the MIT license
"""
import heapq
import math

__all__ = [
    'iter_tab_sizes',
    'TabStops',
    'TextBlock',
]


class TabStops(object):
    """A TabStops has information on how to render (and measure) text.

       The default unit of measurement is "characters," suitable for rendering
       to a fixed-width terminal. The class itself does not care about this unit.

       For the documentation we call the reported unit of measurement the
       "view units."

       @ivar  margin: the amount of extra space between columns, in view units.
       @itype margin: any
       @ivar  min_size: the minimum size of a tab stop, in view units,
                        excluding margin.
       @itype min_size: any
       @ivar  step_size: the size, in view units, of alignment of the tab stops.
       @itype step_size: any
    """
    def __init__(self, margin=1, min_size=1, step_size=1):
        """Construct a new view object.

           The parameters are simply stored in the object.
        """
        self.margin = margin
        self.min_size = min_size
        self.step_size = step_size

    def get_tab_size(self, text_size):
        """Return the minimum tab stop needed to fit a text of the given size.

           The default implementation adjusts for step size, minimum size and
           adds the margin.

           NB: We round up here, instead of (floor() + 1), which the original
               Java implementation does. I think it makes more sense this way
               as we have the margin separately configurable.

           @param text_size: the size of the text, in view units.
           @type  text_size: float or int (or any in overriding classes)
           @return: the preferred tab size, including margin.
           @rtype : int (or any in overriding classes)
        """
        return self.margin + max(
            int(math.ceil(text_size / self.step_size)) * self.step_size,
            self.min_size)

_NOTHING = object()

def _ignore_last(iter):
    """Pass through all items of the given iterator, except the last.

       @param iter: the iterator.
       @type  iter: iter(any)
       @return: an iterator.
       @rtype : iter(any)
    """
    prev = _NOTHING

    for i in iter:
        if prev is not _NOTHING:
            yield prev

        prev = i

def _iter_tab_sizes(lines, tab_stops, size_type, size_update_func, size_func=len, start_tab_sizes=[], end_tab_sizes=[]):
    """See iter_tab_sizes on how this function works.

       The only difference is that this function returns boxed integers
       instead of plain integers. This allows you to update the values of
       all affected lines using a single operation.

       @rtype : iter([size_type])
    """
    tab_sizes = [size_type(x) for x in start_tab_sizes]

    def append_tab_sizes(line):
        col = -1

        for (col, tab_size) in enumerate(line):
            if col >= len(tab_sizes):
                # A new column was created.
                assert col == len(tab_sizes)
                # Wrap the integer for possible later update.
                tab_sizes.append(size_type(tab_size))
            else:
                # Update an old tab size.
                size_update_func(tab_sizes[col], tab_size)

        return col + 1

    line_columns = [] # [[[int]]]

    # For each line, increase tab sizes as appropriate.
    for line in lines:
        num_columns = append_tab_sizes(map(
            tab_stops.get_tab_size,
            map(size_func, _ignore_last(line))))

        del tab_sizes[num_columns:]
        line_columns.append(list(tab_sizes))

    append_tab_sizes(end_tab_sizes)

    return line_columns

def iter_tab_sizes(lines, tab_stops, size_func=len, start_tab_sizes=[], end_tab_sizes=[]):
    """Return the tab stops of the given text block.

       Optionally with hints of the sizes of surrounding lines. If
       start_tab_sizes or end_tab_sizes is not given, they are assumed to be
       the empty list.

       The same thing goes for end_tab_sizes.

       The return value, as well as start_tab_sizes and end_tab_sizes (where
       applicable) must not contain the last column. The last column does not
       matter for layouts, and are simply ignored by the current algorithm. As
       an example, the text (assuming space is tab)

           Hello world

       would cause this function to return

           [ 6 ]

       as there are two columns.

       @param lines: an iterator of iterators of text sizes.
       @type  lines: iter(iter(any))
       @param tab_stops: tab stop settings.
       @type  tab_stops: TabStops
       @param size_func: a function returning the size of a text, in view units.
       @type  size_func: any (usually float or int)
       @param start_tab_sizes: a list of tab sizes of the lines before the first.
                               Defaults to a block boundary (empty list.)
       @type  start_tab_sizes: [any] or NoneType
       @param end_tab_sizes: a list of tab sizes of the lines after the last
                             Defaults to a block boundary (empty list.)
       @type  end_tab_sizes: [any] or NoneType
       @return: an iterator of lists of tab sizes, with one value per line.
       @rtype : iter([any])
    """
    # Wrap the integers in a list to get references to integers.
    # The original Java code uses MutableInteger for this.
    # Wrapping in a list seems to be the most efficient way of doing this in
    # Python 2.7.
    def box(value):
        return [ value ]

    def update_list_max(u, value):
        u[0] = max(u[0], value)

    for tab_sizes in _iter_tab_sizes(lines, tab_stops, box, update_list_max, size_func=size_func, start_tab_sizes=start_tab_sizes, end_tab_sizes=end_tab_sizes):
        # Unpack the wrapped integer.
        yield [i[0] for i in tab_sizes]

class TextBlock(object):
    def __init__(self, lines, tab_stops, size_func=len):
        self.tab_stops = tab_stops
        self.size_func = size_func
        self._lines = [] #lines
        self._tab_sizes = [] #list(self._iter_tab_sizes(lines))
        self._splice(0, 0, lines)

    def __delitem__(self, index):
        if isinstance(index, slice): return self._splice(index.start, index.stop, [])
        elif index < 0: return self._splice(index, len(self._lines) + index + 1, [])
        else: return self._splice(index, index + 1, [])

    def __getitem__(self, index):
        return self._lines.__getitem__(index)

    def __len__(self):
        return self._lines.__len__()

    def __setitem__(self, index, value):
        if isinstance(index, slice): return self._splice(index.start, index.stop, value)
        elif index < 0: return self._splice(index, len(self._lines) + index + 1, [ value ])
        else: return self._splice(index, index + 1, [ value ])

    def append(self, line):
        n = len(self._lines)
        return self._splice(n, n, [ line ])

    def count(self, x):
        return self._lines.count(x)

    def extend(self, lines):
        n = len(self._lines)
        return self._splice(n, n, lines)

    def index(self, *args):
        return self._lines.index(*args)

    def insert(self, index, value):
        return self._splice(index, index, [ value ])

    def pop(self, index=-1):
        if index < 0: return self._splice(index, len(self._lines) + index + 1, [])
        else: return self.splice(index, index + 1, [])

    def remove(self, value):
        index = self.index(value)
        return self.splice(index, index + 1, [])

    def reverse(self):
        self._tab_sizes.reverse()
        return self._lines.reverse()

    def sort(self, *args, **kwargs):
        raise NotImplementedError('sort')

    def iter_tab_sizes(self, start=0, end=None):
        if end is None:
            end = len(self._lines)

        for line in self._tab_sizes[start:end]:
            # Value negated to get the largest value at the root.
            yield [-x[0] for x in line]

    @staticmethod
    def _heap_box(value):
        # Value negated to get the largest value at the root.
        return [ -value ]

    @staticmethod
    def _heap_push(heap, value):
        # Value negated to get the largest value at the root.
        heapq.heappush(heap, -value)

    def _splice(self, start, end, lines):
        if start < 0: start += len(self._lines)
        if end < 0: end += len(self._lines)

        # Remove the old values from the heaps.
        for line_no in xrange(start, end):
            ts = self._tab_sizes[line_no]

            for col in xrange(len(ts)):
                ts[col].remove(
                    -self.tab_stops.get_tab_size(self.size_func(
                        self._lines[line_no][col])))

        self._lines[start:end] = lines
        self._tab_sizes[start:end] = [[] for i in xrange(len(lines))]

        if start > 0:
            tab_sizes = list(self._tab_sizes[start - 1])
        else:
            tab_sizes = []

        # Update tab sizes for the new lines.
        for (i, line) in enumerate(self._lines[start:start + len(lines)]):
            ts = self._tab_sizes[start + i]

            for col in xrange(len(line) - 1):
                tab_size = self.tab_stops.get_tab_size(self.size_func(line[col]))

                if col >= len(tab_sizes):
                    assert col == len(tab_sizes)
                    ts.append(self._heap_box(tab_size))
                    tab_sizes = list(ts)
                else:
                    ts.append(tab_sizes[col])
                    self._heap_push(ts[col], tab_size)

            del tab_sizes[max(0, len(line) - 1):]

        if start + len(lines) < len(self._lines):
            # Update the tab sizes for the following lines.
            # We may have introduced a block split, meaning we have to
            # assign new heaps for the lines below the insertion point.
            num_columns = len(self._lines[start + len(lines)]) - 1
            new_tab_sizes = list(tab_sizes)

            # Change references for all lines after so they don't share a heap
            # with the top ones after a block break.
            for (i, line) in enumerate(self._lines[start + len(lines):]):
                num_columns = min(num_columns, len(line) - 1)

                if num_columns == 0:
                    # End-of-block, so nothing more to do.
                    break

                for col in xrange(num_columns):
                    tab_size = self.tab_stops.get_tab_size(self.size_func(line[col]))

                    if col >= len(new_tab_sizes):
                        new_tab_sizes.append(self._heap_box(tab_size))

                    if self._tab_sizes[start + len(lines) + i][col] is not new_tab_sizes[col]:
                        self._tab_sizes[start + len(lines) + i][col].remove(-self.tab_stops.get_tab_size(self.size_func(line[col])))
                        self._tab_sizes[start + len(lines) + i][col] = new_tab_sizes[col]
                        self._heap_push(new_tab_sizes[col], tab_size)
