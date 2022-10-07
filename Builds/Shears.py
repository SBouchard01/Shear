##################################################################
## Shears.py : Script to add chapters to a video file,          ##
## given the timecodes and titles of the chapters.              ##
##################################################################
## Author: 	S. Bouchard                                         ##
## Date: 	2020-05-05                                          ##
## Version: 	1.0                                             ##
##################################################################
## Requirements: 	ffmpeg, python3, argparse                   ##
##################################################################
## Usage: Shears.py [-h] [-mt MOVIE_TITLE]                      ##
##        [-a AUTHOR] [-y YEAR] [-o OUTPUT] movie_file chapters ##
##################################################################
## Changelog:                                                   ##
## 2020-05-05: 	Initial release                                 ##
##################################################################


#%% Start
import os, subprocess#, re
from subprocess import CREATE_NO_WINDOW

from Functions import timecode_to_ms, ms_to_timecode, parse_timecodes as parse

#%% Check system requirements
# Check if ffmpeg is installed
import subprocess
try:
    subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffmpeg is not installed. Please install it before running this script. (https://ffmpeg.org/)"
    raise SystemExit(err)

# Check if ffprobe is installed
try:
    subprocess.run(['ffprobe', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, creationflags=CREATE_NO_WINDOW)
except:
    err = "ffprobe is not installed. Please install it before running this script. (https://ffmpeg.org/)"
    raise SystemExit(err)


#%% Parsing arguments (Pyhton version in command line)
import argparse
parser = argparse.ArgumentParser(description='Adds chapters to a video file, given the timecodes and titles of the chapters.')

# Positional arguments (required)
parser.add_argument('movie_file', type=str, help='The path to the video file to add chapters to.')
parser.add_argument('chapters', type=str, help='The path to the file containing the timecodes and titles of the chapters.')

# Optional arguments (not required)
parser.add_argument('-mt', '--movie-title', type=str, help='Title of the movie', default='')
parser.add_argument('-a', '--author', type=str, help='Author of the movie', default='')
parser.add_argument('-y', '--year', type=str, help='Year of the movie', default='')

parser.add_argument('-o', '--output', type=str, help='Output file name (without extension)', default='')

# Parse the arguments
args = parser.parse_args()

# Movie title, author and year
movie_title = args.movie_title
author = args.author
movie_year = args.year

movie_file = args.movie_file # Path to the movie file
timecodes_file = args.chapters # Path to the timecodes file
path = os.path.dirname(args.movie_file) # Path to the movie file folder
movie_extension = os.path.splitext(args.movie_file)[1] # Extension of the movie file

# Output file name (if not specified, use the movie title)
output_file = os.path.join(path, movie_title + '_modified' + movie_extension) if args.output == '' else os.path.join(path, args.output + movie_extension)

# Checks if the output file is the same as the input file
if output_file == movie_file:
    err = "The output file cannot be the same as the input file"
    raise SystemExit(err)

# Checks if the output file already exists. Asks the user if they want to overwrite it.
if os.path.isfile(output_file):
    print("The output file already exists. Do you want to overwrite it? (y/n)")
    answer = input()
    if answer.lower() != 'y':
        raise SystemExit("Exiting the script. (The output file already exists)")
    os.remove(output_file)
    

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
video_time_ms = int(float(video_time_s)*1000)
try:
    assert video_time_ms > times_ms[-1]
except AssertionError:
    err = "The video is shorter than the last timecode. Please check the timecodes."
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
        # Deleting the metadata file to keep the folder clean
        os.remove(path+"/metadata.txt")
        print("File created : "+output_file)
except OSError as e:
    print(e)