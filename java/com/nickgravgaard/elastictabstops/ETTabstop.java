package com.nickgravgaard.elastictabstops;

public class ETTabstop
{
	int textWidthPix;
	MutableInteger widestWidthPix = null; // object so we can use refs
	int startPos = 0;
	int endPos = 0;
	boolean endsInTab = false;

	public ETTabstop()
	{
	}
}
