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
       @ivar  min_length: the minimum size of a tab stop, in view units,
                          excluding margin.
       @itype min_length: any
       @ivar  step_size: the size, in view units, of alignment of the tab stops.
       @itype step_size: any
    """
    def __init__(self, margin=1, min_length=1, step_size=1):
        """Construct a new view object.

           The parameters are simply stored in the object.
        """
        self.margin = margin
        self.min_length = min_length
        self.step_size = step_size

    def get_tab_size(self, text_length):
        """Return the minimum tab stop needed to fit a text of the given length.

           The text length may come from get_text_length(), or from somewhere
           else.

           The default implementation adjusts for step size, minimum length and
           adds the margin.

           NB: We round up here, instead of (floor() + 1), which the original
               Java implementation does. I think it makes more sense this way
               as we have the margin separately configurable.

           @param text_length: the size of the text, in view units.
           @type  text_length: float or int (or any in overriding classes)
           @return: the preferred tab size, including margin.
           @rtype : int (or any in overriding classes)
        """
        return self.margin + max(
            int(math.ceil(text_length / self.step_size)) * self.step_size,
            self.min_length)

class TextBlock(object):
    """A text block is the basic unit given to iter_tab_stops().

       This is usually one paragraph of text (surrounded by empty lines or
       document boundaries.) It may contain more than one paragraph, but this
       will be less efficient in iter_tab_stops().

       @ivar  line_count: the number of lines in the block.
       @itype line_count: int
    """
    @property
    def line_count(self):
        raise NotImplementedError

    def iter_lines(self, start_line_no, end_line_no):
        """Return all lines in the given range.

           Referenced line indices must be within the block.

           @param start_line_no: index of the first line to return (zero-based.)
           @type  start_line_no: int
           @param end_line_no: ending line index (exclusive, zero-based.)
           @type  end_line_no: int
           @return: an iterator of iterators of tab sizes, in view units.
           @rtype : iter(iter(any))
        """
        raise NotImplementedError

class ListTextBlock(object):
    """A text block backed by a list of lines and a text size function.
    """
    def __init__(self, lines, size_func=len):
        """Construct a new text block, backed by a list.

           @param lines: a list of lines of text.
           @type  lines: [[any (usually unicode)]]
           @param size_func: a function returning the size of a text, in view units.
           @type  size_func: any (usually float or int)
        """
        self.lines = lines
        self.size_func = size_func

    @property
    def line_count(self):
        return len(self.lines)

    def iter_lines(self, start, end):
        for line in self.lines[start:end]:
            # This yields a generator just to show we *can* do a single pass
            # over the text in iter_tab_stops().
            yield (self.size_func(text) for text in line)

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

def iter_tab_sizes(text_block, tab_stops, start_line_no=0, end_line_no=None, start_tab_sizes=None, end_tab_sizes=None):
    """Return the tab stops of the given text block.

       Optionally limited on the lines reported, and with hints of the sizes of
       surrounding lines. If you use start_line_no > 0 without setting
       start_tab_sizes, the function will have to start scanning from the first
       line, impeding performance.

       The same thing goes for end_tab_sizes.

       The return value, as well as start_tab_sizes and end_tab_sizes (where
       applicable) must not contain the last column. The last column does not
       matter for layouts, and are simply ignored by the current algorithm. As
       an example, the text (assuming space is tab)

           Hello world

       would cause this function to return

           [ 6 ]

       as there are two columns.

       @param text_block: the block of text to process.
       @type  text_block: TextBlock
       @param tab_stops: tab stop settings.
       @type  tab_stops: TabStops
       @param start_line_no: line number of the first line to return (zero based.)
                             Defaults to start of text block.
       @type  start_line_no: int
       @param end_line_no: endling line number (exclusive, zero-based.) Defaults
                           to end of text block.
       @type  end_line_no: int
       @param start_tab_sizes: a list of tab sizes the lines before start_line_no
                               need, or None for no hint.
       @type  start_tab_sizes: [any] or NoneType
       @param end_tab_sizes: a list of tab sizes the lines after the requested
                             lines need, or None for no hint.
       @type  end_tab_sizes: [any] or NoneType
       @return: an iterator of lists of tab sizes, with one value per line.
       @rtype : iter([any])
    """
    if end_line_no is None:
        # Default to all remaining lines.
        end_line_no = text_block.line_count

    if start_tab_sizes is None:
        # We have to start from the top of the block as we don't know the
        # columns above start_line_no.
        start = 0
        tab_sizes = [] # [(int, Length)]
        column_starts = [] # [int]
    else:
        # We know the tab sizes of the lines above, so we don't have to scan
        # them.
        assert start_line_no < text_block.line_count
        start = start_line_no
        tab_sizes = list(enumerate(start_tab_sizes)) # [(int, Length)]
        column_starts = range(len(tab_sizes)) # [int]

    if end_tab_sizes is None:
        # We have to scan to the end.
        end = text_block.line_count
    else:
        # We know how this thing ends.
        end = end_line_no

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
                tab_sizes.append((col, tab_size))
                column_starts.append(len(tab_sizes) - 1)
            else:
                # Update an old tab size.
                tab_sizes[column_starts[col]] = (col, max(tab_sizes[column_starts[col]][1], tab_size))

        return col + 1

    line_lengths = [] # [(int, int)]
    old_num_columns = 0

    # For each line, increase tab sizes as appropriate.
    for (line_no, line) in enumerate(text_block.iter_lines(start, end)):
        num_columns = append_tab_sizes(map(tab_stops.get_tab_size, _ignore_last(line)))
        del column_starts[num_columns:]

        if line_no == 0 or num_columns != old_num_columns:
            line_lengths.append((line_no, num_columns))

        old_num_columns = num_columns

    if end_tab_sizes is not None:
        # We have knowledge of trailing lines, incorporate that information.
        append_tab_sizes(end_tab_sizes)

    # Add the ending record to allow outputting the last group within the loop.
    line_lengths.append((end, 0))

    column_starts = []
    tab_sizes_index = 0
    old_line_no = 0

    # Iterate over groups of lines with the same lengths.
    for (group_line_no, line_len) in line_lengths:
        # Yield one value per line.
        for line_no in xrange(old_line_no, group_line_no):
            # Yield lines within the requested range.
            if start + line_no >= start_line_no and start + line_no < end_line_no:
                # Note that this should use the column settings from the last group.
                yield [tab_sizes[i][1] for i in column_starts]

        # Update column_starts.
        while len(column_starts) < line_len:
            assert tab_sizes[tab_sizes_index][0] == len(column_starts)
            column_starts.append(tab_sizes_index)
            tab_sizes_index += 1

        del column_starts[line_len:]

        old_line_no = group_line_no
