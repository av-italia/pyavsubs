import csv

class Chunk():
    

class Avanz():

    def __init__(self, f, id):
        self.__id   = id
        self.__f    = f
        self.from_disk()

    def from_disk(self):
        self.__data = []
        with open(file = self.__f) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                c = Chunk(
                    row['trn_filename'],
                    row['trn_start'],
                    row['trn_assignee'],
                    row['trn_assigned'],
                    row['trn_completed'],
                    row['rev1_assignee'],

                    )
                self.__data.append(c)
                
