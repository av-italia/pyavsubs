import csv
import re

from utils import import_logical
from utils import import_character
from utils import check_input


class Chunk():
    """
    Single chunk of a translation: memorize several status indicator
    and infos (assignee etc)
    """
    def __init__(self,
                 trn_filename,
                 trn_start,
                 trn_assignee,
                 trn_assigned,
                 trn_completed,
                 rev1_assignee,
                 rev1_assigned,
                 rev1_completed,
                 rev2_filename,
                 rev2_ready,
                 rev2_created,
                 rev2_assignee,
                 rev2_assigned,
                 rev2_completed):

        self.trn_filename   = import_character(trn_filename)
        self.trn_start      = import_character(trn_start)
        self.trn_assignee   = import_character(trn_assignee)
        self.trn_assigned   = import_logical(trn_assigned)
        self.trn_completed  = import_logical(trn_completed)
        self.rev1_assignee  = import_character(rev1_assignee)
        self.rev1_assigned  = import_logical(rev1_assigned)
        self.rev1_completed = import_logical(rev1_completed)
        self.rev2_filename  = import_character(rev2_filename)
        self.rev2_ready     = import_logical(rev2_ready)
        self.rev2_created   = import_logical(rev2_created)
        self.rev2_assignee  = import_character(rev2_assignee)
        self.rev2_assigned  = import_logical(rev2_assigned)
        self.rev2_completed = import_logical(rev2_completed)

    def __str__(self):
        msg = \
        "trn_filename  : " + str(self.trn_filename)   + "\n" + \
        "trn_start     : " + str(self.trn_start)      + "\n" + \
        "trn_assignee  : " + str(self.trn_assignee)   + "\n" + \
        "trn_assigned  : " + str(self.trn_assigned)   + "\n" + \
        "trn_completed : " + str(self.trn_completed)  + "\n" + \
        "rev1_assignee : " + str(self.rev1_assignee)  + "\n" + \
        "rev1_assigned : " + str(self.rev1_assigned)  + "\n" + \
        "rev1_completed: " + str(self.rev1_completed) + "\n" + \
        "rev2_filename : " + str(self.rev2_filename)  + "\n" + \
        "rev2_ready    : " + str(self.rev2_ready)     + "\n" + \
        "rev2_created  : " + str(self.rev2_created)   + "\n" + \
        "rev2_assignee : " + str(self.rev2_assignee)  + "\n" + \
        "rev2_assigned : " + str(self.rev2_assigned)  + "\n" + \
        "rev2_completed: " + str(self.rev2_completed) + "\n\n"
        return msg
        
class Avanz():

    def __init__(self, f = None, id = None):
        self.__id   = id
        self.__f    = f
        self.from_disk()

    def from_disk(self, f = None):
        self.__data = []
        if (f == None):
            f = self.__f
        with open(file = f) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                c = Chunk(row['trn_filename']  ,              
                          row['trn_start']     ,
                          row['trn_assignee']  ,
                          row['trn_assigned']  ,
                          row['trn_completed'] ,
                          row['rev1_assignee'] ,
                          row['rev1_assigned'] ,
                          row['rev1_completed'],
                          row['rev2_filename'] ,
                          row['rev2_ready']    ,
                          row['rev2_created']  ,
                          row['rev2_assignee'] ,
                          row['rev2_assigned'] ,
                          row['rev2_completed'])
                self.__data.append(c)

    def __str__(self):
        """
        List all the data
        """
        print("")
        for u in self.__data:
            print(u)
        return ""

    def to_disk(self, f = None, newdata = None):
        if (f == None):
            f = self.__f
        if (newdata = None):
            export = self.__data
        else:
            export = newdata
        with open(f, 'w') as csvfile:
            fieldnames = ['trn_filename', 'trn_start' ,
                          'trn_assignee', 'trn_assigned', 'trn_completed',
                          'rev1_assignee', 'rev1_assigned', 'rev1_completed',
                          'rev2_filename', 'rev2_ready', 'rev2_created',
                          'rev2_assignee', 'rev2_assigned', 'rev2_completed']
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            for chunk in export:
                writer.writerow({
                    'trn_filename'  : chunk.trn_filename,  
                    'trn_start'     : chunk.trn_start,     
                    'trn_assignee'  : chunk.trn_assignee,  
                    'trn_assigned'  : chunk.trn_assigned,  
                    'trn_completed' : chunk.trn_completed, 
                    'rev1_assignee' : chunk.rev1_assignee, 
                    'rev1_assigned' : chunk.rev1_assigned ,
                    'rev1_completed': chunk.rev1_completed,
                    'rev2_filename' : chunk.rev2_filename ,
                    'rev2_ready'    : chunk.rev2_ready    ,
                    'rev2_created'  : chunk.rev2_created  ,
                    'rev2_assignee' : chunk.rev2_assignee ,
                    'rev2_assigned' : chunk.rev2_assigned ,
                    'rev2_completed': chunk.rev2_completed
                })


    def setup(self, trn_filenames, trn_to_rev_ratio):
        trn_filenames = sorted(trn_filenames)
        
    

    def assignable_files(self, role):
        pass

    def to_be_completed_files(self, role):
        pass

    def filenames(self, phase):
        pass

    def list_assignee(self):
        pass

    def unfinished_homeworks(self):
        pass

    def assign(self, old_f, assignee, new_f, role):
        pass

    def mark_as_completed(self, f, phase):
        pass

    def revs2_todo(self):
        pass

    def revs2_created(self):
        pass

    def get_trn_fn_for_rev2(self):
        pass
    
    def monitoring(self):
        pass

if __name__ == '__main__':
    av = Avanz(f = '/home/l/av_it_subs/subs/gymix/zz_avanzamento.csv')
    print(av)
    av.to_disk('/tmp/asdomar.csv')
    av2 = Avanz('/tmp/asdomar.csv')
