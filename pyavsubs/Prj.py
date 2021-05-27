import os
import Users
import Avanz
import AVsrt
import templates

# Standard locations
# ------------------
# directories
data_dir              = "data"
source_dir            = "source"
subs_dir              = "subs"
sandbox_dir           = os.path.join(subs_dir, "sandbox")
# files
users_file            = os.path.join(data_dir, "users.csv")

# creare dei template, invece che il codice
sndbx_tmpl_revisori1  = os.path.join(sandbox_dir, "template_revisori1.srt")
sndbx_tmpl_traduttori = os.path.join(sandbox_dir, "template_traduttori.srt")
# file templates
# sndbx_tmpl_revisori1  = self.prj_path(sndbx_tmpl_revisori1 )
# sndbx_tmpl_traduttori = self.prj_path(sndbx_tmpl_traduttori)


class Prj:

    def __init__(self, id = "test",
                 yt_id = "testid",
                 base_dir = "/home/l/av_it_subs"):

        # add base_dir to the standard locations
        def prj_path(x):
            return os.path.join(base_dir, x)
        # directories
        prj_dir    = prj_path(os.path.join(subs_dir, id))
        avanz_f = prj_path(os.path.join(prj_dir, 'zz_avanzamento.csv'))
        
        # initialization
        self.id           = id
        self.yt_id        = yt_id
        self.users        = Users.Users(f = prj_path(users_file))
        self.prj_dir      = prj_dir
        self.avanz        = Avanz.Avanz(f = avanz_f, id = id)
        self.prj_path     = prj_path


    def setup(self, chunks_len_mins = 5, trn_to_rev_ratio = 6):
        
        # setup the directory or fail if already set up
        if os.path.isdir(self.prj_dir):
            raise ValueError(self.prj_dir + " already exstisting. Aborting.")
        else:
            os.makedirs(self.prj_dir)
        # import and split source .srt
        src_f = os.path.join(source_dir, "{0}.srt".format(self.id))
        self.source_srt = AVsrt.AVsrt(f = self.prj_path(src_f), id = 'source')
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
            print(templates.unsubbed, file = f)

    def create_sandbox(self):
        trn_users = menu(title = 'Specificare utenti (TRN) per sandbox',
                         choices  = self.users.translators(),
                         multiple = True,
                         strict   = True)
        rev1_users = menu(title = 'Specificare utenti (REV1) per sandbox',
                          choices  = self.users.revisors1(),
                          multiple = True,
                          strict   = True)

        ## sandbox di translators
        if (len(trn_users)):
            ## notify: header
            ascii_header('sandbox traduttori')
            ## check permissions
            allowed_users = self.check_allowed_users(trn_users, 'translator')
            ## files and dirs
            files = sandbox_file(allowed_users, role = "translator")
            # ## copia file
            # tmp = Map(file.copy,
            #            from = list(sandbox_template_traduttori),
            #            to = files,
            #            overwrite = TRUE)
            # ## notify: file list
            # listing(files)

        ## sandbox di revisori (per revisione 1)
        if (len(rev1_users)):
            ## notify: header
            ascii_header('sandbox revisori (fase 1)')
            ## check permissions
            allowed_users = self.check_allowed_users(rev1_users, 'revisor1')
            ## files and dirs
            files = sandbox_file(allowed_users, role = "revisor1")
            # ## copia file
            # tmp = Map(file.copy,
            #            from = list(sandbox_template_revisori1),
            #            to = files,
            #            overwrite = TRUE)
            # ## notify: file list
            # listing(files)
            
        
if __name__ == '__main__':
    prj = Prj()
    # prj.setup()

