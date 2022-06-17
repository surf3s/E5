from os import path
from kivy.utils import platform
from kivy.core.window import Window

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


def filename_only(filename = None):
    if filename:
        p, f = path.split(filename)
        return(f)
    else:
        return('')


def platform_name():
    return(['Windows', 'Linux', 'Android', 'MacOSX', 'IOS', 'Unknown'][['win', 'linux', 'android', 'macosx', 'ios', 'unknown'].index(platform)])


def restore_window_size_position(main_name, main_ini):
    Window.minimum_width = 450
    Window.minimum_height = 450
    if main_ini.get_value(main_name, "SCREENTOP"):
        temp = max(int(main_ini.get_value(main_name, "SCREENTOP")), 0)
        Window.top = temp
    if not main_ini.get_value(main_name, "SCREENLEFT") == '':
        temp = max(int(main_ini.get_value(main_name, "SCREENLEFT")), 0)
        Window.left = temp
    window_width = None
    window_height = None
    if not main_ini.get_value(main_name, "SCREENWIDTH") == '':
        window_width = max(int(main_ini.get_value(main_name, "SCREENWIDTH")), 450)
    if not main_ini.get_value(main_name, "SCREENHEIGHT") == '':
        window_height = max(int(main_ini.get_value(main_name, "SCREENHEIGHT")), 450)
    if window_width and window_height:
        Window.size = (window_width, window_height)
