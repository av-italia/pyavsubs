import re
import math

def import_logical(x):
    """
    Function to import logical values saved in csv
    """
    if ((x == "TRUE") or (x == "True") or (x == True)):
        return True
    elif (x == "NA") or (x == None) or (x == ""):
        return None
    else:
        return False

def import_character(x):
    """
    Function to import characters values saved in csv
    """
    if (x == "" or x == "NA"):
        return None
    else:
        return str(x)

def match_arg(arg, choices):
    res = [expanded for expanded in choices \
           if expanded.startswith(arg)]
    l = len(res)
    if l == 0:
        raise ValueError("Parameter ", arg, "must be one of ", choices)
    elif l > 1:
        raise ValueError(arg, "matches multiple choices from ", choices)
    else:
        return res[0]

def ascii_header(x):
    l = len(x)
    header = ("=" * l)
    print(header)
    print(x.upper())
    print(header, '\n')

def listing(x):
    for i in x:
        print(i)
    print("\n")
