import csv
import math
import re
import matplotlib.pyplot as plt

from pyavsubs.utils import ascii_header
from pyavsubs.utils import import_character
from pyavsubs.utils import import_logical
from pyavsubs.utils import match_arg

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
        try:
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
        except FileNotFoundError:
            print(f, "not found for import. Ignoring.")

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
        if (newdata == None):
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

    def setup(self, trn_filenames, trn_to_rev_ratio, f = None):
        n = len(trn_filenames)
        trn_filename = sorted(trn_filenames)
        start_digit = [re.sub(".+(\d{6}).+", "\\1", f)\
                       for f in trn_filename]
        trn_start = [re.sub("(\d{2})(\d{2})(\d{2})", "\\1:\\2:\\3", d) \
                     for d in start_digit]
        rev2_filename = trn_dig_to_rev_fn(start_digit, trn_to_rev_ratio)

        # the dataset
        empty_char = ["" for i in range(n)]
        all_false  = [False for i in range(n)]
        # 
        # trn_filename    = trn_filename
        # trn_start       = trn_start
        trn_assignee    = empty_char
        trn_assigned    = all_false
        trn_completed   = all_false
        ##
        rev1_assignee   = empty_char
        rev1_assigned   = all_false
        rev1_completed  = all_false
        ##
        # rev2_filename   = rev2_filename
        rev2_ready      = all_false
        rev2_created    = all_false
        rev2_assignee   = empty_char
        rev2_assigned   = all_false
        rev2_completed  = all_false

        avanz = []
        for i in range(n):
            avanz.append(Chunk(trn_filename[i], 
                               trn_start[i],    
                               trn_assignee[i],   
                               trn_assigned[i],   
                               trn_completed[i],                  
                               rev1_assignee[i],  
                               rev1_assigned[i],  
                               rev1_completed[i], 
                               rev2_filename[i],
                               rev2_ready[i],     
                               rev2_created[i],   
                               rev2_assignee[i],  
                               rev2_assigned[i],  
                               rev2_completed[i]))
        self.to_disk(f = f, newdata = avanz)
        
    def assignable_files(self, role):
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        res = []
        for c in self.__data:
            if role == 'translator':
                cond = not c.trn_assigned
                res += [c.trn_filename] if cond else []
            elif role == 'revisor1':
                cond = (c.trn_completed) and (not c.rev1_assigned)
                res += [c.trn_filename] if cond else []
            elif role =='revisor2':
                # return unique values here
                cond = (c.rev2_created) and \
                    (not c.rev2_assigned) and \
                    (not c.rev2_filename in res)
                res += [c.rev2_filename] if cond else []
            else:
                raise ValueError("Unexpected role input:", role)
        return res

    def to_be_completed_files(self, role):
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        res = []
        for c in self.__data:
            if role == 'translator':
                cond = c.trn_assigned and (not c.trn_completed)
                res += [c.trn_filename] if cond else []
            elif role == 'revisor1':
                cond = (c.rev1_assigned) and (not c.rev1_completed)
                res += [c.trn_filename] if cond else []
            elif role =='revisor2':
                # return unique values here
                cond = (c.rev2_assigned) and (not c.rev2_completed) and \
                    (not c.rev2_filename in res)
                res += [c.rev2_filename] if cond else []                
            else:
                raise ValueError("Unexpected role input:", role)
        return res

    def filenames(self, phase):
        phase = match_arg(phase, ['trn', 'rev2'])
        res = []
        for c in self.__data:
            if phase == 'trn':
                res += [c.trn_filename]
            elif phase == 'rev2':
                res += [c.rev2_filename] if (c.rev2_filename not in res) \
                    else []
            else:
                raise ValueError("Unexpected role phase:", phase)
        return res
    
    def unfinished_homeworks(self, user, role):
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        res = []
        for c in self.__data:
            if role == 'translator':
                cond = (user == c.trn_assignee) and (c.trn_assigned) and \
                    (not c.trn_completed)
                res += [c.trn_filename] if cond else []
            elif role == 'revisor1':
                cond = (user == c.rev1_assignee) and (c.rev1_assigned) and \
                    (not c.rev1_completed)
                res += [c.rev1_filename] if cond else []
            elif role =='revisor2':
                cond = (user == c.rev2_assignee) and (c.rev2_assigned) and \
                    (not c.rev2_completed)
                res += [c.rev2_filename] if cond else []
            else:
                raise ValueError("Unexpected role input:", role)
        return res

    def assign(self, old_f, assignee, new_f, role):
        role = match_arg(role, ['translator', 'revisor2'])
        for c in self.__data:
            if role == 'translator':
                cond = (c.trn_filename == old_f)
                if cond:
                    c.trn_assignee = assignee
                    c.trn_assigned = True
                    c.trn_filename = new_f
            elif role =='revisor2':
                cond = (c.rev2_filename == old_f)
                if cond:
                    c.rev2_assignee = assignee
                    c.rev2_assigned = True
                    c.rev2_filename = new_f
            else:
                raise ValueError("Unexpected role input:", role)

    def mark_as_started(self, f, assignee, role):
        role = match_arg(role, ['revisor1'])
        for c in self.__data:
            if role == 'revisor1':
                cond = (c.trn_filename == f)
                if cond:
                    c.rev1_assignee = assignee
                    c.rev1_assigned = True
            else:
                raise ValueError("Unexpected role input:", role)

    def mark_as_completed(self, f, phase):
        phase = match_arg(phase, ['trn', 'rev1', 'rev2'])
        rev2_ready = dict()
        rev2_complete = dict()
        for c in self.__data:
            if phase == 'trn':
                if c.trn_filename == f:
                    c.trn_completed = True
            elif phase == 'rev1':
                if c.trn_filename == f:
                    c.rev1_completed = True
                # checking if all rev1 are completed
                if (c.rev2_filename not in rev2_ready.keys()):
                    rev2_ready[c.rev2_filename] = True
                rev2_ready[c.rev2_filename] = \
                    rev2_ready[c.rev2_filename] and c.rev1_completed
            elif phase == 'rev2':
                if c.rev2_filename == f:
                    c.rev2_completed = True
                # checking if all rev2 are completed
                if (c.rev2_filename not in rev2_complete.keys()):
                    rev2_complete[c.rev2_filename] = True
                rev2_complete[c.rev2_filename] = \
                    rev2_complete[c.rev2_filename] and c.rev2_completed
            else:
                raise ValueError("Unexpected phase input:", phase)

        # update creable rev2     
        if phase == 'rev1':
            for c in self.__data:
                c.rev2_ready = rev2_complete[c.rev2_filename]
        
        # checks: tutte le rev2 complete, creazione
        if phase == 'rev2':
            if (all(rev2_complete.values())):
                ascii_header('Tutte le revisioni sono complete')
                ascii_header('creare il file finale con make final-srt')
        
        
    def revs2_todo(self):
        res = []
        for c in self.__data:
            cond = (c.rev2_ready) and (not c.rev2_created) and \
                (not c.rev2_filename in res)
            res += [c.rev2_filename] if cond else []
        return res

    def revs2_created(self, f):
        for c in self.__data:
            if (c.rev2_filename == f):
                c.rev2_created = True

    def get_trn_fn_for_rev2(self, f):
        res = []
        for c in self.__data:
            res += [c.trn_filename] if (c.rev2_filename == f) else []
        return [sorted(res)]
    
    def list_assignee(self):
        print("\n\n")
        print("Time\tTrn\Rev1\tRev2")
        for c in self.__data:
            line = "{0}\t{1}\t{2}\t{3}".format(c.trn_start,
                                               c.trn_assignee,
                                               c.rev1_assignee,
                                               c.rev2_assignee)
            print(line)
        print("\n\n")
        
    def monitoring(self):
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        cols = {'compl' : 'forestgreen',
                'start' : ['gold', 'khaki'][0],
                'todo'  : 'red'}
        alpha = 0.4
        r_width = 0.33333
        r_height = 0.10

        trn_x = 0.0
        rev1_x = trn_x + r_width
        rev2_x = rev1_x + r_width

        # row_id = 0
        # row_y = 1r_height * (row_id + 1)
        # c = plt.Rectangle((trn_x, row_y), r_width, r_height,
        #                   color = cols["compl"], alpha = alpha)
        # s = plt.Rectangle((rev1_x, row_y), r_width, r_height,
        #                   color = cols["start"], alpha = alpha)
        # t = plt.Rectangle((rev2_x, row_y), r_width, r_height,
        #                   color = cols["todo"], alpha = alpha)
        # ax.add_patch(c)
        # ax.add_patch(s)
        # ax.add_patch(t)

        row_id = len(self.__data)
        for c in self.__data: #c is a Chunk
            row_y = r_height * (row_id - 1)
            trn_rec = plt.Rectangle((trn_x, row_y), r_width, r_height,
                                    color = cols["compl"], alpha = alpha)
            rev1_rec = plt.Rectangle((rev1_x, row_y), r_width, r_height,
                                     color = cols["start"], alpha = alpha)
            rev2_rec = plt.Rectangle((rev2_x, row_y), r_width, r_height,
                                     color = cols["todo"], alpha = alpha)
            ax.add_patch(trn_rec)
            ax.add_patch(rev1_rec)
            ax.add_patch(rev2_rec)
            row_id -= 1
        
        fig.show()

# , 'yellow', 'red'
        
if __name__ == '__main__':
    av = Avanz(f = '/home/l/av_it_subs/subs/gymix/zz_avanzamento.csv')
    # print(av)
    # av.to_disk('/tmp/asdomar.csv')
    # av2 = Avanz('/tmp/asdomar.csv')
    # trn_filenames = ["subs_000000.srt", "subs_000500.srt",
    #                  "subs_001000.srt", "subs_001500.srt",
    #                  "subs_002000.srt", "subs_002500.srt",
    #                  "subs_003000.srt", "subs_003500.srt",
    #                  "subs_004000.srt", "subs_004500.srt"]
    # av.setup(f = '/tmp/setup_test.csv',
    #          trn_filenames = trn_filenames,
    #          trn_to_rev_ratio = 6)
    # print("\n\nassignable files")
    # print(av.assignable_files(role = "tr"))
    # print(av.assignable_files(role = "revisor1"))
    # print(av.assignable_files(role = "revisor2"))
    # print("\n\nto be completed files")
    # print(av.to_be_completed_files(role = "tr"))
    # print(av.to_be_completed_files(role = "revisor1"))
    # print(av.to_be_completed_files(role = "revisor2"))
    # print(av.filenames(phase = 'trn'))
    # print(av)
    av.monitoring()
