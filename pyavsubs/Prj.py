import os
import shutil
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

import Users
import Avanz
import AVsrt
from utils import menu
from utils import match_arg
from utils import listing

# Standard locations
# ------------------
# directories
data_dir         = "data"
source_dir       = "source"
subs_dir         = "subs"
sandbox_dir      = os.path.join(subs_dir, "sandbox")
# files
users_file       = os.path.join(data_dir, "users.csv")
sndbx_tmpl_trn   = os.path.join(sandbox_dir, "template_trn.srt")
sndbx_tmpl_rev1  = os.path.join(sandbox_dir, "template_rev1.srt")
raw_gh_path      = "https://raw.githubusercontent.com/av-italia/subs/main"

# funzione che crea il path file per un dato sandbox (dato da user e ruolo)
def sandbox_f(user, role):
    role = match_arg(role, ["translator", "revisor1", "revisor2"])
    if role == "translator":
        postfix = "trn"
    elif role == "revisor1":
        postfix = "rev1"
    elif role == "revisor2":
        postfix = "rev2"
    else:
        ValueError("There is something wrong here")
    return os.path.join(sandbox_dir,
                        "{0}_{1}.srt".format(user, postfix))


class Prj:


    def __init__(self, id = "test",
                 yt_id = "testid",
                 base_dir = "/home/l/av_it_subs"):
        # add base_dir to the standard locations
        def add_basedir(x):
            return os.path.join(base_dir, x)
        # directories
        prj_dir      = add_basedir(os.path.join(subs_dir, id))
        users_f      = add_basedir(users_file)
        source_srt_f = add_basedir(os.path.join(source_dir,
                                                "{0}.srt".format(id)))
        avanz_f      = os.path.join(prj_dir, 'zz_avanzamento.csv')
        final_srt_f  = os.path.join(prj_dir, "{0}_final.srt".format(id))
        # initialization
        self.id           = id
        self.yt_id        = yt_id
        self.users        = Users.Users(f = users_f)
        self.avanz        = Avanz.Avanz(f = avanz_f, id = id)
        self.source_srt_f = source_srt_f
        self.final_srt_f  = final_srt_f
        self.prj_dir      = prj_dir
        self.add_basedir  = add_basedir


    def setup(self, chunks_len_mins = 5, trn_to_rev_ratio = 6):
        # setup the directory or fail if already set up
        if os.path.isdir(self.prj_dir):
            raise ValueError(self.prj_dir + " already exstisting. Aborting.")
        else:
            os.makedirs(self.prj_dir)
        # import and split source .srt
        self.source_srt = AVsrt.AVsrt(f = self.source_srt_f, id = 'source')
        # now split the source and obtain the chunk fnames to set up monitoring
        cfn = self.source_srt.split(chunks_len_mins = chunks_len_mins,
                                    yt_id           = self.yt_id,
                                    output_dir      = self.prj_dir)
        # setup monitoring
        self.avanz.setup(trn_filenames = cfn,
                         trn_to_rev_ratio = trn_to_rev_ratio)
        # setup unsubbed
        unsubbed_f = os.path.join(self.prj_dir, 'zz_UNSUBBED')
        with open(file = unsubbed_f, mode = 'w') as f:
            pass # empty file is fine


    def create_sandbox(self):
        trn_users = menu(title = 'Specificare utenti (TRN) per sandbox',
                         choices  = self.users.translators(),
                         multiple = True)
        rev1_users = menu(title = 'Specificare utenti (REV1) per sandbox',
                          choices  = self.users.revisors1(),
                          multiple = True)
        ## sandbox di translators
        if (len(trn_users)):
            ## notify: header
            ascii_header('sandbox traduttori')
            ## check permissions
            allowed_users = self.users.keep_allowed(trn_users, 'translator')
            if len(allowed_users) == 0:
                ValueError("No allowed users for this request. Aborting.")
            ## files and dirs
            files = [self.add_basedir(sandbox_f(u, role = "translator"))
                     for u in allowed_users]
            template_path = self.add_basedir(sndbx_tmpl_trn)
            # file copy
            for f in files:
                shutil.copyfile(template_path, f)
            # notification
            listing(files)
        ## sandbox di revisori (per revisione 1)
        if (len(rev1_users)):
            ## notify: header
            ascii_header('sandbox revisori (fase 1)')
            ## check permissions
            allowed_users = self.users.keep_allowed(rev1_users, 'revisor1')
            if len(allowed_users) == 0:
                ValueError("No allowed users for this request. Aborting.")
            ## files and dirs
            files = [self.add_basedir(sandbox_f(u, role = "revisor1"))
                     for u in allowed_users]
            template_path = self.add_basedir(sndbx_tmpl_rev1)
            # file copy
            for f in files:
                shutil.copyfile(template_path, f)
            # notification
            listing(files)
                                   

    def keep_sandboxed(self, users, role):
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        avail = []
        miss  = []
        for u in users:
            s = self.add_basedir(sandbox_f(u, role = role))
            if os.path.isfile(s):
                avail.append(u)
            else:
                miss.append(u)
        if len(miss) > 0:
            msg = "Some users have no sandbox file for "
            print(msg, role, "role: ", miss, '. Ignoring the request.')
        return avail


    def keep_swots(self, users, role):
        role = match_arg(role, ['translator', 'revisor1', 'revisor2'])
        swots = []
        for u in users:
            not_completed = self.avanz.unfinished_homeworks(u, role)
            if len(not_completed) > 0:
                print(u, 'has unfinished files:', not_completed,
                      'Ignoring the request')
            else:
                swots.append(u)
        return swots

                  
    def assign(self):
        try:
            # Utility functions
            # -------------------------------------------
            def worker(old_f, assignee, new_f, from_path, to_path, role):
                os.replace(from_path, to_path)
                self.avanz.assign(old_f = old_f, assignee = assignee,
                                  new_f = new_f, role = role)
            def excluded_users_message(u):
                msg = "some users have no assignable files (finished, yee):" 
                print(msg, u, '\n')
            def try_assign(users, role):
                role = match_arg(role, ['translator', 'revisor2'])
                ascii_header(role)
                # check for user pemissions
                users = self.users.keep_allowed(users, role)
                # check for available sandboxes
                users = self.keep_sandboxed(users, role)
                # check for done homeworks
                users = self.keep_swots(users, role)
                # are there remaining users for the request?
                if len(users) == 0:
                    raise ValueError("No user available for this request.")
                # if there are assignable files, do the thing
                assignable_files = self.avanz.assignable_files(role)
                if len(assignable_files):
                    max_assignments = min(len(users), len(assignable_files))
                    assigned_users = []
                    assigned_paths = []
                    for i in range(max_assignments):
                        assignee = users[i]
                        assigned_users.append(assignee)
                        old_f = assignable_files[i]
                        old_p = os.path.join(self.prj_dir, old_f)
                        new_f = "{0}_{1}.srt".format(
                            os.path.splitext(old_f)[0],
                            assignee
                        )
                        assigned_paths.append(new_f)
                        new_p = os.path.join(self.prj_dir, new_f)
                        worker(old_f, assignee, new_f, old_p, new_p, role)
                    # do list paths for translators
                    if role == 'translator':
                        listing(assigned_paths)
                    elif role == 'revisor2':
                        rev2_urls = ["{0}/{1}".format(raw_gh_path, p) for
                                p in assigned_paths]
                        listing(rev2_urls)
                    else:
                        ValueError("Something wrong here")
                else:
                    print("No assignable files, all done, yee!")
                        
            # Main
            # -------------------------------------------
            assignable_trn = self.avanz.assignable_files('translator')
            assignable_rev2 = self.avanz.assignable_files('revisor2')
            # and if so go for assignment
            if len(assignable_trn):
                trn_users = menu(
                    title = 'Specificare utenti (TRN) per sandbox',
                    choices  = self.users.translators(),
                    multiple = True)
                if len(trn_users):
                    try_assign(trn_users, 'translator')
            # There are files for revision
            if len(assignable_rev2):
                rev2_users = menu(
                    title = 'Specificare utenti (REV2) per sandbox',
                    choices  = self.users.revisors1(),
                    multiple = True)
                if len(rev2_users):
                    try_assign(rev2_users, 'revisor2')
        finally:
            self.avanz.to_disk()


    def mark_progresses(self):
        pass


    def make_final_srt(self, stats = True):
        pass

    
    def final_srt_stats(self):
        # obtain output file for stats
        Tk().withdraw() 
        outfile = asksaveasfilename(
            title = "Save subtitles statistics as csv:",
            initialfile = '{0}_stats'.format(self.id),
            defaultextension = '.csv')
        AVsrt.AVsrt(f = self.final_srt_f, id = self.id).stats(f = outfile)

    
    def list_assignee(self):
        self.avanz.list_assignee()

    
    def list_users(self):
        print(self.users)

    
    def available_rev1(self):
        self.users.mention("revisor1")
        msg 
        print(": files attualmente disponibili per la revisione linguistica:\n\n")
        listing(self.avanz.assignable_files('revisor1'))
        print("\n")
            
    
    def available_rev2(self):
        self.users.mention("revisor2")
        msg 
        print(": files attualmente disponibili per la revisione linguistica:\n\n")
        listing(self.avanz.assignable_files('revisor2'))
        print("\n")

    
    def monitoring(self):
        self.avanz.monitoring()

if __name__ == '__main__':
    prj = Prj()
    ##### prj.setup()
    # prj.setup()
    prj.create_sandbox()
