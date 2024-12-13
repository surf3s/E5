from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.recycleview import RecycleView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Text
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.metrics import Metrics

from decimal import DivisionByZero

import ntpath
import os
from shutil import copyfile
from datetime import datetime
from tinydb import Query, where
import re
import requests
import json
import urllib
import random
import string
from threading import Thread
# from appdata import AppDataPaths
from platformdirs import *

from e5py.constants import __SPLASH_HELP__
from e5py.constants import APP_NAME
from e5py.colorscheme import ColorScheme, make_rgb, BLACK, WHITE, GOOGLE_COLORS, MIDDLE_GREY, DARK_GREY
from e5py.misc import platform_name, locate_file


SCROLLBAR_WIDTH = 5
TEXTBOX_HEIGHT = 30


def width_calculator(fraction_size=.8, maximum_width=800):
    if Window.size[0] * fraction_size > maximum_width:
        return maximum_width / Window.size[0]
    else:
        return fraction_size


def height_calculator(desired_size):
    ratio = desired_size / Window.size[1]
    if ratio > .9:
        ratio = .9
    return ratio


def set_color(popup, colors):
    if not popup:
        return colors.text_color if colors else make_rgb(BLACK)
    else:
        return colors.popup_text_color if colors else make_rgb(WHITE)


class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)


class e5_PopUpMenu(Popup):
    def __init__(self, title, menu_list, message='', menu_selected='', call_back=None, colors=None, **kwargs):
        super(e5_PopUpMenu, self).__init__(**kwargs)

        pop_content = GridLayout(cols=1, size_hint_y=1, spacing=5, padding=5)

        ncols = int(Window.width / 200)
        ncols = max(1, ncols)

        if message:
            label = e5_scrollview_label(message, popup=True, colors=colors)
            label.size_hint = (1, .2)
            pop_content.add_widget(label)

        menu = e5_scrollview_menu(menu_list, menu_selected,
                                                 widget_id='menu',
                                                 call_back=[call_back],
                                                 ncols=ncols,
                                                 colors=colors)
        pop_content.add_widget(menu)
        menu.make_scroll_menu_item_visible()

        pop_content.add_widget(e5_button('Back', selected=True, height=self.calc_button_height(),
                                                 call_back=self.dismiss,
                                                 colors=colors))

        self.content = pop_content
        self.title = title
        self.size_hint = (.9, .9)
        self.auto_dismiss = True

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height


class db_filter(Popup):

    def __init__(self, default_field='', fields=[], call_back=None, colors=None, **kwargs):
        super(db_filter, self).__init__(**kwargs)

        self.size_hint_x = .7
        self.size_hint_y = None

        spinner_dropdown_button = SpinnerOptions
        spinner_dropdown_button.font_size = colors.button_font_size.replace("sp", '') if colors.button_font_size else None
        spinner_dropdown_button.background_color = (0, 0, 0, 1)

        pop_content = GridLayout(cols=1, spacing=5, padding=5)
        field_value = GridLayout(cols=2, spacing=5, padding=5)
        self.fields_dropdown = Spinner(text=default_field, values=fields,
                                        size_hint=(.5, None),
                                        option_cls=spinner_dropdown_button)
        field_value.add_widget(self.fields_dropdown)
        field_value_right = GridLayout(cols=1, spacing=5, padding=5)
        field_value_right.add_widget(e5_label('Select a field and enter a\nvalue to match in this field.', size_hint=(1, .2), halign='left', popup=True))
        self.value_input = e5_textinput(size_hint=(0.75, None), id='value', write_tab=False)
        self.value_input.bind(minimum_height=self.value_input.setter('height'))
        field_value_right.add_widget(self.value_input)
        field_value.add_widget(field_value_right)
        pop_content.add_widget(field_value)
        buttons = e5_side_by_side_buttons(text=['Back', 'Apply'],
                                            button_height=None,
                                            id=['back', 'apply'],
                                            selected=[True, True],
                                            call_back=[self.dismiss, call_back],
                                            colors=colors)
        pop_content.add_widget(buttons)
        self.content = pop_content
        self.content.bind(minimum_height=self.fix_height)
        self.title = 'Filter dataset'

    def fix_height(self, *args):
        instance = Text(text=self.title, font_size=self.title_size)
        width, height = instance.render()
        self.height = self.content.minimum_height * 2 + height + 40


class edm_manual(Popup):

    def __init__(self, type="Manual XYZ", call_back=None, colors=None, **kwargs):
        super(edm_manual, self).__init__(**kwargs)
        self.size_hint_x = .7
        self.size_hint_y = None

        pop_content = GridLayout(cols=1, spacing=5, padding=5)
        if type == "Manual XYZ":
            input = DataGridLabelAndField(col='X', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.xcoord = input.txt
            pop_content.add_widget(input)
            input = DataGridLabelAndField(col='Y', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.ycoord = input.txt
            pop_content.add_widget(input)
            input = DataGridLabelAndField(col='Z', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.zcoord = input.txt
            pop_content.add_widget(input)
            self.hangle = None
            self.vangle = None
            self.sloped = None
        else:
            input = DataGridLabelAndField(col='Horizontal angle', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.hangle = input.txt
            pop_content.add_widget(input)
            input = DataGridLabelAndField(col='Vertical angle', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.vangle = input.txt
            pop_content.add_widget(input)
            input = DataGridLabelAndField(col='Slope distance', colors=colors, popup=True)
            input.txt.bind(on_text_validate=self.next_field)
            self.sloped = input.txt
            pop_content.add_widget(input)
            self.xcoord = None
            self.ycoord = None
            self.zcoord = None
        buttons = e5_side_by_side_buttons(text=['Cancel', 'Next'],
                                            button_height=None,
                                            id=['cancel', 'next'],
                                            selected=[True, True],
                                            call_back=[self.dismiss, call_back],
                                            colors=colors)
        self.call_back = call_back
        pop_content.add_widget(buttons)
        self.content = pop_content
        self.content.bind(minimum_height=self.fix_height)
        self.title = 'Manual Input'
        # self.size_hint = (.9, height_calculator(280))
        self.auto_dismiss = True
        self.type = type

    def fix_height(self, *args):
        instance = Text(text=self.title, font_size=self.title_size)
        width, height = instance.render()
        self.height = self.content.minimum_height + height + 40

    def is_numeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def valid_data(self):
        if self.type == 'Manual XYZ':
            return all([self.is_numeric(txt) for txt in [self.xcoord.textbox.text, self.ycoord.textbox.text, self.zcoord.textbox.text]])
        elif self.type == 'Manual VHD':
            return all([self.is_numeric(txt) for txt in [self.hangle.textbox.text, self.vangle.textbox.text, self.sloped.textbox.text]])

    def on_open(self):
        if self.xcoord is not None:
            self.xcoord.focus = True
        elif self.hangle is not None:
            self.hangle.focus = True

    def next_field(self, instance):
        if instance.id in ['Slope distance', 'Z']:
            self.call_back(instance)
        instance.get_focus_next().focus = True


class e5_textinput_without_clear(TextInput):
    id = ObjectProperty('')
    text_length = ObjectProperty(0)

    def __init__(self, colors=None, multiline=False, **kwargs):
        super(e5_textinput_without_clear, self).__init__()
        self.size_hint_y = None
        if colors is not None:
            if colors.text_font_size is None:
                colors.text_font_size = 12
            self.font_size = colors.text_font_size
        if 'id' in kwargs:
            self.id = kwargs.get('id')
            if self.id in ['X', 'Y', 'Z', 'PRISM', 'SLOPED', 'STATIONX', 'STATIONY', 'STATIONZ', 'DATUMX', 'DATUMY', 'DATUMZ', 'LOCALX', 'LOCALY', 'LOCALZ'] and APP_NAME == 'EDM':
                self.bind(on_text_validate=self.do_coordinate_math)
        if 'text_length' in kwargs:
            self.text_length = kwargs.get('text_length')

        instance = Text(text='Shannon', font_size=self.font_size)
        width, height = instance.render()
        if multiline:
            self.height = (height * 4 + self.border[0] + self.border[2]) * 1.2
        else:
            self.height = (height + self.border[0] + self.border[2]) * 1.2
        self.multiline = multiline

    def do_coordinate_math(self, instance):
        if instance.text:
            try:
                self.text = str(eval(instance.text))
            except (DivisionByZero, NameError, SyntaxError):
                pass

    def insert_text(self, substring, from_undo=False):
        if self.text_length:
            s = '' if len(self.text) > self.text_length else substring
        elif not self.multiline and substring == '\n':
            s = ''
        else:
            s = substring
        return super().insert_text(s, from_undo=from_undo)


class e5_textinput(GridLayout):

    def __init__(self, colors=None, multiline=False, **kwargs):
        super(e5_textinput, self).__init__()

        self.cols = 2
        self.spacing = 0
        self.size_hint = (1, None)
        # self.height = TEXTBOX_HEIGHT - june 1

        self.textbox = e5_textinput_without_clear(colors=colors, multiline=multiline, **kwargs)
        # self.textbox.bind(text = self.update_text)
        # self.text = self.textbox.text
        # self.textbox.text = text
        if 'text' in kwargs:
            self.textbox.text = kwargs.get('text')
        self.add_widget(self.textbox)

        if multiline:
            button_height = (self.textbox.height - self.textbox.border[0] - self.textbox.border[2]) / 1.2
            button_height = (button_height / 4 + self.textbox.border[0] + self.textbox.border[2]) * 1.2
        else:
            button_height = self.textbox.height
        self.clear_button = Button(text='X', width=button_height,
                                    size_hint=(None, None), height=button_height,
                                    background_normal='',
                                    background_color=(.2, .2, .2, 1),
                                    on_press=self.clear_text_box)
        self.add_widget(self.clear_button)

    # def update_text(self, instance, value):
    #     self.text = instance.text

    def clear_text_box(self, instance):
        self.textbox.text = ''


class e5_label(Label):
    id = ObjectProperty('')

    def __init__(self, text, popup=False, colors=None, label_height=None, **kwargs):
        super(e5_label, self).__init__(**kwargs)
        self.text = text
        self.color = set_color(popup, colors)
        if colors:
            if colors.text_font_size:
                self.font_size = colors.text_font_size
        # if label_height is None:
        self.bind(size=self.setter('text_size'))
        # else:
        #     self.height = label_height
        # self.height = 30 if label_height is None else label_height
        # self.halign = 'center'
        self.valign = 'top'


class e5_label_wrapped(e5_label):
    def __init__(self, text, popup=False, colors=None, **kwargs):
        super(e5_label_wrapped, self).__init__(text, popup=False, colors=None, **kwargs)
        self.size_hint = (1, None)
        self.bind(width=lambda *x: self.setter('text_size')(self, (self.width, None)),
                                texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class e5_side_by_side_buttons(GridLayout):
    def __init__(self, text,
                    id=['', ''], selected=[False, False],
                    call_back=[None, None], button_height=None, colors=None, **kwargs):
        super(e5_side_by_side_buttons, self).__init__(**kwargs)
        self.cols = len(id)
        self.spacing = 5
        self.size_hint_y = button_height
        # self.height = button_height
        for i in range(len(id)):
            self.add_widget(e5_button(text[i],
                            id=id[i],
                            selected=selected[i], call_back=call_back[i],
                            button_height=button_height, colors=colors, **kwargs))


class e5_button(FocusBehavior, Button):
    id = ObjectProperty('')

    def __init__(self, text,
                    id='',
                    selected=False, call_back=None, on_focus=None,
                    button_height=None, colors=None, **kwargs):
        super(e5_button, self).__init__(**kwargs)
        self.colors = colors
        self.text = text
        self.size_hint_y = button_height
        self.id = id
        if colors:
            if colors.button_font_size:
                self.font_size = colors.button_font_size
        self.color = colors.button_color if colors else make_rgb(WHITE)
        if colors:
            self.background_color = colors.button_background if selected else colors.optionbutton_background
        else:
            self.background_color = make_rgb(GOOGLE_COLORS['light blue'][2 if selected else 0])
        if call_back:
            self.bind(on_press=call_back)
        self.background_normal = ''
        self.call_back = call_back

    def on_focus(self, instance, value, *largs):
        if self.background_color and self.colors:
            self.background_color = self.colors.button_background if self.focus else self.colors.optionbutton_background


class e5_scrollview_menu(ScrollView):
    id = ObjectProperty(None)
    scrollbox = ObjectProperty(None)
    menu_selected_widget = None

    def __init__(self, menu_list, menu_selected, widget_id='', call_back=[None], ncols=1, colors=None, **kwargs):
        super(e5_scrollview_menu, self).__init__(**kwargs)
        self.colors = colors
        self.scroll_type = ['bars', 'content']
        self.effect_cls = 'ScrollEffect'
        self.scrollbox = GridLayout(cols=ncols, size_hint_y=None, spacing=[5, 20 if platform_name() == 'Android' else 5])
        self.scrollbox.bind(minimum_height=self.scrollbox.setter('height'))

        self.menu_selected_widget = None
        if menu_list:
            if len(call_back) == 1:
                call_back = call_back * len(menu_list)

            height = self.calc_button_height()
            for menu_item in menu_list:
                menu_button = e5_button(menu_item, menu_item, height=height,
                                        selected=(menu_item == menu_selected),
                                        call_back=call_back[menu_list.index(menu_item)],
                                        colors=colors)
                menu_button.halign = 'center'
                menu_button.bind(size=self.set_text_width)
                self.scrollbox.add_widget(menu_button)
                if menu_item == menu_selected:
                    self.menu_selected_widget = menu_button
        else:
            self.scrollbox.add_widget(Button(text='', background_normal=''))
        # self.size_hint = (1, 1)
        self.id = widget_id + '_scroll'
        self.add_widget(self.scrollbox)

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height

    def set_text_width(self, instance, value):
        instance.text_size = (instance.width, None)

    def scroll_menu_clear_selected(self):
        if self.menu_selected_widget:
            self.menu_selected_widget.background_color = self.colors.optionbutton_background
            self.menu_selected_widget = None

    def scroll_menu_get_selected(self):
        return self.menu_selected_widget

    def scroll_menu_set_selected(self, text):
        self.scroll_menu_clear_selected()
        n = 0
        for widget in self.scrollbox.children:
            n = n + 1
            if widget.text.upper() == text.upper():
                widget.background_color = self.colors.button_background
                self.menu_selected_widget = widget
                break
        if n == 1:
            widget.background_color = self.colors.button_background
            self.menu_selected_widget = widget

    def scroll_menu_list(self):
        menu_list = []
        for widget in self.scrollbox.children:
            menu_list.append(widget.text)
        menu_list.reverse()
        return menu_list
        # return([widget.text for widget in self.scroll_menu.children])

    def make_scroll_menu_item_visible(self):
        if self.menu_selected_widget is not None:
            if self.scrollbox.height > self.height:
                self.scroll_to(self.menu_selected_widget)

    def move_scroll_menu_item(self, ascii_code):
        menu_list = self.scroll_menu_list()
        if self.menu_selected_widget is not None:
            index_no = menu_list.index(self.menu_selected_widget.text)
        else:
            index_no = 0

        if index_no >= 0:
            new_index = -1
            if ascii_code == 279:
                new_index = len(menu_list) - 1
            elif ascii_code == 278:
                new_index = 0
            elif ascii_code == 273:  # Up
                new_index = max([index_no - self.children[0].cols, 0])
            elif ascii_code == 276:
                new_index = max([index_no - 1, 0])
            elif ascii_code == 274:  # Down
                new_index = min([index_no + self.children[0].cols, len(menu_list) - 1])
            elif ascii_code == 275:
                new_index = min([index_no + 1, len(menu_list) - 1])
            if new_index >= 0:
                self.scroll_menu_set_selected(menu_list[new_index])
                self.make_scroll_menu_item_visible()
                # if self.get_widget_by_id('field_data'):
                #    self.get_widget_by_id('field_data').text = menu_list[new_index]

    def scroll_menu_char_match(self, match_str):
        menu_list = self.scroll_menu_list()
        if menu_list:
            index_no = menu_list.index(self.scroll_menu_get_selected().text)

            new_index = (index_no + 1) % len(menu_list)
            while not new_index == index_no:
                if menu_list[new_index].upper()[0] == match_str.upper():
                    self.scroll_menu_set_selected(menu_list[new_index])
                    self.make_scroll_menu_item_visible()
                    break
                else:
                    new_index = (new_index + 1) % len(menu_list)
                    # need new logic to auto select when only one case is available


class e5_scrollview_label(ScrollView):
    id = ObjectProperty(None)

    def __init__(self, text, widget_id='', popup=False, colors=None, **kwargs):
        super(e5_scrollview_label, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()
        self.text = text
        self.scroll_type = ['bars', 'content']
        self.effect_cls = 'ScrollEffect'
        scrollbox = GridLayout(cols=1, size_hint_y=None, spacing=5)
        scrollbox.bind(minimum_height=scrollbox.setter('height'))

        self.scrolling_label = e5_label(text=self.text, markup=True,
                                        size_hint_y=None,
                                        color=self.colors.text_color if not popup else self.colors.popup_text_color,
                                        id=widget_id + '_label', popup=popup,
                                        text_size=(self.width, None))
        if colors is not None:
            if colors.text_font_size:
                self.scrolling_label.font_size = colors.text_font_size

        self.scrolling_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        self.scrolling_label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value * .95, None)))

        # info.bind(texture_size=lambda *x: info.setter('height')(info, info.texture_size[1]))
        scrollbox.add_widget(self.scrolling_label)

        self.bar_width = SCROLLBAR_WIDTH
        self.size_hint = (1, 1)
        self.id = widget_id + '_scroll'
        self.add_widget(scrollbox)


class e5_MainScreen(Screen):

    popup = ObjectProperty(None)
    popup_open = False
    event = ObjectProperty(None)
    widget_with_focus = ObjectProperty(None)
    text_color = (0, 0, 0, 1)
    title = APP_NAME
    ini_path = os.path.join(user_data_dir(APP_NAME, 'OSA'), APP_NAME + '.ini')
    menu_height = .1

    def setup_program(self):
        warnings, errors = [], []
        self.ini.open(self.ini_path)
        if not self.ini.first_time:
            if self.ini.get_value(APP_NAME, 'ColorScheme'):
                self.colors.set_to(self.ini.get_value(APP_NAME, 'ColorScheme'))
            if self.ini.get_value(APP_NAME, 'DarkMode').upper() == 'TRUE':
                self.colors.darkmode = True
            else:
                self.colors.darkmode = False

            if self.ini.get_value(APP_NAME, 'ButtonFontSize'):
                self.colors.button_font_size = (self.ini.get_value(APP_NAME, 'ButtonFontSize'))
            if self.ini.get_value(APP_NAME, 'TextFontSize'):
                self.colors.text_font_size = (self.ini.get_value(APP_NAME, 'TextFontSize'))

            if self.ini.get_value(APP_NAME, "CFG"):
                has_errors, errors = self.cfg.open(self.ini.get_value(APP_NAME, "CFG"))
                if self.cfg.filename and not has_errors:
                    warnings, errors = self.open_db()
            self.ini.update(self.colors, self.cfg)
            self.ini.save()
        self.colors.set_colormode()
        self.colors.need_redraw = False
        return warnings, errors

    def get_path(self):
        if self.ini.get_value(APP_NAME, "CFG"):
            return ntpath.split(self.ini.get_value(APP_NAME, "CFG"))[0]
        else:
            return user_documents_dir()

    def get_files(self, fpath, exts=None):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(fpath):
            files.extend(filenames)
            break
        if exts:
            return [filename for filename in files if filename.upper().endswith(exts.upper())]
        else:
            return files

    def open_db(self):
        warnings = []
        errors = []
        database = locate_file(self.cfg.get_value(APP_NAME, 'DATABASE'), self.cfg.path)
        if not database:
            database = os.path.split(self.cfg.filename)[1]
            if "." in database:
                database = database.split('.')[0]
            database = os.path.join(self.cfg.path, database + '.json')
            warning = f"Could not locate the data file {self.cfg.get_value(APP_NAME, 'DATABASE')} as specified in the CFG file.  "
            warning += f'{APP_NAME} looked in the specified location and also in '
            warning += f'in the same folder as the CFG file {self.cfg.path}.  A new empty data file was created as {database}.  '
            warning += 'If this is not correct, leave the program and alter the CFG file '
            warning += "and/or move the data file to the correct location."
            warnings.append(warning)
        if database.lower().endswith('.mdb') or database.lower().endswith('.sdf'):
            database = database[:-4] + '.json'
            warning = APP_NAME + ' does not accept the mdb and sdf data files that were used with EDMWin, EDM-Mobile and E4.  '
            warning += f'A new, empty json format file has been opened in this case.  The filename is {database}.  '
            warning += 'JSON files are human readable ASCII files.'
            if APP_NAME == 'EDM':
                warning += 'To move your data from the old format to this program, '
                warning += 'follow the directions found on the EDM GitHub site '
                warning += 'https://github.com/surf3s/EDM/tree/master/Import_from_EDM-Mobile or https://github.com/surf3s/EDM/tree/master/Import_from_EDMWin.  '
                warning += 'Basically you need to create csv files that can be imported into this program.  '
                warning += 'EDM-Mobile will create them for you.  With EDMWin you need to create them youself.  '
                warning += 'Alternatively, you can hand enter items like datums, units, and prisms using the various menu options under Edit.'
            warnings.append(warning)
        if not self.data.valid_format(database):
            error = f'The file {database} does not load as a valid json file.  If the wrong file has been loaded, edit the CFG file to point to the '
            error += 'correct database.  If the file is the correct one, then it appears that it has become corrupted.  Open the file in any text '
            error += 'editor and assess the situation.  A json file is a human readable file format, and you should be able to see your data.  '
            error += 'If you need more help fixing the problem, you can contact me.'
            errors.append(error)
        else:
            self.data.open(database)
            if self.cfg.get_value(APP_NAME, 'TABLE'):
                self.data.table = self.cfg.get_value(APP_NAME, 'TABLE')
            else:
                self.data.table = '_default'
            self.cfg.update_value(APP_NAME, 'DATABASE', self.data.filename)
            self.cfg.update_value(APP_NAME, 'TABLE', self.data.table)
            self.cfg.save()
            self.data.new_data[self.data.table] = True
        return (warnings, errors)

    def warnings_and_errors_popup(self, warnings, errors):
        message_txt = '\n'
        message_txt += ',\n\n'.join(['Warning: ' + warning for warning in warnings])
        message_txt += ',\n\n'.join(['Error: ' + error for error in errors])
        return e5_MessageBox('Warnings and errors', message_txt, colors=self.colors)

    def show_popup_message(self, dt):
        # print('.', end='')
        self.event.cancel()
        if self.cfg.has_errors or self.cfg.has_warnings:
            if self.cfg.has_errors:
                message_text = f'\nThe following errors were found in the configuration file {self.cfg.filename} '\
                               'and must be corrected before data entry can begin.\n\n'
                self.cfg.filename = ''
                title = 'CFG File Errors'
            elif self.cfg.has_warnings:
                self.cfg.has_warnings = False
                message_text = '\nThough data collection can start, there are the following warnings in '\
                                    f'the configuration file {self.cfg.filename}.\n\n'
                title = 'Warnings'
            message_text = message_text + '\n\n'.join(self.cfg.errors)
        else:
            title = APP_NAME
            message_text = __SPLASH_HELP__
        self.popup = e5_MessageBox(title, message_text, call_back=self.close_popup, colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def get_widget_by_id(self, id):
        for widget in self.walk():
            if hasattr(widget, 'id'):
                if widget.id == id:
                    return widget
        return None

    def get_info(self):
        if self.cfg.current_field.infofile:
            fname = os.path.join(self.cfg.path, self.cfg.current_field.infofile)
            if os.path.exists(fname):
                try:
                    with open(fname, 'r') as f:
                        return f.read()
                except OSError:
                    return f'Could not open file {fname}.'
            else:
                return f'The file {fname} does not exist.'
        else:
            return self.cfg.current_field.info

    def save_window_location(self):
        self.ini.update_value(APP_NAME, 'ScreenTop', max(Window.top, 0))
        self.ini.update_value(APP_NAME, 'ScreenLeft', max(Window.left, 0))
        self.ini.update_value(APP_NAME, 'ScreenWidth', int(Window.size[0] / Metrics.density))
        self.ini.update_value(APP_NAME, 'ScreenHeight', int(Window.size[1] / Metrics.density))
        self.ini.save()

    def open_popup(self):
        self.popup_open = False
        self.popup.open()

    def dismiss_popup(self, *args):
        self.popup_open = False
        if self.popup:
            self.popup.dismiss()
        if self.parent:
            self.parent.current = 'MainScreen'

    def save_record(self):
        valid = self.cfg.validate_current_record()
        if valid:
            if self.data.save(self.cfg.current_record):
                self.make_backup()
            else:
                pass
        else:
            self.popup = e5_MessageBox('Save Error', valid, call_back=self.close_popup, colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True

    def make_backup(self):
        if self.ini.backup_interval > 0:
            try:
                record_counter = int(self.cfg.get_value(APP_NAME, 'RECORDS UNTIL BACKUP')) \
                    if self.cfg.get_value(APP_NAME, 'RECORDS UNTIL BACKUP') else self.ini.backup_interval
                record_counter -= 1
                if record_counter <= 0:
                    backup_path, backup_file = os.path.split(self.data.filename)
                    backup_file, backup_file_ext = backup_file.split('.')
                    backup_file += self.datetime_stamp() if self.ini.incremental_backups else '_backup'
                    backup_file += "." + backup_file_ext
                    backup_file = os.path.join(backup_path, backup_file)
                    copyfile(self.data.filename, backup_file)
                    record_counter = self.ini.backup_interval
                self.cfg.update_value(APP_NAME, 'RECORDS UNTIL BACKUP', str(record_counter))
            except OSError:
                self.popup = e5_MessageBox('Backup Error', "\n An error occurred while attempting to make a backup.  "
                                            "Check the backup settings and that the disk has enough space for a backup.",
                                            call_back=self.close_popup, colors=self.colors)
                self.popup.auto_dismiss = False
                self.popup.open()
                self.popup_open = True

    def date_stamp(self):
        date_stamp = '%s' % datetime.now().replace(microsecond=0)
        date_stamp = date_stamp.split(' ')[0]
        date_stamp = date_stamp.replace('-', '_')
        return '_' + date_stamp

    def datetime_stamp(self):
        time_stamp = '%s' % datetime.now().replace(microsecond=0)
        time_stamp = time_stamp.replace('-', '_')
        time_stamp = time_stamp.replace(' ', '_')
        time_stamp = time_stamp.replace(':', '_')
        return '_' + time_stamp

    def close_popup(self, value):
        self.popup.dismiss()
        self.popup_open = False
        self.event = Clock.schedule_once(self.set_focus, 1)

    def set_focus(self, value):
        self.widget_with_focus.focus = True

    def show_delete_last_object(self):
        last_record = self.data.last_record()
        if last_record:
            message_text = '\n Delete the following records?\n\n'
            if 'UNIT' in last_record.keys() and 'ID' in last_record.keys():
                unit = last_record["UNIT"]
                idno = last_record["ID"]
                a_record = Query()
                records_to_delete = self.data.db.table(self.data.table).search(a_record.UNIT.matches('^' + unit + '$', flags=re.IGNORECASE) and a_record.ID.matches('^' + idno + '$', flags=re.IGNORECASE))
                for record in records_to_delete:
                    for field in self.cfg.fields():
                        if field in record:
                            message_text += "%s : %s \n" % (field, record[field])
                    message_text += '\n\n'
                self.popup = e5_MessageBox('Delete last object', message_text, response_type="YESNO",
                                            call_back=[self.delete_last_object, self.close_popup],
                                            colors=self.colors)
            else:
                self.popup = e5_MessageBox('Delete last object',
                                            '\n For now, this option requires a field called UNIT and another called ID.',
                                            call_back=self.close_popup,
                                            colors=self.colors)
        else:
            self.popup = e5_MessageBox('Delete last object', '\n No records in table to delete.',
                                        call_back=self.close_popup,
                                        colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def delete_last_object(self, value):
        last_record = self.data.last_record()
        unit = last_record["UNIT"]
        idno = last_record["ID"]
        a_record = Query()
        records_to_delete = self.data.db.table(self.data.table).search(a_record.UNIT.matches('^' + unit + '$', flags=re.IGNORECASE) and a_record.ID.matches('^' + idno + '$', flags=re.IGNORECASE))
        for record in records_to_delete:
            self.data.delete(record.doc_id)
        self.data.new_data[self.data.table] = True
        self.close_popup(value)

    def show_delete_last_record(self):
        if self.cfg.filename and self.data.filename:
            last_record = self.data.last_record()
            if last_record:
                message_text = '\n'
                for field in self.cfg.fields():
                    if field in last_record:
                        message_text += "%s : %s \n" % (field, last_record[field])
                self.popup = e5_MessageBox('Delete Last Record', message_text, response_type="YESNO",
                                            call_back=[self.delete_last_record, self.close_popup],
                                            colors=self.colors)
            else:
                self.popup = e5_MessageBox('Delete Last Record', '\n No records in table to delete.',
                                            call_back=self.close_popup,
                                            colors=self.colors)
        else:
            self.popup = e5_MessageBox('E5', '\nOpen a CFG before trying to edit records.',
                                        call_back=self.dismiss_popup,
                                        colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def delete_last_record(self, value):
        last_record = self.data.last_record()
        self.data.delete(last_record.doc_id)
        self.data.new_data[self.data.table] = True
        self.close_popup(value)

    def show_delete_all_records(self, table_name=None):
        if not self.cfg.filename or not self.data.filename:
            self.popup = e5_MessageBox('E5', '\nOpen a CFG before trying to edit records.',
                                        call_back=self.dismiss_popup,
                                        colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True
            return
        if len(self.data.db.table(self.data.table).all()) == 0:
            self.popup = e5_MessageBox('E5', '\nThere are no data records to delete.',
                                        call_back=self.dismiss_popup,
                                        colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True
            return

        if not table_name:
            message_text = '\n You are asking to delete all of the records in the current database table. Are you sure you want to do this?'
            self.delete_table = self.data.table
        else:
            message_text = f'\n You are asking to delete all of the records in the {table_name} table. Are you sure you want to do this?'
            self.delete_table = table_name
        self.popup = e5_MessageBox('Delete All Records', message_text, response_type="YESNO",
                                    call_back=[self.delete_all_records1, self.close_popup],
                                    colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def delete_all_records1(self, value):
        self.popup.dismiss()
        self.popup_open = False
        message_text = f'\nThis is your last chance.  All records in the {self.delete_table} table will be deleted when you press Yes.'
        self.popup = e5_MessageBox('Delete All Records', message_text, response_type="YESNO",
                                    call_back=[self.delete_all_records2, self.close_popup],
                                    colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def delete_all_records2(self, value):
        self.data.delete_all(self.delete_table)
        self.data.new_data[self.data.table] = True
        self.popup.dismiss()
        self.popup_open = False
        if APP_NAME == 'EDM':
            self.update_info_label()

    def show_save_csvs(self, *args):
        if self.cfg.filename and self.data.filename:
            self.csv_data_type = args[0].id.lower() if len(args) > 0 else self.data.table
            filename = ntpath.split(self.cfg.filename)[1].split(".")[0]
            filename = filename + "_" + self.csv_data_type + self.date_stamp() + '.csv'
            content = e5_SaveDialog(filename=filename,
                                    start_path=self.cfg.path,
                                    save=self.save_csvs,
                                    cancel=self.dismiss_popup,
                                    colors=self.colors)
            self.popup = Popup(title="Export CSV file",
                                content=content,
                                size_hint=(0.9, 0.9))
        else:
            self.popup = e5_MessageBox('E5', '\n Open a CFG before exporting to CSV',
                                        call_back=self.dismiss_popup,
                                        colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def save_csvs(self, instance):

        filename = os.path.join(self.popup.content.filesaver.path, self.popup.content.filename)

        self.popup.dismiss()

        response = self.do_save_csv(filename)

        if not response:
            response = f'\n The table {self.csv_data_type} was successfully written as the file {filename}.'
        self.popup = e5_MessageBox('CSV Export', response, call_back=self.close_popup, colors=self.colors)
        self.popup.open()
        self.popup_open = True

    def do_save_csv(self, filename):
        if APP_NAME == 'EDM' and self.csv_data_type != 'points':
            router = {'datums': self.cfg_datums, 'units': self.cfg_units, 'prisms': self.cfg_prisms}
            return router[self.csv_data_type].write_csvs(filename, self.data.db.table(self.csv_data_type))
        else:
            table = self.data.db.table(self.data.table)
            return self.cfg.write_csvs(filename, table)

    def show_save_geojson(self):
        if self.cfg.filename and self.data.filename:
            geojson_compatible = 0
            for fieldname in self.cfg.fields():
                if fieldname in ['X', 'Y', 'Z']:
                    geojson_compatible += 1
                elif fieldname in ['LATITUDE', 'LONGITUDE', 'ELEVATION']:
                    geojson_compatible += 1
                else:
                    field = self.cfg.get(fieldname)
                    if field.inputtype in ['GPS']:
                        geojson_compatible = 2
                if geojson_compatible > 1:
                    break
            if geojson_compatible:
                filename = ntpath.split(self.cfg.filename)[1].split(".")[0]
                filename = filename + '_' + self.data.table + '.geojson'

                content = e5_SaveDialog(filename=filename,
                                        start_path=self.cfg.path,
                                        save=self.save_geojson,
                                        cancel=self.dismiss_popup,
                                        colors=self.colors)
                self.popup = Popup(title="Export geoJSON file",
                                    content=content,
                                    size_hint=(0.9, 0.9))
            else:
                self.popup = e5_MessageBox('E5',
                                            '\nA geoJSON file requires a GPS type field or fields named XY(Z) or Latitude, '
                                            'Longitude and optionally Elevation.',
                                            call_back=self.dismiss_popup,
                                            colors=self.colors)
        else:
            self.popup = e5_MessageBox('E5', '\nOpen a CFG before exporting to geoJSON.',
                                        call_back=self.dismiss_popup,
                                        colors=self.colors)
        self.popup.open()
        self.popup_open = True

    def save_geojson(self, path):
        filename = os.path.join(self.popup.content.filesaver.path, self.popup.content.filename)

        self.popup.dismiss()
        self.popup = Popup(title="Export geoJSON file",
                            content=DataGridLabelAndProgressBar(col='Progress...', popup=True,
                                                                  colors=self.colors, orientation='vertical'),
                                                                  size_hint=(.6, .15))
        self.popup.open()
        self.popup_open = True

        self.popup.status = "Working..."
        self.popup.filename = filename
        self.upload_thread = Thread(target=self.cfg.write_geojson, args=(filename, self.data.db.table(self.data.table), self.popup))
        self.upload_thread.start()

        self.event = Clock.schedule_interval(self.check_file_conversion, 0.5)

    def check_file_conversion(self, dt):
        if self.popup.status != 'Working...':
            response = self.popup.status
            if not response:
                response = f'\n The table {self.data.table} was successfully written as geoJSON to the file {self.popup.filename}.'
            self.popup.dismiss()
            self.popup = e5_MessageBox('geoJSON Export', response, call_back=self.close_popup, colors=self.colors)
            self.popup.open()
            self.popup_open = True
            return False


class e5_gridlayout(GridLayout):
    id = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(e5_gridlayout, self).__init__(**kwargs)


class e5_SettingsScreen(Screen):

    buttons = []
    labels = []

    def __init__(self, cfg=None, ini=None, colors=None, **kwargs):
        super(e5_SettingsScreen, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()
        self.ini = ini
        self.cfg = cfg

    def on_enter(self):
        self.build_screen()

    def build_screen(self):
        self.clear_widgets()
        layout = GridLayout(cols=1,
                            # size_hint_x = width_calculator(.9, 600),
                            size_hint_y=1,
                            spacing=5,
                            padding=5,
                            pos_hint={'center_x': .5, 'center_y': .5})
        layout.bind(minimum_height=layout.setter('height'))

        darkmode = GridLayout(cols=2, size_hint_y=.1, spacing=5, padding=5)
        darkmode_label = e5_label('Dark Mode', colors=self.colors)
        self.labels.append(darkmode_label)
        darkmode.add_widget(darkmode_label)
        darkmode_switch = Switch(active=self.colors.darkmode)
        darkmode_switch.bind(active=self.darkmode)
        darkmode.add_widget(darkmode_switch)
        layout.add_widget(darkmode)

        colorscheme = GridLayout(cols=2, size_hint_y=.6, spacing=5, padding=5)
        colorscheme_label = e5_label('Color Scheme', colors=self.colors)
        self.labels.append(colorscheme_label)
        colorscheme.add_widget(colorscheme_label)
        colorscheme.add_widget(e5_scrollview_menu(self.colors.color_names(),
                                                  menu_selected='',
                                                  colors=self.colors,
                                                  call_back=[self.color_scheme_selected]))
        temp = ColorScheme()
        for widget in colorscheme.walk():
            if hasattr(widget, 'id'):
                if widget.id in self.colors.color_names():
                    temp.set_to(widget.text)
                    widget.background_color = temp.button_background
                    widget.height = 40
                    self.buttons.append(widget)
        layout.add_widget(colorscheme)

        backups = GridLayout(cols=2, size_hint_y=.2, spacing=5, padding=5)
        self.backup_label = e5_label(f'Auto-backup after\n{self.ini.backup_interval} records.',
                                        colors=self.colors)
        self.labels.append(self.backup_label)
        backups.add_widget(self.backup_label)
        slide = Slider(min=0, max=200, step=5,
                        value=self.ini.backup_interval,
                        orientation='horizontal',
                        value_track=True,
                        value_track_color=self.colors.button_background)
        backups.add_widget(slide)
        slide.bind(value=self.update_backup_interval)

        incremental_backup_label = e5_label('Use incremental\nbackups?', colors=self.colors)
        self.labels.append(incremental_backup_label)
        backups.add_widget(incremental_backup_label)
        backups_switch = Switch(active=self.ini.incremental_backups)
        backups_switch.bind(active=self.incremental_backups)
        backups.add_widget(backups_switch)
        layout.add_widget(backups)

        text_font_size = GridLayout(cols=2, size_hint_y=.1, spacing=5, padding=5)
        if self.colors.text_font_size:
            text_font_size_value = int(self.colors.text_font_size.replace("sp", '') if 'sp' in str(self.colors.text_font_size) else self.colors.text_font_size)
        else:
            text_font_size_value = 12
        self.text_font_size_label = e5_label('Text font\nsize is %s' % text_font_size_value, id='label_font_size', colors=self.colors)
        self.labels.append(self.text_font_size_label)
        text_font_size.add_widget(self.text_font_size_label)
        text_font_slide = Slider(min=8, max=20, step=1, value=text_font_size_value,
                                    orientation='horizontal',
                                    value_track=True, value_track_color=self.colors.button_background)
        text_font_size.add_widget(text_font_slide)
        text_font_slide.bind(value=self.update_text_font_size)
        layout.add_widget(text_font_size)

        button_font_size = GridLayout(cols=2, size_hint_y=.1, spacing=5, padding=5)
        button_font_size_value = int(self.colors.button_font_size.replace("sp", '')) if self.colors.button_font_size else 12
        self.button_font_size_label = e5_label('Button size is %s' % button_font_size_value,
                                                id='label_font_size',
                                                colors=self.colors)
        self.labels.append(self.button_font_size_label)
        button_font_size.add_widget(self.button_font_size_label)
        button_font_slide = Slider(min=8, max=30, step=1, value=button_font_size_value,
                                    orientation='horizontal',
                                    value_track=True, value_track_color=self.colors.button_background)
        button_font_size.add_widget(button_font_slide)
        button_font_slide.bind(value=self.update_button_font_size)
        layout.add_widget(button_font_size)

        settings_layout = GridLayout(cols=1,
                                        size_hint_max_x=400 if not platform_name() == 'Android' else None,
                                        size_hint_y=1,
                                        spacing=5, padding=5,
                                        pos_hint={'center_x': .5, 'center_y': .5})
        scrollview = ScrollView(size_hint=(1, 1),
                                 bar_width=SCROLLBAR_WIDTH)
        scrollview.add_widget(layout)
        settings_layout.add_widget(scrollview)

        self.back_button = e5_button('Back', selected=True, call_back=self.go_back, colors=self.colors, height=self.calc_button_height())
        self.buttons.append(self.back_button)
        settings_layout.add_widget(self.back_button)
        self.add_widget(settings_layout)

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height

    def update_text_font_size(self, intance, value):
        self.text_font_size_label.text = 'Text font size is %s' % int(value)
        self.colors.text_font_size = '%ssp' % value
        self.refresh_screen()

    def update_button_font_size(self, intance, value):
        self.button_font_size_label.text = 'Button size is %s' % int(value)
        self.colors.button_font_size = '%ssp' % value
        self.refresh_screen()

    def update_backup_interval(self, instance, value):
        self.ini.backup_interval = int(value)
        self.backup_label.text = 'Auto-backup after\nevery %s\nrecords entered.' % self.ini.backup_interval

    def incremental_backups(self, instance, value):
        self.ini.incremental_backups = value

    def darkmode(self, instance, value):
        self.colors.darkmode = value
        self.colors.set_colormode()
        self.build_screen()

    def color_scheme_selected(self, instance):
        self.colors.set_to(instance.text)
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color

    def refresh_screen(self):
        for widget in self.buttons:
            widget.font_size = self.colors.button_font_size
            widget.height = self.calc_button_height()
        for widget in self.labels:
            widget.font_size = self.colors.text_font_size

    def go_back(self, instance):
        self.popup = e5_MessageBox('E5', '\nNote that some changes to colors and size will not take effect until the program is restarted.',
                                    call_back=self.dismiss_popup,
                                    colors=self.colors)
        self.popup.open()
        self.popup_open = True

    def dismiss_popup(self, *args):
        self.popup.dismiss()
        self.ini.update(self.colors, self.cfg)
        self.parent.current = 'MainScreen'


class e5_InfoScreen(Screen):
    content = ObjectProperty(None)
    back_button = ObjectProperty(None)

    def __init__(self, colors=None, **kwargs):
        super(e5_InfoScreen, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()
        layout = GridLayout(cols=1, size_hint_y=1, spacing=5, padding=5)
        layout.add_widget(e5_scrollview_label(text='', widget_id='content', colors=self.colors))
        layout.add_widget(e5_side_by_side_buttons(['Back', 'Copy'], height=self.calc_button_height(),
                                                    id=['back_button', 'copy_button'],
                                                    selected=[False, False],
                                                    call_back=[self.go_back, self.copy],
                                                    colors=self.colors))
        self.add_widget(layout)
        for widget in self.walk():
            if hasattr(widget, 'id'):
                if widget.id == 'content_label':
                    self.content = widget
                if widget.id == 'back_button':
                    self.back_button = widget

    def go_back(self, *args):
        self.parent.current = 'MainScreen'

    def copy(self, instance):
        Clipboard.copy(self.content.text)

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height


class e5_JSONScreen(e5_InfoScreen):

    def __init__(self, data=None, **kwargs):
        super(e5_JSONScreen, self).__init__(**kwargs)
        self.data = data

    def on_pre_enter(self):
        self.content.text = 'The last 150 lines:\n\n'
        try:
            with open(self.data.filename, 'r') as f:
                content = f.readlines()
            # self.content.text += ''.join(list(reversed(content))[0:150])
            self.content.text += ''.join(list(content)[-150:])
        except TypeError:
            self.content.text = "\nA database file has not yet been opened."
        except OSError:
            self.content.text = "\nAn error occurred when reading the data file '%s'." % (self.data.filename)
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color


class e5_LogScreen(e5_InfoScreen):

    def __init__(self, logger=None, **kwargs):
        super(e5_LogScreen, self).__init__(**kwargs)
        self.logger = logger

    def on_pre_enter(self):
        self.content.text = 'The last 150 lines:\n\n'
        try:
            with open(self.logger.handlers[0].baseFilename, 'r') as f:
                content = f.readlines()
            self.content.text += ''.join(list(reversed(content))[0:150])
        except AttributeError:
            self.content.text = '\nThe logger has not been initialized.'
        except OSError:
            self.content.text = "\nAn error occurred when reading the log file '%s'." % (self.logger.handlers[0].baseFilename)
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color


class e5_INIScreen(e5_InfoScreen):

    def __init__(self, ini=None, **kwargs):
        super(e5_INIScreen, self).__init__(**kwargs)
        self.ini = ini

    def on_pre_enter(self):
        with open(self.ini.filename, 'r') as f:
            self.content.text = f.read()
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color


class e5_CFGScreen(e5_InfoScreen):

    def __init__(self, cfg=None, **kwargs):
        super(e5_CFGScreen, self).__init__(**kwargs)
        self.cfg = cfg

    def on_pre_enter(self):
        if self.cfg.filename:
            try:
                with open(self.cfg.filename, 'r') as f:
                    self.content.text = f.read()
            except OSError:
                self.content.text = "There was an error reading from the CFG file '%s'" % self.cfg.filename
        else:
            self.content.text = '\nOpen a CFG file before trying to view it.'
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color


class e5_LoadDialog(FloatLayout):
    start_path = ObjectProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    button_color = ObjectProperty(None)
    button_background = ObjectProperty(None)
    filters = ObjectProperty(['*.cfg', '*.CFG'])
    font_size = ObjectProperty(None)
    button_height = ObjectProperty(None)


class e5_SaveDialog(BoxLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    start_path = ObjectProperty(None)
    filename = ObjectProperty(None)
    path = ObjectProperty(None)

    def __init__(self, colors=None, **kwargs):
        super(e5_SaveDialog, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()

        content = BoxLayout(orientation='vertical', padding=5, spacing=5)
        self.pathlabel = e5_textinput(text=self.start_path, background_color=(0, 0, 0, 0), foreground_color=(1, 1, 1, .8), size_hint=(1, None))
        self.pathlabel.bind(minimum_height=self.pathlabel.setter('height'))
        content.add_widget(self.pathlabel)
        self.filesaver = FileChooserListView(path=self.start_path)
        self.filesaver.bind(selection=self.path_selected)
        self.filesaver.bind(path=self.path_changed)
        content.add_widget(self.filesaver)

        self.txt = TextInput(text=self.filename, multiline=False, size_hint=(1, None))
        #                        id = 'filename')
        self.txt.bind(text=self.update_filename)
        self.txt.bind(minimum_height=self.txt.setter('height'))
        content.add_widget(self.txt)

        button_height = self.calc_button_height()
        content.add_widget(e5_side_by_side_buttons(text=['Cancel', 'Save'],
                                                    id=['cancel', 'save'],
                                                    call_back=[self.cancel, self.does_file_exist],
                                                    selected=[True, True],
                                                    colors=self.colors,
                                                    button_height=button_height))

        self.add_widget(content)
        self.path = self.start_path

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height

    def update_filename(self, instance, value):
        self.filename = value

    def path_changed(self, instance, value):
        self.path = instance.path
        self.pathlabel.text = instance.path

    def path_selected(self, instance, value):
        self.path = instance.path
        self.txt.text = ntpath.split(value[0])[1] if value else ''

    def does_file_exist(self, instance):
        filename = os.path.join(self.path, self.filename)
        if os.path.isfile(filename):
            self.popup = e5_MessageBox('Overwrite existing file?', '\n You are about to overwrite an existing file - %s.\n\n Continue?' % filename,
                                        response_type="YESNO",
                                        call_back=[self.overwrite_file, self.close_popup],
                                        colors=self.colors)
            self.popup.open()
        else:
            self.save(self)

    def overwrite_file(self, instance):
        self.popup.dismiss()
        self.save(instance)

    def close_popup(self, instance):
        self.popup.dismiss()


class inputBubbleButtons(BubbleButton):
    def __init__(self, **kwargs):
        super(inputBubbleButtons, self).__init__(**kwargs)
        pass


class id_bubble(Bubble):
    def __init__(self, **kwargs):
        super(id_bubble, self).__init__(**kwargs)
        self.add_widget(self.id_button())

    def hash(self, hashlen=5):
        hash = ""
        for a in range(0, hashlen):
            hash += random.choice(string.ascii_uppercase)
        return hash

    def id_button(self):
        id = self.hash()
        btn = inputBubbleButtons(text=str(id))
        # btn.bind(on_press=partial(self.add_text, str(x)))
        return btn


class e5_RecordEditScreen(Screen):

    can_update_data_table = False
    first_field_widget = ObjectProperty(None)

    def __init__(self, data=None, doc_id=None, e5_cfg=None, colors=None, one_record_only=False, **kwargs):
        super(e5_RecordEditScreen, self).__init__(**kwargs)

        self.colors = colors if colors is not None else ColorScheme()
        self.e5_cfg = e5_cfg
        self.data = data
        self.doc_id = doc_id
        self.one_record_only = one_record_only
        self.can_update_data_table = False
        self.layout = GridLayout(cols=1,
                                 size_hint_y=.9 if platform_name() != 'Android' else 1,
                                 size_hint_x=width_calculator(.9, 600) if platform_name() != 'Android' else 1,
                                 spacing=5,
                                 padding=5,
                                 pos_hint={'center_x': .5, 'center_y': .5})
        if self.one_record_only:
            self.record_counter_label = None
        else:
            self.record_counter_label = e5_label('Record counter', size_hint=(1, .08), halign='center')
            self.layout.add_widget(self.record_counter_label)
        self.data_fields = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.make_empty_frame()
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.data_fields)
        self.layout.add_widget(scroll)
        button_height = self.calc_button_height()
        if not self.one_record_only:
            self.layout.add_widget(e5_side_by_side_buttons(text=['First', 'Previous', 'Next', 'Last'],
                                                            id=['first', 'previous', 'next', 'last'],
                                                            call_back=[self.first_record, self.previous_record,
                                                                         self.next_record, self.last_record],
                                                            selected=[True, True, True, True],
                                                            colors=self.colors, height=button_height))
            back_and_filter = e5_side_by_side_buttons(text=['Back', 'Save', 'Filter'],
                                                            id=['back', 'save', 'filter'],
                                                            call_back=[self.call_back, self.save_record, self.filter],
                                                            selected=[True, True, True],
                                                            colors=self.colors, height=button_height)
            self.filter_button = back_and_filter.children[0]
            self.layout.add_widget(back_and_filter)
        else:
            self.layout.add_widget(e5_side_by_side_buttons(text=['Cancel', 'Save'],
                                                            id=['cancel', 'save'],
                                                            call_back=[self.cancel_record, self.save_record_and_exit],
                                                            selected=[True, True],
                                                            colors=self.colors, height=button_height))

        self.add_widget(self.layout)
        self.filter_field = 'Unit-ID'
        self.loading = True
        self.first_time = True

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height

    def on_pre_enter(self):
        self.loading = True
        if self.data.table is not None and self.e5_cfg is not None:
            self.reset_doc_ids()
            self.doc_id = max(self.doc_ids) if self.doc_ids else None
        else:
            self.doc_ids = []
            self.doc_id = None
        self.put_data_in_frame()

    def on_enter(self):
        if not self.first_time:
            if not self.e5_cfg.filename or not self.data.filename:
                self.popup = e5_MessageBox('E5', '\nOpen a CFG before trying to edit records.',
                                            call_back=self.back_without_save,
                                            colors=self.colors)
                self.popup.open()
                self.popup_open = True
                return
            if len(self.data.db.table(self.data.table).all()) == 0:
                self.popup = e5_MessageBox('E5', '\nThere are no data records to edit.',
                                            call_back=self.back_without_save,
                                            colors=self.colors)
                self.popup.open()
                self.popup_open = True
                return

        if self.first_field_widget:
            self.first_field_widget.focus = True
        self.loading = False
        self.changes_made = False
        self.first_time = False

    def on_leave(self):
        # This helps insure that saving on lost focus works properly
        # There is an issue this addresses with building the screens
        # at startup.
        self.loading = True

    def reset_doc_ids(self):
        self.doc_ids = sorted([r.doc_id for r in self.data.db.table(self.data.table).all()] if self.data.db is not None else [])

    def filter(self, instance):
        if instance.text == 'Clear Filter':
            instance.text = 'Filter'
            self.reset_doc_ids()
            self.last_record(None)
            # self.update_record_counter_label()
        else:
            self.popup = db_filter(default_field=self.filter_field, fields=['doc_id', 'Unit-ID'] + self.e5_cfg.fields(),
                                    colors=self.colors, call_back=self.apply_filter)
            self.popup.auto_dismiss = False
            self.popup.open()

    def get_matching_doc_ids(self, filter_field, filter_value):
        matches = []
        if filter_field == 'doc_id':
            matches = self.data.db.table(self.data.table).get(doc_id=filter_value)
        elif filter_field == 'Unit-ID':
            for record in self.data.db.table(self.data.table):
                if "UNIT" in record.keys() and "ID" in record.keys():
                    if f"{str(record['UNIT']).lower()}-{str(record['ID']).lower()}" == filter_value.lower():
                        matches.append(record.doc_id)
        else:
            for record in self.data.db.table(self.data.table):
                if filter_field in record:
                    if str(record[filter_field]).lower() == filter_value.lower():
                        matches.append(record.doc_id)
        return matches

    def apply_filter(self, instance):
        self.filter_field = self.popup.fields_dropdown.text
        filter_value = self.popup.value_input.textbox.text
        if filter_value and self.filter_field:
            self.doc_ids = self.get_matching_doc_ids(self.filter_field, filter_value)
            if self.doc_ids:
                self.first_record(None)
            else:
                self.clear_the_frame()
                self.doc_id = None
                self.update_record_counter_label()
            self.filter_button.text = 'Clear Filter'
        else:
            self.filter_button.text = 'Filter'
        self.popup.dismiss()

    def make_empty_frame(self):
        self.data_fields.bind(minimum_height=self.data_fields.setter('height'))
        self.data_fields.clear_widgets()
        fields = self.e5_cfg.fields()
        self.first_field_widget = None
        if fields:
            first_field = True
            for col in fields:
                field_type = self.e5_cfg.get_value(col, 'TYPE')
                field_length = self.e5_cfg.get_value(col, 'LENGTH')
                field_length = int(field_length) if self.is_numeric(field_length) else 0
                widget = DataGridLabelAndField(col=col, prompt=self.e5_cfg.get_value(col, 'PROMPT'),
                                                colors=self.colors,
                                                note_field=(field_type == 'NOTE'),
                                                text_length=field_length)
                self.data_fields.add_widget(widget)
                if first_field:
                    if field_type not in ['MENU', 'BOOLEAN']:
                        self.first_field_widget = widget.txt
                    first_field = False

    def leave_record_without_save(self, instance):
        self.changes_made = False
        self.close_popup(None)
        self.continue_on_with(None)

    def ask_about_saving(self):
        self.popup = e5_MessageBox('Leave without saving', '\nLeave this record without saving changes?',
                                    response_type="YESNO",
                                    call_back=[self.leave_record_without_save, self.close_popup],
                                    colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()

    def first_record(self, value):
        if self.doc_ids:
            if self.changes_made:
                self.continue_on_with = self.first_record
                self.ask_about_saving()
            else:
                self.doc_id = self.doc_ids[0]
                self.put_data_in_frame()

    def previous_record(self, value):
        if self.doc_ids:
            if self.changes_made:
                self.continue_on_with = self.previous_record
                self.ask_about_saving()
            else:
                current = self.doc_ids.index(self.doc_id)
                new = max(current - 1, 0)
                self.doc_id = self.doc_ids[new]
                self.put_data_in_frame()

    def next_record(self, value):
        if self.doc_ids:
            if self.changes_made:
                self.continue_on_with = self.next_record
                self.ask_about_saving()
            else:
                current = self.doc_ids.index(self.doc_id)
                new = min(current + 1, len(self.doc_ids) - 1)
                self.doc_id = self.doc_ids[new]
                self.put_data_in_frame()

    def last_record(self, value):
        if self.doc_ids:
            if self.changes_made:
                self.continue_on_with = self.last_record
                self.ask_about_saving()
            else:
                self.doc_id = self.doc_ids[-1]
                self.put_data_in_frame()

    def update_record_counter_label(self):
        if self.record_counter_label:
            if self.doc_id:
                current = self.doc_ids.index(self.doc_id) + 1
                self.record_counter_label.text = f'Viewing record {current} of {len(self.doc_ids)} (doc_id={self.doc_id})'
            else:
                self.record_counter_label.text = 'No matching records'

    def clear_the_frame(self):
        self.can_update_data_table = False
        if self.e5_cfg:
            fields = self.e5_cfg.fields()
            for widget in self.layout.walk():
                if hasattr(widget, 'id'):
                    if widget.id in fields:
                        widget.text = ''

    def put_data_in_frame(self):
        self.clear_the_frame()
        if self.doc_id and self.data.table and self.e5_cfg:
            data_record = self.data.db.table(self.data.table).get(doc_id=self.doc_id)
            if data_record:
                for field in self.e5_cfg.fields():
                    for widget in self.layout.walk():
                        if hasattr(widget, 'id'):
                            if widget.id == field:
                                widget.text = '%s' % data_record[field] if field in data_record.keys() else ''
                                widget.bind(text=self.flag_changes_made)
                                widget.bind(on_text_validate=self.check_for_prism_change)
                                if widget.id == "PRISM":
                                    widget.bind(focus=self.show_prisms)
                                else:
                                    widget.bind(focus=self.show_menu)
                                break
        self.can_update_data_table = True
        self.update_record_counter_label()
        self.changes_made = False

    def check_for_prism_change(self, instance):
        if instance.id == 'PRISM':
            if not self.is_numeric(instance.text) and instance.text != '':
                self.popup = e5_MessageBox('Invalid entry',
                                            '\nPrism height must be a valid number.',
                                            response_type="OK",
                                            call_back=self.close_popup,
                                            colors=self.colors)
                self.popup.open()
                return
            prism_height_new = float(instance.text) if self.is_numeric(instance.text) else 0.0
            if prism_height_new != self.prism_height_old:
                z = self.get_widget_by_id(self, 'Z')
                if z:
                    z_old = float(z.text)
                    self.z_new = z_old + self.prism_height_old - prism_height_new
                    message = f"\nUpdate the Z as well from {round(z_old, 3)} to {round(self.z_new, 3)}?"
                    self.popup = e5_MessageBox('Update', message,
                                                    response_type="YESNO",
                                                    call_back=[self.update_z, self.close_popup],
                                                    colors=self.colors)
                    self.popup.open()

    def flag_changes_made(self, instance, value):
        self.changes_made = True

    def check_numeric(self, instance, value):
        cfg_field = self.e5_cfg.get(instance.id)
        if cfg_field.inputtype in ['NUMERIC', 'INSTRUMENT']:
            if not self.is_numeric(value):
                return [f'{instance.id} is listed as a numeric field in the CFG file but the value {value} is not a valid number.']
            else:
                return []
        else:
            return []

    def update_db(self, *args):
        if self.doc_id and self.data.table and self.e5_cfg and self.can_update_data_table:
            update = {}
            for field in self.e5_cfg.fields():
                for widget in self.layout.walk():
                    if hasattr(widget, 'id'):
                        if widget.id == field:
                            if self.e5_cfg.save_as_numeric_field(field):
                                if widget.text == '':
                                    update[widget.id] = 0
                                elif '.' in widget.text:
                                    update[widget.id] = float(widget.text)
                                else:
                                    update[widget.id] = int(widget.text)
                            else:
                                update[widget.id] = widget.text
                            break
            self.data.db.table(self.data.table).update(update, doc_ids=[self.doc_id])
            self.data.new_data[self.data.table] = True
            self.changes_made = False

    def refresh_linked_fields(self, fieldname, value):
        field = self.e5_cfg.get(fieldname)
        if field.link_fields:
            linkfields = self.data.get_link_fields(fieldname, value)
            if linkfields:
                for widget in self.layout.walk():
                    if hasattr(widget, 'id'):
                        if widget.id in linkfields.keys() and widget.id != fieldname:
                            widget.text = linkfields[widget.id]
                            widget_field = self.e5_cfg.get(widget.id)
                            if widget_field.increment:
                                try:
                                    widget.text = str(int(widget.text) + 1)
                                except ValueError:
                                    pass
                            # self.update_db(widget, widget.text)

    def check_required_fields(self):
        save_errors = []
        for field_name in self.e5_cfg.fields():
            field = self.e5_cfg.get(field_name)
            if field.required:
                for widget in self.layout.walk():
                    if hasattr(widget, 'id'):
                        if widget.id == field_name:
                            if widget.text == '':
                                save_errors.append('The field %s requires a value.' % field_name)
        return save_errors

    def convert_widgets_to_record(self):
        data_record = {}
        for field_name in self.e5_cfg.fields():
            for widget in self.layout.walk():
                if hasattr(widget, 'id'):
                    if widget.id == field_name:
                        data_record[field_name] = widget.text
        return data_record

    def get_unique_key(self, data_record):
        unique_key = []
        for field in self.e5_cfg.unique_together:
            unique_key.append("%s" % data_record[field] if field in data_record else '')
        return ",".join(unique_key)

    def check_unique_together(self):
        save_errors = []
        if self.e5_cfg.unique_together and len(self.data.db.table(self.data.table)) > 1:
            # doc_ids = self.data.doc_ids()
            unique_key = self.get_unique_key(self.convert_widgets_to_record())
            hits = []
            for item in self.data.db.table(self.data.table).all():
                if self.get_unique_key(item) == unique_key:
                    hits.append(item)
                    if len(hits) > 1:
                        save_errors.append("Based on the unique together field(s) %s, this record's unique key of %s duplicates an existing record." %
                                            (",".join(self.e5_cfg.unique_together), unique_key))
                        return save_errors
            if len(hits) == 1:
                if hits[0] != self.data.db.table(self.data.table).get(doc_id=self.doc_id):
                    save_errors.append("Based on the unique together field(s) %s, this record's unique key of %s duplicates an existing record." %
                                        (",".join(self.e5_cfg.unique_together), unique_key))
                    return save_errors
        return []

    def check_numeric_fields(self):
        save_errors = []
        for field_name in self.e5_cfg.fields():
            field = self.e5_cfg.get(field_name)
            if field.inputtype in ['NUMERIC', 'INSTRUMENT']:
                for widget in self.layout.walk():
                    if hasattr(widget, 'id'):
                        if widget.id == field_name:
                            if not self.is_numeric(widget.text) and widget.text != '':
                                save_errors.append('The field %s is marked as numeric but the value entered is not a valid number.' % field_name)
        return save_errors

    def check_bad_characters(self):
        save_errors = []
        for field_name in self.e5_cfg.fields():
            for widget in self.layout.walk():
                if hasattr(widget, 'id'):
                    if widget.id == field_name:
                        if "\"" in widget.text:
                            save_errors.append(f'The field {field_name} contains characters that are not recommended in a data file.  These include \" and \\.')
        return save_errors

    def same_coordinates(self, record1, record2):
        if all([field in record1 and field in record2 for field in ['X', 'Y', 'Z']]):
            return record1['X'] == record2['X'] and record1['Y'] == record2['Y'] and record1['Z'] == record2['Z']
        else:
            return False

    def check_for_duplicate_xyz(self):
        if self.data.db is not None:
            if len(self.data.db.table(self.data.table)) > 1:
                doc_ids = self.data.get_doc_ids(self.data.table)
                last_record = self.data.db.table(self.data.table).get(doc_id=doc_ids[-1])
                next_to_last_record = self.data.db.table(self.data.table).get(doc_id=doc_ids[-2])
                if all(field in last_record.keys() for field in ['X', 'Y', 'Z']):
                    dup = self.same_coordinates(last_record, next_to_last_record)
                    if dup:
                        message = f"\nThe last two recorded points (doc_id={doc_ids[-1]} and doc_id={doc_ids[-2]}) have the exact same XYZ coordinates "
                        message += f"of ({last_record['X']}, {last_record['Y']}, {last_record['Z']}) "
                        message += f"and ({next_to_last_record['X']}, {next_to_last_record['Y']}, {next_to_last_record['Z']}).  "
                        message += "This can mean that the data are not coming across from the total station correctly (or at all).  "
                        message += "The point has been saved, but if this was not intended you need to examine the last points recorded "
                        message += "and take a Measure shot to verify that the shots are being correctly transmitted.\n\n"
                        message += "If you are using a Microscribe, check that the green light is on.  "
                        message += "If the red light is on, you need to re-initialize (Setup - Initialize Station) and "
                        message += "re-shoot the last two points."
                        self.popup = e5_MessageBox(title='Warning', message=message)
                        self.popup.open()

    def no_errors_before_save(self):
        save_errors = self.check_required_fields()
        save_errors += self.check_unique_together()
        save_errors += self.check_numeric_fields()
        save_errors += self.check_bad_characters()
        if hasattr(self.data.db.table(self.data.table), 'on_save') and save_errors == []:
            save_errors += self.data.db.table(self.data.table).on_save()
        if save_errors:
            self.popup = e5_MessageBox('Save errors',
                                        '\nCorrect the following errors:\n  ' + '\n  '.join(save_errors),
                                        response_type="OK",
                                        call_back=self.close_popup,
                                        colors=self.colors)
            self.popup.open()
            return False
        return True

    def save_record(self, instance):
        if self.no_errors_before_save():
            self.update_db()
            self.update_link_fields()

    def save_record_and_exit(self, instance):
        if self.no_errors_before_save():
            self.update_db()
            self.update_link_fields()
            self.check_for_duplicate_xyz()
            self.go_mainscreen()

    def close_popup(self, instance):
        self.popup.dismiss()

    def update_link_fields(self):
        if hasattr(self.e5_cfg, 'link_fields'):
            for field_name in self.e5_cfg.link_fields:
                cfg_field = self.e5_cfg.get(field_name)
                for widget in self.layout.walk():
                    if hasattr(widget, 'id'):
                        if widget.id == field_name:
                            q = Query()
                            db_rec = self.data.db.table(field_name).search(q[field_name].matches('^' + widget.text + '$', re.IGNORECASE))
                            if db_rec == []:
                                self.data.db.table(field_name).insert({field_name: widget.text})
                                db_rec = self.data.db.table(field_name).search(where(field_name) == widget.text)
                            for link_field_name in cfg_field.link_fields:
                                for widget in self.layout.walk():
                                    if hasattr(widget, 'id'):
                                        if widget.id == link_field_name:
                                            if (widget.id == 'ID' and self.is_numeric(widget.text)) or widget.id != 'ID':
                                                update = {link_field_name: widget.text}
                                                self.data.db.table(field_name).update(update, doc_ids=[db_rec[0].doc_id])

    def is_numeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def cancel_record(self, instance):
        if hasattr(self.data.db.table(self.data.table), 'on_cancel'):
            self.data.db.table(self.data.table).on_cancel()
        self.parent.current = 'MainScreen'

    def show_menu(self, instance, ValueError):
        if instance.focus and not self.loading:
            cfg_field = self.e5_cfg.get(instance.id)
            if cfg_field:
                self.popup_field_widget = instance
                if cfg_field.inputtype in ['MENU', 'BOOLEAN']:
                    text_length = int(cfg_field.length) if self.is_numeric(cfg_field.length) else 0
                    self.popup = DataGridMenuList(cfg_field.prompt if cfg_field.prompt else instance.id, cfg_field.menu,
                                                    instance.text, self.menu_selection,
                                                    colors=self.colors, text_length=text_length)
                    self.popup.auto_dismiss = False
                    self.popup.open()
                    self.popup_scrollmenu = self.get_widget_by_id(self.popup, 'menu_scroll')
                    self.popup_textbox = self.get_widget_by_id(self.popup, 'new_item')
                    self.popup_addbutton = self.get_widget_by_id(self.popup, 'add_button')
                elif cfg_field.name == 'ID':
                    pass
                    # self.bubblein = id_bubble()
                    # instance.add_widget(self.bubblein)
        elif not instance.focus and not self.loading:
            self.refresh_linked_fields(instance.id, instance.text)

    def menu_selection(self, instance):
        self.popup.dismiss()
        self.popup_field_widget.text = instance.text if not instance.id == 'add_button' else self.popup_textbox.text
        self.refresh_linked_fields(instance.id, instance.text)
        if instance.id == 'add_button' and self.popup_field_widget.text.strip() != '':
            field = self.e5_cfg.get(self.popup_field_widget.id)
            if self.popup_field_widget.text not in field.menu:
                field.menu.append(self.popup_field_widget.text)
                self.e5_cfg.update_value(field.name, 'MENU', ','.join(field.menu))
                self.e5_cfg.save()
        self.popup_field_widget = None
        self.popup_scrollmenu = None

    def find_prism_match(self, value):
        if self.is_numeric(value):
            for prism_name in self.data.names('prisms'):
                prism = self.data.get_prism(prism_name)
                if prism.height == float(value):
                    return prism_name
        return ''

    def show_prisms(self, instance, ValueError):
        if instance.focus and not self.loading:
            self.prism_height_old = float(instance.text) if self.is_numeric(instance.text) else 0.0
            prism_names = self.data.names('prisms')
            if len(prism_names) > 0:
                default_prism = self.find_prism_match(instance.text)
                self.popup_field_widget = instance
                self.popup = DataGridMenuList(title="Select or Enter a Prism Height",
                                                menu_list=prism_names,
                                                menu_selected=default_prism,
                                                call_back=self.offer_to_adjust_z,
                                                colors=self.colors)
                self.popup.open()
                self.popup_scrollmenu = self.get_widget_by_id(self.popup, 'menu_scroll')
                self.popup_textbox = self.get_widget_by_id(self.popup, 'new_item')
                self.popup_addbutton = self.get_widget_by_id(self.popup, 'add_button')

    def offer_to_adjust_z(self, instance):
        self.popup.dismiss()
        if instance.id == 'add_button':
            if self.is_numeric(self.popup_textbox.text):
                self.popup_field_widget.text = self.popup_textbox.text
            else:
                return
        else:
            prism = self.data.get_prism(instance.text)
            self.popup_field_widget.text = str(prism.height)
        prism_height_new = float(self.popup_field_widget.text)
        z = self.get_widget_by_id(self, 'Z')
        if z:
            z_old = float(z.text)
            self.z_new = z_old + self.prism_height_old - prism_height_new
            message = f"\nUpdate the Z as well from {round(z_old, 3)} to {round(self.z_new, 3)}?"
            self.popup = e5_MessageBox('Update', message, response_type="YESNO", call_back=[self.update_z, self.close_popup], colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()

    def update_z(self, instance):
        z = self.get_widget_by_id(self, 'Z')
        prism = self.get_widget_by_id(self, 'PRISM')
        if z and prism:
            z.text = str(round(self.z_new, 3))
        self.popup.dismiss()

    def get_widget_by_id(self, start=None, id=''):
        if not start:
            start = self
        for widget in start.walk():
            if hasattr(widget, 'id'):
                if widget.id == id:
                    return widget
        return None

    def call_back(self, value):
        if self.changes_made:
            self.popup = e5_MessageBox('Leave without saving', '\nLeave this record without saving changes?',
                                        response_type="YESNO",
                                        call_back=[self.back_without_save, self.close_popup],
                                        colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
        else:
            self.go_mainscreen()

    def back_without_save(self, instance):
        self.close_popup(instance)
        self.go_mainscreen()

    def go_mainscreen(self, *args):
        self.parent.current = 'MainScreen'


class e5_DatagridScreen(Screen):

    datagrid = ObjectProperty(None)

    def __init__(self, main_data=None, main_tablename='_default', main_cfg=None, colors=None, addnew=False, **kwargs):
        super(e5_DatagridScreen, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()

        if platform_name() == 'Android':
            self.colors.datagrid_font_size = "11sp"

        self.e5_data = main_data
        self.e5_cfg = main_cfg
        self.tablename = main_tablename

        self.datagrid = DataGridWidget(data=main_data.db.table(main_tablename) if self.e5_data.db is not None and main_tablename else None,
                                        cfg=self.e5_cfg,
                                        colors=self.colors,
                                        addnew=addnew)
        self.add_widget(self.datagrid)
        if main_data.db is not None:
            if main_data.db.tables:
                self.datagrid.data = main_data.db.table(main_tablename)
                self.datagrid.fields = main_cfg

    def on_pre_enter(self):
        if self.e5_data is not None:
            if self.tablename in self.e5_data.new_data:
                if self.e5_data.new_data[self.tablename]:
                    self.datagrid.data = self.e5_data.db.table(self.tablename)
                    self.datagrid.fields = self.e5_cfg
                    self.datagrid.reload_data()
                    self.e5_data.new_data[self.tablename] = False

    def on_enter(self):
        if not self.e5_cfg.filename or not self.e5_data.filename:
            self.popup = e5_MessageBox('E5', '\nOpen a CFG before trying to edit records.',
                                        call_back=self.go_back,
                                        colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True
            return

        Window.bind(on_key_down=self._on_keyboard_down)
        if self.datagrid:
            self.datagrid.switch_to(self.datagrid.tab_list[len(self.datagrid.tab_list) - 1])

    def go_back(self, *args):
        if self.popup:
            self.popup.dismiss()
        if self.parent:
            self.parent.current = 'MainScreen'

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        # print(ascii_code)
        # text_str = args[3]
        if ascii_code in [273, 274, 275, 276, 278, 279]:
            if self.datagrid.popup_scrollmenu:
                self.datagrid.popup_scrollmenu.move_scroll_menu_item(ascii_code)
            return False
        elif ascii_code == 13 and (self.datagrid.popup_scrollmenu or self.datagrid.popup_textbox):
            if self.datagrid.popup_textbox.focus:
                self.datagrid.popup_addbutton.trigger_action(0)
            elif self.datagrid.popup_scrollmenu:
                self.datagrid.popup_scrollmenu.menu_selected_widget.trigger_action(0)
        elif ascii_code == 13:
            return False
        elif ascii_code == 8:
            return False
        elif ascii_code == 27 and (self.datagrid.popup_scrollmenu or self.datagrid.popup_textbox):
            self.datagrid.popup_scrollmenu = None
            self.datagrid.popup_textbox = None
            self.datagrid.popup.dismiss()
        elif ascii_code in [97, 120, 118, 275, 276, 304, 122, 114, 127]:
            return False
        # TODO On key down, see if there is a current record,
        # get the next record in the db,
        # and then try to fire the highlight record stuff
        return True

    def on_leave(self):
        Window.unbind(on_key_down=self._on_keyboard_down)


class e5_MessageBox(Popup):
    def __init__(self, title, message,
                    response_type='OK',
                    response_text=None,
                    call_back=None,
                    colors=None, **kwargs):
        super(e5_MessageBox, self).__init__(**kwargs)
        self.widget_with_focus = None
        self.colors = colors
        self.title = title
        self.response_type = response_type
        self.response_text = response_text
        self.call_back = call_back if call_back else self.dismiss
        self.content = self.build_contents(message)
        self.size_hint = (.8, .8)
        self.size = (400, 400)
        self.auto_dismiss = False

    def build_contents(self, message):
        contents = GridLayout(cols=1, spacing=5)
        self.txt = e5_scrollview_label(message, popup=True, colors=self.colors)
        contents.add_widget(self.txt)
        button_height = self.calc_button_height()
        if self.response_type == 'OK':
            self.widget_with_focus = e5_button('OK',
                                                call_back=self.call_back,
                                                selected=True,
                                                button_height=button_height,
                                                colors=self.colors)
            self.widget_with_focus.bind(on_key_up=self.keystroke)
            contents.add_widget(self.widget_with_focus)
        elif self.response_type == 'CANCEL':
            contents.add_widget(e5_button('CANCEL',
                                                call_back=self.call_back,
                                                selected=True,
                                                button_height=button_height,
                                                colors=self.colors))
        elif self.response_type == 'YESNO':
            contents.add_widget(e5_side_by_side_buttons(text=['Yes', 'No'],
                                                                call_back=self.call_back,
                                                                selected=[False, False],
                                                                button_height=button_height,
                                                                colors=self.colors))
        elif self.response_type == 'YESNOCANCEL':
            contents.add_widget(e5_side_by_side_buttons(text=['Yes', 'No', 'Cancel'],
                                                                call_back=self.call_back,
                                                                selected=[True, True, True],
                                                                button_height=button_height,
                                                                colors=self.colors))
        else:
            contents.add_widget(e5_side_by_side_buttons(text=self.response_text,
                                                                call_back=self.call_back,
                                                                selected=[True, True],
                                                                button_height=button_height,
                                                                colors=self.colors))
        return contents

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height

    def refresh_text(self, text):
        self.content = self.build_contents(text)

    def on_open(self):
        if self.widget_with_focus:
            self.widget_with_focus.focus = True
        Window.bind(on_key_up=self.keystroke)

    def on_dismiss(self):
        Window.unbind(on_key_up=self.keystroke)

    def keystroke(self, key, scancode, codepoint):
        if scancode == 13 and self.widget_with_focus:
            self.widget_with_focus.trigger_action()


class DataUploadScreen(Screen):

    def __init__(self, data=None, cfg=None, colors=None, url=None, username=None, password=None, **kwargs):
        super(DataUploadScreen, self).__init__(**kwargs)

        self.data = data
        self.cfg = cfg
        self.colors = colors if colors is not None else ColorScheme()
        self.height = 1
        self.layout = GridLayout(cols=1,
                                 size_hint_y=.9,
                                 size_hint_x=width_calculator(.9, 600),
                                 spacing=5,
                                 padding=5,
                                 pos_hint={'center_x': .5, 'center_y': .5})
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll_grid = GridLayout(cols=1,
                                        spacing=5,
                                        padding=5,
                                        size_hint_y=None)
        instructions = 'Here the data are uploaded to an online database repository like OSA.  '
        instructions += 'The URL of the repository and your credentials are needed.  '
        instructions += 'You also need the database and table names for the online repository.  '
        instructions += 'If you select overwrite, all data for existing matching records in the '
        instructions += 'online repository will be overwritten with the data here.  Normally you '
        instructions += 'do not want to do this, but if you are making changes here to already '
        instructions += 'uploaded data, you may want to select this option. '
        instructions += 'A local backup of your JSON datafile is made before the upload.  '
        instructions += 'Select Delete to remove the data here after the upload (this is good practice).'
        self.scroll_grid.add_widget(e5_label_wrapped(text=instructions, colors=self.colors))
        self.url = DataGridLabelAndField(col='URL', colors=self.colors)
        if url:
            self.url.txt.text = url
        self.scroll_grid.add_widget(self.url)
        self.username = DataGridLabelAndField(col='Username', colors=self.colors)
        if username:
            self.username.txt.text = username
        self.scroll_grid.add_widget(self.username)
        self.password = DataGridLabelAndField(col='Password', colors=self.colors)
        password = ''
        if password:
            self.password.txt.text = password
        self.password.txt.password = True
        self.scroll_grid.add_widget(self.password)
        self.dbname = DataGridLabelAndField(col='Database name', colors=self.colors)
        self.scroll_grid.add_widget(self.dbname)
        self.tablename = DataGridLabelAndField(col='Table name', colors=self.colors)
        self.scroll_grid.add_widget(self.tablename)
        self.overwrite = DataGridLabelAndToggle(col='Overwrite existing records?')
        self.scroll_grid.add_widget(self.overwrite)
        self.deleteafter = DataGridLabelAndToggle(col='Delete uploaded/updated?')
        self.scroll_grid.add_widget(self.deleteafter)
        self.progress = DataGridLabelAndProgressBar(col='Progress\n')
        self.scroll_grid.add_widget(self.progress)
        self.scroll_grid.add_widget(e5_side_by_side_buttons(text=['Back', 'Test', 'Upload'],
                                                            id=['back', 'test', 'upload'],
                                                            call_back=[self.back, self.test, self. upload],
                                                            selected=[False, False, False],
                                                            colors=self.colors))
        self.scroll.add_widget(self.scroll_grid)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        self.upload_thread = None
        self.test_thread = None

    def on_pre_enter(self):
        database = self.cfg.get_value(APP_NAME, 'ONLINE_DATABASE')
        if database:
            self.dbname.txt.text = database

        table = self.cfg.get_value(APP_NAME, 'ONLINE_TABLE')
        if table:
            self.tablename.txt.text = table

        username = self.cfg.get_value(APP_NAME, 'ONLINE_USERNAME')
        if username:
            self.username.txt.text = username

        url = self.cfg.get_value(APP_NAME, 'ONLINE_URL')
        if url:
            self.url.txt.text = url

    def on_enter(self):
        if not self.cfg.filename or not self.data.filename:
            self.popup = e5_MessageBox('E5', '\nOpen a CFG before trying upload records.',
                                        call_back=self.go_back,
                                        colors=self.colors)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True
            return

    def go_back(self, *args):
        self.popup.dismiss()
        self.parent.current = 'MainScreen'

    def back(self, instance):
        if self.dbname.txt.textbox.text:
            self.cfg.update_value(APP_NAME, 'ONLINE_DATABASE', self.dbname.txt.text)

        if self.tablename.txt.textbox.text:
            self.cfg.update_value(APP_NAME, 'ONLINE_TABLE', self.tablename.txt.text)

        if self.username.txt.textbox.text:
            self.cfg.update_value(APP_NAME, 'ONLINE_USERNAME', self.username.txt.text)

        if self.url.txt.textbox.text:
            self.cfg.update_value(APP_NAME, 'ONLINE_URL', self.url.txt.text)

        self.cfg.save()
        self.parent.current = 'MainScreen'

    def connected_to_internet(self):
        try:
            # This is hardwired to OSA but it could be anything on the internet
            urllib.request.urlopen('https://www.oldstoneage.com')
            return True
        except (urllib.error.HTTPError, urllib.error.URLError):
            return False

    def get_auth_token(self, route):
        try:
            if not route['username'] or not route['password']:
                return (False, 'A username and password must be provided')
            response = requests.post(route['url'] + 'get-token/', data={'username': route['username'], 'password': route['password']})
            if not response.ok:
                return (False, response.reason)
            return (True, json.loads(response.text))
        except urllib.error.HTTPError as e:
            return (False, e.code)
        except urllib.error.URLError as e:
            return (False, e.reason)
        except Exception as inst:
            return (False, str(inst))

    def connected_to_rest(self, route):
        try:
            if not route['api']:
                return (False, 'Username and Password authentication not yet coded')
            response = requests.get(route['url'] + 'connected/', headers={'Authorization': f"Token {route['api']}"})
            if response.status_code == 401:
                return (False, response.reason)
            return (True, json.loads(response.text))
        except urllib.error.HTTPError as e:
            return (False, e.code)
        except urllib.error.URLError as e:
            return (False, e.reason)
        except Exception as inst:
            return (False, str(inst))

    def get_structure(self, route):
        response = requests.get(f"{route['url']}structure/{route['database']}/{route['table']}/",
                                headers={'Authorization': f"Token {route['api']}"})
        try:
            return json.loads(response.text)
        except ValueError:
            return ''

    def get_details(self, route, detail_keys):
        if route['type'] == 'Standard':
            response = requests.get(f"{route['url']}{route['database']}/{route['table']}{detail_keys}/",
                                        headers={'Authorization': f"Token {route['api']}"})
        else:
            response = requests.get(f"{route['url']}{route['database']}/{route['table']}/detail{detail_keys}/",
                                    headers={'Authorization': f"Token {route['api']}"})
        return json.loads(response.text)

    def replace_keyfields(self, route, record, unique_together, structure):
        new_record = record.copy()
        for field in record.keys():
            if structure[field]['type'] == 'ForeignKey' and field != 'squid':
                second_route = route.copy()
                second_route['table'] = field
                detail = '/' + record[field]
                response = self.get_details(second_route, detail)
                if 'id' in response:
                    new_record[field] = response['id']
        return new_record

    def fix_numeric_fields(self, record, structure):
        new_record = record.copy()
        for field in record.keys():
            if structure[field]['type'] in ['IntegerField', 'FloatField'] and record[field] == "":
                new_record[field] = None
        return new_record

    def remove_non_e5_cfg_fields(self, record, cfg_fields):
        delete_list = []
        cfg_fields_lower = [field.lower() for field in cfg_fields]
        for key in record.keys():
            if key.lower() not in cfg_fields_lower:
                delete_list.append(key)
        if delete_list:
            for key in delete_list:
                record.pop(key, None)
        return record

    def unique_together_as_url(self, route, record, unique_together, structure):
        details = []
        for field in unique_together:
            if structure[field]['type'] == 'ForeignKey' and field != 'squid':
                second_route = route.copy()
                second_route['table'] = field
                detail = '/' + record[field]
                response = self.get_details(second_route, detail)
                if 'id' in response:
                    details.append(str(response['id']))
                else:
                    details.append('None')
            else:
                details.append(record[field])
        # detail = [record[field] if field in record.keys() else '' for field in unique_together]
        return '/' + '/'.join([detail if detail != '' else 'None' for detail in details])

    def unique_together_as_humanreadable(self, record, unique_together):
        detail = [str(record[field]) if field in record.keys() else '' for field in unique_together]
        return '-'.join(detail)

    def record_already_exists(self, route, record, unique_together, structure):
        detail = self.unique_together_as_url(route, record, unique_together, structure)
        response = self.get_details(route, detail)
        if response == {}:
            return 'Lookup error.'
        if 'detail' in response.keys():
            if response['detail'] == 'Not found.':
                return False
        return response

    def is_numeric(self, value):
        if value is None:
            return True
        else:
            try:
                float(value)
                return True
            except (ValueError, TypeError):
                return False

    def is_integer(self, value):
        if value is None:
            return True
        else:
            try:
                int(value)
                return True
            except ValueError:
                return False

    def get_route(self):
        return {'url': self.url.txt.textbox.text, 'api': '',
                    'username': self.username.txt.textbox.text, 'password': self.password.txt.textbox.text,
                    'database': self.dbname.txt.textbox.text.lower(), 'table': self.tablename.txt.textbox.text.lower()}

    def check_connection_issues(self, route):
        if not self.connected_to_internet():
            return ('Could not establish an internet connection to www.oldstoneage.com.  Check that you are connected to the internet.', route)
        if not route['url']:
            return ('Provide a URL to the base address of the API for this database (e.g. https://www.oldstoneage.com/api/).', route)
        if not route['api'] and (not route['username'] or not route['password']):
            return ('Provide either an API key or a username and password.', route)
        connected, status = self.get_auth_token(route)
        if not connected:
            return ('Username or password is invalid.  Or URL is invalid.  The URL should look something like https://www.oldstoneage.com/api/', route)
        route['api'] = status['token']
        connected, status = self.connected_to_rest(route)
        if not connected:
            return ("Could not connect to the URL provided above with those credentials.  "
                        "This URL should look something like https://www.oldstoneage.com/api/ but modified for your database.  "
                        f"The exact error message was '{status}'.", route)
        if not self.dbname.txt.text or not self.tablename.txt.text:
            return ('Provide a database and table name.', route)
        route['type'] = status['type']
        return ('', route)

    def check_for_cfg_fields_not_online(self, structure):
        online_fields = [field.lower() for field, value in structure.items() if field not in ['pk', 'unique_together']]
        missing_fields = []
        for field in self.cfg.fields():
            if field.lower() not in online_fields:
                missing_fields.append(field)

        if missing_fields:
            return (f"The following fields are in the CFG but not in the online database: {', '.join(missing_fields)}.\n\n"
                    "Data cannot be transfered until this is fixed.")
        else:
            return ''

    def parse_error(self, record, unique_together, error):
        error_message = self.unique_together_as_humanreadable(record, unique_together) + ' - '
        for field, value in error.items():
            if field in record.keys():
                error_message += f"{record[field]} in {field} - {' '.join(value)}\n"
            else:
                error_message += f"{field} - {' '.join(value)}\n"
        return error_message

    def clean_the_record(self, record, structure):
        for field, value in record.items():
            if field in structure.keys():
                field_online_structure = structure[field]
                if field_online_structure['type'] == 'BooleanField':
                    if value.lower() in ['yes', 'true']:
                        record[field] = True
                    elif value.lower() in ['no', 'false']:
                        record[field] = False
                    elif value.lower() in ['na', 'n/a', '']:
                        record[field] = None
        return record

    def update_upload_progress(self, dt):
        if self.upload_thread is not None:
            if self.progress.label.text == 'Done\n':
                if self.error_message:
                    fails = list(dict.fromkeys(self.fails))
                    self.popup = e5_MessageBox('Data Upload',
                                                f"\n{self.additions} records were added. {len(self.overwrites)} were updated.  {len(self.fails)} records "
                                                    f"could not be added or updated.\n\nThese are the reported errors:\n{self.error_message}\nAnd these are "
                                                    f"the affected records:\n{', '.join(fails)}",
                                                call_back=self.close_popup)
                else:
                    self.popup = e5_MessageBox('Data Upload',
                                                f'\n{self.additions} records were added. {len(self.overwrites)} were updated.',
                                                call_back=self.close_popup)
                self.popup.auto_dismiss = False
                self.popup.open()
                self.event.cancel()
                self.progress.bar.value = 0

    def update_test_progress(self, dt):
        if self.test_thread is not None:
            if self.progress.label.text == 'Done\n':
                if not self.error_message:
                    if len(self.overwrites) > 0:
                        self.overwrites = list(dict.fromkeys(self.overwrites))
                        message = f"\nTest results.  A data upload would add {self.additions} records and modify {len(self.overwrites)} records."
                        message += f"\n\nThe modified records would be {', '.join(self.overwrites)}"
                        self.popup = e5_MessageBox('Data Upload Test', message, call_back=self.close_popup)
                    else:
                        message = f"\nTest results.  A data upload would add {self.additions} records and modify {len(self.overwrites)} records."
                        self.popup = e5_MessageBox('Data Upload Test', message, call_back=self.close_popup)
                else:
                    if len(self.fails) > 0:
                        self.fails = list(dict.fromkeys(self.fails))
                        message = f"\nA data upload would add {self.additions} records, modify {len(self.overwrites)} records.  "
                        message += f"However, the upload test produced errors.  Here first is a descripion of the errors:\n{self.error_message}."
                        message += f"\n\nHere is a list of the problem cases:\n{', '.join(self.fails)}"
                        self.popup = e5_MessageBox('Data Upload Test', message, call_back=self.close_popup)
                    else:
                        self.popup = e5_MessageBox('Data Upload Test',
                                                    f'\n{self.error_message}',
                                                    call_back=self.close_popup)
                self.popup.auto_dismiss = False
                self.popup.open()
                self.event.cancel()
                self.progress.bar.value = 0

    def do_upload_of_edm_data(self):
        self.overwrites = []
        self.additions = 0
        self.fails = []
        route = self.get_route()

        #  TODO this is just to remove a flakeer8 error
        structure = ''

        self.progress.label.text = 'Checking connection\n'
        self.error_message, route = self.check_connection_issues(route)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        self.progress.label.text = 'Retrieving structure\n'
        route['table'] = 'xyz'
        xyz_structure = self.get_structure(route)
        if not xyz_structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the xyz table from website.'
            self.progress.label.text = 'Done\n'
            return

        route['table'] = 'context'
        context_structure = self.get_structure(route)
        if not context_structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the context table from website.'
            self.progress.label.text = 'Done\n'
            return

        self.error_message = self.check_for_cfg_fields_not_online(xyz_structure + context_structure)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        unique_together_xyz = ['unit', 'id', 'suffix']
        # unique_together_context = ['unit', 'id']
        # unique_keys = {}
        self.error_message = ''
        n_records = len(self.data.db.table(self.data.table))
        record_counter = 0
        to_delete = []
        for record in self.data.db.table(self.data.table).all():
            record_copy = record.copy()
            doc_id = record_copy.doc_id
            record_copy = {k.lower(): v for k, v in record_copy.items()}
            record_copy = self.remove_non_e5_cfg_fields(record_copy, self.cfg.fields())
            record_copy = self.clean_the_record(record_copy, xyz_structure)
            record_copy = self.clean_the_record(record_copy, context_structure)
            record_copy = self.fix_numeric_fields(record_copy, xyz_structure)
            record_copy = self.fix_numeric_fields(record_copy, context_structure)

            record_counter += 1
            self.progress.label.text = f'Uploading {self.unique_together_as_humanreadable(record_copy, unique_together_xyz)}\n'
            self.progress.bar.value = record_counter / n_records

            online_record = self.record_already_exists(route, record_copy, self.cfg.unique_together, structure)
            if online_record == 'Lookup error':
                self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - "\
                                      "Unable to test whether this record already exists."
                self.fails.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
            elif online_record and self.overwrite.check.active:
                if route['type'] == 'Standard':
                    url = f"{route['url']}{route['database']}/{route['table']}/{online_record['squid']}/"
                else:
                    url = f"{route['url']}{route['database']}/{route['table']}/update/{online_record['id']}/"
                record_copy['id'] = online_record['id']
                record_copy = self.replace_keyfields(route, record_copy, self.cfg.unique_together, structure)
                record_copy = self.fix_numeric_fields(record_copy, structure)
                record_copy = self.remove_non_e5_cfg_fields(record_copy, self.cfg.fields())
                response = requests.patch(url, data=record_copy, headers={'Authorization': f"Token {route['api']}"})
                if response.status_code == 400:
                    self.error_message += self.parse_error(record_copy, self.cfg.unique_together, json.loads(response.text))
                    self.fails.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
                elif response.status_code == 500:
                    self.error_message += f'{self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - {response.reason}'
                    self.fails.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
                elif response.reason == 'OK':
                    self.overwrites.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
                    if self.deleteafter.check.active:
                        to_delete.append(doc_id)
                else:
                    self.error_message += f'{self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - \
                                            Unexpected response - {response.reason}'
            elif not online_record:
                record_copy = self.replace_keyfields(route, record_copy, self.cfg.unique_together, structure)
                record_copy = self.fix_numeric_fields(record_copy, structure)
                record_copy = self.remove_non_e5_cfg_fields(record_copy, self.cfg.fields())
                if route['type'] == 'Standard':
                    url = f"{route['url']}{route['database']}/{route['table']}/"
                else:
                    url = f"{route['url']}{route['database']}/{route['table']}/create/"
                response = requests.post(url, data=record_copy, headers={'Authorization': f"Token {route['api']}"})
                if response.status_code == 400:
                    self.error_message += self.parse_error(record_copy, self.cfg.unique_together, json.loads(response.text))
                    self.fails.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
                elif response.status_code == 500:
                    self.error_message += f'{self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - {response.reason}'
                    self.fails.append(self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together))
                elif response.reason == 'Created' or response.reason == 'OK':
                    self.additions += 1
                    if self.deleteafter.check.active:
                        to_delete.append(doc_id)
                else:
                    self.error_message += f'{self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - '
                    self.error_message += 'Unexpected response - {response.reason}\n'
            else:
                self.error_message += f'{self.unique_together_as_humanreadable(record_copy, self.cfg.unique_together)} - '
                self.error_message += 'Record already exists and overwrite set to false.\n'

        if self.deleteafter.check.active:
            self.progress.label.text = 'Deleting uploaded and updated records\n\n'
            self.data.db.table(self.data.table).remove(doc_ids=to_delete)
        self.progress.label.text = 'Done\n'
        return

    def do_upload(self):
        self.overwrites = []
        self.additions = 0
        self.fails = []
        route = self.get_route()
        self.progress.bar.value = 0

        self.progress.label.text = 'Checking connection\n'
        self.error_message, route = self.check_connection_issues(route)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        self.progress.label.text = 'Retrieving structure\n'
        structure = self.get_structure(route)
        if not structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the data table from website.  '
            self.error_message += 'Make sure the name of the database and the name of the table are correct.'
            self.progress.label.text = 'Done\n'
            return

        self.error_message = self.check_for_cfg_fields_not_online(structure)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        unique_together = structure['unique_together'][0]
        self.error_message = ''
        n_records = len(self.data.db.table(self.data.table))
        record_counter = 0
        to_delete = []
        for record in self.data.db.table(self.data.table).all():
            doc_id = record.doc_id
            record = {k.lower(): v for k, v in record.items()}
            record = self.clean_the_record(record, structure)

            record_counter += 1
            self.progress.label.text = f'Uploading {self.unique_together_as_humanreadable(record, unique_together)}\n'
            self.progress.bar.value = record_counter / n_records

            online_record = self.record_already_exists(route, record, unique_together, structure)
            if online_record == 'Lookup error':
                self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
                self.error_message += "Unable to test whether this record already exists."
                self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif online_record and self.overwrite.check.active:
                if route['type'] == 'Standard':
                    url = f"{route['url']}{route['database']}/{route['table']}/{online_record['squid']}/"
                else:
                    url = f"{route['url']}{route['database']}/{route['table']}/update/{online_record['id']}/"
                record['id'] = online_record['id']
                record = self.replace_keyfields(route, record, unique_together, structure)
                record = self.fix_numeric_fields(record, structure)
                record = self.remove_non_e5_cfg_fields(record, self.cfg.fields())
                response = requests.patch(url, data=record, headers={'Authorization': f"Token {route['api']}"})
                if response.status_code == 400:
                    self.error_message += self.parse_error(record, unique_together, json.loads(response.text))
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif response.status_code == 500:
                    self.error_message += f'{self.unique_together_as_humanreadable(record, unique_together)} - {response.reason}'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif response.reason == 'OK':
                    self.overwrites.append(self.unique_together_as_humanreadable(record, unique_together))
                    if self.deleteafter.check.active:
                        to_delete.append(doc_id)
                else:
                    self.error_message += f'{self.unique_together_as_humanreadable(record, unique_together)} - Unexpected response - {response.reason}'
            elif not online_record:
                record = self.replace_keyfields(route, record, unique_together, structure)
                record = self.fix_numeric_fields(record, structure)
                record = self.remove_non_e5_cfg_fields(record, self.cfg.fields())
                if route['type'] == 'Standard':
                    url = f"{route['url']}{route['database']}/{route['table']}/"
                else:
                    url = f"{route['url']}{route['database']}/{route['table']}/create/"
                response = requests.post(url, data=record, headers={'Authorization': f"Token {route['api']}"})
                if response.status_code == 400:
                    self.error_message += self.parse_error(record, unique_together, json.loads(response.text))
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif response.status_code == 500:
                    self.error_message += f'{self.unique_together_as_humanreadable(record, unique_together)} - {response.reason}'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif response.reason == 'Created' or response.reason == 'OK':
                    self.additions += 1
                    if self.deleteafter.check.active:
                        to_delete.append(doc_id)
                else:
                    self.error_message += f'{self.unique_together_as_humanreadable(record, unique_together)} - Unexpected response - {response.reason}\n'
            else:
                self.error_message += f'{self.unique_together_as_humanreadable(record, unique_together)} - Record already exists and overwrite set to false.\n'

        if self.deleteafter.check.active:
            self.progress.label.text = 'Deleting uploaded and updated records\n\n'
            self.data.db.table(self.data.table).remove(doc_ids=to_delete)
        self.progress.label.text = 'Done\n'
        return

    def duplicate_check(self, route, record, unique_together, structure):
        already_in_db = self.record_already_exists(route, record, unique_together, structure)
        if already_in_db == 'Lookup error.':
            self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
            self.error_message += "Unable to test whether this record already exists."
            self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
        elif already_in_db and self.overwrite.check.active:
            self.overwrites.append(self.unique_together_as_humanreadable(record, unique_together))
        elif already_in_db and not self.overwrite.check.active:
            self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
            self.error_message += "Already exists but overwrite is set to False."
            self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
        else:
            self.additions += 1

    def field_check(self, record, structure, unique_together):
        for field, value in record.items():
            if field not in structure:
                self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                self.error_message += 'the field {field} is in datafile but not in the online database.'
                self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                continue
            field_online_structure = structure[field]
            if field_online_structure['type'] == 'CharField':
                if len(record[field]) > field_online_structure['length']:
                    self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
                    self.error_message += f"{record[field]} in {field} exceeds the valid field length. Maximum length is {field_online_structure['length']}.  "
                    self.error_message += f"Actual length is {len(record[field])}."
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif field_online_structure['type'] == 'FloatField':
                if not self.is_numeric(record[field]):
                    self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                    self.error_message += f'the value {record[field]} for {field} must be numeric.'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif field_online_structure['type'] == 'IntegerField':
                if not self.is_integer(record[field]):
                    self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                    self.error_message += f'the value {record[field]} for {field} must be an integer.'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif field_online_structure['type'] == 'DateTimeField':
                pass
            elif field_online_structure['type'] == 'BooleanField':
                if record[field] not in [True, False, None]:
                    self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                    self.error_message += f'the value {record[field]} for {field} must be True or False.'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif field_online_structure['type'] == 'ForeignKey':
                pass    # TODO look up in related table

    def do_test_of_edm_data(self):

        self.overwrites = []
        self.additions = 0
        self.fails = []
        route = self.get_route()

        self.progress.label.text = 'Checking connection\n'
        self.error_message, route = self.check_connection_issues(route)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        self.progress.label.text = 'Retrieving structure\n'
        route['table'] = 'xyz'
        xyz_structure = self.get_structure(route)
        if not xyz_structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the xyz table from website.'
            self.progress.label.text = 'Done\n'
            return

        route['table'] = 'context'
        context_structure = self.get_structure(route)
        if not context_structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the context table from website.'
            self.progress.label.text = 'Done\n'
            return

        self.error_message = self.check_for_cfg_fields_not_online(xyz_structure + context_structure)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        unique_together_xyz = ['unit', 'id', 'suffix']
        unique_together_context = ['unit', 'id']
        unique_keys = {}
        self.error_message = ''
        n_records = len(self.data.db.table(self.data.table))
        record_counter = 0
        for record in self.data.db.table(self.data.table).all():
            record_copy = record.copy()
            record_copy = {k.lower(): v for k, v in record_copy.items()}
            record_copy = self.remove_non_e5_cfg_fields(record_copy, self.cfg.fields())
            record_copy = self.clean_the_record(record_copy, xyz_structure)
            record_copy = self.clean_the_record(record_copy, context_structure)
            record_copy = self.fix_numeric_fields(record_copy, xyz_structure)
            record_copy = self.fix_numeric_fields(record_copy, context_structure)

            record_counter += 1
            self.progress.label.text = f'Testing upload of {self.unique_together_as_humanreadable(record_copy, unique_together_xyz)}\n'
            self.progress.bar.value = record_counter / n_records

            route['table'] = 'context'
            self.duplicate_check(route, record_copy, unique_together_context, context_structure)
            route['table'] = 'xyz'
            self.duplicate_check(route, record_copy, unique_together_xyz, xyz_structure)

            if self.unique_together_as_humanreadable(record_copy, unique_together_xyz) not in unique_keys.keys():
                unique_keys[self.unique_together_as_humanreadable(record_copy, unique_together_xyz)] = 1
            else:
                unique_keys[self.unique_together_as_humanreadable(record_copy, unique_together_xyz)] += 1

            self.field_check(record_copy, xyz_structure + context_structure, unique_together_xyz)

        if len(unique_keys) != record_counter:
            self.error_message += "\n\nWARNING: The following records are duplicated in the data file.  "\
                                  "When they are transfered they will overwrite each other: "\
                                  f"{', '.join([item for item, value in unique_keys.items() if value > 1])}"

        self.progress.label.text = 'Done\n'
        return

    def do_test(self):
        self.overwrites = []
        self.additions = 0
        self.fails = []
        route = self.get_route()

        self.progress.label.text = 'Checking connection\n'
        self.error_message, route = self.check_connection_issues(route)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        self.progress.label.text = 'Retrieving structure\n'
        structure = self.get_structure(route)
        if not structure:
            self.error_message = 'Something went wrong that should not have.  Could not retreive structure of the data table from website.'
            self.progress.label.text = 'Done\n'
            return

        self.error_message = self.check_for_cfg_fields_not_online(structure)
        if self.error_message:
            self.progress.label.text = 'Done\n'
            return

        unique_together = structure['unique_together'][0]
        unique_keys = {}
        self.error_message = ''
        n_records = len(self.data.db.table(self.data.table))
        record_counter = 0
        for record in self.data.db.table(self.data.table).all():
            record = {k.lower(): v for k, v in record.items()}
            record = self.clean_the_record(record, structure)

            record_counter += 1
            self.progress.label.text = f'Uploading {self.unique_together_as_humanreadable(record, unique_together)}\n'
            self.progress.bar.value = record_counter / n_records

            already_in_db = self.record_already_exists(route, record, unique_together, structure)
            if already_in_db == 'Lookup error.':
                self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
                self.error_message += "Unable to test whether this record already exists."
                self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            elif already_in_db and self.overwrite.check.active:
                self.overwrites.append(self.unique_together_as_humanreadable(record, unique_together))
            elif already_in_db and not self.overwrite.check.active:
                self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
                self.error_message += "Already exists but overwrite is set to False."
                self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
            else:
                self.additions += 1

            if self.unique_together_as_humanreadable(record, unique_together) not in unique_keys.keys():
                unique_keys[self.unique_together_as_humanreadable(record, unique_together)] = 1
            else:
                unique_keys[self.unique_together_as_humanreadable(record, unique_together)] += 1

            record = self.remove_non_e5_cfg_fields(record, self.cfg.fields())
            record = self.fix_numeric_fields(record, structure)

            for field, value in record.items():
                if field not in structure:
                    self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                    self.error_message += f'the field {field} is in datafile but not in the online database.'
                    self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                    continue
                field_online_structure = structure[field]
                if field_online_structure['type'] == 'CharField':
                    if len(record[field]) > field_online_structure['length']:
                        self.error_message += f"\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - "
                        self.error_message += f"{record[field]} in {field} exceeds the valid field length. "
                        self.error_message += f"Maximum length is {field_online_structure['length']}.  Actual length is {len(record[field])}."
                        self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif field_online_structure['type'] == 'FloatField':
                    if not self.is_numeric(record[field]):
                        self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                        self.error_message += f'the value {record[field]} for {field} must be numeric.'
                        self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif field_online_structure['type'] == 'IntegerField':
                    if not self.is_integer(record[field]):
                        self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                        self.error_message += f'the value {record[field]} for {field} must be an integer.'
                        self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif field_online_structure['type'] == 'DateTimeField':
                    pass
                elif field_online_structure['type'] == 'BooleanField':
                    if record[field] not in [True, False, None]:
                        self.error_message += f'\n\nRecord {self.unique_together_as_humanreadable(record, unique_together)} - '
                        self.error_message += f'the value {record[field]} for {field} must be True or False.'
                        self.fails.append(self.unique_together_as_humanreadable(record, unique_together))
                elif field_online_structure['type'] == 'ForeignKey':
                    pass    # TODO look up in related table

        if len(unique_keys) != record_counter:
            self.error_message += "\n\nWARNING: The following records are duplicated in the data file.  "
            self.error_message += "When they are transfered they will overwrite each other: "
            self.error_message += f"{', '.join([item for item, value in unique_keys.items() if value > 1])}"

        self.progress.label.text = 'Done\n'
        return

    def test(self, instance):
        self.event = Clock.schedule_interval(self.update_test_progress, 0.5)
        self.test_thread = Thread(target=self.do_test)
        self.test_thread.start()

    def upload(self, instance):
        # backup the data file
        self.event = Clock.schedule_interval(self.update_upload_progress, 0.5)
        self.upload_thread = Thread(target=self.do_upload)
        self.upload_thread.start()

    def close_popup(self, instance):
        self.popup.dismiss()


# region Data Grid
# Code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

class DataGridMenuList(Popup):

    def __init__(self, title, menu_list, menu_selected='', call_back=None, colors=None, text_length=0, **kwargs):
        super(DataGridMenuList, self).__init__(**kwargs)

        self.colors = colors if colors else ColorScheme()
        button_height = self.calc_button_height()
        pop_content = GridLayout(cols=1, size_hint_y=1, spacing=5, padding=5)

        new_item = GridLayout(cols=2, spacing=5, size_hint_y=None)
        new_item_left = GridLayout(cols=1, spacing=5, size_hint_y=None)
        if menu_list:
            new_item_instructions_text = 'Enter a new menu item and press add or select from the menu below.  New menu items are saved in the CFG.'
        else:
            new_item_instructions_text = 'Enter a new menu item and press add.  New menu items are saved in the CFG.'
        new_item_instructions = e5_label(new_item_instructions_text, popup=True, text_size=(self.width * 2, None))
        new_item_left.add_widget(new_item_instructions)
        self.txt = e5_textinput(id='new_item', size_hint_y=None, text_length=text_length)
        self.txt.bind(minimum_height=self.txt.setter('height'))
        if colors:
            if colors.text_font_size:
                self.txt.font_size = colors.text_font_size
        new_item_left.add_widget(self.txt)
        new_item.add_widget(new_item_left)
        self.add_button = e5_button('Add', id='add_button', selected=True, call_back=call_back, button_height=.15, colors=colors)
        new_item.add_widget(self.add_button)
        # new_item.bind(minimum_height = new_item.setter('height'))
        pop_content.add_widget(new_item)

        ncols = max(int(Window.width / 200), 1)

        self.menu = None
        if menu_list:
            self.menu = e5_scrollview_menu(menu_list, menu_selected,
                                                    widget_id='menu',
                                                    call_back=[call_back],
                                                    ncols=ncols,
                                                    colors=colors)
            pop_content.add_widget(self.menu)
            self.menu.make_scroll_menu_item_visible()

        pop_content.add_widget(e5_button('Back', selected=True,
                                                 call_back=self.dismiss,
                                                 button_height=button_height,
                                                 colors=colors))

        self.content = pop_content

        self.title = title
        self.size_hint = (.9, .9 if menu_list else .33)
        self.auto_dismiss = True
        self.call_back = call_back

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height

    def on_open(self):
        self.txt.textbox.focus = True
        self.txt.textbox.select_all()
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        if ascii_code == 13 and self.txt.textbox.focus and self.txt.textbox.text != "":
            self.call_back(self.add_button)
        elif ascii_code == 13:
            if self.menu:
                if self.menu.scroll_menu_get_selected():
                    self.call_back(self.menu.scroll_menu_get_selected())
        elif self.menu:
            self.menu.move_scroll_menu_item(ascii_code)

    def on_dismiss(self):
        Window.unbind(on_key_down=self._on_keyboard_down)


class DataGridTextInput(e5_textinput):

    id = ObjectProperty(None)

    def __init__(self, call_back=None, **kwargs):
        super(DataGridTextInput, self).__init__(**kwargs)
        self.call_back = call_back

    def keyboard_on_key_up(self, window, keycode):
        # print(keycode)
        return super(DataGridTextInput, self).keyboard_on_key_up(window, keycode)


class DataGridTextBox(Popup):

    result = ObjectProperty(None)
    save_button = ObjectProperty(None)

    def __init__(self, title, label=None, text='', multiline=False, call_back=None,
                        button_text=['Back', 'Save'], colors=None, text_length=0, **kwargs):
        super(DataGridTextBox, self).__init__(**kwargs)
        self.size_hint_x = .6
        self.size_hint_y = None
        self.colors = colors if colors else ColorScheme()
        content = GridLayout(cols=1, spacing=5, padding=10)
        if label:
            # e5_label(text = col, id = '__label', colors = colors)
            # content.add_widget(Label(text = label, text_size = (None, 30)))
            content.add_widget(e5_label(text=label, colors=self.colors, popup=True))
        self.txt = DataGridTextInput(text=text, size_hint_y=None,
                                        text_length=text_length,
                                        colors=self.colors,
                                        # height = 30 if not multiline else 90,
                                        multiline=multiline, id='new_item')
        # if self.colors:
        #  if self.colors.text_font_size:
        #      self.txt.textbox.font_size = self.colors.text_font_size
        #  if not multiline:
        #      if self.colors.text_font_size:
        #         self.txt.height = int(self.colors.text_font_size.replace('sp', '')) * 1.8
        self.result = text
        self.txt.textbox.bind(text=self.update)
        self.txt.textbox.bind(on_text_validate=self.accept_value)
        content.add_widget(self.txt)
        button_height = self.calc_button_height()
        # button_height = 80
        buttons = e5_side_by_side_buttons(button_text,
                                            # button_height=.5,
                                            id=[title, 'add_button'],
                                            selected=[True, True],
                                            call_back=[self.dismiss, call_back],
                                            colors=self.colors)
        self.save_button = buttons.children[0]
        content.add_widget(buttons)
        self.title = title
        self.content = content
        # if not multiline:
        #     self.size_hint = (width_calculator(.8, 800), .35 if label is None else .5)
        # else:
        #     self.size_hint = (width_calculator(.8, 800), .45 if label is None else .6)
        self.content.bind(minimum_height=self.fix_height)
        self.auto_dismiss = True

        self.event = Clock.schedule_once(self.set_focus, .35)

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height

    def fix_height(self, *args):
        instance = Text(text=self.title, font_size=self.title_size)
        width, height = instance.render()
        self.height = self.content.minimum_height + height + 60

    def set_focus(self, instance):
        self.txt.textbox.focus = True
        self.txt.textbox.select_all()

    def on_open(self):
        self.txt.textbox.focus = True
        self.txt.textbox.select_all()

    def update(self, instance, value):
        self.result = value

    def accept_value(self, instance):
        self.save_button.trigger_action(0)


class DataGridHeaderCell(Button):
    def __init__(self, text, colors, **kwargs):
        super(DataGridHeaderCell, self).__init__(**kwargs)
        self.background_color = colors.button_background
        self.background_color = DARK_GREY
        self.background_normal = ''
        self.color = make_rgb(WHITE)
        self.text = text
        if colors.datagrid_font_size:
            self.font_size = colors.datagrid_font_size


class DataGridTableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, titles=None, colors=None, *args, **kwargs):
        super(DataGridTableHeader, self).__init__(*args, **kwargs)

        for title in titles:
            self.header.add_widget(DataGridHeaderCell(title, colors))


class DataGridScrollCell(Button):
    text = StringProperty(None)
    is_even = BooleanProperty(None)
    # datagrid_even = ListProperty(None)
    # datagrid_odd = ListProperty(None)
    datagrid_even = [189.0 / 255, 189.0 / 255, 189.0 / 255, 1]
    datagrid_odd = [224.0 / 255, 224.0 / 255, 224.0 / 255, 1]

    def __init__(self, **kwargs):
        super(DataGridScrollCell, self).__init__(**kwargs)
        self.background_normal = ''


class DataGridTableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)

    datagrid_doc_id = None
    datagrid_background_color = None
    # datagrid_widget_row = []

    datatable_widget = None

    popup = ObjectProperty(None)

    def __init__(self, list_dicts=[], column_names=None, tb=None, e5_cfg=None, colors=None, *args, **kwargs):
        self.nrows = len(list_dicts) if len(list_dicts) != 1 else 2
        self.ncols = len(column_names)
        self.id = 'datatable'
        self.colors = colors if colors else ColorScheme()
        self.e5_cfg = e5_cfg

        super(DataGridTableData, self).__init__(*args, **kwargs)

        self.data = []
        black = make_rgb(BLACK)
        button_height = self.calc_button_height()
        if len(list_dicts) == 1:
            # This is a hack to deal with a Kivy but where the grid does not display if there is
            # only one row.  So the solution is to insert a dummy row.
            for column in column_names:
                self.data.append({'text': '',
                                    'is_even': False,
                                    'callback': self.editcell,
                                    'key': 0,
                                    'field': column,
                                    'db': tb,
                                    'id': 'datacell',
                                    'datagrid_even': self.colors.datagrid_even,
                                    'datagrid_odd': self.colors.datagrid_odd,
                                    'height': button_height,
                                    'color': black})
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            for column in column_names:
                value = ord_dict[column] if column in ord_dict.keys() else ''
                content = {'text': value,
                            'is_even': is_even,
                            'callback': self.editcell,
                            'key': ord_dict['doc_id'],
                            'field': column,
                            'db': tb,
                            'id': 'datacell',
                            'datagrid_even': self.colors.datagrid_even,
                            'datagrid_odd': self.colors.datagrid_odd,
                            'height': button_height,
                            'color': black}
                if self.colors.datagrid_font_size:
                    content['font_size'] = self.colors.datagrid_font_size
                self.data.append(content)

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = int(100 * (font_height / base_height))
        return height

    def is_numeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def clear_highlight_row(self):
        if self.datagrid_doc_id:
            for record in self.data:
                record['background_color'] = self.colors.datagrid_even if record['is_even'] else self.colors.datagrid_odd
            self.refresh_from_data()
            self.datagrid_doc_id = ''

    def set_highlight_row(self):
        for record in self.data:
            if record['key'] == self.datagrid_doc_id:
                record['background_color'] = self.colors.optionbutton_background
        self.refresh_from_data()

    # def get_editcell_row(self, key):
    #    row_widgets = []
    #    for widget in self.walk():
    #        if hasattr(widget, 'id'):
    #            if widget.id == 'datacell':
    #                if widget.key == key:
    #                    row_widgets.append(widget)
    #    return(row_widgets)

    def get_editcell(self, key, field):
        for widget in self.walk():
            if hasattr(widget, 'id'):
                if widget.id == 'datacell':
                    if widget.field == field and widget.key == key:
                        return widget
        return None

    def editcell(self, key, field, db):
        # self.key = key
        if field == 'doc_id' and self.datagrid_doc_id == key:
            self.clear_highlight_row()
            return
        self.clear_highlight_row()
        self.datagrid_doc_id = key
        editcell_widget = self.get_editcell(key, field)
        self.datagrid_background_color = editcell_widget.background_color
        self.set_highlight_row()
        self.field = field
        self.tb = db
        cfg_field = self.e5_cfg.get(field)
        self.inputtype = cfg_field.inputtype.upper()
        text_length = int(cfg_field.length) if self.is_numeric(cfg_field.length) else 0
        if field == 'doc_id':
            return
        if self.inputtype in ['MENU', 'BOOLEAN']:
            self.popup = DataGridMenuList(field, cfg_field.menu,
                                            editcell_widget.text, self.menu_selection,
                                            self.colors, text_length=text_length)
            self.popup.auto_dismiss = False
            self.popup.open()
        elif self.inputtype in ['TEXT', 'NUMERIC', 'NOTE']:
            self.popup = DataGridTextBox(title=field, text=editcell_widget.text,
                                            multiline=self.inputtype == 'NOTE',
                                            call_back=self.menu_selection,
                                            colors=self.colors, text_length=text_length)
            self.popup.auto_dismiss = False
            self.popup.open()
        self.datatable_widget.popup_scrollmenu = self.datatable_widget.get_widget_by_id(self.popup, 'menu_scroll')
        self.datatable_widget.popup_textbox = self.datatable_widget.get_widget_by_id(self.popup, 'new_item')
        self.datatable_widget.popup_addbutton = self.datatable_widget.get_widget_by_id(self.popup, 'add_button')
        self.datatable_widget.popup = self.popup

    def menu_selection(self, instance):
        self.popup.dismiss()
        if self.field in ['HANGLE', 'VANGLE'] and APP_NAME == 'EDM':
            new_data = {self.field: self.datatable_widget.popup_textbox.text}
        elif self.inputtype in ['MENU', 'BOOLEAN']:
            new_data = {self.field: instance.text if not instance.text == 'Add' else self.datatable_widget.popup_textbox.text}
        elif self.inputtype == 'NUMERIC':
            edm_fields = ['X', 'Y', 'Z', 'PRISM', 'SLOPED', 'STATIONX', 'STATIONY', 'STATIONZ', 'DATUMX', 'DATUMY', 'DATUMZ', 'LOCALX', 'LOCALY', 'LOCALZ']
            if self.field in edm_fields and APP_NAME == 'EDM':
                try:
                    self.datatable_widget.popup_textbox.text = str(eval(self.datatable_widget.popup_textbox.text))
                except (DivisionByZero, NameError, SyntaxError):
                    pass
            try:
                if '.' in self.datatable_widget.popup_textbox.text:
                    new_data = {self.field: float(self.datatable_widget.popup_textbox.text)}
                else:
                    new_data = {self.field: int(self.datatable_widget.popup_textbox.text)}
            except ValueError:
                new_data = {self.field: self.datatable_widget.popup_textbox.text}
        else:
            new_data = {self.field: self.datatable_widget.popup_textbox.text}
        is_valid = self.e5_cfg.validate_datafield(new_data, self.tb)
        if is_valid is True:
            self.tb.update(new_data, doc_ids=[int(self.datagrid_doc_id)])
            self.update_recycle_data(self.datagrid_doc_id, self.field, new_data[self.field])
            # for widget in self.walk():
            #    if hasattr(widget, 'id'):
            #        if widget.id == 'datacell':
            #            if widget.key == self.datagrid_doc_id and widget.field == self.field:
            #                widget.text = str(new_data[self.field])
            self.datatable_widget.popup_scrollmenu = None
            self.datatable_widget.popup_textbox = None
        else:
            self.popup = e5_MessageBox('Data error', is_valid)
            self.popup.auto_dismiss = False
            self.popup.open()

    def update_recycle_data(self, doc_id, field, value):
        for record in self.data:
            if record['key'] == doc_id and record['field'] == field:
                record['text'] = str(value)
                self.refresh_from_data()
                break


class DataGridTable(BoxLayout):

    def __init__(self, list_dicts=[], column_names=None, tb=None, e5_cfg=None, colors=None, *args, **kwargs):

        super(DataGridTable, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = DataGridTableHeader(column_names, colors)
        self.table_data = DataGridTableData(list_dicts=list_dicts, column_names=column_names,
                                            tb=tb, e5_cfg=e5_cfg, colors=colors)

        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value


class DataGridGridPanel(BoxLayout):

    def populate_data(self, tb, tb_fields, colors=None):
        if tb is not None and tb_fields is not None:
            self.colors = colors if colors else ColorScheme()
            self.tb = tb
            self.sort_key = None
            self.column_names = ['doc_id'] + tb_fields.fields()
            self.tb_fields = tb_fields
            self._generate_table()

    def _generate_table(self, sort_key=None, disabled=None):
        self.clear_widgets()
        data = []
        table_fields = self.tb_fields.fields()
        for tb_row in self.tb:
            reformatted_row = {}
            reformatted_row['doc_id'] = str(tb_row.doc_id)
            for field in table_fields:
                reformatted_row[field] = str(tb_row[field]) if field in tb_row else ''
            data.append(reformatted_row)
        data = sorted(data, key=lambda k: int(k['doc_id']), reverse=True)
        self.recycleview_box = DataGridTable(list_dicts=data, column_names=self.column_names,
                                                tb=self.tb, e5_cfg=self.tb_fields, colors=self.colors)
        self.add_widget(self.recycleview_box)


class DataGridCasePanel(BoxLayout):

    changed = False
    id = 'datagridcase'

    def populate(self, data, fields, colors=None, call_back=None, revert=None):
        if data is not None and fields is not None:
            self.colors = colors if colors else ColorScheme()
            self.edit_list.bind(minimum_height=self.edit_list.setter('height'))
            self.edit_list.clear_widgets()
            for col in fields.fields():
                label_and_text = DataGridLabelAndField(col=col, prompt=fields.get(col).prompt, colors=self.colors)
                label_and_text.txt.textbox.bind(on_text_validate=self.next_field)
                self.edit_list.add_widget(label_and_text)
                label_and_text.txt.textbox.bind(text=self.changes)
            self.add_widget(e5_side_by_side_buttons(text=['Revert', 'Save'],
                                                    call_back=[revert, call_back],
                                                    colors=self.colors,
                                                    button_height=self.calc_button_height()))
        self.changed = False

    def next_field(self, instance):
        pass

    def changes(self, instance, value):
        self.changed = True

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height


class DataGridLabelAndProgressBar(BoxLayout):

    def __init__(self, col, active=False, colors=None, popup=False, **kwargs):
        super(DataGridLabelAndProgressBar, self).__init__(**kwargs)
        self.colors = colors if colors is not None else ColorScheme()
        self.size_hint = (0.9, None)
        self.bind(minimum_height=self.setter('height'))
        self.spacing = 10
        self.label = e5_label(text=col, id='__label', colors=self.colors, popup=popup, size_hint_y=None, halign='center')
        self.label.bind(texture_size=self.label.setter('size'))
        self.bar = ProgressBar(max=1)
        self.bar.height = 50
        self.add_widget(self.label)
        self.add_widget(self.bar)


class DataGridLabelAndToggle(BoxLayout):

    def __init__(self, col, active=False, colors=None, popup=False, **kwargs):
        super(DataGridLabelAndToggle, self).__init__(**kwargs)
        self.colors = colors if colors is not None else ColorScheme()
        self.size_hint = (0.9, None)
        self.bind(minimum_height=self.setter('height'))
        self.spacing = 10
        label = e5_label(text=col, id='__label', colors=self.colors, popup=popup)
        label.bind(texture_size=label.setter('size'))
        self.check = Switch(active=active, size_hint=(0.75, None))
        self.check.height = 30
        self.add_widget(label)
        self.add_widget(self.check)


class DataGridLabelAndField(GridLayout):

    popup = ObjectProperty(None)
    sorted_result = None

    def __init__(self, col, colors, prompt='', note_field=False, popup=False, text_length=0, height=None, **kwargs):
        super(DataGridLabelAndField, self).__init__(**kwargs)
        self.update_db = False
        self.widget_type = 'data'
        self.cols = 2
        # if not note_field:
        #     if colors:
        #         if colors.text_font_size:
        #             self.height = int(colors.text_font_size.replace('sp', '')) * 1.9
        self.size_hint = (0.9, None)
        self.spacing = 1
        self.label = e5_label(text=prompt if prompt else col, id='__label',
                                colors=colors,
                                popup=popup,
                                size_hint_y=None,
                                halign='right')
        # self.label.bind(text_size = self.label.setter('size'))
        # self.label.bind(texture_size = self.fix_height)
        self.txt = e5_textinput(multiline=note_field,
                                size_hint=(0.75, None),
                                id=col,
                                size_hint_y=None,
                                text_length=text_length,
                                write_tab=False,
                                colors=colors)
        # if colors:
        #     if colors.text_font_size:
        #         self.txt.font_size = colors.text_font_size
        # self.txt.height = 10
        self.add_widget(self.label)
        self.add_widget(self.txt)
        # self.label.height = 20
        # self.txt.textbox.height = self.label.height
        # self.label.height = self.txt.textbox.height
        self.height = self.txt.textbox.height
        self.label.padding = [10, self.txt.textbox.border[2] * 2]
        # self.bind(minimum_height = self.txt.textbox.setter('height'))


class DataGridDeletePanel(GridLayout):

    def populate(self, message=None, call_back=None, colors=None):
        self.colors = colors if colors else ColorScheme()
        self.clear_widgets()
        self.cols = 1
        self.spacing = 5
        if message is not None:
            self.add_widget(e5_scrollview_label(message, popup=False, colors=self.colors))
            self.add_widget(e5_button('Delete', id='delete', selected=True, call_back=call_back, colors=self.colors, button_height=self.calc_button_height()))
        else:
            self.add_widget(e5_scrollview_label('\nHighlight a record in the grid view (data tab) by clicking on its doc_id, '
                                                'and then delete that record here.',
                                                popup=False, colors=self.colors))

    def calc_button_height(self):
        instance = Text(text='Test', font_size=28)
        width, base_height = instance.render()
        instance = Text(text='Test', font_size=self.colors.button_font_size.replace('sp', ''))
        width, font_height = instance.render()
        height = .2 * (font_height / base_height)
        return height


class DataGridAddNewPanel(GridLayout):

    def populate(self, data, fields, colors=None, addnew=False, call_back=None):
        if data is not None and fields is not None:
            self.colors = colors if colors else ColorScheme()
            self.cols = 1
            if addnew:
                self.addnew_list.bind(minimum_height=self.addnew_list.setter('height'))
                self.addnew_list.clear_widgets()
                for col in fields.fields():
                    label_and_text = DataGridLabelAndField(col=col, colors=self.colors)
                    label_and_text.txt.bind(on_text_validate=self.next_field)
                    self.addnew_list.add_widget(label_and_text)
                self.button = e5_button('Add record', id='addnew', selected=False, call_back=call_back, colors=self.colors)
                self.add_widget(self.button)
                self.call_back = call_back
            else:
                self.clear_widgets()
                if APP_NAME == 'EDM':
                    self.add_widget(e5_scrollview_label('\nAdding records in this way is not enabled for the main points table but is enabled '
                                                        'for datums, units and prisms.',
                                                        popup=False, colors=self.colors))
                else:
                    self.add_widget(e5_scrollview_label('\nAdding records in this way is not enabled in E5 because it would bipass conditions '
                                                        'and error checking (but it is enabled in EDM which is why it appears in this list of tabs).',
                                                        popup=False, colors=self.colors))

    def next_field(self, instance):
        if instance.get_focus_next() == self.button:
            if self.call_back:
                self.call_back(instance)
                instance.get_focus_next().get_focus_next().focus = True
        else:
            instance.get_focus_next().focus = True


class DataGridWidget(TabbedPanel):
    data = ObjectProperty(None)
    fields = ObjectProperty(None)
    colors = ObjectProperty(None)

    popup = None
    popup_open = False
    popup_scrollmenu = None
    popup_addbutton = None
    popup_textbox = None
    popup_field_widget = None

    def __init__(self, data=None, cfg=None, colors=None, addnew=False, **kwargs):
        super(DataGridWidget, self).__init__(**kwargs)

        self.addnew = addnew

        if data is not None:
            self.data = data
        if cfg is not None:
            self.fields = cfg
            self.cfg = cfg

        self.colors = colors if colors else ColorScheme()
        self.color = self.colors.text_color
        self.background_color = self.colors.window_background
        self.background_image = ''

        if data is not None and self.fields is not None:
            self.populate_panels()

        # if not addnew:
        #    self.tab_list.remove(self.get_tab_by_name('Add New'))

        for tab in self.tab_list:
            tab.color = make_rgb(WHITE)
            tab.background_color = MIDDLE_GREY
            if self.colors.datagrid_font_size:
                tab.font_size = self.colors.datagrid_font_size

    def record_count(self):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        return datatable.nrows if datatable else 0

    def reload_data(self):
        # This next conditional is to avoid an exception in unit testing
        if hasattr(self, 'panel1'):
            self.panel1.populate_data(tb=self.data, tb_fields=self.cfg, colors=self.colors)
            if self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable'):
                self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable').datatable_widget = self
        # self.populate_panels()

    # def load_data(self, data, fields):
    #    self.data = data
    #    self.fields = fields
    #    self.populate_panels()

    def populate_panels(self):
        # This next conditional is to avoid an exception in unit testing
        if hasattr(self, 'panel1'):
            self.panel1.populate_data(tb=self.data, tb_fields=self.cfg, colors=self.colors)
            self.panel2.populate(data=self.data, fields=self.fields, colors=self.colors,
                                    call_back=self.save_record, revert=self.load_record)
            self.panel3.populate(colors=self.colors)
            self.panel4.populate(addnew=self.addnew,
                                    data=self.data,
                                    fields=self.fields,
                                    colors=self.colors,
                                    call_back=self.addnew_record)
            if self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable'):
                self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable').datatable_widget = self

    def open_panel1(self):
        self.check_changes()
        if self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable'):
            self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable').datatable_widget = self
        self.panel1.children[0].children[0].refresh_from_data()

    def open_panel2(self):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        if datatable is not None:
            if datatable.datagrid_doc_id is not None and datatable.datagrid_doc_id != '':
                data_record = self.data.get(doc_id=int(datatable.datagrid_doc_id))
                for widget in self.panel2.walk():
                    if hasattr(widget, 'id'):
                        if widget.id in self.fields.fields():
                            widget.text = str(data_record[widget.id]) if widget.id in data_record else ''
                            widget.bind(focus=self.show_menu)
            else:
                cfg_fields = self.fields.fields()
                for widget in self.panel2.walk():
                    if hasattr(widget, 'id'):
                        if widget.id in cfg_fields:
                            widget.text = ''
            self.get_widget_by_id(self.panel2, 'datagridcase').changed = False

    def open_panel3(self):
        self.check_changes()
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        if datatable is not None:
            if datatable.datagrid_doc_id:
                data_record = self.data.get(doc_id=int(datatable.datagrid_doc_id))
                if data_record:
                    serialize_record = '\nDelete this record?\n\n'
                    for field in self.fields.fields():
                        if field in data_record.keys():
                            serialize_record += field + f" : {data_record[field]}\n"
                    self.panel3.populate(message=serialize_record,
                                            call_back=self.confirm_delete_record,
                                            colors=self.colors)

    def open_panel4(self):
        self.check_changes()
        if self.fields is not None:
            cfg_fields = self.fields.fields()
            # TODO this seems like a bug - not sure why edit_panel is being cleared here
            for widget in self.ids.edit_panel.children[0].walk():
                if hasattr(widget, 'id'):
                    if widget.id in cfg_fields:
                        widget.text = ''

    def show_menu(self, instance, value):
        if instance.focus:
            cfg_field = self.fields.get(instance.id)
            if cfg_field:
                self.popup_field_widget = instance
                if cfg_field.inputtype in ['MENU', 'BOOLEAN']:
                    self.popup = DataGridMenuList(instance.id, cfg_field.menu,
                                                    instance.text, self.menu_selection, colors=self.colors)
                    self.popup.auto_dismiss = False
                    self.popup.open()
                    self.popup_scrollmenu = self.get_widget_by_id(self.popup, 'menu_scroll')
                    self.popup_textbox = self.get_widget_by_id(self.popup, 'new_item')
                    self.popup_addbutton = self.get_widget_by_id(self.popup, 'add_button')

    def menu_selection(self, instance):
        self.popup.dismiss()
        self.popup_field_widget.text = instance.text if not instance.id == 'add_button' else self.popup_textbox.text
        self.popup_field_widget = None
        self.popup_scrollmenu = None

    def check_changes(self):
        if self.get_widget_by_id(self.panel2, 'datagridcase').changed:
            self.open_popup(e5_MessageBox('Save changes?', '\nSave the changes made to this record?',
                                            response_type='YESNO',
                                            call_back=[self.save_record, self.save_record_not],
                                            colors=self.colors))

    def clear_addnew(self):
        cfg_fields = self.fields.fields()
        for widget in self.ids.addnew_panel.children[1].walk():
            if hasattr(widget, 'id'):
                if widget.id in cfg_fields:
                    if widget.text:
                        widget.text = ''

    def load_record(self, instance):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        if datatable is not None:
            if datatable.datagrid_doc_id is not None and datatable.datagrid_doc_id != '':
                data_record = self.data.get(doc_id=int(datatable.datagrid_doc_id))
                self.load_record_into_widgets(self.panel2, data_record)

    def load_record_into_widgets(self, root, record):
        for widget in root.walk():
            if hasattr(widget, 'id'):
                if widget.id in self.fields.fields():
                    if widget.id in record.keys():
                        widget.text = str(record[widget.id])
                    else:
                        widget.text = ''

    def build_record_from_widgets(self, root):
        new_record = {}
        cfg_fields = self.fields.fields()
        for widget in root.walk():
            if hasattr(widget, 'id'):
                if widget.id in cfg_fields:
                    if widget.text:
                        if self.cfg.save_as_numeric_field(widget.id):
                            if '.' in widget.text:
                                new_record[widget.id] = float(widget.text)
                            else:
                                new_record[widget.id] = int(widget.text)
                        else:
                            new_record[widget.id] = widget.text
        return new_record

    def strip_strings_from_number_fields(self, new_record):
        for field, value in new_record.items():
            f = self.cfg.get(field)
            if f.inputtype == 'NUMERIC':
                try:
                    new_record[field] = float(value)
                except ValueError:
                    pass
        return new_record

    def addnew_record(self, instance):
        new_record = self.build_record_from_widgets(self.ids.addnew_panel.children[1])
        valid_data = self.cfg.validate_datarecord(new_record, self.data)
        if valid_data is True:
            self.data.insert(self.strip_strings_from_number_fields(new_record))
            self.data.new_data = True  # TODO Needs to reference parent
            self.panel1.populate_data(tb=self.data, tb_fields=self.fields, colors=self.colors)
            self.clear_addnew()
        else:
            self.popup = e5_MessageBox("Save error", valid_data, call_back=self.close_popup)
            self.popup.auto_dismiss = False
            self.popup.open()
            self.popup_open = True

    def save_record(self, instance):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        if datatable is not None:
            new_record = self.build_record_from_widgets(self.panel2)
            valid_data = self.cfg.validate_datarecord(new_record, self.data)
            if valid_data is True:
                unique_error = self.check_unique_together(int(datatable.datagrid_doc_id), new_record)
                if unique_error == '':
                    self.data.update(new_record, doc_ids=[int(datatable.datagrid_doc_id)])
                    self.get_widget_by_id(self.panel2, 'datagridcase').changed = False
                    self.update_datagrid_record(datatable.datagrid_doc_id, new_record)
                    self.data.new_data = True  # TODO Needs to reference parent
                    self.close_popup(None)
                else:
                    self.open_popup(e5_MessageBox("Save error", unique_error, call_back=self.close_popup))
            else:
                self.open_popup(e5_MessageBox("Save error", valid_data, call_back=self.close_popup))

    def save_record_not(self, instance):
        self.get_widget_by_id(self.panel2, 'datagridcase').changed = False
        self.close_popup(None)

    def get_field_type(self, fieldname):
        f = self.cfg.get(fieldname)
        return f.inputtype

    def get_unique_key(self, data_record):
        unique_key = []
        for field in self.cfg.unique_together:
            unique_key.append("%s" % data_record[field] if field in data_record else '')
        return ",".join(unique_key)

    def check_unique_together(self, current_doc_id, new_record):
        unique_error = ''
        if self.cfg.unique_together and len(self.data) > 1:
            unique_key = self.get_unique_key(new_record)
            for record in self.data.all():
                if record.doc_id != current_doc_id:
                    if unique_key == self.get_unique_key(record):
                        unique_error = f'Based on the unique together field(s) {",".join(self.cfg.unique_together)}, '
                        unique_error += f'this record\'s unique key of {unique_key} duplicates another record.  This is not allowed.'
                        break
        return unique_error

    def update_datagrid_record(self, doc_id, new_record):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        for record in datatable.data:
            if record['key'] == doc_id and record['field'] in new_record.keys():
                record['text'] = str(new_record[record['field']])
        self.get_tab_by_name('Data').content.recycleview_box.table_data.refresh_from_data()

    def update_datagrid_field(self, doc_id, field, value):
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        for record in datatable.data:
            if record['key'] == doc_id and record['field'] == field:
                record['text'] = str(value)
                self.get_tab_by_name('Data').content.recycleview_box.table_data.refresh_from_data()
                break

    def confirm_delete_record(self, instance):
        self.popup = e5_MessageBox('Delete record', '\nAre you sure you want to delete this record?',
                                    response_type="YESNO",
                                    call_back=[self.delete_record, self.close_popup],
                                    colors=self.colors)
        self.popup.auto_dismiss = False
        self.popup.open()
        self.popup_open = True

    def delete_record(self, value):
        self.close_popup(value)
        datatable = self.get_widget_by_id(self.get_tab_by_name('Data').content, 'datatable')
        if datatable is not None:
            doc_id = int(datatable.datagrid_doc_id)
            self.data.remove(doc_ids=[doc_id])
            datatable.datagrid_doc_id = None
            # datatable.datagrid_widget_row = None
            self.reload_data()
            self.panel3.populate(colors=self.colors)
            self.switch_to(self.get_tab_by_name('Data'))

    def open_popup(self, content):
        self.popup = content
        self.popup.open()
        self.popup_open = True

    def close_popup(self, value):
        if self.popup:
            self.popup.dismiss()
        self.popup_open = False

    # repeats code above - could be put into a general functions package
    def get_widget_by_id(self, start=None, id=''):
        start_here = self if start is None else start
        for widget in start_here.walk():
            if hasattr(widget, 'id'):
                if widget.id == id:
                    return widget
        return None

    def get_tab_by_name(self, text=''):
        for tab in self.tab_list:
            if tab.text == text:
                return tab
        return None

    def close_panels(self):
        self.check_changes()
        self.parent.parent.current = 'MainScreen'

    def cancel(self):
        pass

# End code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py
# endregion
