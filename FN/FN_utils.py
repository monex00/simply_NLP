import hashlib
from random import randint
from random import seed
from nltk.corpus import framenet as fn

def print_frames_with_ids():
    for x in fn.frames():
        print('{}\t{}'.format(x.ID, x.name))


def get_frames_ids():
    return [f.ID for f in fn.frames()]


def get_frameset_for_student(surname, list_len=5):
    nof_frames = len(fn.frames())
    base_idx = (abs(int(hashlib.sha512(surname.encode('utf-8')).hexdigest(), 16)) % nof_frames)
    print('\nstudent: ' + surname)
    framenet_ids = get_frames_ids()
    i = 0
    offset = 0
    seed(1)
    while i < list_len:
        f_id = framenet_ids[(base_idx + offset) % nof_frames]
        f = fn.frame(f_id)
        f_name = f.name
        print('\tID: {a:4d}\tframe: {framename}'.format(a=f_id, framename=f_name))
        offset = randint(0, nof_frames)
        i += 1