import csv

from utils import import_character
from utils import import_logical
from utils import match_arg

class User():
    """
    Single user class: memorize GitHub username and roles (translator,
    revisor1 and revisor2) 
    """
    
    def __init__(self, gh_user, translator, revisor1, revisor2):
        self.gh_user    = gh_user
        self.translator = translator
        self.revisor1   = revisor1
        self.revisor2   = revisor2

    def __str__(self):
        msg = "user: {0}, trn: {1}, rev1: {2}, rev2: {3}".format(
            self.gh_user,
            self.translator,
            self.revisor1,  
            self.revisor2)
        return msg
      

class Users():
    """
    Users (translators, revisors) of the project
    """
    
    def __init__(self, f):
        """
        Initialize data importing from csv
        """

        self.__data = []
        
        with open(file = f) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                commented = row['gh_user'].startswith("#")
                if not commented:
                    u = User(import_character(row['gh_user']),
                             import_logical(row['translator']),
                             import_logical(row['revisor1']),
                             import_logical(row['revisor2']))
                    self.__data.append(u)

    def __str__(self):
        """
        List all the data
        """
        print("")
        for u in self.__data:
            print(u)
        return ""
    
    def translators(self):
        """
        Returns GitHub login name for translators
        """
        return [u.gh_user for u in self.__data if u.translator]
            

    def revisors1(self):
        """
        Returns GitHub login name for linguistic revisors
        """
        return [u.gh_user for u in self.__data if u.revisor1]


    def revisors2(self): 
        """
        Returns GitHub login name for readability revisors
        """
        return [u.gh_user for u in self.__data if u.revisor2]

    def mention(self, role):
        """
        Summon gh users
        """
        if role == 'translators':
            us = self.translators()
        elif role == 'revisors1':
            us = self.revisors1()
        elif role == 'revisors2':
            us = self.revisors2()
        else:
            msg = "role must be 'translators', 'revisors1' or 'revisors2'"
            raise ValueError(msg)
        tags = ["@" + u for u in us]
        return " ".join(tags)

    def keep_allowed(self, users, role):
        ## input github logins and check that are allowed as role
        ## siano stati abilitati in data/users.csv (a seconda del permesso
        ## specificato) restituisce gli utenti abilitati, segnala se ve ne
        ## sono di non abilitati e interrompe se nessuno è abilitato
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        if role == 'translator':
            allowed = self.translators()
        elif role == 'revisor1':
            allowed = self.revisors1()
        elif  role == 'revisor2':
            allowed = self.revisors2()
        else:
            ValueError("there is something wrong here.")
        rval = []
        for u in users:
            if u in allowed:
                rval.append(u)
            else:
                print("Ignoring request for", u, ". Not allowed")
        return rval
        
if __name__ == '__main__':
    u = Users('/home/l/av_it_subs/data/users.csv')
    u
    # u.mention(role = 'revisors2')
    # u.translators()
    # u.revisors1()
    # u.revisors2()
