import re

def timecode_to_ms(timecode):
    """Converts a timecode to milliseconds

    Args:
        timecode (str): A string of the form "HH:MM:SS" or "MM:SS"

    Returns:
        ms (int): The timecode in milliseconds
    """
    # Splitting the timecode into hours, minutes and seconds
    if len(timecode.split(":")) == 3:
        H, M, S = timecode.split(":")
    elif len(timecode.split(":")) == 2:
        H = 0
        M, S = timecode.split(":")
    else:
        raise ValueError("The timecode is not in the correct format")
    
    # Converting the timecode to milliseconds
    ms = int(H) * 3600000 + int(M) * 60000 + int(S) * 1000
    
    return ms


def ms_to_timecode(ms):
    """Converts milliseconds to a timecode

    Args:
        ms (float): The time in milliseconds

    Returns:
        timecode (str): The timecode in the form HH:MM:SS
    """
    # Converting the time in seconds
    s = ms / 1000
    
    # Converting the time in hours, minutes and seconds
    H = int(s // 3600)
    M = int((s % 3600) // 60)
    S = int(s % 60)
    
    # Formatting the timecode
    timecode = "{:02d}:{:02d}:{:02d}".format(H, M, S)
    
    return timecode


def escape_characters(string):
    """takes a string and adds a backslash before the following characters : =, ;, #, \\

    Args:
        string (str): The string to modify

    Returns:
        string (str): The modified string
    """
    for char in [":", "=", ";", "#", "\\"]:
        string = string.replace(char, "\\" + char)
    return string


def parse_timecodes(L: list = input) -> list:
    """Parses a string to extract timecodes and titles

    Args:
        input (list): A list of timecodes followed by titles

    Returns:
        times (list): list of timecodes
        titles (list): list of titles
    """
    # Creating the variables to return
    times=[]
    titles=[]
    
    # Extracting the timecodes and titles from L
    for i in range (len(L)):
        T = L[i].split(" ") # Splitting the data in words
        t = re.search(r"(\d+:\d+:\d+|\d+:\d+)", L[i]) # Extracting the timecode with a regular expression, either HH:MM:SS or MM:SS
        
        # If we can't find a timecode, we skip the line
        if t == None:
            continue
        else :
            t = t.group()
            T.remove(t) # Removing the timecode from the list of words
            s = " ".join(T) # Joining the remaining words to form the title
            
            # Appending the timecode and title to the lists
            times.append(t)
            titles.append(escape_characters(s)) # Escaping the characters that could cause problems with ffmpeg
            
    # Checks if the number of timecodes and titles are the same
    if len(times) != len(titles):
        raise ValueError("The number of timecodes and titles are not the same")
        
    return times, titles


def Error_Window(title, message):
    """Displays an error window

    Args:
        title (str): The title of the window
        message (str): The message to display
    """
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()
    
def Info_Window(title, message):
    """Displays an information window

    Args:
        title (str): The title of the window
        message (str): The message to display
    """
    import tkinter as tk
    from tkinter import messagebox
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title, message)
    root.destroy()