import customtkinter 
import tkinter as tk # Graphical interface
from tkinter import font as tkFont


class HyperlinkManager(object):
    """A class to easily add clickable hyperlinks to Text areas.
    Usage:
      callback = lambda : webbrowser.open("http://www.google.com/")
      text = tk.Text(...)
      hyperman = tkHyperlinkManager.HyperlinkManager(text)
      text.insert(tk.INSERT, "click me", hyperman.add(callback))
    From http://effbot.org/zone/tkinter-text-hyperlink.htm
    """
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        """Adds an action to the manager.
        :param action: A func to call.
        :return: A clickable tag to use in the text widget.
        """
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return ("hyper", tag)

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if (tag[:6] == "hyper-"):
                self.links[tag]()
                return


class RichText(tk.Text):
    """A class from https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter which allows for rich text in tkinter"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Inherit from tk.Text
        
        # If current font is not set, set it to default
        if "font" not in kwargs:
            default_font = tkFont.nametofont("TkDefaultFont")
        else:
            # Get something in the form of (family, size)
            family = kwargs["font"][0]
            size = int(kwargs["font"][1])
            
            default_font = tkFont.Font(family=family, size=size) # Creating the default font

        font_name = default_font.cget("family") # Getting the font name
        font_size = default_font.cget("size") # Getting the font size
        
        self.configure(font=(font_name, font_size)) # Setting the font of the text to the default font (otherwise it is tkInter default font)
        
        # Get different fonts from the default font
        em = default_font.measure("m")
        default_size = default_font.cget("size")
        bold_font = tkFont.Font(**default_font.configure())
        italic_font = tkFont.Font(**default_font.configure())
        h1_font = tkFont.Font(**default_font.configure())

        # Configure the fonts
        bold_font.configure(weight="bold")
        italic_font.configure(slant="italic")
        h1_font.configure(size=int(default_size*2), weight="bold")

        # Create a tag for each font
        self.tag_configure("default", font=default_font)
        self.tag_configure("bold", font=bold_font)
        self.tag_configure("italic", font=italic_font)
        self.tag_configure("h1", font=h1_font, spacing3=default_size)
        self.tag_configure("hyperlink", foreground="blue", underline=1)
        

        # Create a tag for bullets
        lmargin2 = em + default_font.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=em, lmargin2=lmargin2)

    def insert_bullet(self, index, text):
        """Insert a bullet at the given index"""
        self.insert(index, f"\u2022 {text}", "bullet")



class CTkRichText(customtkinter.CTkTextbox):
    """
    A class from https://stackoverflow.com/questions/63099026/fomatted-text-in-tkinter 
    which allows for rich text, modified for customtkinter.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # Inherit from tk.Text
        
        # If current font is not set, set it to default
        if "font" not in kwargs:
            default_font = tkFont.nametofont("TkDefaultFont")
        else:
            # Get something in the form of (family, size)
            family = kwargs["font"][0]
            size = int(kwargs["font"][1])
            
            default_font = tkFont.Font(family=family, size=size) # Creating the default font

        font_name = default_font.cget("family") # Getting the font name
        font_size = default_font.cget("size") # Getting the font size
        
        self.configure(text_font=(font_name, font_size)) # Setting the font of the text to the default font (otherwise it is tkInter default font)
        
        # Get different fonts from the default font
        em = default_font.measure("m")
        default_size = default_font.cget("size")
        bold_font = tkFont.Font(**default_font.configure())
        italic_font = tkFont.Font(**default_font.configure())
        h1_font = tkFont.Font(**default_font.configure())

        # Configure the fonts
        bold_font.configure(weight="bold")
        italic_font.configure(slant="italic")
        h1_font.configure(size=int(default_size*2), weight="bold")

        # Create a tag for each font
        self.tag_configure("default", font=default_font)
        self.tag_configure("bold", font=bold_font)
        self.tag_configure("italic", font=italic_font)
        self.tag_configure("h1", font=h1_font, spacing3=default_size)
        self.tag_configure("hyperlink", foreground="blue", underline=1)
        self.tag_configure("warning", font=bold_font, foreground="red", underline=1)
        

        # Create a tag for bullets
        lmargin2 = em + default_font.measure("\u2022 ")
        self.tag_configure("bullet", lmargin1=em, lmargin2=lmargin2)
        

    def insert_bullet(self, index, text):
        """Insert a bullet at the given index"""
        self.insert(index, f"\u2022 {text}", "bullet")
        