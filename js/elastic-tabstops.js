/*
 * A Javascript library for elastic tabstops.
 *
 * See http://nickgravgaard.com/elastictabstops/
 *
 * Copyright (c) 2012 Tommie Gannert
 * Distributed under the MIT license
 */
ElasticTabstops = new function() {
	var self = this

	function isDefined(value) {
		return typeof(value) != "undefined"
	}

	function getDefault(value, def) {
		if (isDefined(value))
			return value

		return def
	}

	function getLength(array) {
		return array.length
	}

	function map(func, array) {
		var len = array.length
		var ret = []

		for (var i = 0; i < len; ++i)
			ret.push(func(array[i]))

		return ret
	}

	function range(end) {
		var ret = []

		for (var i = 0; i < end; ++i)
			ret.push(i)

		return ret
	}

	function TabStops(options) {
		var self = this

		options = getDefault(options, {})
		this.options = options

		this.getTabSize = function(textLength) {
			var margin = getDefault(self.options.margin, 1)
			var minLength = getDefault(self.options.minLength, 1)
			var stepSize = getDefault(self.options.stepSize, 1)

			return margin + Math.max(
				Math.ceil(textLength / stepSize) * stepSize,
				minLength)
		}

		return this
	}

	function getTabSizes(lines, tabStops, options) {
		options = getDefault(options, {})
		var sizeFunc = getDefault(options.sizeFunc, getLength)
		var endTabSizes = getDefault(options.endTabSizes, [])
		var tabSizes = getDefault(options.startTabSizes, []).slice()
		var initialColumnStarts = range(tabSizes.length)

		function appendTabSizes(line) {
			for (var col = 0; col < line.length; ++col) {
				var tabSize = line[col]

				if (col >= columnStarts.length) {
					tabSizes.push(tabSize)
					columnStarts.push(tabSizes.length - 1)
				} else {
					tabSizes[columnStarts[col]] = Math.max(tabSizes[columnStarts[col]], tabSize)
				}
			}

			return col
		}

		var columnStarts = initialColumnStarts.slice()
		var lineLengths = []
		var oldNumColumns = -1

		for (var lineNo = 0; lineNo < lines.length; ++lineNo) {
			var line = lines[lineNo]
			var numColumns = appendTabSizes(map(
				tabStops.getTabSize, map(
					sizeFunc,
					line.slice(0, line.length - 1))))

			columnStarts.splice(numColumns, columnStarts.length - numColumns)

			if (numColumns != oldNumColumns)
				lineLengths.push([ lineNo, numColumns ])

			oldNumColumns = numColumns
		}

		appendTabSizes(endTabSizes)

		lineLengths.push([ lineNo, 0 ])

		var columnStarts = initialColumnStarts.slice()
		var tabSizesIndex = columnStarts.length
		var oldLineNo = 0
		var ret = []

		for (var li = 0; li < lineLengths.length; ++li) {
			var groupLineNo = lineLengths[li][0]
			var numColumns = lineLengths[li][1]

			for (var lineNo = oldLineNo; lineNo < groupLineNo; ++lineNo) {
				var cols = []

				for (var i = 0; i < columnStarts.length; ++i)
					cols.push(tabSizes[columnStarts[i]])

				ret.push(cols)
			}

			while (columnStarts.length < numColumns) {
				columnStarts.push(tabSizesIndex)
				tabSizesIndex++
			}

			columnStarts.splice(numColumns, columnStarts.length - numColumns)

			oldLineNo = groupLineNo
		}

		return ret
	}

	this.TabStops = TabStops
	this.getTabSizes = getTabSizes

	return this
}()
