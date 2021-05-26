import csv
import math
import srt

chunks_header_template = """## --------------------------------------------------------
## Inizio spezzone: {0}
## --------------------------------------------------------\n"""

def secs_to_digits(s):
    ## return numeric second to a XXYYZZ character format where
    ## XX=hours, YY=minutes, ' ZZ=seconds
    sec_in_a_hour = 1 * 60 * 60
    sec_in_a_min  = 60
    remaining = int(s)
    hours = math.floor(remaining / sec_in_a_hour)
    remaining = remaining - hours * sec_in_a_hour
    minutes = math.floor(remaining / sec_in_a_min)
    secs = remaining - minutes * sec_in_a_min
    return str(hours).zfill(2) + str(minutes).zfill(2) + str(secs).zfill(2)


class Chunk():
    """ Class representing a chunk of subs (aka a single translate file) """
    def __init__(self, fn, h, subs):
        self.fn = fn    # filename: subs_00000.srt
        self.h = h      # the file header
        self.subs = subs # its subs

    def to_srt(self, output_dir):
        fp = output_dir + '/' + self.fn
        with open(fp, 'w') as f:
            print(self.h, file = f)
            for s in self.subs:
                ## add comments
                commented_lines = ["## " + l for l in s.content.split('\n')]
                s.content = "\n".join(commented_lines + ["", "", ""])
            output = srt.compose(self.subs, reindex = False, strict = False)
            print(output, file = f)

class AVsrt:

    def __init__(self,
                 id = "",
                 f = None,       # one or many (list) file
                 comment = '##',
                 set_id_as_prog = True,
                 debug = False):

        
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
        if debug:
            self.raw  = content

        # parsing
        subs_generator = srt.parse("".join(content))
        subs = list(subs_generator)
        if set_id_as_prog:
            subs = list(srt.sort_and_reindex(subs))
            
        self.subs = subs

    def write(self, f):
        with open(f, mode = 'w') as file:
            print(srt.compose(self.subs), file = file)

    def stats(self, f = None):
        with open(f, 'w') as csvfile:
            fieldnames = ["id", "text", "start", "stop", "secs",
                          "nchars", "cps", "nchars_longest_line", "nlines",
                          "high_cps", "long_line", "too_many_lines", "nfails"]
            writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
            writer.writeheader()
            for s in self.subs:
                secs = (s.end - s.start).total_seconds() 
                nchars = len(s.content.replace("\n", "").replace(" ", ""))
                cps = nchars / secs               
                nchars_longest_line = max(
                    [len(x) for x in s.content.replace(" ", "").split("\n")]
                )
                nlines = len(s.content.split("\n"))
                high_cps  =  cps > 30          
                long_line = nchars_longest_line > 42                          
                too_many_lines = nlines > 2   
                nfails = too_many_lines + long_line + high_cps
                writer.writerow({
                    "id"                   : s.index,
                    "text"                 : s.content.replace('\n', '|'),
                    "start"                : s.start,
                    "stop"                 : s.end,
                    "secs"                 : secs,
                    "nchars"               : nchars,
                    "cps"                  : cps,
                    "nchars_longest_line"  : nchars_longest_line,
                    "nlines"               : nlines,
                    "high_cps"             : high_cps,
                    "long_line"            : long_line,
                    "too_many_lines"       : too_many_lines,
                    "nfails"               : nfails
                })

    def split(self, chunks_len_mins = 5, yt_id = "", output_dir = "."):

        if (yt_id == ""):
            raise ValueError("You must give the YouTube id of the video")

        chunks_len_secs = chunks_len_mins * 60
        max_secs = math.floor(max(
            [s.start.total_seconds() for s in self.subs]
        )) + 1
        chunks_start_secs = list(range(0, max_secs, chunks_len_secs))
        # chunks_id = list(range(1, len(chunks_start_secs)))
        chunks_digits = [secs_to_digits(s) for s in chunks_start_secs]
        chunks_fname = ["subs_{0}.srt".format(d) for d in chunks_digits]
        yt_links = ["https://youtu.be/{0}?t={1}".format(yt_id, css)
                    for css in chunks_start_secs]
        headers = [chunks_header_template.format(ytl) for ytl in yt_links]
        z = zip(chunks_start_secs, chunks_fname, headers)
        chunks = []
        for chunk_start, fn, h in z:
            chunk_stop = chunk_start + chunks_len_secs
            subs = [s for s in self.subs
                    if  ((s.start.total_seconds() >= chunk_start)
                         and (s.start.total_seconds() < chunk_stop))]
            c = Chunk(fn = fn, h = h, subs = subs)
            chunks.append(c)

        [c.to_srt(output_dir = output_dir) for c in chunks]

        
            
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
    # F = ["revs_000000_002500_AlessiaQ91_c.srt",
    #      "revs_003000_005500_pmav83_c.srt",
    #      "revs_010000_012500_Titty11_c.srt"
    # ]
    # s = AVsrt(f = [basep + f for f in F])
    # prog_id = [s.index for s in s.subs]
    # print(prog_id)

    # # -------------
    # # Misc Methods
    # # -------------
    # s.write(f = '/tmp/asd.srt')
    # s.stats(f = '/tmp/stats.csv')
    s = AVsrt(f = '/home/l/av_it_subs/source/test.srt')
    s.split(yt_id = "asdomar", output_dir = '/tmp')
