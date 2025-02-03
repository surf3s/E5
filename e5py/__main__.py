'''
Clearly I don't understand Python package making, filenaming standards, and folder structures.
main.py was added to make Buildozer work (needed for Android)
This file, __main__.py, was added to make the command line python e5py work after installing the package from PyPi.
'''

import e5py.e5 as e5
from kivy.lang.builder import Builder

if __name__ == '__main__':
    e5.resources.resource_add_path(e5.resourcePath())
    e5.Config.set('input', 'mouse', 'mouse,multitouch_on_demand')      # Removes red dot
    e5.Config.set('kivy', 'exit_on_escape', '0')                       # Changes what escape does 
    Builder.load_file('main.kv')
    e5.E5App().run()
