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
    tab_sizes = list(start_tab_sizes)

    # These are indices into tab_sizes, one for each column of the line.
    # This indirection allows us to easily update the indentation for
    # multiple lines. The original Java code used a boxed integer instead.
    initial_column_starts = range(len(tab_sizes))

    def append_tab_sizes(line):
        """Update the tab_sizes and column_starts with newly found tab sizes.

           Note that this function does not prune the column_starts list.

           @param line: an iterable of tab sizes.
           @type  line: iter(any)
           @return: the number of columns
           @rtype:  int
        """
        col = -1

        for (col, tab_size) in enumerate(line):
            if col >= len(column_starts):
                # A new column was created.
                assert col == len(column_starts)
                tab_sizes.append(tab_size)
                column_starts.append(len(tab_sizes) - 1)
            else:
                # Update an old tab size.
                tab_sizes[column_starts[col]] = max(tab_sizes[column_starts[col]], tab_size)

        return col + 1

    column_starts = list(initial_column_starts)
    line_lengths = [] # [(int, int)]
    old_num_columns = -1 # Make sure the first item is always output.
    line_no = -1

    # For each line, increase tab sizes as appropriate.
    for (line_no, line) in enumerate(lines):
        num_columns = append_tab_sizes(map(
            tab_stops.get_tab_size, map(
                size_func,
                _ignore_last(line))))

        del column_starts[num_columns:]

        if num_columns != old_num_columns:
            line_lengths.append((line_no, num_columns))

        old_num_columns = num_columns

    append_tab_sizes(end_tab_sizes)

    # Add the ending record to allow outputting the last group within the loop.
    line_lengths.append((line_no + 1, 0))

    column_starts = list(initial_column_starts)
    tab_sizes_index = len(column_starts)
    old_line_no = 0

    # Iterate over groups of lines with the same lengths.
    for (group_line_no, num_columns) in line_lengths:
        # Yield one value per line.
        for line_no in xrange(old_line_no, group_line_no):
            # Note that this uses the column settings from the previous group.
            yield [tab_sizes[i] for i in column_starts]

        # Update column_starts.
        while len(column_starts) < num_columns:
            column_starts.append(tab_sizes_index)
            tab_sizes_index += 1

        del column_starts[num_columns:]

        old_line_no = group_line_no
