# Shear

Shear is a simple tool for adding chapters to a video file. It is designed to be used with [FFmpeg](https://ffmpeg.org/), and is written in Python 3.

## Installation
For Windows systems, download the latest release from the [releases page](). It is a portable executable.

For linux or MacOs systems, you will need to download the source code, and compile the executable with [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/). 

Dependencies are listed in `requirements.txt`.

### Detailled installation
1. Download the latest release from the [releases page]().
2. Download the latest version of [FFmpeg](https://ffmpeg.org/download.html).
3. Extract the FFmpeg build to a folder.
4. Add the path to the FFmpeg executable to your PATH environment variable.
5. Extract the Shear release to a folder.
6. Install the dependencies with `pip install -r requirements.txt`.
7. Compile `Shear_UX.py` with `auto-py-to-exe`.
8. Run Shear.exe
9. Select the video file you want to add chapters to.
10. Select the chapters file.
11. Select the output file.
12. You can add a title, an author and a year to the metadata of the output file.

## Usage
Shear is designed to be used with [FFmpeg](https://ffmpeg.org/).

The video files used can be any format that FFmpeg supports. The output file will be of the same format as the input file.

The chapters file should be a text file, with each line containing the start time and end time of a chapter. The times should be in the format `HH:MM:SS` or `MM:SS`.

**Warning:** The chapters must be in order, because I don't know at the moment if they will be reordered by FFmpeg.

In the files, you will also find a `Shear.py` file. This is a Python script that can be used to add chapters to a video file. It is not recommended to use it, because it is not as user-friendly as the executable, but can be used with arguments. The syntax is as follows:

`Shear.py <input file> <chapters file> [-h] [-o <output file>] [-mt <movie title>] [-a <author>] [-y <year>]`


## More to come !
I plan to add more features to Shear, such as:

- [ ] Making the whole process in one GUI window (using [`CustomTkinter`](https://github.com/TomSchimansky/CustomTkinter))
- [ ] Adding an installation tool (if possible)
- [ ] Display the chapters in the GUI (long term goal)