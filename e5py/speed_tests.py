from kivy.uix.screenmanager import ScreenManager
from e5 import MainScreen
import time

sm = ScreenManager()
sm.add_widget(MainScreen(name='MainScreen'))

main = sm.screens[0]

start = time.time()
for a in range(20):
    main.load_cfg('CFGs/ap_shannon_1.cfg')

end = time.time()
print(end - start)


# 30 seconds before refactoring