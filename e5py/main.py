'''
This may seem like a strange way to handle where the code goes (I don't know) but I did it this way because
1) I only just added this file because buildozer requires a main.py when building an Android app
2) And previously I didn't quite understand how packages work and thought that I needed the program name on the file
3) And it goes against every programmer fiber in my body to name all my programs main.py and risk overwriting them.
Anyway, it seems to work okay.
'''

import e5py.e5 as e5

if __name__ == '__main__':
    e5.resources.resource_add_path(e5.resourcePath())
    e5.Config.set('input', 'mouse', 'mouse,multitouch_on_demand')      # Removes red dot
    e5.Config.set('kivy', 'exit_on_escape', '0')                       # Changes what escape does
    e5.E5App().run()
