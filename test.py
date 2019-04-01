from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label

sm = ScreenManager()

class MainScreen(Screen):
    def __init__(self, txt = None, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.add_widget(Label(text = txt))

class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        sm.add_widget(MainScreen(txt = 'test'))
        pass

    def build(self):
        return(sm)

if __name__ == '__main__':
    TestApp().run()