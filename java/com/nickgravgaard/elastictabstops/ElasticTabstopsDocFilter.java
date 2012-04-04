// ElasticTabstopsDocFilter - a document filter that implements elastic tabstops
// This code is public domain so feel free to use it in any way you see fit
// You don't have to but it would be nice if you sent me any improvements you make
// see http://nickgravgaard.com/elastictabstops/
// last modified by Nick Gravgaard on 2006-07-09

package com.nickgravgaard.elastictabstops;

import java.awt.FontMetrics;
import javax.swing.text.*;

public class ElasticTabstopsDocFilter extends DocumentFilter
{
	FontMetrics m_fm;

	/*
	// tabstops are multiples of 32 pixels plus 8 pixels of padding
	int m_tabMultiples = 32; // must be greater than 0
	int m_tabMinimum = 0;
	int m_tabPadding = 8;
	*/

	// tabstops are at least 32 pixels plus 8 pixels of padding
	int m_tabMultiples = 1; // must be greater than 0
	int m_tabMinimum = 32;
	int m_tabPadding = 8;

	public ElasticTabstopsDocFilter()
	{
	}

	public ElasticTabstopsDocFilter(FontMetrics fm)
	{
		m_fm = fm;
	}

	public void insertString(FilterBypass fb, int offs, String str, AttributeSet a) throws BadLocationException
	{
		super.insertString(fb, offs, str, a);
		StyledDocument doc = (StyledDocument)fb.getDocument();
		stretchTabstops(doc);
	}

	public void remove(FilterBypass fb, int offs, int length) throws BadLocationException
	{
		super.remove(fb, offs, length);
		StyledDocument doc = (StyledDocument)fb.getDocument();
		stretchTabstops(doc);
	}

	public void replace(FilterBypass fb, int offs, int length, String str, AttributeSet a) throws BadLocationException
	{
		super.replace(fb, offs, length, str, a);
		StyledDocument doc = (StyledDocument)fb.getDocument();
		stretchTabstops(doc);
	}

	// todo: needs optimising - a lot of this should be cached if possible
	void stretchTabstops(StyledDocument doc)
	{
		Element section = doc.getDefaultRootElement();

		int maxTabstops = 32; // todo: magic number hardcoded
		int lineCount = section.getElementCount();
		ETLine lines[] = new ETLine[lineCount];
		ETTabstop grid[][] = new ETTabstop[lineCount][maxTabstops];

		// initialise array
		for (int l = 0; l < lineCount; l++) // for each line
		{
			lines[l] = new ETLine();
			for (int t = 0; t < maxTabstops; t++) // for each column
			{
				grid[l][t] = new ETTabstop();
			}
		}

		// get width of text in cells
		for (int l = 0; l < lineCount; l++) // for each line
		{
			Element line = section.getElement(l);
			int lineStart = line.getStartOffset();
			int lineEnd = line.getEndOffset();
			lines[l].startPos = lineStart;
			lines[l].endPos = lineEnd;
			try
			{
				String lineText = doc.getText(lineStart, lineEnd - lineStart);
				int textWidthInTab = 0;
				int currentTabNum = 0;
				int lineLength = lineText.length();
				for (int c = 0; c < lineLength; c++) // for each char in current line
				{
					char currentChar = lineText.charAt(c);
					if (currentChar == '\n')
					{
						grid[l][currentTabNum].endsInTab = false;
						grid[l][currentTabNum].endPos = lineStart + c;
						textWidthInTab = 0;
					}
					else if (currentChar == '\t')
					{
						grid[l][currentTabNum].endsInTab = true;
						grid[l][currentTabNum].endPos = lineStart + c;
						grid[l][currentTabNum].textWidthPix = calcTabWidth(textWidthInTab);
						currentTabNum++;
						grid[l][currentTabNum].startPos = lineStart + c + 1;
						lines[l].numTabs++;
						textWidthInTab = 0;
					}
					else
					{
						textWidthInTab += m_fm.charWidth(currentChar);
					}
				}
			}
			catch (BadLocationException ex)
			{
			}
		}

		// find columns blocks and stretch to fit the widest cell
		for (int t = 0; t < maxTabstops; t++) // for each column
		{
			// all tabstops in column block point to same number
			MutableInteger theWidestWidthPix = new MutableInteger(0); // reference
			int maxWidth = 0;
			for (int l = 0; l < lineCount; l++) // for each line
			{
				if (grid[l][t].endsInTab)
				{
					grid[l][t].widestWidthPix = theWidestWidthPix; // copy ref
					if (grid[l][t].textWidthPix < maxWidth)
					{
						grid[l][t].textWidthPix = maxWidth;
					}
					else
					{
						maxWidth = grid[l][t].textWidthPix;
						theWidestWidthPix.val = maxWidth;
					}
				}
				else // end column block
				{
					theWidestWidthPix = new MutableInteger(0); // reference
					maxWidth = 0;
				}
			}
		}

		// apply tabstop sizes to the text
		for (int l = 0; l < lineCount; l++) // for each line
		{
			// accumulate tabstop widths
			int accTabstop = 0;
			for (int t = 0; t < lines[l].numTabs; t++)
			{
				accTabstop += grid[l][t].widestWidthPix.val;
				grid[l][t].textWidthPix = accTabstop;
			}

			Element line = section.getElement(l);
			int lineStart = line.getStartOffset();
			int lineEnd = line.getEndOffset();
			setBlocksTabstops(doc, lineStart, lineEnd, grid[l], lines[l].numTabs);
		}
	}

	int calcTabWidth(int textWidthInTab)
	{
		textWidthInTab = (((int)(textWidthInTab / m_tabMultiples)) + 1) * m_tabMultiples;
		if (textWidthInTab < m_tabMinimum)
		{
			textWidthInTab = m_tabMinimum;
		}
		textWidthInTab += m_tabPadding;
		return textWidthInTab;
	}

	void setBlocksTabstops(StyledDocument doc, int start, int length, ETTabstop[] tabstopPositions, int tabstopCount)
	{
		TabStop[] tabs = new TabStop[tabstopCount];
 
		for (int j = 0; j < tabstopCount; j++)
		{
			tabs[j] = new TabStop(tabstopPositions[j].textWidthPix);
		}

		TabSet tabSet = new TabSet(tabs);
		SimpleAttributeSet attributes = new SimpleAttributeSet();
		StyleConstants.setTabSet(attributes, tabSet);

		doc.setParagraphAttributes(start, length, attributes, false);
	}

}
