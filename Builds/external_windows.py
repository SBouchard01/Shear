import os 
import customtkinter 
from tkinter import DISABLED
from PIL import  ImageTk, Image
import webbrowser

from Classes import CTkRichText


class Help_window():
    """Window with the credits"""
    
    WIDTH = 498
    HEIGHT = 557 # to change back to 500 when the part on language selection is removed ?
    
    def __init__(self, master=None):
        
        # If the master is given, create a toplevel window
        if master==None : 
            self = customtkinter.CTk() 
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Get the path of the script
            self.icon = path + "\Ressources\Shears_icon.ico" # Get the path of the icon
            self.iconbitmap(self.icon)
            self.geometry(f"{Help_window.WIDTH}x{Help_window.HEIGHT}")
        else : 
            self = customtkinter.CTkToplevel(master)
            self.icon = master.icon
            self.iconbitmap(self.icon)
            
            # Place the window in the center of the main window
            x = master.winfo_x() + master.winfo_width() // 2 - Help_window.WIDTH // 2
            y = master.winfo_y() + master.winfo_height() // 2 - Help_window.HEIGHT // 2
            self.geometry(f"{Help_window.WIDTH}x{Help_window.HEIGHT}+{x}+{y}")
            
        self.title("Help")
        #self.minsize(Help_window.WIDTH, Help_window.HEIGHT)
        #window.resizable(False, False) # TODO : Uncomment this line when complextkinter is updated to 5.0.0, otherwise the window disappears and blocks the main window
        
        # Configure grid layout
        self.grid_rowconfigure(0, minsize=10) # Add a space between the top of the window and the text
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        
        
        # ========== Frame for the title ==========
        self.title_frame = customtkinter.CTkFrame(self)
        self.title_frame.grid(row=1, column=0, columnspan=2)
        color = self.title_frame.bg_color
        self.title_frame.configure(fg_color=color)
        
        # Configure grid layout
        self.title_frame.grid_columnconfigure((0,3), minsize=20) # Empty columns for spacing
        
        # Logo
        image = ImageTk.PhotoImage(Image.open(self.icon).resize((35, 35)))
        Title_icon = customtkinter.CTkLabel(self.title_frame, 
                                            image=image, 
                                            width=1)
        Title_icon.grid(row=0, column=1, pady=8)
        
        # Title
        self.Title = customtkinter.CTkLabel(self.title_frame, 
                                       text="Shears Help", 
                                       text_font=("Roboto Medium", 15), 
                                       anchor="w", 
                                       width=6)
        self.Title.grid(row=0, column=2)
        
        # ========== Frame for the Help ==========
        self.help_frame = customtkinter.CTkFrame(self)
        self.help_frame.grid(row=2, column=0, sticky="nsew")
        color = self.help_frame.bg_color
        self.help_frame.configure(fg_color=color)
        
        # Configure grid layout
        self.help_frame.grid_rowconfigure(0, weight=1)
        self.help_frame.grid_columnconfigure(1, weight=1)

        
        
        # Textbox in which the help is displayed
        self.help_text = CTkRichText(self.help_frame, font=("Roboto Medium", 10))
        self.help_text.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.help_text.configure(fg_color=color)
        
        # Add the text in the textbox 
        self.help_text.insert("end", "Shears is a program to add chapters to a video file.\n\n")
        
        self.help_text.insert("end", "    Movie selction : ", "bold")
        self.help_text.insert("end", "Browse your computer to select a video file\n\n")
        
        self.help_text.insert("end", "    Subtitles : ", "bold")
        self.help_text.insert("end", "Browse your computer to select a subtitles file, in ")
        self.help_text.insert("end", ".srt", "italic")
        self.help_text.insert("end", "  format\n\n")
        
        self.help_text.insert("end", "    Metadata : ", "bold")
        self.help_text.insert("end", "You can add a title, an author and a year to the file's metadata\n\n")
        
        self.help_text.insert("end", "    Chapters : ", "bold")
        self.help_text.insert("end", "You can add chapters with the table, or with a ")
        self.help_text.insert("end", ".txt", "italic")
        self.help_text.insert("end", "  file\n\n")
        
        self.help_text.insert("end", "For each chapter in the file, there must be a line with the name of the chapter and the timecode at whitch the chapter starts.\n\n")
        
        self.help_text.insert("end", "/!\\ Warning !", "warning")
        self.help_text.insert("end", " The timecodes must be in the format [HH:MM:SS] or [MM:SS]\n\n")
        
        self.help_text.insert("end", "    Output (optional) : ", "bold")
        self.help_text.insert("end", "Browse your computer to select a folder where the file will be saved. If you don't select a folder, "\
                                "the file will be saved in the same folder as the original file and named automatically.\n\n")
        
        # TODO : Remove this when language selection is implemented
        self.help_text.insert("end", "    Language support : ", "bold")
        self.help_text.insert("end", "The language support is not yes implemented. It will be available in the next version.\n\n")
        
        self.help_text.insert("end", "    Debug mode : ", "bold")
        self.help_text.insert("end", "The debug mode allows you to see the command line used to add the chapters to the file and displays some more errors.\n\n")
        
        self.help_text.insert("end", "\n\tYou can find more information on the github page of the project\t", "italic")

        
        # Disable the textbox
        self.help_text.configure(state=DISABLED) 
        
        # Add a button to open the github page for more information
        self.github_button = customtkinter.CTkButton(self.help_frame,
                                                text="More information",
                                                command=lambda: print(self.winfo_height(), self.winfo_width()))
        self.github_button.grid(row=3, column=1, sticky="", padx=10, pady=10)
            
        # Bind the enter and escape keys to close the window
        self.bind("<Return>", lambda e: self.destroy()) 
        self.bind("<Escape>", lambda e: self.destroy())        

        # Display the window
        if master == None : 
            self.mainloop()
        else: # Grab the focus and wait for the window to be destroyed if part of an app
            self.grab_set()
            self.focus_set()
            self.wait_window()


class Credits_window():
    """Window with the credits"""
    
    WIDTH = 300
    HEIGHT = 300
    
    def __init__(self, master=None):
        
        # If the master is given, create a toplevel window
        if master==None : 
            self = customtkinter.CTk() 
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Get the path of the script
            self.icon = path + "\Ressources\Shears_icon.ico" # Get the path of the icon
            self.iconbitmap(self.icon)
            self.geometry(f"{Credits_window.WIDTH}x{Credits_window.HEIGHT}")
        else : 
            self = customtkinter.CTkToplevel(master)
            self.icon = master.icon
            self.iconbitmap(self.icon)
            
            # Place the window in the center of the main window
            x = master.winfo_x() + master.winfo_width() // 2 - Credits_window.WIDTH // 2
            y = master.winfo_y() + master.winfo_height() // 2 - Credits_window.HEIGHT // 2
            self.geometry(f"{Credits_window.WIDTH}x{Credits_window.HEIGHT}+{x}+{y}")
            
            
        self.title("Credits")
        self.minsize(Credits_window.WIDTH, Credits_window.HEIGHT)
        #window.resizable(False, False) # TODO : Uncomment this line when complextkinter is updated to 5.0.0, otherwise the window disappears and blocks the main window
        
        # Configure grid layout
        self.grid_rowconfigure(0, minsize=20) # Add a space between the top of the window and the text
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        
        
        # ========== Frame for the title ==========
        self.title_frame = customtkinter.CTkFrame(self)
        self.title_frame.grid(row=1, column=0, columnspan=2)
        color = self.title_frame.bg_color
        self.title_frame.configure(fg_color=color)
        
        # Configure grid layout
        self.title_frame.grid_columnconfigure((0,3), minsize=50) # Empty columns for spacing
        
        # Logo
        image = ImageTk.PhotoImage(Image.open(self.icon).resize((50, 50)))
        Title_icon = customtkinter.CTkLabel(self.title_frame, 
                                            image=image, 
                                            width=1)
        Title_icon.grid(row=0, column=1, pady=8)
        
        # Title
        self.Title = customtkinter.CTkLabel(self.title_frame, 
                                       text="Shears", 
                                       text_font=("Roboto Medium", 20), 
                                       anchor="w", 
                                       width=6)
        self.Title.grid(row=0, column=2)
        
        # ========== Frame for the credits ==========
        self.credits_frame = customtkinter.CTkFrame(self)
        self.credits_frame.grid(row=2, column=0, columnspan=2)
        # Make the frame invisible
        color = self.credits_frame.bg_color
        self.credits_frame.configure(fg_color=color)
        
        # Configure grid layout (2x3)
        self.credits_frame.grid_columnconfigure(1, minsize=10) # Empty columns for spacing
        self.credits_frame.grid_rowconfigure((2,4), minsize=30) # Empty columns for spacing
        
        # The creator (Label + Hyperlink in the form of a button)
        self.creator_label = customtkinter.CTkLabel(self.credits_frame, 
                                               text="Created by ",
                                               text_font=("Roboto Medium", 10, "bold"), 
                                               anchor="w",
                                               width=20)
        self.creator_label.grid(row=1, column=0, sticky="we")
        
        self.creator_link = customtkinter.CTkButton(self.credits_frame,
                                               text="Simon Bouchard",
                                               text_font=("Roboto Medium", 10),
                                               width=20,
                                               #border_width=1,
                                               command=lambda: webbrowser.open("https://github.com/SBouchard01"))
        self.creator_link.grid(row=1, column=2, sticky="we")
        
        # FFMPEG (Label + Hyperlink in the form of a button)
        self.ffmpeg_label = customtkinter.CTkLabel(self.credits_frame,
                                              text="Code running with ",
                                              text_font=("Roboto Medium", 10, "bold"),
                                              anchor="w",
                                              width=20)
        self.ffmpeg_label.grid(row=3, column=0, sticky="we")
        
        self.ffmpeg_link = customtkinter.CTkButton(self.credits_frame,
                                              text="FFMPEG", 
                                              text_font=("Roboto Medium", 10), 
                                              width=20, 
                                              #border_width=1,
                                              command=lambda: webbrowser.open("https://ffmpeg.org/"))
        self.ffmpeg_link.grid(row=3, column=2, sticky="we")
        
        # The graphical interface (Label + Hyperlink in the form of a button)
        self.gui_label = customtkinter.CTkLabel(self.credits_frame,
                                           text="Graphical interface ",
                                           text_font=("Roboto Medium", 10, "bold"),
                                           anchor="w",
                                           width=20)
        self.gui_label.grid(row=5, column=0, sticky="we")
        
        self.gui_link = customtkinter.CTkButton(self.credits_frame,
                                           text="customtkinter",
                                           text_font=("Roboto Medium", 10),
                                           width=20,
                                           #border_width=1,
                                           command=lambda: webbrowser.open("https://github.com/TomSchimansky/CustomTkinter"))
        self.gui_link.grid(row=5, column=2, sticky="we")

        
        # Bind the enter and escape keys to close the window
        self.bind("<Return>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy()) 

        # Display the window
        if master == None : 
            self.mainloop()
        else: # Grab the focus and wait for the window to be destroyed if part of an app
            self.grab_set()
            self.focus_set()
            self.wait_window()

# Tests
if __name__ == "__main__":
    app = Help_window()

