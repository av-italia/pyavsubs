import srt

class AVsrt:

    def __init__(self,
                 id = "",
                 f = None,       # one or many (list) file
                 comment = '##',
                 set_id_as_prog = True,
                 validate = True):

        
        if isinstance(f, str):
            f = [f]
        elif isinstance(f, list):
            pass
        else:
            raise ValueError("f must be a str path or a list of path")

        # id of the srt
        self.id = id
        
        # raw content
        content = []
        for file in sorted(f):
            with open(file) as s:
                for line in s:
                    if not line.startswith(comment):
                        content.append(line)
        self.raw  = content

        # parsing
        subs_generator = srt.parse("".join(content))
        subs = list(subs_generator)
        if set_id_as_prog:
            i = 1
            for s in subs:
                s.index = i
                i = i + 1
        self.subs = subs

    def write(self, f):
        with open(f, mode = 'w') as file:
            print(srt.compose(self.subs), file = file)

    def stats(self):
        pass

    def split(self):
        pass

    def print(self):
        pass
        
        
if __name__ == '__main__':

    # -------------
    # READING TESTS
    # -------------
    
    basep = "/home/l/av_it_subs/subs/hnva2/"
    def path(x):
        return basep + x

    # ## perfect srt
    # s = AVsrt(f = path('hnva2_final.srt'))
    # print(s.raw)
    # print(s.subs)

    # ## srt with comments
    # s = AVsrt(f = path('subs_010500_kudelka85_c.srt'))
    # print(s.raw)
    # print(s.subs)

    # ## bunch of srt (with duplicated id)
    F = ["revs_000000_002500_AlessiaQ91_c.srt",
         "revs_003000_005500_pmav83_c.srt",
         "revs_010000_012500_Titty11_c.srt"
    ]
    s = AVsrt(f = [basep + f for f in F])
    # prog_id = [s.index for s in s.subs]
    # print(prog_id)

    # -------------
    # WRITING TESTS
    # -------------
    s.write(f = '/tmp/asd.srt')
