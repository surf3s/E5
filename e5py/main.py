'''
This may seem like a strange way to handle where the code goes (I don't know) but I did it this way because
1) I only just added this file because buildozer requires a main.py when building an Android app
2) And previously I didn't quite understand how packages work and thought that I needed the program name on the file
3) And it goes against every programmer fiber in my body to name all my programs main.py and risk overwriting them.
Anyway, it seems to work okay.
'''

'''
IMPORTANT - if you are running E5 in Python from the source code, you need to do
pip install -e .
to add the program to the list of installed programs so that modules can be referred to in this way.
'''
import e5py.e5 as e5
from kivy.lang.builder import Builder

if __name__ == '__main__':
    e5.resources.resource_add_path(e5.resourcePath())
    e5.Config.set('input', 'mouse', 'mouse,multitouch_on_demand')      # Removes red dot
    e5.Config.set('kivy', 'exit_on_escape', '0')                       # Changes what escape does
    Builder.load_file('main.kv')
    e5.E5App().run()
