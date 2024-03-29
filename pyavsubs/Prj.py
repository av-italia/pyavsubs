import os
import shutil
# from tkinter import Tk
# from tkinter.filedialog import asksaveasfilename

from pyavsubs.Users import Users
from pyavsubs.Avanz import Avanz
from pyavsubs.AVsrt import AVsrt
from pyavsubs.utils import ascii_header
from pyavsubs.utils import menu
from pyavsubs.utils import match_arg
from pyavsubs.utils import listing

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

# external programs
img_viewer = 'feh -F'
browser = 'firefox'

# www-urls
github_repo = "https://github.com/av-italia/subs/tree/main/subs/"
raw_gh_path = "https://raw.githubusercontent.com/av-italia/subs/main"

# File templates
# --------------
# zz_UNSUBBED
unsubbed_tmpl = """\
========
Template
========
00:00:33
## Testo inglese
Testo tradotto in italiano

=================================================
Inserire qui sotto
=================================================

"""


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

    def __init__(self,
                 id = "test",
                 yt_id = "testid",
                 base_dir = "."
                 # base_dir = "/home/l/av_it_subs"
    ):
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
        self.users        = Users(f = users_f)
        self.avanz        = Avanz(f = avanz_f, id = id)
        self.source_srt_f = source_srt_f
        self.final_srt_f  = final_srt_f
        self.prj_dir      = prj_dir
        self.add_basedir  = add_basedir


    def setup(self, chunks_len_mins = 5, trn_to_rev_ratio = 6):
        # setup the directory or fail if already set up
        if os.path.isdir(self.prj_dir):
            print(self.prj_dir + " already exstisting. Ignoring setup request.")
        else:
            os.makedirs(self.prj_dir)
            # import and split source .srt
            self.source_srt = AVsrt(f = self.source_srt_f, id = 'source')
            # now split the source and obtain the chunk fnames to set up monitoring
            cfn = self.source_srt.split(chunks_len_mins = chunks_len_mins,
                                        yt_id           = self.yt_id,
                                        output_dir      = self.prj_dir)
            # setup monitoring (and reloading)
            self.avanz.setup(trn_filenames = cfn,
                             trn_to_rev_ratio = trn_to_rev_ratio)
            self.avanz.from_disk()
            # setup unsubbed
            unsubbed_f = os.path.join(self.prj_dir, 'zz_UNSUBBED')
            with open(file = unsubbed_f, mode = 'w') as f:
                f.write(unsubbed_tmpl)


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
            template_path = sndbx_tmpl_trn
            files = [sandbox_f(u, role = "translator") for u in allowed_users]
            # file copy
            for f in files:
                shutil.copyfile(self.add_basedir(template_path),
                                self.add_basedir(f))
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
            template_path = sndbx_tmpl_rev1
            files = [sandbox_f(u, role = "revisor1") for u in allowed_users]
            # file copy
            for f in files:
                shutil.copyfile(self.add_basedir(template_path),
                                self.add_basedir(f))
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
                        new_p = os.path.join(self.prj_dir, new_f)
                        assigned_paths.append(new_p)
                        worker(old_f, assignee, new_f, old_p, new_p, role)
                    # remove ./ from the path for pretty printing
                    assigned_paths = [p[2:] for p in assigned_paths]
                    # do list paths for translators
                    if role == 'translator':
                        listing(assigned_paths) #todohere
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
                    title = 'Specificare utenti (TRN) per assegnazione traduzione',
                    choices  = self.users.translators(),
                    multiple = True)
                if len(trn_users):
                    try_assign(trn_users, 'translator')
            # There are files for revision
            if len(assignable_rev2):
                rev2_users = menu(
                    title = 'Specificare utenti (REV2) per assegnazione revisione',
                    choices  = self.users.revisors2(),
                    multiple = True)
                if len(rev2_users):
                    try_assign(rev2_users, 'revisor2')
        finally:
            self.avanz.to_disk()


    def mark_progresses(self):
        # do all the stuff and save to disk avanz on exit
        try:
            # --------------
            # completed TRN
            # -------------
            trn_in_progress = self.avanz.to_be_completed_files('translator')
            if (trn_in_progress):
                compl_trn = menu(
                    title = 'Specificare files (TRN) per i quali è stata COMPLETATA la TRADUZIONE',
                    choices  = trn_in_progress,
                    multiple = True)
                for t in compl_trn:
                    self.avanz.mark_as_completed(t, 'trn')
                # notify revisors
                if compl_trn:
                    self.available_rev1()
            # -------------
            # started REV1
            # ------------
            assignable_rev1 = self.avanz.assignable_files('revisor1')
            if assignable_rev1:
                started_rev1 = menu(
                    title = 'Specificare files (REV1) per i quali è INIZIATA la PRIMA REVISIONE (LINGUISTICA)',
                    choices  = assignable_rev1,
                    multiple = True)
                for r in started_rev1:
                    u = menu(title = 'Chi è il revisore di: {0}'.format(r),
                             choices = self.users.revisors1())[0]
                    self.avanz.mark_as_started(r, u, 'revisor1')
            # --------------
            # completed REV1
            # --------------
            rev1_in_progress = self.avanz.to_be_completed_files('revisor1')
            if (rev1_in_progress):
                compl_rev1 = menu(
                    title = 'Specificare files (TRN) per i quali è stata COMPLETATA la PRIMA REVISIONE (LINGUISTICA)',
                    choices  = rev1_in_progress,
                    multiple = True)
                for r in compl_rev1:
                    self.avanz.mark_as_completed(r, 'rev1')
            # --------------
            # completed REV2
            # --------------
            rev2_in_progress = self.avanz.to_be_completed_files('revisor2')
            if (rev2_in_progress):
                compl_rev2 = menu(
                    title = 'Specificare files (REV) per i quali è stata COMPLETATA la SECONDA REVISIONE (LEGGIBILITA)',
                    choices  = rev2_in_progress,
                    multiple = True)
                for r in compl_rev2:
                    self.avanz.mark_as_completed(r, 'rev2')
            # ------------------
            # REV2 to be created
            # ------------------
            rev2_todo = self.avanz.revs2_todo()
            for r in rev2_todo:
                print("\nCreating " + r + " rev file.\n")
                trns = self.avanz.get_trn_fn_for_rev2(r)
                paths = [os.path.join(self.prj_dir, t) for t in trns]
                rev = AVsrt(id = r, f = paths)
                rev.write(f = os.path.join(self.prj_dir, r))
                self.avanz.revs2_created(r)
            if rev2_todo:
                # notify revisors
                self.available_rev2()

        finally:
            self.avanz.to_disk()



    def make_final_srt(self, stats = True):
        revs = [os.path.join(self.prj_dir, f)
                for f in self.avanz.filenames('rev2')]
        final_srt = AVsrt(id = self.id, f = revs)
        final_srt.write(self.final_srt_f)
        print("final srt saved in " + self.final_srt_f)
        if stats:
            self.final_srt_stats()

    
    def final_srt_stats(self):
        outfile = '/tmp/{0}_stats.csv'.format(self.id)
        AVsrt(f = self.final_srt_f, id = self.id).stats(f = outfile)
        print("final srt stats saved in " + outfile)

    
    def list_assignee(self):
        self.avanz.list_assignee()

    
    def list_users(self):
        print(self.users)

    
    def available_rev1(self):
        print("\n")
        self.users.mention("revisors1")
        print(", files disponibili per la revisione linguistica:\n")
        files = [os.path.join(self.prj_dir, r)[2:]
                 for r in self.avanz.assignable_files('revisor1')]
        listing(files)
        print("\n")
            
    
    def available_rev2(self):
        print("\n")
        self.users.mention("revisors2")
        print(": files attualmente disponibili per la revisione di leggibilità:\n")
        listing(self.avanz.assignable_files('revisor2'))
        print("\n")

    
    def monitoring(self):
        self.avanz.monitoring(viewer = img_viewer)

    # -----
    # utils
    # -----
    def browse_repo(self, browser = browser):
        os.system(browser + ' ' + github_repo + self.id)


    def git_pull(self):
        os.chdir(self.add_basedir("")) #mv to basedir
        os.system('git pull')


    def git_status(self):
        os.chdir(self.add_basedir("")) #mv to basedir
        os.system('git status')


    def git_add_commit(self, commit_msg = 'update'):
        os.chdir(self.add_basedir("")) #mv to basedir
        os.system("git add .")
        os.system("git commit -m '{0}'".format(commit_msg))

    def git_push(self, commit_msg = 'update'):
        os.chdir(self.add_basedir("")) #mv to basedir
        os.system("git push")
        
    def burn_with_source(self):
        cmd = "ffmpeg -i source/{0}.srt /tmp/{0}.ass && ffmpeg -i video/{0}.mp4 -vf ass=/tmp/{0}.ass /tmp/{0}_en_subtitled.mp4".format(self.id)
        os.system(cmd)


    def menu(self):
        choices = ["Setup",
                   "Create sandboxes",
                   "Assign TRN or REV2",
                   "Mark progresses",
                   "Monitoring",
                   "List available REV1",
                   "List available REV2",
                   "Make final srt",
                   "Final SRT stats",
                   "List assignee",
                   "List users",
                   # -----
                   # utils
                   # -----
                   "git pull",
                   "git status",
                   "git add and commit",
                   "git push",
                   "Browse project repository",
                   "Burn video with source"
        ]

        while True:
            sel = menu(choices = choices,
                       title = 'MAIN MENU (prj = ' + self.id + ')')
            if len(sel):
                sel = sel[0]
                if sel == "Setup":
                    self.setup()
                elif sel == "Create sandboxes":
                    self.create_sandbox()
                elif sel == "Assign TRN or REV2":
                    self.assign()
                elif sel == "Mark progresses":
                    self.mark_progresses()
                elif sel == "Monitoring":
                    self.monitoring()
                elif sel == "List available REV1":
                    self.available_rev1()
                elif sel == "List available REV2":
                    self.available_rev2()
                elif sel == "Make final srt":
                    self.make_final_srt()
                elif sel == "Final SRT stats":
                    self.final_srt_stats()
                elif sel == "List assignee":
                    self.list_assignee()
                elif sel == "List users":
                    self.list_users()
                elif sel == "git pull":
                    self.git_pull()
                elif sel == "git status":
                    self.git_status()
                elif sel == "git add and commit":
                    self.git_add_commit()
                elif sel == "git push":
                    self.git_push()
                elif sel == "Browse project repository":
                    self.browse_repo()
                elif sel == "Burn video with source":
                    self.burn_with_source()
                else:
                    raise ValueError("Something wrong in selection menu")
            else:
                break

            
        
        
if __name__ == '__main__':
    prj = Prj()
    ##### prj.setup()
    # prj.setup()
    prj.create_sandbox()
