import re
import math

def import_logical(x):
    """
    Function to import logical values saved in csv by R
    """
    if ((x == "TRUE") or (x == "True") or (x == True)):
        return True
    elif (x == "NA") or (x == None):
        return None
    else:
        return False

def import_character(x):
    if (x == "" or x == "NA"):
        return None
    else:
        return str(x)

def check_input(x, ok):
    if (x in ok):
        return x
    else:
        ValueError(x, "can be only in ", ok)

def trn_dig_to_rev_fn(std, ratio):
    n_revs = math.floor(len(std)/ratio) + 1
    start_rev = std[::ratio]
    stop_rev  = std[ratio -1: :ratio]
    # add last if missing
    last = std[len(std) - 1]
    if last not in stop_rev:
        stop_rev.append(last) 
    revs = ["{0}_{1}.srt".format(sta, sto) \
            for sta, sto in zip(start_rev, stop_rev)]
    # ripeti ogni elemento ratio volte
    revs = [r for r in revs for prog in range(ratio)]
    # tieni solo quelle utili
    return revs[:len(std):]
        
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
    
    
