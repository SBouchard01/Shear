##################################################################
## Shears_UI.py : Script to add chapters to a video file,       ##
## given the timecodes and titles of the chapters,              ##
## with complete graphic interface.                             ##
##################################################################
## Author: 	S. Bouchard                                         ##
## Date: 	2020-05-05                                          ##
## Version: 	1.0                                             ##
##################################################################
## Requirements: 	ffmpeg, python3, customtkinter              ##
##################################################################
##          Executable created with auto-py-to-exe              ##
##        (https://pypi.org/project/auto-py-to-exe/)            ##
##################################################################
## Changelog:                                                   ##
## 2020-05-05: 	Initial release                                 ##
##################################################################

#%% Imports
import os
import re
import subprocess
from subprocess import CREATE_NO_WINDOW

# Language modules
from pycountry import languages
from langdetect import detect, DetectorFactory

# GUI modules
import customtkinter
import tkinter.font as tkfont
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import END, ttk
from tkinter.messagebox import askyesno

# Custom modules
from Functions import resource_path, timecode_to_ms, ms_to_timecode, parse_timecodes as parse, Error_Window
from external_windows import Help_window, Credits_window

#%% Application class definition

class Application(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()
        
        # Some properties of the window
        self.icon = resource_path("Ressources/Shears_icon.ico")
        self.iconbitmap(self.icon)
        self.title("Shears")
        self.geometry(f"{Application.WIDTH}x{Application.HEIGHT}")
        self.resizable(True, True)
        self.minsize(Application.WIDTH, Application.HEIGHT)
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # call .on_closing() when app gets closed

        # Get the default font and prints it with the size
        # default_font = tkfont.nametofont("TkDefaultFont")
        # print("Default font : " + default_font.actual()["family"] + " " + str(default_font.actual()["size"]))

        # Configure grid layout (1x2)
        self.grid_columnconfigure((0, 2, 3), weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) # The bottom frame is not resizable

        # Placing the Ok and Cancel buttons on the bottom right
        self.Ok_button = customtkinter.CTkButton(master=self,
                                                 text="Ok",
                                                 border_width=1,
                                                 command=self.Ok_button_event)
        self.Ok_button.grid(row=1, column=2, sticky="e", padx=10, pady=10)

        # Binding the enter key to the Ok button
        self.bind("<Return>", lambda event: self.return_event())

        self.Cancel_button = customtkinter.CTkButton(master=self,
                                                     text="Cancel",
                                                     border_width=1,
                                                     command=self.on_closing)
        self.Cancel_button.grid(row=1, column=3, sticky="e", padx=10, pady=10)

        # Binding the escape key to the Cancel button
        self.bind("<Escape>", lambda event: self.on_closing())

        # ============ Create two frames ============
        # The left frame is not resizable and is on rows 1 and 2
        self.left_frame = customtkinter.CTkFrame(master=self,
                                                 corner_radius=0)
        self.left_frame.grid(row=0, column=0, rowspan=2, sticky="nswe")

        # The right frame is resizable and is on columns 1, 2 and 3
        self.right_frame = customtkinter.CTkFrame(master=self)
        self.right_frame.grid(row=0, column=1, columnspan=3, sticky="nswe", padx=20, pady=20)

        # ============== Left frame =================
        # Get the width of the left frame
        left_width = self.left_frame.cget("width")

        # Configure grid layout (1x11)
        self.left_frame.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.left_frame.grid_rowconfigure(5, minsize=10)  # row for a frame
        self.left_frame.grid_rowconfigure(6, weight=1)  # empty row as spacing
        self.left_frame.grid_rowconfigure(9, minsize=20) # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.left_frame,
                                              text="Shears",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.help_button = customtkinter.CTkButton(master=self.left_frame,
                                                   text="Help",
                                                   command=self.help_button_event)
        self.help_button.grid(row=2, column=0, pady=10, padx=20)

        self.credits_button = customtkinter.CTkButton(master=self.left_frame,
                                                      text="Credits",
                                                      command=self.credits_button_event)
        self.credits_button.grid(row=3, column=0, pady=10, padx=20)

        # ============= Metadata Frame ==============

        self.metadata_frame = customtkinter.CTkFrame(master=self.left_frame,
                                                     border_width=2,
                                                     corner_radius=11)
        self.metadata_frame.grid(row=5, column=0, sticky="nswe", padx=10, pady=10)

        # Configure grid layout (1x4)
        self.metadata_frame.grid_rowconfigure(4, minsize=10) # empty row with minsize as spacing

        # Title : Metadata
        self.label_2 = customtkinter.CTkLabel(master=self.metadata_frame,
                                              text="Metadata",
                                              text_font=("Roboto Medium", -16))
        self.label_2.grid(row=0, column=0, sticky="w", padx=10, pady=10, ipadx=20)

        # Fields
        self.title_field = customtkinter.CTkEntry(master=self.metadata_frame,
                                                  placeholder_text="Title")
        self.title_field.grid(row=1, column=0, sticky="we", padx=10, pady=10)

        self.author_field = customtkinter.CTkEntry(master=self.metadata_frame,
                                                   placeholder_text="Author")
        self.author_field.grid(row=2, column=0, sticky="we", padx=10, pady=10)

        self.year_field = customtkinter.CTkEntry(master=self.metadata_frame,
                                                 placeholder_text="Year")
        self.year_field.grid(row=3, column=0, sticky="we", padx=10, pady=10)

        # ========== End of Metadata Frame ==========

        self.debug_switch = customtkinter.CTkSwitch(master=self.left_frame,
                                                    text="Debug mode",
                                                    command=self.debug_switch_event)
        self.debug_switch.grid(row=7, column=0, pady=10, padx=20, sticky="we")

        self.debug_mode = False  # Debug mode is off by default

        # Create a frame for the language selection
        self.language_frame = customtkinter.CTkFrame(master=self.left_frame,
                                                     width=left_width,
                                                     corner_radius=0)
        self.language_frame.grid(row=8, column=0, rowspan=3, sticky="nswe")

        # Set the color of the language frame
        color = self.language_frame.bg_color
        self.language_frame.configure(fg_color=color)

        # Configure grid layout (1x3)
        self.language_frame.grid_columnconfigure((0, 1), minsize=left_width/2)
        self.language_frame.grid_rowconfigure(1, minsize=10)

        self.label_lng = customtkinter.CTkLabel(master=self.language_frame,
                                                text="Language:",
                                                anchor="center",
                                                width=1)
        self.label_lng.grid(row=0, column=0, sticky="nsew")

        self.language_menu = customtkinter.CTkOptionMenu(master=self.language_frame,
                                                         values=["Français", "Anglais"],
                                                         width=1,
                                                         command=self.language_menu_event)
        self.language_menu.configure(width=left_width/2)
        self.language_menu.grid(row=0, column=1, pady=5, padx=5, sticky="we")

        # ============== Right frame ================
        # Get the width of the right frame
        right_width = self.right_frame.cget("width")

        # Configure grid layout (6x2)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(1, minsize=right_width/5) 
        self.right_frame.grid_rowconfigure(0, minsize=10) # empty row with minsize as spacing
        self.right_frame.grid_rowconfigure(5, weight=1)  # empty row as spacing

        # Section title (not sure if it's necessary)
        # self.label_3 = customtkinter.CTkLabel(master=self.right_frame,
        #                                         text="Shears",
        #                                         text_font=("Roboto Medium", -16))
        # self.label_3.grid(row=1, column=0, columnspan=2, sticky="we", padx=10, pady=10, ipadx=20)

        # Movie selection
        self.movie_field = customtkinter.CTkEntry(master=self.right_frame,
                                                  placeholder_text="Movie file")
        self.movie_field.grid(row=2, column=0, sticky="we", padx=10, pady=10)

        self.movie_button = customtkinter.CTkButton(master=self.right_frame,
                                                    text="Browse",
                                                    command=self.browse_movie_event)
        self.movie_button.grid(row=2, column=1, sticky="we", padx=10, pady=10)

        # Subtitle selection
        self.subtitle_field = customtkinter.CTkEntry(master=self.right_frame,
                                                     placeholder_text="Subtitle file",
                                                     state="normal")
        self.subtitle_field.grid(row=3, column=0, sticky="we", padx=10, pady=10)

        self.subtitle_button = customtkinter.CTkButton(master=self.right_frame,
                                                       text="Browse",
                                                       command=self.browse_subtitle_event)
        self.subtitle_button.grid(row=3, column=1, sticky="we", padx=10, pady=10)

        # Timecodes file selection
        self.timecodes_field = customtkinter.CTkEntry(master=self.right_frame,
                                                      placeholder_text="Timecodes file")
        self.timecodes_field.grid(row=4, column=0, sticky="we", padx=10, pady=10)

        self.timecodes_button = customtkinter.CTkButton(master=self.right_frame,
                                                        text="Browse",
                                                        command=self.browse_timecodes_event)
        self.timecodes_button.grid(row=4, column=1, sticky="we", padx=10, pady=10)

        # ============= Table ==============

        # Create a frame for the table
        self.table_frame = customtkinter.CTkFrame(master=self.right_frame,
                                                  corner_radius=5)
        self.table_frame.grid(row=5, column=0, sticky="nswe", padx=10, pady=10)

        # Configure grid layout (3x2)
        self.table_frame.grid_rowconfigure(1, weight=1)  # Make the table expandable
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Set the color of the table frame
        #color = self.table_frame.bg_color
        self.table_frame.configure(fg_color='silver')

        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")
        style.configure("Treeview", rowheight=19) # Sets the height of the rows to fit the frame

        # Set the tables columns
        columns = ("Start time", "Chapter title")

        self.table = ttk.Treeview(self.table_frame,
                                  style="Treeview",
                                  columns=columns,
                                  height=9,
                                  show="headings")
        self.table.grid(row=1, column=0, sticky="nswe", padx=0, pady=0)

        # Define headings
        for col in columns:
            self.table.heading(col, text=col)

        # Define column width
        self.table.column("Start time", minwidth=70, width=70, stretch=False)
        self.table.column("Chapter title", minwidth=225, width=225)

        # Bind actions to the table
        # self.table.bind('<Motion>', 'break') # Make columns not resizable
        # If a line is selected, update the entry field with row_selection
        self.table.bind('<ButtonRelease-1>', lambda e: self.row_selection())

        # Add a y-scrollbar
        self.table_scrollbar = ttk.Scrollbar(self.table_frame, 
                                             orient="vertical", 
                                             command=self.table.yview)
        self.table.configure(yscrollcommand=self.table_scrollbar.set)
        self.table_scrollbar.grid(row=1, column=1, sticky="ns", padx=0, pady=0)

        # Add a x-scrollbar
        self.table_scrollbar_x = ttk.Scrollbar(self.table_frame, 
                                               orient="horizontal", 
                                               command=self.table.xview)
        self.table.configure(xscrollcommand=self.table_scrollbar_x.set)
        self.table_scrollbar_x.grid(row=2, column=0, sticky="we", padx=0, pady=0)

        # Table modification frame on second column
        self.table_mod_frame = customtkinter.CTkFrame(master=self.right_frame,
                                                      border_width=2,
                                                      corner_radius=20,
                                                      width=right_width/5)
        self.table_mod_frame.grid(row=5, column=1, sticky="n", padx=10, pady=10)

        # Configure grid layout (1x7)
        self.table_mod_frame.grid_rowconfigure(0, minsize=2)  # Empty rows for spacing
        self.table_mod_frame.grid_rowconfigure((3, 6, 8), minsize=10)  # Empty rows for spacing
        self.table_mod_frame.grid_rowconfigure((0, 1), weight=0)  # Empty row for spacing

        # Set two entries and an add button with labels above

        # Entry 1
        self.label_4 = customtkinter.CTkLabel(master=self.table_mod_frame,
                                              anchor="w",
                                              text="Start time")
        self.label_4.grid(row=1, column=0, columnspan=2, sticky="we", padx=13, pady=5)

        self.time_entry = customtkinter.CTkEntry(master=self.table_mod_frame,
                                                 placeholder_text="Start time")
        self.time_entry.grid(row=2, column=0, columnspan=2, sticky="we", padx=10, pady=0)

        # Entry 2
        self.label_5 = customtkinter.CTkLabel(master=self.table_mod_frame,
                                              anchor="w",
                                              text="Chapter title")
        self.label_5.grid(row=4, column=0, columnspan=2, sticky="we", padx=13, pady=0)

        self.chapter_entry = customtkinter.CTkEntry(master=self.table_mod_frame,
                                                    placeholder_text="Chapter title")
        self.chapter_entry.grid(row=5, column=0, columnspan=2, sticky="we", padx=10, pady=0)

        self.add_line_button = customtkinter.CTkButton(master=self.table_mod_frame,
                                                       text="Add line",
                                                       width=1,
                                                       text_font=("Arial", 8),
                                                       command=self.add_button)
        self.add_line_button.grid(row=7, column=0, sticky="we", padx=5, pady=10)

        self.clear_button = customtkinter.CTkButton(master=self.table_mod_frame,
                                                    text="Clear line",
                                                    width=1,
                                                    text_font=("Arial", 8),
                                                    command=self.clear_line)
        self.clear_button.grid(row=7, column=1, sticky="we", padx=5, pady=10)

        # ========== End of Table ==========

        # Save as field
        self.save_field = customtkinter.CTkEntry(master=self.right_frame,
                                                 placeholder_text="Save as")
        self.save_field.grid(row=7, column=0, sticky="we", padx=10, pady=10)

        self.save_button = customtkinter.CTkButton(master=self.right_frame,
                                                   text="Browse",
                                                   command=self.browse_save_event)
        self.save_button.grid(row=7, column=1, sticky="we", padx=10, pady=10)

        # Set default values and deactivations
        self.language_menu.set("Français")

        # self.subtitle_field.configure(state="disabled") # Disable the subtitle field for now
        # self.subtitle_button.configure(state="disabled") # Disable the subtitle button for now
        self.language_menu.configure(state="disabled") # Disable the language menu for now


# ============= Functions for background tasks ============

    @staticmethod
    def timecode_verification(string: str):
        """Verify if a string is valid timecode"""

        if re.match(r"^\d{2}:\d{2}:\d{2}$|^\d{2}:\d{2}$", string):
            # Reformat the timecode to HH:MM:SS if it is MM:SS
            if len(string.split(":")) == 2:
                string = "00:" + string
            return string
        else:
            raise ValueError("Invalid timecode : " + string)


    @staticmethod
    def measure_string(string: str):
        """Measures the a string in pixels"""

        # Get a font to measure a standard width
        font = tkfont.nametofont("TkDefaultFont")
        font_size = font.measure("0")  # Get the width of a character
        measure = len(string) * font_size # Multiply the number of characters by the width of a character
        
        return measure  # Return the result


    @staticmethod
    def detect_language(path):
        """Detects the language of the subtitle file"""

        if not os.path.isfile(path):
            return None

        # Open the subtitle file
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        # Remove the lines with the timecodes
        text = re.sub(r"\d{2}:\d{2}:\d+,\d+ --> \d{2}:\d{2}:\d+,\d+", "", text)
        # Remove the lines with the numbers
        text = re.sub(r"\d+", "", text)
        # Remove the empty lines
        text = re.sub(r"\n+", "\n", text)

        # Detect the language
        DetectorFactory.seed = 0
        language = detect(text)
        iso_369_2 = languages.get(alpha_2=language).alpha_3
        return iso_369_2


    def add_to_table(self, times, chapters):
        """Replaces the table with the given values"""

        # Order the lists by time
        times, chapters = (list(t) for t in zip(*sorted(zip(times, chapters))))

        # Erase the table
        for record in self.table.get_children():
            self.table.delete(record)

        # Add the timecodes and chapters to the table
        for i in range(len(times)):
            self.table.insert('', 'end', text=str(i), values=(times[i], chapters[i]))


    def resize_table(self, chapter):
        """Resize the table column to fit the new chapter title if needed"""

        # Get the current width of the column
        old_size = self.table.column("Chapter title", option="width")
        new_size = self.measure_string(chapter)  # Get the width of the input
        if new_size > old_size:
            # Resize the column if the input is longer than the current size
            self.table.column("Chapter title", width=new_size)

# =================== Action Functions ===================

    def return_event(self):
        """Event when the user press enter. If the cursor is in the table_mod_frame, 
        add the line, otherwise, execute the Ok button"""

        if str(self.focus_get()) == '.!ctkframe2.!ctkframe2.!ctkentry.!entry' \
                or str(self.focus_get()) == '.!ctkframe2.!ctkframe2.!ctkentry2.!entry':
            self.add_button()
        else:
            self.Ok_button_event()


    def help_button_event(self):
        """Opens a window with how to use the program"""
        Help_window(self)


    def credits_button_event(self):
        """Opens a toplevel window with the credits of the program"""
        Credits_window(self)


    def browse_movie_event(self):
        """Browse for a movie file and replace the placeholder text with the path"""

        # Open a file selection dialog window
        file_path = askopenfilename(title='Select the movie',
                                    filetypes=[('Video files', ('*.mp4', '*.mkv', '*.avi')), ("all files", "*.*")])

        # Replace the placeholder text with the path
        self.movie_field.delete(0, END)
        self.movie_field.insert(0, file_path)


    def browse_subtitle_event(self):
        """Browse for a subtitle file and replace the placeholder text with the path"""

        # Open a file selection dialog window
        file_path = askopenfilename(title='Select the subtitle file',
                                    filetypes=[('Subtitles files', ('*.txt', '*.sbv', '*.srt', '*.vtt')), ("all files", "*.*")])

        # Replace the placeholder text with the path
        self.subtitle_field.delete(0, END)
        self.subtitle_field.insert(0, file_path)


    def browse_save_event(self):
        """Browse for a save location and replace the placeholder text with the path"""

        # Open a file selection dialog window
        file_path = asksaveasfilename(title='Select the output file')

        # Replace the placeholder text with the path
        self.save_field.delete(0, END)
        self.save_field.insert(0, file_path)


    def language_menu_event(self, value):
        # TODO : Add language support
        # Temprary placeholder for optionmenu events
        self.language_menu.configure(width=1)

        if self.debug_mode == True:
            print("Language changed to : " + value)


    def browse_timecodes_event(self):
        """Browse for a chaptering file and replace the placeholder text with the path
        Replaces the table content with the timecodes from the file"""

        # Open a file selection dialog window
        file_path = askopenfilename(title='Select the timecodes file',
                                    filetypes=[('Text files', '*.txt'), ("all files", "*.*")])

        if not os.path.isfile(file_path):
            return

        # Read the file
        with open(file_path, "r") as timecodes_file:
            lines = timecodes_file.read()

        input = lines.split("\n")  # Split the lines into a list

        try:
            # Parse the lines into a list of times and a list of titles
            times, titles = parse(input)

            # If the lists are empty, raise an error
            if len(times) == 0 or len(titles) == 0:
                raise ValueError("No chapters found.")
        except ValueError as e:  # Just in case the file is not formatted correctly
            Error_Window("Error", 
                         str(e)+"\nPlease check the file formatting and try again.")
            return

        # Order the times and titles by time
        times, titles = (list(t) for t in zip(*sorted(zip(times, titles))))

        # Erase the table
        for record in self.table.get_children():
            self.table.delete(record)

        # Add the timecodes and chapters to the table
        for i in range(len(times)):
            self.table.insert('', 'end', text=str(i), values=(times[i], titles[i]))

        # Replace the placeholder text with the path
        self.timecodes_field.delete(0, END)
        self.timecodes_field.insert(0, file_path)


    def row_selection(self):
        """Select a row and display the timecode and chapter in the entry fields"""

        try:
            # Get the selected row
            selected_row = self.table.selection()[0]
        except:
            return  # If the table is empty, do nothing

        # Get the values of the selected row
        values = self.table.item(selected_row, "values")

        # Display the values in the entry fields
        self.time_entry.delete(0, END)
        self.time_entry.insert(0, values[0])
        self.chapter_entry.delete(0, END)
        self.chapter_entry.insert(0, values[1])


    def add_button(self):
        # Check if the timecode is valid
        try:
            timecode = self.timecode_verification(self.time_entry.get())
        except ValueError as e:
            timecode = self.time_entry.get()
            if timecode == "":
                msg = "Please enter a timecode"
            else:
                msg = f"The timecode \"{self.time_entry.get()}\" is invalid.\n\n"\
                    "The timecode must be in the format HH:MM:SS or MM:SS\n"\
                    "Please check the timecode and try again."
            Error_Window("Invalid Timecode", msg)
            return

        chapter = self.chapter_entry.get()

        # Get current table content
        times = [self.table.item(record)["values"][0]
                 for record in self.table.get_children()]
        chapters = [str(self.table.item(record)["values"][1])
                    for record in self.table.get_children()]

        # Checks if the timecode is already in the table
        if timecode in times:
            msg = f"The timecode \"{timecode}\" is already a chapter !\n"\
                "Do you want to replace it ?"
            answer = askyesno("Timecode already exists", msg)
            if answer == True:
                # Remove the old timecode and chapter from times, chapters
                index = times.index(timecode)
                times.pop(index)
                chapters.pop(index)
            else:
                return

        # Escape special characters in the chapter name with dedicated function (Not needed anymore)
        #chapter = escape_characters(chapter)

        # Add the new timecode and chapter to the lists
        times.append(timecode)
        chapters.append(chapter)

        # Replace the table content with the new lists
        self.add_to_table(times, chapters)

        # Resize the chapter column if needed
        self.resize_table(chapter)

        # Clear the input fields
        self.time_entry.delete(0, END)
        self.chapter_entry.delete(0, END)


    def clear_line(self):
        """Clear the selected line in the table"""

        # Get the index of the selected line
        try:
            index = self.table.selection()[0]
            timecode_table = self.table.item(index)["values"][0]
            chapter_table = str(self.table.item(index)["values"][1])
        except IndexError as e:
            # No line selected
            return

        # Check if the timecode and chapter are the same as the input fields (otherwise it might be a mistake)
        timecode_entry = self.time_entry.get()
        chapter_entry = self.chapter_entry.get()

        if timecode_entry == timecode_table and chapter_entry == chapter_table:
            # Delete the line
            self.table.delete(index)

            # Clear the input fields
            self.time_entry.delete(0, END)
            self.chapter_entry.delete(0, END)
        else:
            if self.debug_mode == True:  # Only display the message if the debug mode is on
                msg = f"Timecode and chapter in the table do not match the input fields."
                Error_Window("Error", msg)


    def Ok_button_event(self):
        """Checks if the inputs are valid and puts the data in variables to access from the main program"""

        self.get_metadata()  # Get the metadata from the input fields (even if they are empty)

        try:
            self.get_values()  # Get the values from the input fields
        except ValueError as e:
            if str(e) != "":
                Error_Window("Error", str(e))
            return

        # ========== Main program ==========

        # If the table is not empty, create the metadata file
        if len(self.times) != 0:
            try:
                self.create_metadata()  # Create the metadata file
                self.add_chapters()  # Add the chapters to the metadata file
            except AssertionError:
                err = "The video is shorter than the last timecode.\n"\
                      "Please check the timecodes."
                Error_Window("Error", err)
                return
        # Handle the case where the table is empty but the metadata is not
        elif self.movie_title != "" or self.author != "" or self.movie_year != "":
            self.create_metadata()  # Create the metadata file without chapters
        else:
            # No metadata file, but we still need to pass a value to the rest of the code
            self.metadata_file = ""

        # If the output file already exists, delete it (The user has then already been asked if he wants to overwrite it by tkinter)
        if os.path.isfile(self.output_file):
            os.remove(self.output_file)

        # Create the command
        cmd = "ffmpeg -y "  # Overwrite the output file if it already exists
        file_input = f"-i \"{self.movie_file}\" "
        # Keep pthe metadata from the input file, add the metadata from the metadata file
        args_metadata = "-map_metadata 0 -map_metadata 1 -codec copy "
        # Add the subtitles to the metadata
        args_subtitles = "-c:s mov_text -metadata:s:s:0 language="
        output = f" \"{self.output_file}\""
        error_args = " -v error"  # Only display the errors

        # Add the metadata to the video
        if os.path.isfile(self.metadata_file):
            metadata_input = f"-i \"{self.metadata_file}\" "
        else:
            metadata_input = ""  # If there is no metadata file, don't add it to the command

        # Add the subtitles to the video
        if os.path.isfile(self.subtitle_file):
            subtitle_imput = f"-i \"{self.subtitle_file}\" "
            lang = self.detect_language(self.subtitle_file)
        else:
            # If there is no subtitle file, don't add it to the command, nor the language
            subtitle_imput = ""
            lang = ""

        # Run ffmpeg (Handle final error with a yes/no popup + open terminal in debug mode??)
        ffmpeg_cmd = cmd + file_input + metadata_input + subtitle_imput + \
            args_metadata + args_subtitles + lang + output + error_args

        try:  # Should allways work, but just in case
            if subprocess.run(ffmpeg_cmd, capture_output=True, creationflags=CREATE_NO_WINDOW).returncode != 0:
                raise OSError("FFMPEG encountered an error")

        except OSError as e:  # If FFmpeg encounters an error
            if self.debug_mode == True:
                msg = f"FFMPEG encountered an error.\n"\
                      f"Do you want to open the terminal ?"
                # Ask the user if he wants to open the terminal to see the error
                answer = askyesno("Error", msg)

                if answer == True:
                    # Open the terminal with the command
                    os.system("start cmd /k " + ffmpeg_cmd)

            else:
                msg = f"FFMPEG encountered an error.\n\n"\
                      f"Please check the inputs and try again.\n"\
                      f"You can learn more about the error in debug mode."
                Error_Window("Error", msg)
            return

        # Open folder after the process is finished (comment this line if you don't want to open the folder)
        os.startfile(os.path.dirname(self.output_file))

        # Delete the metadata file if debug mode is off
        if self.debug_mode == False:
            os.remove(self.metadata_file)


    def debug_switch_event(self):
        self.debug_mode = not self.debug_mode

        if self.debug_mode == True:
            print("Debug mode enabled")
        else:
            print("Debug mode disabled")


    def on_closing(self):
        self.destroy()


# ========== Main code functions ==========

    def get_values(self):
        """Returns the values of the variables and checks if the inputs are valid"""

        # ========== Movie file ==========
        self.movie_file = self.movie_field.get()
        self.movie_file_extension = os.path.splitext(self.movie_file)[1]

        # Checks if the movie file exists
        if not os.path.isfile(self.movie_file):
            msg = f"The movie file \"{self.movie_file}\" does not exist."
            raise ValueError(msg)

        # ========= Subtitles ==========
        self.subtitle_file = self.subtitle_field.get()
        self.subtitle_language = self.detect_language(self.subtitle_file)

        # If the subtitle file do not exists
        if not os.path.isfile(self.subtitle_file) and self.subtitle_file != "":
            msg = f"The subtitle file \"{os.path.basename(self.subtitle_file)}\" does not exist."
            raise ValueError(msg)

        # ========= Chapters ==========
        self.times = [self.table.item(record)["values"][0]
                      for record in self.table.get_children()]
        self.chapters = [str(self.table.item(record)["values"][1])
                         for record in self.table.get_children()]

        # If the table is empty, there is no subtitle file and no metadata, raise an error
        if len(self.times) == 0 and self.subtitle_file == ""\
                                and self.movie_title == "" \
                                and self.author == "" \
                                and self.movie_year == "":
            msg = f"No chapters, metadata or subtitles found."
            raise ValueError(msg)

        # If there are empty chapters titles
        if "" in self.chapters:
            msg = f"Empty chapter title detected."
            raise ValueError(msg)

        # ========== Output ==========
        # Checks if the output field is empty. If yes, create it in the same directory as the input and ask for confirmation
        if self.save_field.get() == "":
            # Get the name of the movie file and its extension
            self.output_file = os.path.splitext(self.movie_file)[0] + "_Shear" + self.movie_file_extension
            n = 1
            # If the file already exists, add a number to the name
            while os.path.isfile(self.output_file):
                self.output_file = os.path.splitext(self.movie_file)[0] + f"_Shear({n})"+self.movie_file_extension
                n += 1
            
            msg = f"There is no output file specified.\n\n"\
                  f"Do you want to create it in the current directory ?\n"\
                  f"The file will be named \"{os.path.basename(self.output_file)}\""
            answer = askyesno("No output file", msg)
            
            if answer == False:
                raise ValueError
            else:
                # Put the output file in the field
                self.save_field.insert(0, self.output_file)
                
        else:  # If the output field is not empty
            self.output_file = self.save_field.get()

        # Checks if the output file has the correct extension. If not, add it and ask for confirmation
        self.output_file_extension = os.path.splitext(self.output_file)[1]
        if self.movie_file_extension != self.output_file_extension:
            msg = f"The output file extension is different from the movie file extension.\n\n"\
                  f"Do you want to change it to {self.movie_file_extension} ?"
            answer = askyesno("Different extensions", msg)
            
            if answer == False:
                raise ValueError
            else:
                self.output_file = os.path.splitext(self.output_file)[0] + self.movie_file_extension
                self.save_field.delete(0, END)
                self.save_field.insert(0, self.output_file) # Put the new output file in the field

        # Checks if the output file is not the same as the movie file. If it is, propose to change the name and ask for confirmation
        if self.movie_file == self.output_file:
            n = 1
            # If the file already exists, add a number to the name
            while os.path.isfile(self.output_file):
                self.output_file = os.path.splitext(self.movie_file)[0] + f"_Shear({n})"+self.movie_file_extension
                n += 1
                
            msg = f"The output file is the same as the movie file.\n\n"\
                  f"Do you want to change it to \"{os.path.basename(self.output_file)}\" ?"
            answer = askyesno("Same file", msg)
            
            if answer == False:
                msg = f"The output file cannit be the same as the movie file."
                raise ValueError(msg)
            else:
                self.save_field.delete(0, END)
                self.save_field.insert(0, self.output_file) # Put the new output file in the field


    def get_metadata(self):
        """Puts the input metadata in variables"""

        self.movie_title = self.title_field.get()
        self.author = self.author_field.get()
        self.movie_year = self.year_field.get()


    def create_metadata(self):
        """Creates a metadata file with only title, author and year"""

        # Creating the metadata file, and adding the title, author and year (source : http://underpop.online.fr/f/ffmpeg/help/metadata.htm.gz)
        path = os.getcwd()
        with open(path+"/metadata.txt", "w") as f:
            f.write(';FFMETADATA1\n')
            f.write('title='+self.movie_title +
                    '\n') if self.movie_title != '' else None
            f.write('date='+self.movie_year +
                    '\n') if self.movie_year != '' else None
            f.write('artist='+self.author+'\n') if self.author != '' else None
            f.write('\n')

        self.metadata_file = path+"/metadata.txt"


    def add_chapters(self):
        """Creates a metadata file with chapters and subtitles"""

        # Convert the times in milliseconds
        times_ms = [timecode_to_ms(time) for time in self.times]

        # Checks if the video is longer than the last timecode (source : https://ffmpeg.org/ffprobe.html#Main-options)
        video_time_s = float(subprocess.check_output(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', self.movie_file]).decode('utf-8'))
        #os.popen("ffprobe -i \""+movie_file+"\" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1").read()
        video_time_ms = int(float(video_time_s)*1000)

        assert video_time_ms > times_ms[-1], "The video is shorter than the last timecode."

        # Adding the chapters to the metadata file (already created)
        with open(self.metadata_file, "a") as f:

            # Writing the timecodes and titles in the metadata file
            for i in range(len(times_ms)-1):
                f.write('[CHAPTER]\n')
                f.write('TIMEBASE=1/1000\n')
                f.write('# Chapter '+str(i+1)+' starts at '+self.times[i]+'\n')
                f.write('START='+str(times_ms[i])+'\n')
                f.write('# Chapter '+str(i+1)+' ends at ' +
                        self.times[i+1]+' (minus 1 millisecond)\n')
                f.write('END='+str(times_ms[i+1]-1)+'\n')
                f.write('title='+self.chapters[i]+'\n\n')

            # Writing the last timecode and title in the metadata file
            i = len(times_ms)-1
            f.write('[CHAPTER]\n')
            f.write('TIMEBASE=1/1000\n')
            f.write('# Chapter '+str(i+1)+' starts at '+self.times[i]+'\n')
            f.write('START='+str(times_ms[i])+'\n')
            f.write('# Chapter '+str(i+1)+' ends at ' +
                    ms_to_timecode(video_time_ms)+' (minus 1 millisecond)\n')
            f.write('END='+str(video_time_ms)+'\n')
            f.write('title='+self.chapters[i]+'\n\n')


#%% Check system requirements

# Check if ffmpeg is installed
try:
    subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffmpeg is not installed. Please install it before running this app. (https://ffmpeg.org/)"
    Error_Window("Error", err)
    raise SystemExit(err)

# Check if ffprobe is installed
try:
    subprocess.run(['ffprobe', '-version'], stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffprobe is not installed. Please install it before running this app. (https://ffmpeg.org/)"
    Error_Window("Error", err)
    raise SystemExit(err)


#%% Call the app
app = Application()
app.mainloop()

# TODO : in README.md, add ffmpeg installation and how to add it to the PATH






#%% ==================== Q&A ====================

# Q : Propose to install ffmpeg if it is not installed or redirect to a tutorial
# ANSWER : Annoying and OS dependent, leaving it to the user

# Q : Check if FFMPEG handles file conversion (ex : .mp4 to .avi)
# ANSWER : Yes but annoying, I will keep the same extension as the input file

# Q : Verify that ffmpeg can overwrite the file ?
# ANSWER : Not always, to avoid errors we will keep the output file and movie file different.

# Q : Find a way to highlight the final file when opening the folder
# ANSWER : Seems to be possible with subprocess.Popen() but it doesn't works (always opens the user's home folder)

# Q : How could the code be improved ?
# ANSWER : I could use a class for the table and the "add to table" frames. 

# Q : How to compile the code into an executable ?
# ANSWER : The following command, replacing [.] by the path to the Shears code 
# pyinstaller --noconfirm --onefile --windowed --icon "[.]/Shears/Ressources/Shears_icon.ico" --name "Shears" --add-data "[.]/customtkinter;customtkinter/" --add-data "[.]/Shears/Ressources/Shears_icon.ico;Ressources/"  "[.]/Shears/Builds/Shears_UI.py"