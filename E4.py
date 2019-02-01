# First screen should be first field is the CFG is current
# Otherwise a blank screen

# Make the menulist and info boxes actually scroll
# When a menulist, when an item is selected, insert into text box and then trigger next button
# When doing a next, load data from current data if it exists.
# When doing a back, load data from current data if it exists.
# Write condition evaluation
# Write data save
# Then work on data grid and editing records
# If a new menu item is entered instead of selected, offer to add it to the menu
# Add a CFG option to sort menus
# Filter input on a numeric box to numbers only
# Better support for keyboard input (i.e. pressing keys moves to menu item and enter selects)

# Long term
#   Think about whether to allow editing of CFG in the program
#   Support for images from phone camera or otherwise
#   Get location data from GPS

__version__ = '1.0.0'

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
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

import os 
import random
import datetime
import logging
import logging.handlers as handlers
import time

logger = logging.getLogger('E4')
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('E4.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)

logger.addHandler(fh)

# My libraries for this project
from blockdata import blockdata
from dbs import dbs

# The database - pure Python
from tinydb import TinyDB, Query, where

from collections import OrderedDict

OPTIONBUTTON_BACKGROUND = (128/255, 216/255, 255/255, 1) #80D8FF (lighter blue)
OPTIONBUTTON_COLOR = (0, 0, 0, 1) # black
BUTTON_BACKGROUND = (0, .69, 255/255, 1) #00B0FF (deep blue)
BUTTON_COLOR =  (0, 0, 0, 1) # black
WINDOW_BACKGROUND = (255/255, 255/255, 255/255, 1) #FFFFFF
WINDOW_COLOR = (0, 0, 0, 1)

TEXT_FONT_SIZE = "15sp"
BUTTON_FONT_SIZE = "15sp"

DATAGRID_ODD = (224.0/255, 224.0/255, 224.0/255, 1)
DATAGRID_EVEN = (189.0/255, 189.0/255, 189.0/255, 1)

class db(dbs):
    MAX_FIELDS = 300
    db = None
    filename = None
    db_name = 'data'

    def __init__(self, filename):
        if filename=='':
            filename = 'e4_data.json'
        self.filename = filename
        self.db = TinyDB(self.filename)

    def status(self):
        txt = 'The data file is %s\n' % self.filename
        txt += 'There are %s records in the data file.\n' % len(self.db)
        return(txt)

    def create_defaults(self):
        pass

    def get(self, name):
        unit, id = name.split('-')
        p = self.db.search( (where('unit')==unit) & (where('id')==id) )
        if p:
            return(p)
        else:
            return(None)

    def names(self):
        name_list = []
        for row in self.db:
            name_list.append(row['unit'] + '-' + row['id'])
        return(name_list)

    def fields(self):
        global e4_cfg 
        return(e4_cfg.fields())

    def delete_all(self):
        self.db.purge()

    def export_csv(self):
        pass

    def delete_record(self):
        pass

    def add_record(self):
        pass

class ini(blockdata):
    
    blocks = []
    filename = ''

    def __init__(self, filename):
        if filename=='':
            filename = 'E4.ini'
        self.filename = filename
        self.blocks = self.read_blocks()

    def update(self):
        global e4_cfg
        self.update_value('E4','CFG', e4_cfg.filename)
        self.save()

    def save(self):
        self.write_blocks()

    def status(self):
        txt = 'The INI file is %s.\n' % self.filename
        return(txt)

class cfg(blockdata):

    blocks = []
    filename = ""
    current_field = ""
    BOF = True
    EOF = False
    current_record = {}

    class field:
        name = ''
        inputtype = ''
        prompt = ''
        length = 0
        menu = ''
        conditions = []
        increment = False
        carry = False 
        unique = False
        info = ''
        data = {}
        def __init__(self, name):
            self.name = name

    def __init__(self, filename):
        if filename=='':
            filename = 'E4.cfg'
        self.load(filename)
        self.validate()
    
    def valid_datarecord(self, data_record):
        for field in data_record:
            f = self.get(field)
            value = data_record[field]
            if f.required and not value:
                return('Required field %s is empty.  Please provide a value.' % field)
            if f.length!=0 and len(value) > f.length:
                return('Maximum length for %s is set to %s.  Please shorten your response.  Field lengths can be set in the CFG file.  A value of 0 means no length limit.')
        return(True)

    def get(self, field_name):
        if not field_name:
            return('')
        else:
            f = self.field(field_name)
            f.name = field_name
            f.inputtype = self.get_value(field_name, 'TYPE')
            f.prompt = self.get_value(field_name, 'PROMPT')
            f.length = self.get_value(field_name, 'LENGTH')
            f.unique = self.get_value(field_name,"UNIQUE")
            if self.get_value(field_name, 'MENU'):
                f.menu = self.get_value(field_name, 'MENU').split(",")
            else:
                f.menu = ''
            f.info = self.get_value(field_name, 'INFO')
            for condition_no in range(0, 6):
                if self.get_value(field_name, "CONDITION%s" % condition_no):
                    f.conditions.append(self.get_value(field_name, "CONDITION%s" % condition_no))
            return(f)

    def put(self, field_name, f):
        self.update_value(field_name, 'PROMPT', f.prompt)
        self.update_value(field_name, 'LENGTH', f.length)
        self.update_value(field_name, 'TYPE', f.inputtype)
        #self.update_value(field_name, 'MENU', f.menu)

    def fields(self):
        field_names = self.names()
        del_fields = ['E4']
        for del_field in del_fields:
            if del_field in field_names:
                field_names.remove(del_field)
        return(field_names)

    def build_default(self):
        pass

    def validate(self):
        for field_name in self.fields():
            f = self.get(field_name)
            if f.prompt == '':
                f.prompt = field_name
            f.inputtype = f.inputtype.upper()
            self.put(field_name, f)
        
    def save(self):
        self.write_blocks()

    def load(self, filename):
        self.filename = filename 
        self.blocks = self.read_blocks()
        if self.blocks==[]:
            self.build_default()
        self.BOF = True
        if len(self.blocks)>0:
            self.EOF = False
        else:
            self.EOF = True
        self.current_field = ""

    def status(self):
        txt = 'CFG file is %s\n' % self.filename
        txt += 'and contains %s fields.' % len(self.blocks)
        return(txt)

    def next(self):
        if self.EOF:
            self.current_field = ''
        else:
            if self.BOF:
                self.BOF = False
                self.EOF = False
                self.current_field = self.fields()[0]
            else:
                field_index = self.fields().index(self.current_field)
                field_index += 1
                if field_index > len(self.blocks):
                    self.EOF = True
                    self.current_field = ""
                else:
                    self.EOF = False
                    self.BOF = False
                    self.current_field = self.fields()[field_index]
        return(self.get(self.current_field))

        # This routine needs to get the current field and then advance it by one
        # checking conditionals as it goes
        # If advancing passed the end, then set currentfield to empty and set EOF

    def previous(self):
        # need to implement conditions
        if self.BOF:
            self.current_field = ''
        else:
            if self.EOF:
                self.BOF = False
                self.EOF = False
                self.current_field = self.fields()[-1]
            else:
                field_index = self.fields().index(self.current_field)
                field_index -= 1
                if field_index < 0:
                    self.BOF = True
                    self.current_field = ""
                else:
                    self.EOF = False
                    self.BOF = False
                    self.current_field = self.fields()[field_index]
        return(self.get(self.current_field))

    def start(self):
        self.BOF = False
        self.EOF = False
        self.current_field = self.fields()[0]
        return(self.get(self.current_field))
        # build current_record 
        #   in doing so do not clear carry fields
        #   save in dictionary key field type arrangement
        #   check EDM for how I did it there

    def _conditional(self):
        return(True)
        # evaluate whether the current field should be entered
        # return a true or a false

class record_button(Button):
    def __init__(self,id,text,**kwargs):
        super(Button, self).__init__(**kwargs)
        self.text = text
        self.id = id
        self.size_hint_y = None
        self.id = id
        self.color = BUTTON_COLOR
        self.background_color = BUTTON_BACKGROUND
        self.background_normal = ''

class LoadDialog(FloatLayout):
    start_path =  ObjectProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)

class MainTextNumericInput(ScrollView):
    def __init__(self, **kwargs):
        super(MainTextNumericInput, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.size = (Window.width, Window.height/1.9)
        __content = GridLayout(cols = 1, spacing = 5, size_hint_y = None)
        __content.bind(minimum_height=__content.setter('height'))
        __content.add_widget(TextInput(size_hint_y = None, multiline = False, id = 'new_item'))
        self.add_widget(__content)


class MainScreen(Screen):

    _popup = ObjectProperty(None)
    _field = None

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self._field = e4_cfg.start()

        mainscreen = BoxLayout(orientation = 'vertical', size_hint_y = None, id = 'inputbox')
        #inputbox.bind(minimum_height = inputbox.setter('height'))

        label = Label(text = self._field.prompt, size_hint_y = None, height = .2,
                     color = (0,0,0,1), id = 'field_prompt',
                     halign = 'left',
                     font_size = TEXT_FONT_SIZE)
        mainscreen.add_widget(label)
        label.bind(texture_size = label.setter('size'))
        label.bind(size_hint_min_x = label.setter('width'))
        
        mainscreen.add_widget(TextInput(size_hint_y = None,
                                         multiline = False,
                                         id = 'field_data',
                                         font_size = TEXT_FONT_SIZE))
        #self.add_widget(inputbox)

        scroll_content = BoxLayout(orientation = 'horizontal', size_hint_y = None, id = 'scroll_content')
        self.add_scroll_content(scroll_content)
        mainscreen.add_widget(scroll_content)

        buttons = GridLayout(cols = 2, size_hint_y = None)
        back_button = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        font_size = BUTTON_FONT_SIZE,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        buttons.add_widget(back_button)
        back_button.bind(on_press = self.go_back)

        next_button = Button(text = 'Next', size_hint_y = None,
                        color = BUTTON_COLOR,
                        font_size = BUTTON_FONT_SIZE,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        buttons.add_widget(next_button)
        next_button.bind(on_press = self.go_next)
        mainscreen.add_widget(buttons)
        self.add_widget(mainscreen)

    def add_scroll_content(self, content_area):
    
        content_area.clear_widgets()

        if self._field.menu or self._field.info:

            if self._field.menu:
                scrollbox = GridLayout(cols = 1, size_hint_y = None, id = 'inputbox')
                for menu_item in self._field.menu:
                    scrollbox.add_widget(Label(text = menu_item, size_hint_y = None,
                                color = (0,0,0,1), id = 'info',
                                halign = 'left',
                                font_size = TEXT_FONT_SIZE))
                #root1 = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/2))
                root1 = ScrollView(size_hint=(1, None))
                root1.add_widget(scrollbox)
                content_area.add_widget(root1)

            if self._field.info:
                scrollbox = GridLayout(cols = 1, size_hint_y = None, id = 'inputbox')
                info = Label(text = self._field.info, size_hint_y = None,
                            color = (0,0,0,1), id = 'info',
                            halign = 'left',
                            font_size = TEXT_FONT_SIZE)
                scrollbox.add_widget(info)    
                #root2 = ScrollView(size_hint=(1, None), size=(Window.width, scroll_content.height))
                root2 = ScrollView(size_hint=(1, None))
                root2.add_widget(scrollbox)
                content_area.add_widget(root2)

    def on_pre_enter(self):
        for widget in self.walk():
            if widget.id=='content':
                pass
                # insert content here based on current cfg field
                
    def show_load_cfg(self):
        content = LoadDialog(load = self.load, 
                            cancel = self.dismiss_popup,
                            start_path = os.path.dirname(os.path.abspath( __file__ )))
        self._popup = Popup(title = "Load CFG file", content = content,
                            size_hint = (0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        global e4_cfg, e4_ini
        e4_cfg.load(os.path.join(path, filename[0]))
        e4_ini.update()
        self.dismiss_popup()

    def dismiss_popup(self):
        self._popup.dismiss()
        self.parent.current = 'MainScreen'

    def update_mainscreen(self):
        for widget in self.walk():
            if widget.id=='field_prompt':
                widget.text = e4_cfg.current_field
            if widget.id=='scroll_content':
                self.add_scroll_content(widget)
                break

    def save_field(self):
        for widget in self.walk():
            if widget.id=='field_data':
                self._field.data[self._field.name] = widget.text 
                widget.text = ''
                break

    def go_back(self, value):
        self.save_field()
        self._field = e4_cfg.previous()
        self.update_mainscreen()

    def go_next(self, value):
        self.save_field()
        self._field = e4_cfg.next()
        if e4_cfg.EOF:
            self.save_record()
            self._field = e4_cfg.start()
        self.update_mainscreen()

    def save_record(self):
        pass

class InitializeOnePointHeader(Label):
    pass

class InitializeDirectScreen(Screen):

    popup = ObjectProperty(None)

    def datum_list(self):
        layout_popup = GridLayout(cols = 1, spacing = 10, size_hint_y = None)
        layout_popup.bind(minimum_height=layout_popup.setter('height'))
        for datum in datums.names(EDMpy.edm_datums):
            button1 = Button(text = datum, size_hint_y = None, id = datum,
                        color = OPTIONBUTTON_COLOR,
                        background_color = OPTIONBUTTON_BACKGROUND,
                        background_normal = '')
            layout_popup.add_widget(button1)
            button1.bind(on_press = self.initialize_direct)
        button2 = Button(text = 'Cancel', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout_popup.add_widget(button2)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.9))
        root.add_widget(layout_popup)
        self.popup = Popup(title = 'Initial Direct',
                    content = root,
                    size_hint = (None, None),
                    size=(400, 400),
                    #pos_hint = {None, None},
                    auto_dismiss = False)
        button2.bind(on_press = self.popup.dismiss)
        self.popup.open()

    def initialize_direct(self, value):
        EDMpy.edm_station.X = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        EDMpy.edm_station.Y = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        EDMpy.edm_station.Z = EDMpy.edm_datums.datums[EDMpy.edm_datums.datums.Name==value.id].iloc[0]['X']
        self.popup.dismiss()
        self.parent.current = 'MainScreen'

class InitializeSetAngleScreen(Screen):
    def set_angle(self, foreshot, backshot):
        if foreshot:
            totalstation.set_horizontal_angle(foreshot)
        elif backshot:
            # flip angle 180
            totalstation.set_horizontal_angle(foreshot)
        self.parent.current = 'MainScreen'

class InitializeOnePointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeOnePointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class InitializeTwoPointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeTwoPointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class InitializeThreePointScreen(Screen):
    def __init__(self,**kwargs):
        super(InitializeThreePointScreen, self).__init__(**kwargs)
        self.add_widget(InitializeOnePointHeader())
        self.add_widget(DatumLister())

class MenuList(Popup):
    def __init__(self, title, menu_list, call_back, **kwargs):
        super(MenuList, self).__init__(**kwargs)
        __content = GridLayout(cols = 1, spacing = 5, size_hint_y = None)
        __content.bind(minimum_height=__content.setter('height'))
        for menu_item in menu_list:
            __button = Button(text = menu_item, size_hint_y = None, id = title,
                        color = OPTIONBUTTON_COLOR,
                        background_color = OPTIONBUTTON_BACKGROUND,
                        background_normal = '')
            __content.add_widget(__button)
            __button.bind(on_press = call_back)
        if title!='PRISM':
            __new_item = GridLayout(cols = 2, spacing = 5, size_hint_y = None)
            __new_item.add_widget(TextInput(size_hint_y = None, id = 'new_item'))
            __add_button = Button(text = 'Add', size_hint_y = None,
                                    color = BUTTON_COLOR,
                                    background_color = BUTTON_BACKGROUND,
                                    background_normal = '', id = title)
            __new_item.add_widget(__add_button)
            __add_button.bind(on_press = call_back)
            __content.add_widget(__new_item)
        __button1 = Button(text = 'Back', size_hint_y = None,
                                color = BUTTON_COLOR,
                                background_color = BUTTON_BACKGROUND,
                                background_normal = '')
        __content.add_widget(__button1)
        __button1.bind(on_press = self.dismiss)
        __root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.9))
        __root.add_widget(__content)
        self.title = title
        self.content = __root
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.auto_dismiss = True

class TextNumericInput(Popup):
    def __init__(self, title, call_back, **kwargs):
        super(TextNumericInput, self).__init__(**kwargs)
        __content = GridLayout(cols = 1, spacing = 5, size_hint_y = None)
        __content.bind(minimum_height=__content.setter('height'))
        __content.add_widget(TextInput(size_hint_y = None, multiline = False, id = 'new_item'))
        __add_button = Button(text = 'Next', size_hint_y = None,
                                    color = BUTTON_COLOR,
                                    background_color = BUTTON_BACKGROUND,
                                    background_normal = '', id = title)
        __content.add_widget(__add_button)
        __add_button.bind(on_press = call_back)
        __button1 = Button(text = 'Back', size_hint_y = None,
                                color = BUTTON_COLOR,
                                background_color = BUTTON_BACKGROUND,
                                background_normal = '')
        __content.add_widget(__button1)
        __button1.bind(on_press = self.dismiss)
        __root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height/1.9))
        __root.add_widget(__content)
        self.title = title
        self.content = __root
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.auto_dismiss = True

class MessageBox(Popup):
    def __init__(self, title, message, **kwargs):
        super(MessageBox, self).__init__(**kwargs)
        __content = BoxLayout(orientation = 'vertical')
        __label = Label(text = message, size_hint=(1, 1), valign='middle', halign='center')
        __label.bind(
            width=lambda *x: __label.setter('text_size')(__label, (__label.width, None)),
            texture_size=lambda *x: __label.setter('height')(__label, __label.texture_size[1]))
        __content.add_widget(__label)
        __button1 = Button(text = 'Back', size_hint_y = .2,
                            color = BUTTON_COLOR,
                            background_color = BUTTON_BACKGROUND,
                            background_normal = '')
        __content.add_widget(__button1)
        __button1.bind(on_press = self.dismiss)
        self.title = title
        self.content = __content
        self.size_hint = (.8, .8)
        self.size=(400, 400)
        self.auto_dismiss = True

class YesNo(Popup):
    def __init__(self, title, message, yes_callback, no_callback, **kwargs):
        super(YesNo, self).__init__(**kwargs)
        __content = BoxLayout(orientation = 'vertical')
        __label = Label(text = message, size_hint=(1, 1), valign='middle', halign='center')
        __label.bind(
            width=lambda *x: __label.setter('text_size')(__label, (__label.width, None)),
            texture_size=lambda *x: __label.setter('height')(__label, __label.texture_size[1]))
        __content.add_widget(__label)
        __button1 = Button(text = 'Yes', size_hint_y = .2,
                            color = BUTTON_COLOR,
                            background_color = BUTTON_BACKGROUND,
                            background_normal = '')
        __content.add_widget(__button1)
        __button1.bind(on_press = yes_callback)
        __button2 = Button(text = 'No', size_hint_y = .2,
                            color = BUTTON_COLOR,
                            background_color = BUTTON_BACKGROUND,
                            background_normal = '')
        __content.add_widget(__button2)
        __button2.bind(on_press = no_callback)
        self.title = title
        self.content = __content
        self.size_hint = (.8, .8)
        self.size=(400, 400)
        self.auto_dismiss = True

class EditPointScreen(Screen):

    global e4_cfg
    global e4_data

    popup = ObjectProperty(None)

    def on_pre_enter(self):
        #super(Screen, self).__init__(**kwargs)
        self.clear_widgets()
        layout = GridLayout(cols = 2, spacing = 10, size_hint_y = None, id = 'fields')
        layout.bind(minimum_height=layout.setter('height'))
        for field_name in e4_cfg.fields():
            f = e4_cfg.get(field_name)
            layout.add_widget(Label(text = field_name,
                                size_hint_y = None, color = BUTTON_COLOR))
            if field_name in ['SUFFIX','X','Y','Z','PRISM','DATE','VANGLE','HANGLE','SLOPED']:
                if field_name == 'SUFFIX':
                    layout.add_widget(Label(text = str(edm_station.suffix), id = 'SUFFIX',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'X':
                    layout.add_widget(Label(text = str(edm_station.x), id = 'X',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'Y':
                    layout.add_widget(Label(text = str(edm_station.y), id = 'Y',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'Z':
                    layout.add_widget(Label(text = str(edm_station.z), id = 'Z',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'SLOPED':
                    layout.add_widget(Label(text = str(edm_station.sloped), id = 'SLOPED',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'HANGLE':
                    layout.add_widget(Label(text = edm_station.hangle, id = 'HANGLE',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'VANGLE':
                    layout.add_widget(Label(text = edm_station.vangle, id = 'VANGLE',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'DATE':
                    layout.add_widget(Label(text = "%s" % datetime.datetime.now(), id = 'DATE',
                                        size_hint_y = None, color = BUTTON_COLOR))
                if field_name == 'PRISM':
                    prism_button = Button(text = str(edm_station.prism), size_hint_y = None,
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '',
                                    id = field_name)
                    layout.add_widget(prism_button)
                    prism_button.bind(on_press = self.show_menu)
            else:
                if f.inputtype == 'TEXT':
                    layout.add_widget(TextInput(multiline=False, id = field_name))
                if f.inputtype == 'NUMERIC':
                    layout.add_widget(TextInput(id = field_name))
                if f.inputtype == 'MENU':
                    button1 = Button(text = 'MENU', size_hint_y = None,
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '',
                                    id = field_name)
                    layout.add_widget(button1)
                    button1.bind(on_press = self.show_menu)
        button2 = Button(text = 'Save', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button2)
        button2.bind(on_press = self.save)
        button3 = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button3)
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)
        self.add_widget(root)

    def show_menu(self, value):
        if value.id!='PRISM':  
            self.popup = MenuList(value.id, e4_cfg.get(value.id).menu, self.menu_selection)
        else:
            self.popup = MenuList(value.id, edm_prisms.names(), self.prism_change)
        self.popup.open()

    def prism_change(self, value):
        edm_station.z = edm_station.z + edm_station.prism
        edm_station.prism = edm_prisms.get(value.text).height 
        edm_station.z = edm_station.z - edm_station.prism
        for child in self.walk():
            if child.id == value.id:
                child.text = str(edm_station.prism)
            if child.id == 'Z':
                child.text = str(edm_station.z)
        self.popup.dismiss()

    def menu_selection(self, value):
        for child in self.walk():
            if child.id == value.id:
                if value.text == 'Add':
                    for widget in self.popup.walk():
                        if widget.id == 'new_item':
                            child.text = widget.text
                            e4_cfg.update_value(value.id,'MENU',
                                                e4_cfg.get_value(value.id,'MENU') + "," + widget.text) 
                else:
                    child.text = value.text
        self.popup.dismiss()

    def save(self, value):
        new_record = {}
        for widget in self.walk():
            for f in e4_data.fields():
                if widget.id == f:
                    new_record[f] = widget.text
        valid = e4_cfg.valid_datarecord(new_record)
        if valid:
            e4_data.db.insert(new_record)
            edm_units.update_defaults(new_record)
            self.parent.current = 'MainScreen'
        else:
            self.popup = MessageBox('Save Error', valid_record)
            self.popup.open()

class EditPointsScreen(Screen):
    def __init__(self,**kwargs):
        super(EditPointsScreen, self).__init__(**kwargs)
        global e4_data
        self.add_widget(DfguiWidget(e4_data))

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    """ Adds selection and focus behaviour to the view. """
    selected_value = StringProperty('')
    btn_info = ListProperty(['Button 0 Text', 'Button 1 Text', 'Button 2 Text'])

class SelectableButton(RecycleDataViewBehavior, Button):
    """ Add selection support to the Label """
    index = None

    def refresh_view_attrs(self, rv, index, data):
        """ Catch and handle the view changes """
        self.index = index
        return super(SelectableButton, self).refresh_view_attrs(rv, index, data)

    def on_press(self):
        self.parent.selected_value = 'Selected: {}'.format(self.parent.btn_info[int(self.id)])

    def on_release(self):
        MessageBox().open()

class RV(RecycleView):
    rv_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = [{'text': "Datum " + str(x), 'id': str(x)} for x in range(30)]

class DatumLister(BoxLayout,Screen):
    def __init__(self, list_dicts=[], *args, **kwargs):

        super(DatumLister, self).__init__(*args, **kwargs)
        self.orientation = "vertical"
        self.add_widget(RV())

class EditDatumScreen(Screen):
    pass

class StationConfigurationScreen(Screen):
    def __init__(self,**kwargs):
        super(StationConfigurationScreen, self).__init__(**kwargs)
    
        layout = GridLayout(cols = 2, spacing = 5)

        # Station type menu
        self.StationLabel = Label(text="Station type", color = WINDOW_COLOR)
        layout.add_widget(self.StationLabel)
        self.StationMenu = Spinner(text="Simulate", values=("Leica", "Wild", "Topcon", "Simulate"), id = 'station',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.StationMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.StationMenu)

        # Communications type menu
        self.CommTypeLabel = Label(text="Communications", color = WINDOW_COLOR)
        layout.add_widget(self.CommTypeLabel)
        self.CommTypeMenu = Spinner(text="None", values=("Serial", "Bluetooth"), id = 'communications',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.CommTypeMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.CommTypeMenu)

        # Port number
        self.PortNoLabel = Label(text="Port Number", color = WINDOW_COLOR)
        layout.add_widget(self.PortNoLabel)
        self.PortNoMenu = Spinner(text="COM1", values=("COM1", "COM2","COM3","COM4","COM5","COM6"), id = 'comport',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.PortNoMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.PortNoMenu)

        # Speed
        self.SpeedLabel = Label(text="Speed", color = WINDOW_COLOR)
        layout.add_widget(self.SpeedLabel)
        self.SpeedMenu = Spinner(text="1200", values=("1200", "2400","4800","9600"), id = 'baudrate',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.SpeedMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.SpeedMenu)

        # Parity
        self.ParityLabel = Label(text="Parity", color = WINDOW_COLOR)
        layout.add_widget(self.ParityLabel)
        self.ParityMenu = Spinner(text="Even", values=("Even", "Odd","None"), id = 'parity',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.ParityMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.ParityMenu)

        # Databits
        self.DataBitsLabel = Label(text="Data bits", color = WINDOW_COLOR)
        layout.add_widget(self.DataBitsLabel)
        self.DataBitsMenu = Spinner(text="7", values=("7", "8"), id = 'databits',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.DataBitsMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.DataBitsMenu)

        # Stopbits
        self.StopBitsLabel = Label(text="Stop bits", color = WINDOW_COLOR)
        layout.add_widget(self.StopBitsLabel)
        self.StopBitsMenu = Spinner(text="1", values=("0", "1", "2"), id = 'stopbits',
                                    color = OPTIONBUTTON_COLOR,
                                    background_color = OPTIONBUTTON_BACKGROUND,
                                    background_normal = '')
        self.StopBitsMenu.size_hint  = (0.3, 0.2)
        layout.add_widget(self.StopBitsMenu)

        button1 = Button(text = 'Save', size_hint_y = None, id = 'save',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button1)
        button1.bind(on_press = self.close_screen)
        button2 = Button(text = 'Back', size_hint_y = None, id = 'cancel',
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        layout.add_widget(button2)
        button2.bind(on_press = self.close_screen)

        self.add_widget(layout)

    def close_screen(self, instance):
        if instance.id=='save':
            for child in self.children[0].children:
                if child.id=='stopbits':
                    EDMpy.edm_station.stopbits = child.text
                if child.id=='baudrate':
                    EDMpy.edm_station.baudrate = child.text
                if child.id=='databits':
                    EDMpy.edm_station.databits = child.text
                if child.id=='comport':
                    EDMpy.edm_station.comport = child.text
                if child.id=='parity':
                    EDMpy.edm_station.parity = child.text
                if child.id=='communications':
                    EDMpy.edm_station.communications = child.text
                if child.id=='station':
                    EDMpy.edm_station.make = child.text
                ## need code to open com port here
        self.parent.current = 'MainScreen'

class InfoScreen(Screen):
    def __init__(self,**kwargs):
        super(InfoScreen, self).__init__(**kwargs)

        layout = GridLayout(cols = 1, size_hint_y = None)
        layout.bind(minimum_height=layout.setter('height'))
        label = Label(text = "", size_hint_y = None,
                     color = (0,0,0,1), id = 'content',
                     halign = 'left',
                     font_size = TEXT_FONT_SIZE)
        layout.add_widget(label)
        label.bind(texture_size = label.setter('size'))
        label.bind(size_hint_min_x = label.setter('width'))
        button = Button(text = 'Back', size_hint_y = None,
                        color = BUTTON_COLOR,
                        font_size = BUTTON_FONT_SIZE,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
        root = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        root.add_widget(layout)
        self.add_widget(root)
        self.add_widget(button)
        button.bind(on_press = self.go_back)

class StatusScreen(InfoScreen):
    def on_pre_enter(self):
        for widget in self.walk():
            if widget.id=='content':
                txt = e4_data.status() + e4_cfg.status() + e4_ini.status()
                widget.text = txt

    def go_back(self, value):
        self.parent.current = 'MainScreen'

class LogScreen(InfoScreen):
    def on_pre_enter(self):
        for widget in self.walk():
            if widget.id=='content':
                with open('E4.log','r') as f:
                    widget.text = f.read()

    def go_back(self, value):
        self.parent.current = 'MainScreen'

class AboutScreen(InfoScreen):
    def on_pre_enter(self):
        for widget in self.walk():
            if widget.id=='content':
                widget.text = '\n\nE4py by Shannon P. McPherron\n\nVersion ' + __version__ + ' Alpha\nApple Pie\n\nAn OldStoneAge.Com Production\n\nJanuary, 2019'

    def go_back(self, value):
        self.parent.current = 'MainScreen'

# Code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

class HeaderCell(Button):
    color = BUTTON_COLOR
    background_color = BUTTON_BACKGROUND
    background_normal = ''

class TableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, titles = None, *args, **kwargs):
        super(TableHeader, self).__init__(*args, **kwargs)

        for title in titles:
            self.header.add_widget(HeaderCell(text = title))

class ScrollCell(Button):
    text = StringProperty(None)
    is_even = BooleanProperty(None)
    color = BUTTON_COLOR
    background_normal = ''

class TableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    popup = ObjectProperty(None)

    def __init__(self, list_dicts=[], column_names = None, df_name = None, *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(column_names)

        super(TableData, self).__init__(*args, **kwargs)

        self.data = []
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            #row_vals = ord_dict.values()
            k = -1
            if df_name=='points':
                key = list(ord_dict)[0] + '-' + list(ord_dict)[1]
            else:
                key = list(ord_dict)[0]
            for text in ord_dict:
                k += 1
                self.data.append({'text': str(text), 'is_even': is_even,
                                    'callback': self.editcell,
                                    'key': key, 'field': column_names[k],
                                    'db': df_name, 'id': 'datacell' })

    def sort_data(self):
        #TODO: Use this to sort table, rather than clearing widget each time.
        pass

    def editcell(self, key, field, db):
        self.key = key
        self.field = field
        self.db = db
        if db == 'points':
            cfg_field = e4_cfg.get(field)
            self.inputtype = cfg_field.inputtype
            if cfg_field.inputtype == 'MENU':
                self.popup = MenuList(field, e4_cfg.get(field).menu, self.menu_selection)
                self.popup.open()
            if cfg_field.inputtype in ['TEXT','NUMERIC']:
                self.popup = TextNumericInput(field, self.menu_selection)
                self.popup.open()
        else:
            self.popup = TextNumericInput(field, self.menu_selection)
            self.popup.open()

    def menu_selection(self, value):
        ### need some data validation
        if self.db == 'points':
            print(value.id)
            unit, id = self.key.split('-')
            new_data = {}
            if self.inputtype=='MENU':
                new_data[self.field] = value.text
            else:
                for widget in self.popup.walk():
                    if widget.id == 'new_item':
                        new_data[self.field] = widget.text
            field_record = Query()
            e4_data.db.update(new_data, (field_record.UNIT == unit) & (field_record.ID == id))
            for widget in self.walk():
                if widget.id=='datacell':
                    if widget.key == self.key and widget.field == self.field:
                        widget.text = new_data[self.field]
        self.popup.dismiss()

class Table(BoxLayout):

    def __init__(self, list_dicts=[], column_names = None, df_name = None, *args, **kwargs):

        super(Table, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = TableHeader(column_names)
        self.table_data = TableData(list_dicts = list_dicts, column_names = column_names, df_name = df_name)

        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

class DataframePanel(BoxLayout):
    """
    Panel providing the main data frame table view.
    """

    def populate_data(self, df):
        self.df_orig = df
        self.sort_key = None
        self.column_names = self.df_orig.fields()
        self.df_name = df.db_name 
        self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        data = []
        for row in self.df_orig.db:
            data.append(row.values())
        #data = sorted(data, key=lambda k: k[self.sort_key]) 
        self.add_widget(Table(list_dicts = data, column_names = self.column_names, df_name = self.df_name))

class AddNewPanel(BoxLayout):
    
    def populate(self, df):
        self.df_name = df.db_name            
        self.addnew_list.bind(minimum_height=self.addnew_list.setter('height'))
        for col in df.fields():
            self.addnew_list.add_widget(AddNew(col, df.db_name))
        self.addnew_list.add_widget(AddNew('Save', df.db_name))

    def get_addnews(self):
        result=[]
        for opt_widget in self.addnew_list.children:
            result.append(opt_widget.get_addnew())
        return(result)

class AddNew(BoxLayout):

    global edm_datums
    global edm_prisms
    global edm_units
    
    popup = ObjectProperty(None)
    sorted_result = None

    def __init__(self, col, df_name, **kwargs):
        super(AddNew, self).__init__(**kwargs)
        self.df_name = df_name
        self.widget_type = 'data'
        self.height="30sp"
        self.size_hint=(0.9, None)
        self.spacing=10
        if col=='Save':
            self.label = Label(text = "")
            self.button = Button(text = "Save", size_hint=(0.75, 1), font_size="15sp",
                        color = BUTTON_COLOR,
                        background_color = BUTTON_BACKGROUND,
                        background_normal = '')
            self.button.bind(on_press = self.append_data)
            self.add_widget(self.label)
            self.add_widget(self.button)
            self.widget_type = 'button'
        else:
            self.label = Label(text = col, color = WINDOW_COLOR)
            self.txt = TextInput(multiline=False, size_hint=(0.75, None), font_size="15sp")
            self.txt.bind(minimum_height=self.txt.setter('height'))
            self.add_widget(self.label)
            self.add_widget(self.txt)

    def get_addnew(self):
        return (self.label.text, self.txt.text)

    def append_data(self, instance):
        result = {}
        message = ''
        for obj in instance.parent.parent.children:
            if obj.widget_type=='data':
                result[obj.label.text] = obj.txt.text 
                obj.txt.text = ''
        sorted_result = {}
        ### this code needs one set of if/then that then sets a variable that refres
        ### to the class that is being operated on
        if self.df_name == 'prisms':
            for f in edm_prisms.fields():
                sorted_result[f] = result[f]
            if edm_prisms.duplicate(sorted_result):
                message = 'Overwrite existing prism named %s' % sorted_result['name']
            else:
                message = edm_prisms.valid(sorted_result)
                if not message:
                    edm_prisms.db.insert(sorted_result)
        if self.df_name == 'units':
            for f in edm_units.fields():
                sorted_result[f] = result[f]
            edm_units.db.insert(sorted_result)
        if self.df_name == 'datums':
            for f in edm_datums.fields():
                sorted_result[f] = result[f]
            edm_datums.db.insert(sorted_result)
        if message:
            self.sorted_result = sorted_result
            self.popup = YesNo('Edit', message, self.replace, self.do_nothing)
        else:
            for obj in instance.parent.parent.children:
                if obj.widget_type=='data':
                    obj.txt.text = ''

    def replace(self, value):
        if self.df_name == 'prisms':
            edm_prisms.replace(self.sorted_result)
        if self.df_name == 'units':
            edm_units.replace(self.sorted_result)
        if self.df_name == 'datums':
            edm_datums.replace(self.sorted_result)
        ### Need to clear form here as well
        self.popup.dismiss()

    def do_nothing(self, value):
        self.popup.dismiss()

class DfguiWidget(TabbedPanel):

    def __init__(self, df, **kwargs):
        super(DfguiWidget, self).__init__(**kwargs)
        self.df = df
        self.df_name = df.db_name
        self.panel1.populate_data(df)
        self.panel4.populate(df)
        self.color = BUTTON_COLOR
        self.background_color = WINDOW_BACKGROUND
        self.background_image = ''

    # This should be changed so that the table isn't rebuilt
    # each time settings change.
    def open_panel1(self):
        self.panel1._generate_table()
    
    def cancel(self):
        pass

# End code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

class YesNoCancel(Popup):
    def __init__(self, caption, cancel = False, **kwargs):
        super(YesNoCancel, self).__init__(**kwargs)
        box = BoxLayout()
        self.label = Label(text = caption)
        self.button1 = Button(text = "Yes", size_hint=(0.75, 1), font_size="15sp")
        self.button1.bind(on_press = self.yes)
        self.button2 = Button(text = "No", size_hint=(0.75, 1), font_size="15sp")
        self.button2.bind(on_press = self.no)
        box.add_widget(self.label)
        box.add_widget(self.button1)
        box.add_widget(self.button2)
        if cancel == True:
            box.button3 = Button(text = "Cancel", size_hint=(0.75, 1), font_size="15sp")
            box.button3.bind(on_press = self.cancel)
            box.add_widget(self.button3)
        self.add_widget(box)
        self.open()
    def yes(self, instance):
        return('Yes')
    def no(self, instance):
        return('No')
    def cancel(self, instance):
        return('Cancel')

class E4py(App):

    def build(self):
        Window.clearcolor = WINDOW_BACKGROUND
        self.title = "E4py " + __version__

        #sm.current = 'main'
        #df = create_dummy_data(0)
        #df = edm_datums.datums 
        #test = YesNoCancel("This is a test of a yes no popup box", cancel=False)
        #print(test)
        #return(DfguiWidget(EDMpy.edm_datums.datums, "datums"))
    
Factory.register('E4py', cls=E4py)

if __name__ == '__main__':
    logger.info('E4 started.')
    database = 'E4'
    e4_ini = ini('E4.ini')
    e4_cfg = cfg(e4_ini.get_value("E4", "CFG"))
    e4_data = db(database + '_data.json')
    if not e4_cfg.filename:
        e4_cfg.filename = 'EDMpy.cfg'
    e4_cfg.save()
    e4_ini.update()
    e4_ini.save()
    
    E4py().run()