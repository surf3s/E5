from kivy.uix.screenmanager import ScreenManager
from e5 import MainScreen
import time
import timeit

sm = ScreenManager()
sm.add_widget(MainScreen(name='MainScreen'))

main = sm.screens[0]

# start = time.time()
# for a in range(20):
#     main.load_cfg('CFGs/ap_shannon_1.cfg')

# end = time.time()
# print(end - start)


# 30 seconds before refactoring- 30 seconds after.  Optimizing blockdata.py for Python dictionaries did nothing
# reset screens is what is taking the time

cfgfile_name = 'CFGs/ap_shannon_1.cfg'
main.load_cfg(cfgfile_name)



