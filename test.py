
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
    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)

        bx = GridLayout(cols = 2, size_hint_y = .8)
        bx.add_widget(Label(text='Field 1'))    
        bx.add_widget(TextInput())
        bx.add_widget(Label(text='Field 2'))    
        bx.add_widget(TextInput())
        bx.add_widget(Label(text='Field 3'))    
        bx.add_widget(TextInput())
        self.add_widget(bx)

class Test(App):
    def build(self):
        return(MainScreen())

if __name__ == '__main__':
    Test().run()