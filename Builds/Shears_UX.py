##################################################################
## Shears_UX.py : Script to add chapters to a video file,       ##
## given the timecodes and titles of the chapters,              ##
## with graphic interface.                                      ##
##################################################################
## Author: 	S. Bouchard                                         ##
## Date: 	2020-05-05                                          ##
## Version: 	1.0                                             ##
##################################################################
## Requirements: 	ffmpeg, python3, tkinter                    ##
##################################################################
##          Executable created with auto-py-to-exe              ##
##        (https://pypi.org/project/auto-py-to-exe/)            ##
##################################################################
## Changelog:                                                   ##
## 2020-05-05: 	Initial release                                 ##
##################################################################


#%% Start
import os, subprocess
from subprocess import CREATE_NO_WINDOW

from Functions import timecode_to_ms, ms_to_timecode, parse_timecodes as parse, Error_Window, Info_Window


#%% Check system requirements

# Check if ffmpeg is installed
try:
    subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffmpeg is not installed. Please install it before running this script. (https://ffmpeg.org/)"
    Error_Window("Error", err)
    raise SystemExit(err)

# Check if ffprobe is installed
try:
    subprocess.run(['ffprobe', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffprobe is not installed. Please install it before running this script. (https://ffmpeg.org/)"
    Error_Window("Error", err)
    raise SystemExit(err)


#%% Selecting files with graphical interface (Pyhton version in graphical interface)
from tkinter import Tk #(source : https://tkdocs.com/)
from tkinter.filedialog import askopenfilename, asksaveasfilename

#Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
root = Tk()
root.withdraw() # Hides the root window
root.title("Movie details") # Sets the title of the root window

# Selecting the movie file and the timecodes file
movie_file = askopenfilename(title='Select the movie', filetypes=[('Video files', ('*.mp4', '*.mkv', '*.avi')),("all files","*.*")])
# Raise an error if no file is selected
if movie_file == '':
    raise SystemExit("No movie file selected")

timecodes_file = askopenfilename(title='Select the timecodes file', filetypes=[('Text files', '*.txt'),("all files","*.*")])
# Raise an error if no file is selected
if timecodes_file == '':
    raise SystemExit("No timecodes file selected")

# Setting the output file
movie_file_extension = os.path.splitext(movie_file)[1]
output_file = asksaveasfilename(title='Select the output file')

# Raise an error if no file is selected
if output_file == '':
    raise SystemExit("Process cancelled by user (no output file selected)")

# Replace the extension of the output file with the extension of the movie file (if not already the case)
if os.path.splitext(output_file)[1] != movie_file_extension :
    output_file = os.path.splitext(output_file)[0] + movie_file_extension
    
# Checks if the output file is the same as the input file
if output_file == movie_file:
    err = "The output file cannot be the same as the input file"
    Error_Window("Error", err)
    raise SystemExit(err)

# Checks if the output file already exists : The user has then already been asked if he wants to overwrite it by tkinter
if os.path.isfile(output_file):
    os.remove(output_file)


# One dialog box with three fields to input the movie title, author and year
from tkinter import simpledialog, Label, Entry, Tk

class MyDialog(simpledialog.Dialog):
        
    def body(self, master):
        """Create dialog body.  Return widget that should have initial focus.

        Args:
            master (_type_): master widget -- the parent window, in this case the dialog

        Returns:
            _type_: widget -- the widget that should have the initial focus when the dialog is created
        """
        
        # Creates a message to display in bold on the first row of the dialog box
        Label(master, text="Enter the movie details (leave empty if not needed) :", font='Helvetica 10 bold').grid(row=0, column=0, columnspan=2, sticky="w")

        # Creates the labels for the entry fields
        Label(master, text="Movie title:").grid(row=1, column=0, sticky="w")
        Label(master, text="Author:").grid(row=2, column=0, sticky="w")
        Label(master, text="Year:").grid(row=3, column=0, sticky="w")

        # Creates the entry fields
        self.e1 = Entry(master)
        self.e2 = Entry(master)
        self.e3 = Entry(master)

        # Places the entry fields in the dialog box
        self.e1.grid(row=1, column=1)
        self.e2.grid(row=2, column=1)
        self.e3.grid(row=3, column=1)
        
        return self.e1 # initial focus

    def apply(self):
        """This method is called when the user hits the OK button.
            It sets the result to be the text of the entry widget.
        """
        # Gets the text from the entry fields
        movie_title = self.e1.get()
        author = self.e2.get()
        movie_year = self.e3.get()
        
        # Sets the result to be the text from the entry fields
        self.result = movie_title, author, movie_year
        
d = MyDialog(root) # Creates the dialog box
try:
    movie_title, author, movie_year = d.result # Gets the result from the dialog box
except TypeError: # Gets TypeError if the user cancels (self.result is then None)
    raise SystemExit("Process cancelled by user")

root.destroy() # Destroys the root window to clean up


#%% Actual code 

# Open a text file in which are put the inputs and parsing them
with open(timecodes_file) as f:
    lines = f.read()

input = lines.split("\n")

# Extracting the timecodes and titles
times, titles = parse(input)

# Converting the timecodes to milliseconds
times_ms = [timecode_to_ms(t) for t in times]

# Checking if the video is longer than the last timecode (source :  https://ffmpeg.org/ffprobe.html#Main-options)
video_time_s = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', movie_file]).decode('utf-8'))
#os.popen("ffprobe -i \""+movie_file+"\" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1").read()
video_time_ms = int(float(video_time_s)*1000)
try:
    assert video_time_ms > times_ms[-1]
except AssertionError:
    err = "The video is shorter than the last timecode. Please check the timecodes."
    Error_Window("Error", err)
    raise SystemExit("The video is shorter than the last timecode")

# print("Video time: "+str(video_time_ms)+" ms")
# print("Last timecode: "+str(times_ms[-1])+" ms")

# Creating the metadata file (source : http://underpop.online.fr/f/ffmpeg/help/metadata.htm.gz)
path = os.getcwd()
with open(path+"/metadata.txt", "w") as f:
    f.write(';FFMETADATA1\n')
    f.write('title='+movie_title+'\n') if movie_title != '' else None
    f.write('date='+movie_year+'\n') if movie_year != '' else None
    f.write('artist='+author+'\n') if author != '' else None
    f.write('\n')
    
    # Writing the timecodes and titles in the metadata file
    for i in range(len(times_ms)-1):
        f.write('[CHAPTER]\n')
        f.write('TIMEBASE=1/1000\n')
        f.write('# Chapter '+str(i+1)+' starts at '+times[i]+'\n')
        f.write('START='+str(times_ms[i])+'\n')
        f.write('# Chapter '+str(i+1)+' ends at '+times[i+1]+' (minus 1 millisecond)\n')
        f.write('END='+str(times_ms[i+1]-1)+'\n')
        f.write('title='+titles[i]+'\n\n')
    
    # Writing the last timecode and title in the metadata file
    i = len(times_ms)-1
    f.write('[CHAPTER]\n')
    f.write('TIMEBASE=1/1000\n')
    f.write('# Chapter '+str(i+1)+' starts at '+times[i]+'\n')
    f.write('START='+str(times_ms[i])+'\n')
    f.write('# Chapter '+str(i+1)+' ends at '+ms_to_timecode(video_time_ms)+' (minus 1 millisecond)\n')
    f.write('END='+str(video_time_ms)+'\n')
    f.write('title='+titles[i]+'\n\n')

# Adding the metadata to the video (source : https://ffmpeg.org/ffmpeg.html#Synopsis)
cmd = "ffmpeg -y -i \""+movie_file+"\" -i \""+path+"/metadata.txt\" -map_metadata 1 -codec copy \""+output_file+"\" -v error"
try : # Should allways work, but just in case
    if subprocess.run(cmd, capture_output=True, creationflags=CREATE_NO_WINDOW).returncode != 0:
        raise OSError("ffmpeg failed. Try to run this command in terminal to see the error : \n"+cmd)
    else : 
        # Create an information window to tell the user that the process is finished
        Info_Window("Success", "The video has been successfully processed.\n\nThe output file is : "+output_file)
        # Open the directory where the output file is
        # os.startfile(os.path.dirname(output_file))
        # Deleting the metadata file to keep the folder clean
        os.remove(path+"/metadata.txt")
except OSError as e:
    Error_Window("Error", e)
    print(e)