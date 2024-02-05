import tkinter.colorchooser
import tkinter

class ColorChooser(tkinter.Toplevel):
	def __init__(self, widlist):
		self.root = tkinter.Tk()
		self.root.withdraw()
		super().__init__(self.root)
		self.title('Choose Color')
		self.widgetlist = list()
		
		for widget in widlist:
			self.widgetlist.append(widget)
		
		self.colorbg = self.widgetlist[0].cget('background')
		self.colorfg = self.widgetlist[0].cget('foreground')
		
		self.btnfg = tkinter.Button(self, text='Text color', font=('TkDefaultFont', 16), command=lambda args=['fg']: self.chcolor(args))
		self.btnfg.pack(padx=10, pady=10)
		
		self.btnbg = tkinter.Button(self, text='Ref. color', font=('TkDefaultFont', 16), command=lambda args=['bg']: self.chcolor(args))
		self.btnbg.pack(padx=10, pady=10)
		
		
	def chcolor(self, args, event=None):
		self.btnfg.config(state='disabled')
		self.btnbg.config(state='disabled')
		
		if args[0] == 'bg':
			self.colorbg = tkinter.colorchooser.askcolor(initialcolor=self.colorbg)[1]
			
			try:
				self.btnbg.config(bg=self.colorbg)
				self.btnfg.config(bg=self.colorbg)
				
				for widget in self.widgetlist:
					widget.config(bg=self.colorbg)
					
				self.btnfg.config(state='normal')
				self.btnbg.config(state='normal')
				
			
			except (tkinter.TclError, AttributeError) as e:
				# because if closed editor, this survives
				pass
			
			
		else:
			self.colorfg = tkinter.colorchooser.askcolor(initialcolor=self.colorfg)[1]
			
			try:
				self.btnbg.config(fg=self.colorfg)
				self.btnfg.config(fg=self.colorfg)
				
				for widget in self.widgetlist:
					widget.config(fg=self.colorfg)
					
				self.btnfg.config(state='normal')
				self.btnbg.config(state='normal')
				
	
			except (tkinter.TclError, AttributeError) as e:
				# because if closed editor, this survives
				pass
			
			











