// ETDemo - a demonstration of elastic tabstops
// last modified by Nick Gravgaard on 2008-10-02

package com.nickgravgaard.etdemo;

import com.nickgravgaard.elastictabstops.*;

import java.awt.*;
import javax.swing.*;
import javax.swing.text.AbstractDocument;
import javax.swing.text.StyledDocument;

public class ETDemo extends JApplet
{
	private static final long serialVersionUID = 20081005L;
	private static final int appWidth = 640;
	private static final int appHeight = 480;
	
	private JTextPane mTextPane = new JTextPane();

    private RootPaneContainer mRPC;

    // this contructor is used when we run as an applet
    public ETDemo()
    {
        mRPC = this;
    }

    // this contructor is used when we run as an application
    public ETDemo(JFrame frame)
    {
    	mRPC = frame;
    }
	
	public void init()
	{
		try
		{
			UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		}
		catch (Exception e) {}
		
		// layout main content panel
		JPanel panel = new JPanel();
		panel.setLayout(new BorderLayout());
		panel.add(new JScrollPane(mTextPane), BorderLayout.CENTER);

		mRPC.setContentPane(panel);
		this.setSize(appWidth, appHeight);
		
		mTextPane.setFont(new Font("Verdana", java.awt.Font.PLAIN, 11));
		StyledDocument styledDoc = mTextPane.getStyledDocument();
		AbstractDocument doc = (AbstractDocument)styledDoc;
		FontMetrics fm = mTextPane.getFontMetrics(mTextPane.getFont());
		doc.setDocumentFilter(new ElasticTabstopsDocFilter(fm));
		String initialText = ""
			+ "/* Hopefully this Java program should demonstrate how elastic tabstops work.\t*/\n"
			+ "/* Try inserting and deleting different parts of the text and watch as the tabstops move.\t*/\n"
			+ "/* If you like this, please ask the writers of your text editor to implement it.\t*/\n"
			+ "\n"
			+ "#include <stdio.h>\n"
			+ "\n"
			+ "struct ipc_perm\n"
			+ "{\n"
			+ "\tkey_t\tkey;\n"
			+ "\tushort\tuid;\t/* owner euid and egid\t*/\n"
			+ "\tushort\tgid;\t/* group id\t*/\n"
			+ "\tushort\tcuid;\t/* creator euid and egid\t*/\n"
			+ "\tcell-missing\t\t/* for test purposes\t*/\n"
			+ "\tushort\tmode;\t/* access modes\t*/\n"
			+ "\tushort\tseq;\t/* sequence number\t*/\n"
			+ "};\n"
			+ "\n"
			+ "int someDemoCode(\tint fred,\n"
			+ "\tint wilma)\n"
			+ "{\n"
			+ "\tx();\t/* try making\t*/\n"
			+ "\tprintf(\"hello!\\n\");\t/* this comment\t*/\n"
			+ "\tdoSomethingComplicated();\t/* a bit longer\t*/\n"
			+ "\tfor (i = start; i < end; ++i)\n"
			+ "\t{\n"
			+ "\t\tif (isPrime(i))\n"
			+ "\t\t{\n"
			+ "\t\t\t++numPrimes;\n"
			+ "\t\t}\n"
			+ "\t}\n"
			+ "\treturn numPrimes;\n"
			+ "}\n"
			+ "\n"
			+ "---- and now for something completely different: a table ----\n"
			+ "\n"
			+ "Title\tAuthor\tPublisher\tYear\n"
			+ "Generation X\tDouglas Coupland\tAbacus\t1995\n"
			+ "Informagic\tJean-Pierre Petit\tJohn Murray Ltd\t1982\n"
			+ "The Cyberiad\tStanislaw Lem\tHarcourt Publishers Ltd\t1985\n"
			+ "The Selfish Gene\tRichard Dawkins\tOxford University Press\t2006\n"
			+ "";
		
		mTextPane.setText(initialText);
	}
	
	public static void main(String[] args)
	{
		JFrame frame = new JFrame();
		final ETDemo app = new ETDemo(frame);

		app.init();

		frame.setTitle("Elastic tabstops demo");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.setSize(appWidth, appHeight);
		frame.setVisible(true);

		app.start();
	}
}
