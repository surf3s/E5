
__version__ = '1.0.0'

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.switch import Switch
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.config import Config

import os 
import random
import datetime
import logging
import logging.handlers as handlers
import time
import ntpath

# My libraries for this project
from blockdata import blockdata
from dbs import dbs

# The database - pure Python
from tinydb import TinyDB, Query, where

from collections import OrderedDict

OPTIONBUTTON_BACKGROUND = (128/255, 216/255, 255/255, 1) #80D8FF (lighter blue)
OPTIONBUTTON_COLOR = (0, 0, 0, 1) # black
OPTIONBUTTON_FONT_SIZE = "15sp"

BUTTON_BACKGROUND = (0, .69, 255/255, 1) #00B0FF (deep blue)
BUTTON_COLOR =  (0, 0, 0, 1) # black
BUTTON_FONT_SIZE = "15sp"

WINDOW_BACKGROUND = (255/255, 255/255, 255/255, 1) #FFFFFF
WINDOW_COLOR = (0, 0, 0, 1)

POPUP_BACKGROUND = (0, 0, 0, 1)
POPUP_TEXT_COLOR = (1, 1, 1, 1)

TEXT_FONT_SIZE = "15sp"
TEXT_COLOR = (0, 0, 0, 1)

DATAGRID_ODD = (224.0/255, 224.0/255, 224.0/255, 1)
DATAGRID_EVEN = (189.0/255, 189.0/255, 189.0/255, 1)

class MainScreen(Screen):

    current_button_id = 'bt1'

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)

        bx = GridLayout(cols = 2, size_hint_y = .8)

        bx.add_widget(Label(text='Field 1'))    
        tx1 = TextInput(multiline = False, write_tab = False, id='tx1')
        bx.add_widget(tx1)
        tx1.bind(on_text_validate = self.next_widget)

        bx.add_widget(Label(text='Field 2'))    
        tx2 = TextInput(multiline = False, write_tab = False, id='tx2')
        bx.add_widget(tx2)

        bx.add_widget(Label(text='Field 3'))    
        tx3 = TextInput(multiline = False, write_tab = False)
        bx.add_widget(tx3)

        scrollbox = GridLayout(cols = 1, size_hint_y = None)
        scrollbox.bind(minimum_height=scrollbox.setter('height'))
        
        bt1 = Button(text='Button1', background_color = (1, 0, 0, 1), id='bt1', size_hint_y = None)
        scrollbox.add_widget(bt1)

        bt2 = Button(text='Button2', background_color = (0, 1, 0, 1), id='bt2', size_hint_y = None)
        scrollbox.add_widget(bt2)

        bt3 = Button(text='Button2', background_color = (0, 1, 0, 1), id='bt3', size_hint_y = None)
        scrollbox.add_widget(bt3)

        bt4 = Button(text='Button2', background_color = (0, 1, 0, 1), id='bt4', size_hint_y = None)
        scrollbox.add_widget(bt4)

        bt5 = Button(text='Button2', background_color = (0, 1, 0, 1), id='bt5', size_hint_y = None)
        scrollbox.add_widget(bt5)

        bt6 = Button(text='Button2', background_color = (0, 1, 0, 1), id='bt6', size_hint_y = None)
        scrollbox.add_widget(bt6)

        root = ScrollView(size_hint=(1, None), size = (1, 200), id='scrollview')
        root.add_widget(scrollbox)

        bx.add_widget(root)

        self.add_widget(bx)
        
        bt1.focus = True

        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        text_str = args[3]
        print('INFO: The key %s has been pressed %s' % (ascii_code, text_str))
        for widget in self.walk():
            try:
                if widget.focus:
                    print(widget.id)
            except:
                pass

        if ascii_code==274:
            if self.current_button_id=='bt1':
                next_button_id='bt2'
            if self.current_button_id=='bt2':
                next_button_id='bt3'
            for widget in self.walk():
                if widget.id==self.current_button_id:
                    widget.background_color = (.2,.2,.2,1)
                if widget.id==next_button_id:
                    widget.background_color = (.9,.9,.9,1)
                    break
            self.current_button_id = next_button_id
            for widget2 in self.walk():
                if widget2.id=='scrollview':
                    widget2.scroll_to(widget)

        return True # return True to accept the key. Otherwise, it will be used by the system.

    def next_widget(self, value):
        print(value.id)
        for widget in self.walk():
            if widget.id == 'tx1':
                for widget2 in self.walk():
                    if widget2.id == 'bt1':
                        widget2.background_color = (0,0,0,1)
                        break

class Test(App):
    def build(self):
        return(MainScreen())

if __name__ == '__main__':
    Test().run()