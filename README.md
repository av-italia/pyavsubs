# pyavsubs

Here you can find the software I use to manage the process/team
involved in Italian subtitles creation for (long) YouTube videos, in
case it could be useful for someone else. This is a Python port of
[this](https://github.com/lbraglia/lbav2) R package: the dependencies
are [srt](https://github.com/cdown/srt) and
[matplotlib](https://matplotlib.org/) libraries.

Our first subbed video was [this
one](https://www.youtube.com/watch?v=cJ9kGZMbyVw); we're now
completing [Gary's mix](https://www.youtube.com/watch?v=3gLOVtbG6QI).

Here is the background machinery, the repository with the subs
themselves is [here](https://github.com/av-italia/subs).

## Usage

If you want to make your own subs have some programming skill and want
to reuse our software, install this package, open a `python3`
interpreter in the subs directory (for me it's the clone of
[this](https://github.com/av-italia/subs) repo on my machine), then

```python
from pyavsubs.Prj import Prj
Prj(id = 'gymix', yt_id = 'Lox6tAor5Xo').menu()
```

where `gymix` is the project id (which maps to the directory under
`subs`), while `lw53nODhRXU` is the YouTube id of the support video
used for translations. After commanding `menu`, an interactive menu is
given:

```
=========================
        MAIN MENU        
=========================

Select a number or 0 to exit 

1. Setup
2. Create sandboxes
3. Assign TRN or REV2
4. Mark progresses
5. Monitoring
6. List available REV1
7. List available REV2
8. Make final srt
9. Final SRT stats
10. List assignee
11. List users 

Selection (0 to exit): 

```

where:

1. Setup: create the project directory under `subs` and split a source sub
   (derived from YT automatic sub generator) into 5min length chunks
   
2. Create sandboxes: set up test files for translator and revisors

3. Assign TRN or REV2: assign a chunk to be translated or revised
   (readability revision)

4. Mark progresses: update progress information for monitoring
   purposes (eg which translation are completed, which revision are
   started, completed and so on)

5. Monitoring: make a monitorin graph

6. List available REV1: list files translated but not linguistically
   revised yet

7. List available REV2: list files linguistically revised but not from
   a readability standpoint yet

8. Make final srt: compose the final `.srt` by collapsing revised
   files

9. Final SRT stats: compute the readability stats for the final `.srt` in
   order to spot subs which are difficult to read

10. List assignee: list all chunks and assigned translator/revisors
    for each of them

11. List users: list all the users in the `data/users.csv` "database"
