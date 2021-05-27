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


def menu(title = None, choices = None, multiple = False, strict = False):
    available_ind = [i + 1 for i in range(len(choices))]
    avail_with_0  = [0] + available_ind
    the_menu = "\n".join([str(i) + '. '+ str(c)
                          for i, c in zip(available_ind, choices)])

    if multiple:
        msg = "Selection (values as '1, 2-3, 6') or 0 to exit: "
    else:
        msg = "Selection (0 to exit): "

    if title:
        print(title, "\n")

    print(the_menu, "\n\n", msg)
          
    return the_menu
