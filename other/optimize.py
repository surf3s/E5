from  timeit import Timer

from main import cfg, MainScreen
from os import listdir, path

def read_cfgs(fpath):
    for file in listdir(fpath):
        if file[-4:].lower() == '.cfg':
            e4_cfg = cfg(path.join(fpath, file))
            e4_cfg.open()

t = Timer(lambda: read_cfgs('CFGs'))

print(t.timeit(number = 5))