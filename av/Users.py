import pandas as pd

class Users():
    """
    Users (translators, revisors) of the project
    """
    
    def __init__(self, f):
        """
        Initialize data importing from csv
        """
        self.__data = pd.read_csv(f, comment = '#')

    def list_users(self):
        """
        List all the data
        """
        print(self.__data)
        
    def translators(self):
        """
        Returns GitHub login name for translators
        """
        pass

    def revisors1(self):
        """
        Returns GitHub login name for linguistic revisors
        """
        pass

    def revisors2(self): 
        """
        Returns GitHub login name for readability revisors
        """
        pass

    def mention(self, role):
        if role == 'translator':
            pass
        elif role == 'revisor1':
            pass
        elif role == 'revisor2':
            pass
        else:
            pass        
        
        

if __name__ == '__main__':
    u = Users('/home/l/av_it_subs/data/users.csv')
    u.list_users()
