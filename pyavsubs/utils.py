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
    
