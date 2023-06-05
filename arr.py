# TODO:

# self.history should be class(if need mutable attrs) or named tuple
# from flags to states if possible
# check if manually insert invalid url


## tab to optionmenu ,space to open, up down move, return select
## n = self.nametowidget(self.optionmenu.menuname)
## n.invoke(n.index('active'))

# from standard library
import urllib.request
import html.parser
import webbrowser
import pathlib
import json
import re

import tkinter.scrolledtext
import tkinter.font
import tkinter

# from requirements
import html2text

# from current directory
import changefont
import changecolor
import rssfeed

# Main-class is Browser and it is last at the bottom
#####################################################

# Constants used in Browser-class:

ICONPATH = r'./icons/rssicon.png'
CONFPATH = r'./rss.cnf'
RSSLINKS = r'./sources.txt'
IGNORES  = r'./ignored_lines.txt'
HELPTEXT = '''
  left: Previous page
  j:	Search title from page
  n:	Clear search
  Esc:	Close help / Close edit-sources / Iconify window
	
  ctrl-period:	increase titlepage tabstop
  ctrl-comma:	decrease titlepage tabstop
  ctrl-plus: 	increase scrollbar width
  ctrl-minus:	decrease scrollbar width
	
  ctrl-p:	Font chooser
  ctrl-s:	Color chooser
  ctrl-W:	Save configuration
  Alt-i:	Edit ignored lines

  ctrl-mouseleft: Open link in default browser

  At bottom-pane, when clicked address with mouse-right: copy link
	
  When editing sources, leave an empty line after last line and then
  write name for the feed to be in the dropdown-menu and then add
  URL-address of the RSS-feed to next line.'''
		

class MyHTMLParser(html.parser.HTMLParser):
	'''	Parse URL-links in HTML-page.
		
		Every link-name and link-address is saved in a tuple.
		Tuples are stored in a list: self.addresses. These tuples
		are used in Browser-class: in make_page() and in tag_link()
		to make hyper-links for tkinter Text-widget.
		
		Certain types of links are ignored to shorten the list.
	'''
	
	
	def __init__(self):
		super().__init__()
		self.flag = False
		self.ignore = [
						'#',
						'(',
						')',
						';',
						'facebook',
						'play.google',
						'apps.apple',
						'instagram',
						'linkedin',
						'twitter',
						'whatsapp',
						'mailto:?'
					]
		self.address = ""
		self.linkname = ""
		self.addresses = list()
		self.domain = ""
	
	
	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for item in attrs:
				if item[0] == "href":
					tmp = item[1]
					
					if self.chk_ignores(tmp): break

					if self.domain not in tmp:
						
						# is it an internal link:
						if "http" not in tmp:
							# from this:
							#'spam?ref=nav/page/page2'
							# to this:
							#'page/page2'
							tmp = re.sub('[^/]*/', '', tmp, 1)
							# and then add domain
							tmp = self.domain + '/' + tmp
							
						# no, it was not internal:
						#'http://anotherdomain.com/spam?ref=nav/page/page2'
						# so do nothing:
						else:
							pass
					else:
						# it is full URL, including current domain,
						# so do nothing:
						pass

					self.address = tmp
					self.flag = True
					break
	

	def chk_ignores(self, spam):
		for item in self.ignore:
			if item in spam:
				return True
		return False


	def handle_data(self, data):
		if self.flag:
			self.linkname = data
			
			
	def handle_endtag(self, tag):
		if tag == 'a' and self.flag:
			self.linkname = " ".join(self.linkname.split())
			self.addresses.append((self.linkname, self.address))
			self.flag = False


class Browser(tkinter.Toplevel):
	'''	RSS-browser made with tkinter PanedWindow and ScrolledText -widgets
		to name a few. To run it:
		
		import arr
		from tkinter import Tk
		root=Tk().withdraw()
		u=arr.Browser(root)

	'''

	def __init__(self, root, url=None):
		super().__init__(root, class_='ARR')
		self.top = root
		self.protocol("WM_DELETE_WINDOW", self.quit_me)
		self.user_agent = "https://github.com/SamuelKos/ARR"
		self.history = []
		self.input = url
		self.flag_back = False
		self.flag_rss = False
		self.state = None
		self.helptxt = HELPTEXT
		self.title('ARR')
		self.fgcolor = '#D3D7CF'
		self.bgcolor ='#000000'
		self.pos = '1.0'
		
		try:
			with open( IGNORES, 'r', encoding='utf-8' ) as f:
				self.ignored_lines = f.read().splitlines()
				
		except EnvironmentError as e:
			print( e.__str__() )
			print( '\n Could not open file %s' % IGNORES )
		
			self.ignored_lines = [
					'Facebook',
					'Twitter',
					'SiteWide ContentPlaceholder',
					'Wide ContentPlaceholder',
					'Main ContentPlaceholder'
					]
		
			
		self.fontname = None
		self.goodfonts = [
					'Noto Mono',
					'Bitstream Vera Sans Mono',
					'Liberation Mono',
					'Inconsolata'
					]
					
		fontfamilies = [ f for f in tkinter.font.families() ]

		for fontname in self.goodfonts:
			if fontname in fontfamilies:
				self.fontname = fontname
				break
		
		if self.fontname == None:
			self.font1 = tkinter.font.Font(family='TkDefaulFont', size=12)
			self.font2 = tkinter.font.Font(family='TkDefaulFont', size=10)
		
		else:
			self.font1 = tkinter.font.Font(family=self.fontname, size=12)
			self.font2 = tkinter.font.Font(family=self.fontname, size=10)
		
		
		if ICONPATH:
			try:
				self.icon = tkinter.Image("photo", file=ICONPATH)
				self.tk.call('wm','iconphoto', self._w, self.icon)
			except tkinter.TclError as e:
				print(e)
		
		self.rsslinks = RSSLINKS
		self.u = rssfeed.RssFeed(RSSLINKS)
		self.sources = list(self.u._sources.keys())
		
		########### Layout Begin ############################################
		self.framtop = tkinter.Frame(self)
		self.framtop.pack(side=tkinter.TOP, fill=tkinter.X)
		self.frambottom = tkinter.Frame(self)
		self.frambottom.pack(side=tkinter.TOP, fill=tkinter.BOTH)
		
		self.entry = tkinter.Entry(self.framtop, font=self.font2)
		self.entry.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)
		
		self.btn_open=tkinter.Button(self.framtop, font=self.font2, text='Open', command=self.make_titlepage)
		self.btn_open.pack(side=tkinter.LEFT)
		
		self.var = tkinter.StringVar()
		self.var.set(self.sources[0])
		self.optionmenu = tkinter.OptionMenu(self.framtop, self.var, *self.sources, command=self.make_titlepage)
		
		# set font of dropdown button:
		self.optionmenu.config(font=self.font2, takefocus=1)
		
		# set font of dropdown items:
		menu = self.nametowidget(self.optionmenu.menuname)
		menu.config(font=self.font2)
		
		self.optionmenu.pack(side=tkinter.LEFT)

		self.pane = tkinter.PanedWindow(self.frambottom, bg='grey', sashpad=1, orient=tkinter.VERTICAL)
		self.pane.pack(fill=tkinter.BOTH, expand=True)
 
		self.fram1 = tkinter.Frame(self.pane)
		self.fram2 = tkinter.Frame(self.pane)
		self.pane.add(self.fram1)
		self.pane.add(self.fram2)

		self.text1 = tkinter.scrolledtext.ScrolledText(self.fram1,
			font=self.font1, tabstyle='wordprocessor', background=self.bgcolor,
			foreground=self.fgcolor, insertbackground=self.fgcolor,
			blockcursor=True)
		
		self.text2 = tkinter.scrolledtext.ScrolledText(self.fram2,
			font=self.font2, background=self.bgcolor, foreground=self.fgcolor)
		
		self.elementborderwidth = 4
		self.scrollbar_width = 30
		self.first_tabstop = 2

		self.text1.vbar.config(elementborderwidth=self.elementborderwidth)
		self.text2.vbar.config(elementborderwidth=self.elementborderwidth)
		self.text1.vbar.config(width=self.scrollbar_width)
		self.text2.vbar.config(width=self.scrollbar_width)
		self.titletabs=(f'{self.first_tabstop}c', )
		self.lmarg2=f'{self.first_tabstop}c'

		self.text1.config(state='disabled')
		self.text2.config(state='disabled')
		
		# Because texts are disabled, we must make next lambda to
		# be able copy text from them with ctrl-c:
		self.text1.bind("<1>",		lambda event: self.text1.focus_set())
		self.text1.bind("<j>", self.search_next)
		self.text1.bind("<n>", self.clear_search)
		# to be able to scroll with arrow-keys in disabled text-widget:
		self.text1.bind("<Up>",   self.arrow_up_override)
		self.text1.bind("<Down>", self.arrow_down_override)
		self.text1.bind("<space>", self.space_override)
		self.text2.bind("<Enter>",	self.enter_text2)
		self.text2.bind("<Leave>",	self.leave_text2)
		self.text1.pack(side=tkinter.BOTTOM,  expand=True, fill=tkinter.BOTH)
		self.text2.pack(side=tkinter.BOTTOM,  expand=True, fill=tkinter.BOTH)
				
		# links in text2 are parsed with:
		self.parser = MyHTMLParser()
		# page in text1 is parsed with:
		self.h = html2text.HTML2Text()
		self.h.ignore_links = True
		self.h.ignore_images = True
		
		self.bind("<Control-s>",		self.color_choose)
		self.bind("<Alt-i>",			self.edit_ignored_lines)
		self.bind("<Control-p>",		self.font_choose)
		self.bind("<Control-W>",		self.save_config)
		self.bind("<Escape>",			lambda e: self.iconify())
		self.bind("<Return>",			lambda a: self.make_page())
		self.bind("<Left>",				lambda event: self.back_hist(event))
		self.bind("<Control-comma>",	self.decrease_tabstop_width)
		self.bind("<Control-period>",	self.increase_tabstop_width)
		self.bind("<Control-plus>",		self.increase_scrollbar_width)
		self.bind("<Control-minus>",	self.decrease_scrollbar_width)
		self.bind("<Button-3>",			lambda event: self.raise_popup(event))
		
		self.popup_whohasfocus = None
		self.popup = tkinter.Menu(self, font=self.font2, tearoff=0)
		self.popup.bind("<FocusOut>", self.popup_focusOut)
		# so that popup would go away when clicked somewhere else
		
		self.popup.add_command(label=" editsources", command=self.editsources)
		self.popup.add_command(label=" choose font", command=self.font_choose)
		self.popup.add_command(label="        help", command=self.help)
		
		# Try to apply saved configurations:
		try:
			f = open(CONFPATH)
		except FileNotFoundError: pass
		except OSError as e:
			print(e.__str__())
			print('\nCould not load configuration file %s' % CONFPATH)
		else:
			self.load_config(f)
			f.close()
		
		
		self.text1.focus_set()
			
		if self.input:
			self.make_page(self.input)
		######## Init End ###############################################

	
	def space_override(self, event=None):
		
		if self.state  in [ 'page', 'title' ]:
			
			self.text1.yview_scroll(21, tkinter.UNITS)
			return 'break'
			
		else:
			return

			
	def arrow_up_override(self, event=None):
	
		if self.state in [ 'page', 'title' ]:
			self.text1.yview_scroll(-1, tkinter.UNITS)
			return 'break'
		else:
			return
			

	def arrow_down_override(self, event=None):

		if self.state  in [ 'page', 'title' ]:
			self.text1.yview_scroll(1, tkinter.UNITS)
			return 'break'
		else:
			return

			
	def clear_search(self, event=None):
		''' Remove highlighting of search. Shortcut: n
		'''
		if self.state == 'page':
			self.text1.tag_remove('sel', '1.0', tkinter.END)
			return 'break'
		else:
			return
	
	
	def search_next(self, event=None):
		''' Search and highlight next occurence of title. Shortcut: j
		'''
		if self.state != 'page':
			return
			
		if self.history[-1][2]:
			if self.pos != '1.0':
				pos = "%s + 1c" % self.pos
			else:
				pos = self.pos
			
			wordlen = len(self.history[-1][2])
			pattern = self.history[-1][2]
			
			pos = self.text1.search(pattern, pos, tkinter.END)
			
			# Try again from the beginning this time:
			if not pos:
				pos = self.text1.search(pattern, '1.0', tkinter.END)

				if not pos:
					self.pos = '1.0'
					return "break"
			
			if pos:
				self.text1.tag_remove('sel', '1.0', tkinter.END)
				self.pos = pos
				self.text1.see(pos)
				lastpos = "%s + %dc" % (pos, wordlen)
				self.text1.tag_add('sel', pos, lastpos)
				
				return "break"
				
		else:
			return "break"


	def save_config(self, event=None):
		try:
			f = open(CONFPATH, 'w', encoding='utf-8')
		except OSError as e:
			print(e.__str__())
			print('\nCould not save configuration')
		else:
			data = dict()
			data['fgcolor'] = self.text1.cget('foreground')
			data['bgcolor'] = self.text1.cget('background')
			data['font1'] = self.font1.config()
			data['font2'] = self.font2.config()
			data['scrollbar_width'] = self.scrollbar_width
			data['elementborderwidth'] = self.elementborderwidth
			integer, decimal = str(float(self.first_tabstop)).split('.')
			decimal = decimal[0]
			data['first_tabstop_integer'] = integer
			data['first_tabstop_decimal'] = decimal
	
			string_representation = json.dumps(data)
			f.write(string_representation)
			f.close()
			self.title('Configuration saved')

			
	def load_config(self, fileobject):
		string_representation = fileobject.read()
		data = json.loads(string_representation)
		
		self.fgcolor = data['fgcolor']
		self.bgcolor = data['bgcolor']
		
		fontfamilies = [f for f in tkinter.font.families()]
		font = data['font1']['family']
		
		if font not in fontfamilies:
			print(f'Font {font.upper()} does not exist.')
		
		else:
			self.font1.config(**data['font1'])
			self.font2.config(**data['font2'])
		
		self.scrollbar_width 	= data['scrollbar_width']
		self.elementborderwidth	= data['elementborderwidth']
		
		self.text1.vbar.config(width=self.scrollbar_width)
		self.text2.vbar.config(width=self.scrollbar_width)
		self.text1.vbar.config(elementborderwidth=self.elementborderwidth)
		self.text2.vbar.config(elementborderwidth=self.elementborderwidth)
		
		integer = data['first_tabstop_integer']
		decimal = data['first_tabstop_decimal']
		tmp = integer +'.'+ decimal
		self.first_tabstop = float(tmp)
		
		self.titletabs = (f'{self.first_tabstop}c', )
		self.lmarg2 = f'{self.first_tabstop}c'
		
		self.text1.tag_config('indent_tag', lmargin2=self.lmarg2,
			tabs=self.titletabs)
		self.text1.config(background=self.bgcolor, foreground=self.fgcolor,
			insertbackground=self.fgcolor)
		self.text2.config(background=self.bgcolor, foreground=self.fgcolor,
			insertbackground=self.fgcolor)
			
		
	def enter(self, tagname, event=None):
		''' When mousecursor enters hyperlink tagname.
		'''
		if self.flag_rss:
			self.text1.config(cursor="hand2")
		else:
			self.text2.tag_config(tagname, underline=1)


	def leave(self, tagname, event=None):
		''' When mousecursor leaves hyperlink tagname.
		'''
		if self.flag_rss:
			self.text1.config(cursor="")
		else:
			self.text2.tag_config(tagname, underline=0)
		

	def lclick(self, event=None):
		'''	When hyperlink tagname is clicked.
		'''
		self.tag_link(event)
		
	
	def rclick(self, event=None):
		'''	When hyperlink in text2 is clicked with mouse right.
		'''
		i = int(self.text2.tag_names(tkinter.CURRENT)[0].split("-")[1])
		addr = self.parser.addresses[i][1]
		
		self.clipboard_clear()
		self.clipboard_append(addr)

	
	def increase_tabstop_width(self, event=None):
		'''	Increase width of first tabstop in titlepage.
			Shortcut: Ctrl-period
		'''
		if not self.flag_rss:
			self.bell()
			return 'break'
		
		if self.first_tabstop >= 10:
			self.bell()
			return 'break'
			
		self.first_tabstop += 0.2
		
		self.titletabs = (f'{self.first_tabstop}c', )
		self.lmarg2 = f'{self.first_tabstop}c'
		
		self.text1.tag_config('indent_tag', lmargin2=self.lmarg2,
			tabs=self.titletabs)
		
		return 'break'


	def decrease_tabstop_width(self, event=None):
		'''	Increase width of first tabstop in titlepage.
			Shortcut: Ctrl-comma
		'''
		if not self.flag_rss:
			self.bell()
			return 'break'
		
		if self.first_tabstop <= 1:
			self.bell()
			return 'break'
			
		self.first_tabstop -= 0.2
		
		self.titletabs = (f'{self.first_tabstop}c', )
		self.lmarg2 = f'{self.first_tabstop}c'
		
		self.text1.tag_config('indent_tag', lmargin2=self.lmarg2,
			tabs=self.titletabs)
		
		return 'break'
		
	
	def increase_scrollbar_width(self, event=None):
		'''	Change width of scrollbars.
			Shortcut: Ctrl-plus
		'''
		if self.scrollbar_width >= 100:
			self.bell()
			return 'break'
			
		self.scrollbar_width += 7
		self.elementborderwidth += 1
		
		self.text1.vbar.config(width=self.scrollbar_width)
		self.text2.vbar.config(width=self.scrollbar_width)
		self.text1.vbar.config(elementborderwidth=self.elementborderwidth)
		self.text2.vbar.config(elementborderwidth=self.elementborderwidth)
	
		return 'break'
		
		
	def decrease_scrollbar_width(self, event=None):
		'''	Change width of scrollbars.
			Shortcut: Ctrl-minus
		'''
		if self.scrollbar_width <= 0:
			self.bell()
			return 'break'
			
		self.scrollbar_width -= 7
		self.elementborderwidth -= 1
		
		self.text1.vbar.config(width=self.scrollbar_width)
		self.text2.vbar.config(width=self.scrollbar_width)
		self.text1.vbar.config(elementborderwidth=self.elementborderwidth)
		self.text2.vbar.config(elementborderwidth=self.elementborderwidth)
			
		return 'break'
		
		
	def font_choose(self, event=None):
		self.choose = changefont.FontChooser([self.font1, self.font2])
			
		return 'break'
		
	
	def color_choose(self, event=None):
		self.color = changecolor.ColorChooser([self.text1, self.text2])
		return 'break'
		
		
########### Edit ignores begin

	def edit_ignored_lines(self, event=None):
		labeltext = \
'''If feed contains disruptive lines, like 'Share', 'Comment' etc.
which consumes display-space and your time scrolling through this spam
copy those lines here below. You can copy many lines at once
if there is for example a social media block, just copy whole block and
paste here, empty lines does not matter. Lines are treated separately
so copying a block of lines ignores all those lines also separately.'''

		tmptop = tkinter.Toplevel()#self.top)
		tmptop.title('Edit ignored lines')
		
		self.ignored_lines.sort()
		ignores = '\n'.join(self.ignored_lines)
		
		tmptop.btnsave = tkinter.Button(tmptop, text='Save', font=self.font2)
		tmptop.btnsave.pack(padx=10, pady=10)
		
		tmptop.labelhelp = tkinter.Label(tmptop, text=labeltext, font=self.font2, justify=tkinter.LEFT)
		tmptop.labelhelp.pack(padx=10)
		
		tmptop.text = tkinter.scrolledtext.ScrolledText(tmptop, font=self.font1, background=self.bgcolor,
			foreground=self.fgcolor, insertbackground=self.fgcolor, blockcursor=True, wrap=tkinter.NONE)
		
		tmptop.text.pack(padx=10, pady=10)
		
		tmptop.text.vbar.config( elementborderwidth = self.elementborderwidth )
		tmptop.text.vbar.config( elementborderwidth = self.elementborderwidth )
		tmptop.text.vbar.config( width = self.scrollbar_width )
		tmptop.text.vbar.config( width = self.scrollbar_width )
		
		tmptop.text.insert('1.0', ignores)
		
		tmptop.btnsave.config(command=lambda args=[tmptop]: self.save_ignored_lines(args))
		
		return 'break'
		
	
	def save_ignored_lines(self, args, event=None):
		parent = args[0]
		tmp = parent.text.get('1.0', tkinter.END).splitlines()
		
		self.ignored_lines = [ line.strip() for line in tmp if len(line.strip()) > 0 ]
		# remove duplicates
		s = set(self.ignored_lines)
		self.ignored_lines = [ line for line in s ]
		
		ignores = '\n'.join(self.ignored_lines)
		
		try:
			with open( IGNORES, 'w', encoding='utf-8' ) as f:
				f.write(ignores)
				
		except EnvironmentError as e:
			print(e.__str__())
			print('\n Could not save file %s' % './ignored_lines.txt')
		
		parent.destroy()
			
########### Edit ignores End
		
	def raise_popup(self, event, *args):
		self.popup_whohasfocus = event.widget
		self.popup.post(event.x_root, event.y_root)
		self.popup.focus_set()
		# needed to remove popup when clicked somewhere else
		
		
	def popup_focusOut(self, event=None):
		self.popup.unpost()
		
		
	def rebind(self, event=None):
		return 'break'
		
		
	def make_titlepage(self, event=None):
		'''	Fetch selected feed with rssfeed (titles and links).
			Then make title-page with hyperlinks.
		'''
		self.state = 'title'
		source = self.var.get()
		
		if not self.flag_back:
			self.history.append(('titlepage', source))
		else:
			source = self.history[-1][1]
			self.flag_back = False
		
		self.title('Loading..')
		self.update_idletasks()
		self.wipe()
		
		try:
			self.u.select_source(source)
			 
		except (OSError, ValueError) as err:
			s  = 'Something went wrong:\n\n%s' % err.__str__()
			self.text1.insert(tkinter.END, s)
			self.flag_rss = True
			self.text1.config(state='disabled')
			self.text2.config(state='disabled')
			self.title(source.upper() + ': %d' % len(self.history))
			self.update_idletasks()
			raise
			
		t = self.u._title_of_feed
		self.title( f'{t}: {len(self.history)}' )
		count = len(self.u._titles)
		self.flag_rss = True
		
		for tag in self.text1.tag_names():
				if 'hyper' in tag:
					self.text1.tag_delete(tag)
	
		for i in range(count):
			tmp = ''
			title = self.u._titles[i]
			addr = self.u._links[i]
			self.parser.addresses.append((addr, addr))
			tagname = "hyper-%s" % i
			self.text1.tag_config(tagname, underline=1)
			
			self.text1.tag_bind(tagname, "<ButtonRelease-1>",
					lambda event: self.lclick(event))
				
			self.text1.tag_bind(tagname, "<Control-ButtonRelease-1>",
					lambda event: self.lclick(event))
			
			self.text1.tag_bind(tagname, "<Enter>",
				lambda event, arg=tagname: self.enter(arg, event))
			
			self.text1.tag_bind(tagname, "<Leave>",
				lambda event, arg=tagname: self.leave(arg, event))
			
			self.text1.insert(tkinter.INSERT, str(i+1), tagname)
			tmp += ':\t%s' % title
			tmp += '\n\n'
			self.text1.insert(tkinter.END, tmp)
		
		# set indentation of titles:
		self.text1.tag_add('indent_tag', '1.0', tkinter.END)
		
		self.text1.tag_config('indent_tag', lmargin2=self.lmarg2, wrap='word', tabs=self.titletabs)
		# not sure if this is necessary:
		self.text1.tag_lower('indent_tag')
		
		self.text1.focus_set()
		self.text1.config(state='disabled')
		self.text2.config(state='disabled')
		
		
	def stop_editsources(self, event=None):
		self.wipe()
		
		self.bind("<Return>", lambda a: self.make_page())
		self.bind("<Escape>", lambda e: self.iconify())
		self.bind("<Left>", lambda event: self.back_hist(event))
		
		self.btn_open.config(text='Open', command=self.make_titlepage)
		
		self.optionmenu = tkinter.OptionMenu(self.framtop, self.var, *self.sources, command=self.make_titlepage)
		self.optionmenu.config(font=self.font2)
		menu = self.nametowidget(self.optionmenu.menuname)
		menu.config(font=self.font2)
		self.optionmenu.pack(side=tkinter.LEFT)
		
		self.entry.config(state='normal')
		
		# Parse history for removed feeds:
		for i,item in enumerate(self.history):
			if item[0] == 'titlepage' and item[1] not in self.sources:
				_ = self.history.pop(i)
		
		self.back_hist(flag_help=True)
		
		if event != None:
			return 'break'
		
		
	def save_sources(self):
		tmp = self.text1.get('1.0', tkinter.END).splitlines()
		names = list()
		addresses = list()

		for line in tmp:
			if 'http' in line:
				addresses.append(line.strip())
			else:
				if len(line.strip()) > 0:
					names.append(line.strip())
		
		data = dict()
		
		if len(names) == len(addresses) and len(names) != 0:
			for i in range(len(names)):
				data[names[i]] = addresses[i]

			#save data with rssfeed.save() into sources.txt
			self.u._save(RSSLINKS, data)
			self.u = rssfeed.RssFeed(RSSLINKS)
			self.sources = list(self.u._sources.keys())
			self.var.set(self.sources[0])
			self.stop_editsources()
			
				
	def editsources(self):
		self.state = 'edit'
		self.wipe()
		self.entry.config(state='disabled')
		self.optionmenu.destroy()
		self.btn_open.config(text='Save', command=self.save_sources)
		self.bind("<Return>", lambda e: self.rebind())
		self.bind("<Left>", lambda e: self.rebind())
		self.bind("<Escape>", self.stop_editsources)
		
		for name in self.u._sources:
			addr = self.u._sources[name]
			self.text1.insert(tkinter.INSERT, '%s\n%s\n\n' % (name, addr))

				
	def stop_help(self, event=None):
		self.bind("<Escape>", lambda e: self.iconify())
		self.entry.config(state='normal')
		self.back_hist(flag_help=True)
		
		if event != None:
			return 'break'

	
	def help(self):
		self.state = 'help'
		self.wipe()
		self.text1.insert(tkinter.INSERT, self.helptxt)
		self.text1.config(state='disabled')
		self.text2.config(state='disabled')
		self.entry.config(state='disabled')
		self.bind("<Escape>", self.stop_help)
		

	def back_hist(self, event=None, flag_help=False):
	
		if event != None:
			if 'entry' in str(event.widget).split('.')[-1]:
				return
		
		self.flag_back = True
		
		if flag_help and len(self.history) > 0:
			self.wipe()
			
			if self.history[-1][0] == 'titlepage':
				self.make_titlepage(self.history[-1][1])
			else:
				self.make_page(self.history[-1][1])
				
		elif len(self.history) > 1:
			self.history = self.history[:-1]
			self.wipe()
			
			if self.history[-1][0] == 'titlepage':
				self.make_titlepage(self.history[-1][1])
			else:
				self.make_page(link=self.history[-1][1])
		else:
			self.bell()
			self.flag_back = False


	def enter_text2(self, event):
		self.text2.config(cursor="hand2")
		self.bind("<Button-3>", lambda e: self.rebind())


	def leave_text2(self, event):
		self.text2.config(cursor="")
		self.bind("<Button-3>", lambda event: self.raise_popup(event))
	

	def wipe(self):
		self.entry.delete(0,tkinter.END)
		self.parser.addresses.clear()
		self.text1.config(state='normal')
		self.text2.config(state='normal')
		self.text1.delete(1.0, tkinter.END)
		self.text2.delete(1.0, tkinter.END)
		
		for tag in self.text2.tag_names():
			self.text2.tag_delete(tag)
		for tag in self.text1.tag_names():
			self.text1.tag_delete(tag)
			
		
	def tag_link(self, event):
		
		if self.flag_rss:
			i = int(self.text1.tag_names(tkinter.CURRENT)[1].split("-")[1])
		else:
			i = int(self.text2.tag_names(tkinter.CURRENT)[0].split("-")[1])
			
		addr = self.parser.addresses[i][1]
		
		# control-touchpad-left in my laptop
		if event.state == 260:
			webbrowser.open(addr)
		
		elif event.num == 1:# mouse left
			self.wipe()
			
			if self.flag_rss:
				self.input = addr
				self.make_page(addr, i)
			else:
				self.make_page(addr)
			
			
	def make_page(self, link=None, title_index=None):
		self.state = 'page'

		# address is not from hyperlink:
		if link == None or self.input:
			if link == None:
				link = self.entry.get().strip()
			if self.input:
				link = self.input
				self.input = None
			self.parser.domain = re.sub('(//[^/]*)/.*', r'\1', link)
			self.wipe()
							
		if self.parser.domain not in link:
			# wipe already done in taglink
			# current domain: http://onepage.com
			# link: 'http://anotherpage.com/spam?ref=nav/page/page2'
			
			# need to parse new domain from this:
			#'http://anotherpage.com/spam?ref=nav/page/page2'
			# to this:
			#'http://anotherpage.com'
			self.parser.domain = re.sub('(//[^/]*)/.*', r'\1', link)

		# final check
		if self.parser.domain.endswith('/'):
			self.parser.domain = self.parser.domain[:-1]

		if not self.flag_back:
			if title_index != None:
			
				# Try to get four words for better matching.
				tmp = self.u._titles[title_index].split()
				
				if len(tmp) > 3:
					pattern = ' '.join(tmp[:4])
				elif len(tmp) > 0:
					pattern = ' '.join(tmp[:len(tmp)])
				else:
					pattern = False
				
				self.history.append(('page', link, pattern))
			else:
				self.history.append(('page', link, False))
			
		self.flag_back = False
		self.flag_rss = False
		self.entry.insert(tkinter.END, link)
		self.title('Loading..')
		self.update_idletasks()
		
		req = urllib.request.Request(link)
		req.add_header('User-Agent', self.user_agent)
		self.text1.config(cursor="")
		self.text2.config(cursor="")
		
		# Fetch html-page
		try:
			res = urllib.request.urlopen(req, timeout = 8)
			
		except OSError as err:
			self.title('ARR: %d' % len(self.history))
			s  = 'Something went wrong:\n\n%s' % err.__str__()
			self.text1.insert(tkinter.END, s)
			
		else:
			self.title('ARR: %d' % len(self.history))
			res = res.read().decode('utf-8')
			self.parser.feed(res)	# HTMLParser parses links
			s = self.h.handle(res)	# html2text parses page
			
############# Modify page Begin

			# Remove ignored lines from page:
			tmp = ''
			l = s.splitlines()
			
			for line in l:
				if line.strip() not in self.ignored_lines:
					tmp += line + '\n'
			
			# Leave max 2 empty lines
			tmp = re.sub('(\n){4,}', 3*'\n', tmp)

############# Modify page End
			
			self.text1.insert(tkinter.END, tmp)
			
			for tag in self.text2.tag_names():
				if 'hyper' in tag:
					self.text2.tag_delete(tag)
			
			for i,item in enumerate(self.parser.addresses):
				tagname = "hyper-%s" % i
				self.text2.tag_config(tagname)
				
				self.text2.tag_bind(tagname, "<ButtonRelease-1>",
					lambda event: self.lclick(event))
					
				self.text2.tag_bind(tagname, "<ButtonRelease-3>",
					lambda event: self.rclick(event))
				
				self.text2.tag_bind(tagname, "<Enter>",
					lambda event, arg=tagname: self.enter(arg, event))
				
				self.text2.tag_bind(tagname, "<Leave>",
					lambda event, arg=tagname: self.leave(arg, event))
				
				name = item[0] +" "+  item[1] +"\n"
				self.text2.insert(tkinter.INSERT, name, tagname)
			
			if self.history[-1][2]:
				# try to get linenum of title in page. Pattern is string
				# with four first words in title.
				# For skipping to right place in page.
				pattern = self.history[-1][2]
				pos = self.text1.search(pattern, '1.0', tkinter.END)
				if pos:
					line = int(pos.split('.')[0])
					if line > 20:
						self.text1.see('%s + 20 lines' % pos)
						# ensure we see something before and after
						self.update_idletasks()
						self.text1.see(pos)
					
					
		self.text1.focus_set()
		self.text1.config(state='disabled')
		self.text2.config(state='disabled')


	def quit_me(self, event=None):
		self.save_config()
		self.quit()
		self.destroy()


if __name__ == '__main__':
	r = tkinter.Tk().withdraw()
	b = Browser(r)
	b.mainloop()

