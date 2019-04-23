from os import path
from kivy.utils import platform

# See if the file as given can be found.
# If not, try to find it in the same folder as the CFG file.
# This can happen when a CFG and associated files are copied to a 
# new folder or computer or device.
def locate_file(filename, cfg_path = None):
    if path.isfile(filename):
        return(filename)
    if cfg_path:
        p, f = path.split(filename)
        if path.isfile(path.join(cfg_path, f)):
            return(path.join(cfg_path, f))
    return('')

def platform_name():
    return(['Windows','Linux','Android','MacOSX','IOS','Unknown'][['win', 'linux', 'android', 'macosx', 'ios', 'unknown'].index(platform)])
