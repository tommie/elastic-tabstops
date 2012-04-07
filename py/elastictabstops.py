"""
A Python library for elastic tabstops.

See http://nickgravgaard.com/elastictabstops/

For an example usage, see py/examples/eltab.

Copyright (c) 2012 Tommie Gannert
Distributed under the MIT license
"""
import math


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

def _iter_tab_sizes(lines, tab_stops, size_func=len, start_tab_sizes=[], end_tab_sizes=[]):
    """See iter_tab_sizes on how this function works.

       The only difference is that this function returns boxed integers
       instead of plain integers. This allows you to update the values of
       all affected lines using a single operation.

       @rtype : iter([[any]])
    """
    # Wrap the integers in a list to get references to integers.
    # The original Java code uses MutableInteger for this.
    # Wrapping in a list seems to be the most efficient way of doing this in
    # Python 2.7.
    tab_sizes = [[ x ] for x in start_tab_sizes ]

    def append_tab_sizes(line):
        col = -1

        for (col, tab_size) in enumerate(line):
            if col >= len(tab_sizes):
                # A new column was created.
                assert col == len(tab_sizes)
                # Wrap the integer for possible later update.
                tab_sizes.append([ tab_size ])
            else:
                # Update an old tab size.
                tab_sizes[col][0] = max(tab_sizes[col][0], tab_size)

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
    for tab_sizes in _iter_tab_sizes(lines, tab_stops, size_func=size_func, start_tab_sizes=start_tab_sizes, end_tab_sizes=end_tab_sizes):
        # Unpack the wrapped integer.
        yield [i[0] for i in tab_sizes]
