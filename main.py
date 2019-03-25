# Errors:

# To Do
# Add GPS field
# Test species menu
# Build tests.py
# Debug and test conditionals
# Handle database and table names in the CFG and program better
# On unique fields, give a warning but let data entry continue
#   then overwrite previous record
# Implement 'sort' option on menus
# Key press on boolean moves to right menu item but adds key press too

# Need to establish a unique key for each record
# E4 conditions seem to accept OR at the end - check other options and implement
# Add a CFG option to sort menus

# Long term
#   Consider putting a dropdown menu into the grid view for sorting and maybe searching
#   Think about whether to allow editing of CFG in the program
#   Get location data from GPS
# Once I have factor figured out, consider doing factory register for validating data and other things

__version__ = '1.0.1'
__date__ = 'March, 2019'

#region Imports
from kivy.utils import platform
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
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
from datetime import datetime
import ntpath
from string import ascii_uppercase
from shutil import copyfile

import logging
import logging.handlers as handlers

# My libraries for this project
from blockdata import blockdata
from dbs import dbs
from e5_widgets import *
from constants import *
from colorscheme import *

# The database - pure Python
from tinydb import TinyDB, Query, where

from collections import OrderedDict
#endregion

#region Data Classes

class db(dbs):
    MAX_FIELDS = 300
    db = None
    filename = None
    db_name = 'data'
    datagrid_doc_id = None
    table = '_default'

    def __init__(self, filename = ''):
        if filename:
            self.filename = filename
        self.filename = filename

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        try:
            self.db = TinyDB(self.filename)
        except:
            self.db = None
            self.filename = ''

    def status(self):
        if self.filename:
            txt = '\nThe JSON data file is %s.\n\n' % self.filename
            if self.db:
                if len(self.db.tables()) > 0:
                    txt += 'There are %s tables in this data file as follows:\n' % len(self.db.tables())
                    for table_name in self.db.tables():
                        txt += "  A table named '%s' with %s records.\n" % (table_name, len(self.db.table(table_name)))
                    txt += '\nIn total there are %s records in the data file.\n' % len(self.db)
                    txt += "The current table is '%s'.\n\n" % self.table
                else:
                    txt += 'There are no tables in this data file.\n\n'
            else:
                txt += 'The data file is empty or has not been initialized.\n'
        else:
            txt = '\nA data file has not been opened.\n'
        return(txt)

    def get(self, name):
        unit, id = name.split('-')
        p = self.db.search( (where('unit')==unit) & (where('id')==id) )
        if p:
            return(p)
        else:
            return(None)

    # Can likely delete this or use a DB key or the first unique field
    def names(self):
        name_list = []
        for row in self.db:
            name_list.append(row['unit'] + '-' + row['id'])
        return(name_list)

    def fields(self, tablename = ''):
        if not tablename:
            table = self.db.table(tablename)
        else:
            table = self.db.table('_default')
        fieldnames = []
        for row in table:
            for fieldname in row.keys():
                if not fieldname in fieldnames:
                    fieldnames.append(fieldname) 
        return(fieldnames)

    def delete_all(self):
        self.db.purge()

class ini(blockdata):
    
    def __init__(self, filename = ''):
        if filename=='':
            filename = 'E5.ini'
        self.filename = filename
        self.incremental_backups = False
        self.backup_interval = 0
        self.first_time = True

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        self.blocks = self.read_blocks()
        self.first_time = (self.blocks == [])
        self.is_valid()
        self.incremental_backups = self.get_value('E5','IncrementalBackups').upper() == 'TRUE'
        self.backup_interval = int(self.get_value('E5','BackupInterval'))

    def is_valid(self):
        for field_option in ['DARKMODE','INCREMENTALBACKUPS']:
            if self.get_value('E5',field_option):
                if self.get_value('E5',field_option).upper() == 'YES':
                    self.update_value('E5',field_option,'TRUE')
            else:
                self.update_value('E5',field_option,'FALSE')

        if self.get_value('E5', "BACKUPINTERVAL"):
            test = False
            try:
                test = int(self.get_value('E5', "BACKUPINTERVAL"))
                if test < 0:
                    test = 0
                elif test > 200:
                    test = 200
                self.update_value('E5', 'BACKUPINTERVAL', test)
            except:
                self.update_value('E5', 'BACKUPINTERVAL', 0)
        else:
            self.update_value('E5', 'BACKUPINTERVAL', 0)

    def update(self):
        self.update_value('E5','CFG', e4_cfg.filename)
        self.update_value('E5','ColorScheme', e5_colors.color_scheme)
        self.update_value('E5','DarkMode', e5_colors.darkmode)
        self.update_value('E5','IncrementalBackups', self.incremental_backups)
        self.update_value('E5','BackupInterval', self.backup_interval)
        self.save()

    def save(self):
        self.write_blocks()

    def status(self):
        txt = '\nThe INI file is %s.\n' % self.filename
        return(txt)

class field:
    def __init__(self, name):
        self.name = name
        self.inputtype = ''
        self.prompt = ''
        self.length = 0
        self.menu = ''
        self.menufile = ''
        self.conditions = []
        self.increment = False
        self.carry = False 
        self.unique = False
        self.info = ''
        self.infofile = ''          
        self.data = ''
        self.key = False            # Not yet implemented (maybe not necessary)
        self.required = False
        self.sorted = False         # Not yet implemented
        self.valid = []
        self.validfile = ''
        self.invalid = []
        self.invalidfile = ''
        self.lookupfile = ''
        self.lookupdb = None

class cfg(blockdata):

    def __init__(self, filename = ''):
        self.initialize()
        if filename:
            self.filename = filename

    def initialize(self):
        self.blocks = []
        self.filename = ""
        self.path = ""
        self.current_field = None
        self.current_record = {}
        self.BOF = True
        self.EOF = False
        self.has_errors = False
        self.has_warnings = False
        self.key_field = None   # not implimented yet
        self.description = ''   # not implimented yet

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        self.load()

    def empty_record(self):
        if self.current_record:
            for key in self.current_record:
                if not self.get(key).carry and not self.get(key).increment:
                    self.current_record[key] = ''
        for field_name in self.fields():
            if self.get(field_name).inputtype == 'DATETIME':
                self.current_record[field_name] = '%s' % datetime.now().replace(microsecond=0)
            if self.get(field_name).increment:
                try:
                    self.current_record[field_name] = '%s' % (int(self.current_record[field_name]) + 1)
                except:
                    self.current_record[field_name] = '1'

    def validate_current_record(self):
        return(True)

    def get(self, field_name):
        if not field_name:
            return('')
        else:
            f = field(field_name)
            f.name = field_name
            f.inputtype = self.get_value(field_name, 'TYPE')
            f.prompt = self.get_value(field_name, 'PROMPT')
            f.length = self.get_value(field_name, 'LENGTH')
            f.unique = self.get_value(field_name,"UNIQUE").upper() == 'TRUE'
            f.increment = self.get_value(field_name,"INCREMENT").upper() == 'TRUE'
            f.carry = self.get_value(field_name,"CARRY").upper() == 'TRUE'
            f.required = self.get_value(field_name,"REQUIRED").upper() == 'TRUE'
            f.sorted = self.get_value(field_name,"SORTED").upper() == 'TRUE'

            f.menu = []
            if f.inputtype == 'MENU':
                if self.get_value(field_name, 'MENU'):
                    f.menu = self.get_value(field_name, 'MENU').split(",")
                if self.get_value(field_name, 'MENU FILE'):
                    f.menufile = self.get_value(field_name, 'MENU FILE')
                    if f.menufile:
                        try:
                            with open(self.get_value(field_name, 'MENU FILE')) as fileio:
                                f.menu = fileio.readlines()
                        except:
                            pass
                if f.menu:
                    f.menu = self.clean_menu(f.menu)
                    f._menu_item_maxlen = max([len(menuitem) for menuitem in f.menu])

            f.info = self.get_value(field_name, 'INFO')
            f.infofile = self.get_value(field_name, 'INFO FILE')
            if f.infofile:
                try:
                    with open(f.infofile) as fileio:
                        f.info = fileio.read()
                except:
                    f.info = "Error: Could not read from the info file '%s'." % f.infofile

            f.validfile = self.get_value(field_name, 'VALID FILE')
            f.valid = []
            if f.validfile:
                try:
                    with open(f.validfile) as fileio:
                        f.valid = fileio.readlines()
                except:
                    pass

            f.invalidfile = self.get_value(field_name, 'INVALID FILE')
            f.invalid = []
            if f.invalidfile:
                try:
                    with open(f.invalidfile) as fileio:
                        f.invalid = fileio.readlines()
                except:
                    pass

            if f.lookupfile:
                # convert the name to a json extension
                # open the db 
                # and return here a handle to it
                f.lookupdb = None
                pass

            for condition_no in range(1, 6):
                if self.get_value(field_name, "CONDITION%s" % condition_no):
                    f.conditions.append(self.get_value(field_name, "CONDITION%s" % condition_no))
            return(f)

    # Remove leading and trailing spaces
    # and remove empty items once this is done.
    def clean_menu(self, menulist):
        for menu_item in menulist:
            menu_item = menu_item.strip()
        menulist = list(filter(('').__ne__, menulist))
        return(menulist)

    def put(self, field_name, f):
        self.update_value(field_name, 'PROMPT', f.prompt)
        self.update_value(field_name, 'LENGTH', f.length)
        self.update_value(field_name, 'TYPE', f.inputtype)
        self.update_value(field_name, 'INFO FILE', f.infofile)
        self.update_value(field_name, 'MENU FILE', f.menufile)
        self.update_value(field_name, 'VALID FILE', f.invalidfile)
        self.update_value(field_name, 'INVALID FILE', f.validfile)
        self.update_value(field_name, 'LOOKUP FILE', f.lookupfile)

    def get_field_data(self, field_name = None):
        f = field_name
        if not f:
            if self.current_field:
                f = self.current_field.name
            else:
                return(None)
        if f in self.current_record.keys():
            return(self.current_record[f])
        else:
            return(None)

    def fields(self):
        field_names = self.names()
        del_fields = ['E5']
        for del_field in del_fields:
            if del_field in field_names:
                field_names.remove(del_field)
        return(field_names)

    def data_is_valid(self):
        if self.current_field.required and self.current_record[self.current_field.name]=='':
            return('\nError: This field is marked as required.  Please provide a response.')
        if self.current_field.unique:
            if self.current_record[self.current_field.name]=='':
                return('\nError: This field is marked as unique.  Empty entries are not allowed in unique fields.')
            for data_row in e4_data.db:
                if self.current_field.name in data_row:
                    if data_row[self.current_field.name] == self.current_record[self.current_field.name]:
                        return('\nError: This field is marked as unique and you are trying to add a duplicate entry.')
        if self.current_field.inputtype == 'NUMERIC':
            try:
                val = int(self.current_record[self.current_field.name])
            except ValueError:
                return('\nError: This field is marked as numeric but a non-numeric value was provided.')
        if self.current_field.valid:
            if not any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.valid):
                return("\nError: The entry '%s' does not appear in the list of valid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.validfile) )
        if self.current_field.invalid:
            if any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.invalid):
                return("\nError: The entry '%s' appears in the list of invalid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.invalidfile) )
        return(True)

    def is_valid(self):
        # Check to see that conditions are numbered 
        self.has_errors = False
        self.has_warnings = False
        self.errors = []
        if len(self.fields())==0:
            self.errors.append('Error: No fields defined in the CFG file.')
            self.has_errors = True
        else:
            self.rename_block('E4','E5')        # Convert E4 file to E5
            prior_fieldnames = []
            for field_name in self.fields():

                # This change makes an E4 file compatible with E5
                if self.get_value(field_name, "LOOK UP"):
                    self.rename_key(field_name, 'LOOK UP', 'LOOKUP FILE')

                if self.get_value(field_name, 'LOOKUP FILE'):
                    filename = locate_file(self.get_value(field_name, 'LOOKUP FILE'), self.path)
                    if filename:
                        self.update_value(field_name, 'LOOKUP FILE', filename)
                        try:
                            # read the first line to get fieldnames
                            # look for a fieldname match with the current fieldname
                            # create a TinyDB
                            # go through each line and write to TinyDB
                            fieldnames = []
                            firstline = True
                            with open(filename) as fileio:
                                lineno = 0
                                for line in fileio:
                                    lineno += 1
                                    data = line.split(',')    
                                    if firstline:
                                        fieldnames = data
                                        firstline = False
                                    else:
                                        if len(data) == len(fieldnames):
                                            self.has_errors = True
                                            self.errors.append("ERROR: The CSV file '%s' had a problem on line %s.  The number of fields provided does not match the expected number of field." % (filename, lineno))
                                            break
                                    # insert data into a data record
                                    data_record = {}
                                    for field in fieldnames:
                                        data_record[field] = data[field]
                                    e4_data.db.insert(e4_cfg.current_record)

                        except:
                            pass
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the lookup file '%s' for the field %s." % (self.get_value(field_name, 'LOOKUP FILE'), field_name))

                for field_option in ['UNIQUE','CARRY','INCREMENT','REQUIRED','SORTED']:
                    if self.get_value(field_name, field_option):
                        if self.get_value(field_name, field_option).upper() == 'YES':
                            self.update_value(field_name, field_option, 'TRUE')

                f = self.get(field_name)

                if self.get_value(field_name, "LENGTH"):
                    test = False
                    try:
                        test = int(f.length) > 0 and int(f.length) < 256
                    except:
                        pass
                    if not test:
                        self.errors.append('Error: The length specified for field %s must be between 1 and 255.' % field_name)
                        self.has_errors = True

                if f.prompt == '':
                    f.prompt = field_name

                f.inputtype = f.inputtype.upper()
                if not f.inputtype in ['TEXT','NOTE','NUMERIC','MENU','DATETIME','BOOLEAN','CAMERA','GPS','INSTRUMENT']:
                    self.errors.append('Error: The value %s for the field %s is not a valid input type.  Valid input types include Text, Note, Numeric, Instrument, Menu, Datetime, Boolean, Camera and GPS.' % (f.inputtype, field_name))
                    self.has_errors = True

                if f.infofile:
                    if locate_file(f.infofile, self.path):
                        f.infofile = locate_file(f.infofile, self.path)
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the info file '%s' for the field %s." % (f.infofile, field_name))

                if f.validfile:
                    if locate_file(f.validfile, self.path):
                        f.validfile = locate_file(f.validfile, self.path)
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the valid file '%s' for the field %s." % (f.validfile, field_name))

                if f.invalidfile:
                    if locate_file(f.invalidfile, self.path):
                        f.invalidfile = locate_file(f.invalidfile, self.path)
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the valid file '%s' for the field %s." % (f.invalidfile, field_name))

                if f.lookupfile:
                    if locate_file(f.lookupfile, self.path):
                        f.lookupfile = locate_file(f.lookupfile, self.path)

                if f.inputtype == 'MENU' and (len(f.menu)==0 and f.menufile == ''):
                    self.errors.append('Error: The field %s is listed a menu, but no menu list or menu file was provided with a MENU or MENUFILE option.' % field_name)
                    self.has_errors = True

                if f.menufile:
                    if locate_file(f.menufile, self.path):
                        f.menufile = locate_file(f.menufile, self.path)
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the menu file '%s' for the field %s." % (f.menufile, field_name))
                
                if any((c in set(r' !@#$%^&*()?/\{}<.,.|+=_-~`')) for c in field_name):
                    self.errors.append('Warning: The field %s has non-standard characters in it.  E5 will attempt to work with it, but it is highly recommended that you rename it as it will likely cause problems elsewhere.' % field_name)
                    self.has_warnings = True

                if len(f.conditions)>0:
                    n = 0
                    for condition in f.conditions:
                        n += 1
                        condition_parsed = condition.split(' ')
                        condition_parsed = self.clean_menu(condition_parsed)
                        if len(condition_parsed)<2 or len(condition_parsed)>3:
                            self.errors.append('Error: Condition number %s for the field %s is not correctly formatted.  A condition requires a target field and a matching value.' % (n, field_name))
                            self.has_errors = True
                        else:
                            condition_fieldname = condition_parsed[0]
                            if not condition_fieldname.upper() in prior_fieldnames:
                                self.errors.append('Error: Condition number %s for the field %s references field %s which has not been defined prior to this.' % (n, field_name, condition_fieldname))
                                self.has_errors = True
                            else:
                                condition_field = self.get(condition_fieldname)
                                if condition_field.inputtype == 'MENU':
                                    if condition_parsed[1] == 'NOT':
                                        condition_matches = condition_parsed[2].split(',')
                                    else:
                                        condition_matches = condition_parsed[1].split(',')
                                    condition_matches = self.clean_menu(condition_matches)
                                    condition_matches = list(filter(("''").__ne__, condition_matches))
                                    condition_matches = list(filter(('""').__ne__, condition_matches))
                                    for condition_match in condition_matches:
                                        if condition_match.upper() not in [x.upper() for x in condition_field.menu]:
                                            self.errors.append('Warning: Condition number %s for the field %s tries to match the value "%s" to the menulist in field %s, but field %s does not contain this value.' % (n, field_name, condition_match, condition_fieldname, condition_fieldname))
                                            self.has_warnings = True

                self.put(field_name, f)
                prior_fieldnames.append(field_name.upper())

        return(self.has_errors)

    def save(self):
        self.write_blocks()

    def load(self, filename = ''):
        if filename:
            self.filename = filename
        self.path = ntpath.split(self.filename)[0]

        self.blocks = []
        if os.path.isfile(self.filename):
            self.blocks = self.read_blocks()
        else:
            self.filename = ''
        self.BOF = True
        if len(self.blocks)>0:
            self.EOF = False
        else:
            self.EOF = True
        self.current_field = None
        self.is_valid()

    def status(self):
        if self.filename:
            txt = '\nThe CFG file is %s\n' % self.filename
            txt += 'and contains %s fields.' % len(self.blocks)
        else:
            txt = 'A CFG file has not been opened.\n'
        return(txt)

    def next(self):
        if self.EOF:
            self.current_field = None
        else:
            if self.BOF:
                self.BOF = False
                self.EOF = False
                self.current_field = self.get(self.fields()[0])
            else:
                field_index = self.fields().index(self.current_field.name)
                while True:
                    field_index += 1
                    if field_index > (len(self.fields()) - 1):
                        self.EOF = True
                        self.current_field = None
                        break
                    else:
                        self.current_field = self.get(self.fields()[field_index])
                        if self.condition_test():
                            self.EOF = False
                            self.BOF = False
                            break
        return(self.current_field)

    def previous(self):
        if self.BOF:
            self.current_field = None
        else:
            if self.EOF:
                self.BOF = False
                self.EOF = False
                self.current_field = self.get(self.fields()[-1])
            else:
                field_index = self.fields().index(self.current_field.name)
                while True:
                    field_index -= 1
                    if field_index < 0:
                        self.BOF = True
                        self.current_field = None
                        break
                    else:
                        self.current_field = self.get(self.fields()[field_index])
                        if self.condition_test():
                            self.EOF = False
                            self.BOF = False
                            break
        return(self.current_field)

    def start(self):
        if len(self.fields())>0 and not self.has_errors:
            self.BOF = False
            self.EOF = False
            self.current_field = self.get(self.fields()[0])
            self.empty_record()
        else:
            self.BOF = True
            self.EOF = True
            self.current_field = None
            self.current_record = {}
        return(self.current_field)

    def condition_test(self):
        if len(self.current_field.conditions) == 0:
            return(True)
        condition_value = True
        for condition in self.current_field.conditions:
            condition = condition.split(" ")
            condition_field = condition[0]
            if len(condition) == 2:
                condition_matches = condition[1].upper().split(',')
                condition_not = False
            else:
                condition_matches = condition[2].upper().split(',')
                condition_not = True
            if condition_field in self.current_record.keys():
                if not self.current_record[condition_field].upper() in condition_matches:
                    if not condition_not:
                        condition_value = False 
                else:
                    condition_value = False
            else:
                if not condition_not:
                    condition_value = False
            if not condition_value:
                break
        return(condition_value)

    def write_csvs(self, filename, table):
        try:
            f = open(filename, 'w')
            for row in table:
                csv_row = ''
                for fieldname in self.fields():
                    if fieldname in row.keys():
                        if self.get(fieldname).inputtype in ['NUMERIC','INSTRUMENT']:
                            if csv_row:
                                csv_row = csv_row + ',%s' % row[fieldname] 
                            else:
                                csv_row = "%s" % row[fieldname] 
                        else:
                            if csv_row:
                                csv_row = csv_row + ',"%s"' % row[fieldname]
                            else: 
                                csv_row = '"%s"' % row[fieldname]
                    else:
                        if self.get(fieldname).inputtype in ['NUMERIC','INSTRUMENT']:
                            if csv_row:
                                csv_row = csv_row + ','
                        else:
                            if csv_row:
                                csv_row = csv_row + ',""'
                            else: 
                                csv_row = '""'
                f.write(csv_row + '\n')
            f.close()
            return(None)
        except:
            return('Could not write data to %s.' % (filename))
#endregion

#region File Menu
class LoadDialog(FloatLayout):
    start_path =  ObjectProperty(None)
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    button_color = ObjectProperty(None)
    button_background = ObjectProperty(None)

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    cancel = ObjectProperty(None)
    button_color = ObjectProperty(None)
    button_background = ObjectProperty(None)
    start_path = ObjectProperty(None)

#endregion

class YesNo(Popup):
    def __init__(self, title, message, yes_callback, no_callback, **kwargs):
        super(YesNo, self).__init__(**kwargs)
        content = BoxLayout(orientation = 'vertical')
        label = Label(text = message,
                        size_hint=(1, 1),
                        valign='middle',
                        halign='center')
        label.bind(
            width=lambda *x: label.setter('text_size')(label, (label.width, None)),
            texture_size=lambda *x: label.setter('height')(label, label.texture_size[1]))
        content.add_widget(label)
        button1 = Button(text = 'Yes', size_hint_y = .2,
                            color = e5_colors.button_color,
                            background_color = e5_colors.button_background,
                            background_normal = '')
        content.add_widget(button1)
        button1.bind(on_press = yes_callback)
        button2 = Button(text = 'No', size_hint_y = .2,
                            color = e5_colors.button_color,
                            background_color = e5_colors.button_background,
                            background_normal = '')
        content.add_widget(button2)
        button2.bind(on_press = no_callback)
        self.title = title
        self.content = content
        self.size_hint = (.8, .8)
        self.size=(400, 400)
        self.auto_dismiss = False

class MessageBox(Popup):
    def __init__(self, title, message, call_back = None, button_text = 'OK', **kwargs):
        super(MessageBox, self).__init__(**kwargs)
        popup_contents = GridLayout(cols = 1, spacing = 5)
        popup_contents.add_widget(e5_scrollview_label(message, popup = True, colors = e5_colors))
        if not call_back:
            call_back = self.dismiss
        popup_contents.add_widget(e5_button(button_text,
                                            call_back = call_back,
                                            selected = True,
                                            button_height = .1))
        self.title = title
        self.content = popup_contents
        self.size_hint = (.8, .8)
        self.size = (400, 400)
        self.auto_dismiss = False

class MainScreen(Screen):

    popup = ObjectProperty(None)
    popup_open = False
    event = ObjectProperty(None)
    widget_with_focus = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(MainScreen, self).__init__(**kwargs)

        # Used for KV file settings
        self.text_color = e5_colors.text_color
        self.button_color = e5_colors.button_color
        self.button_background = e5_colors.button_background

        self.add_widget(BoxLayout(orientation = 'vertical',
                                size_hint_y = .9,
                                size_hint_x = .8,
                                pos_hint={'center_x': .5},
                                id = 'mainscreen',
                                padding = 20,
                                spacing = 20))

        self.fpath = ''

        self.build_mainscreen()

    def build_mainscreen(self):

        mainscreen = self.get_widget_by_id('mainscreen')
        mainscreen.clear_widgets()

        if e4_cfg.filename:
            e4_cfg.start()

            if not e4_cfg.EOF or not e4_cfg.BOF:
                self.data_entry()
                if e4_cfg.has_warnings:
                    self.event = Clock.schedule_once(self.show_popup_message, 1)
            else:
                self.cfg_menu()
                self.event = Clock.schedule_once(self.show_popup_message, 1)

        else:
            if e4_ini.first_time:
                e4_ini.first_time = False
                self.event = Clock.schedule_once(self.show_popup_message, 1)
            self.cfg_menu()

    def set_dropdown_menu_colors(self):
        pass

    def get_path(self):
        if e4_ini.get_value("E5", "CFG"):
            return(ntpath.split(e4_ini.get_value("E5", "CFG"))[0])
        else:
            return(os.getcwd())

    def get_files(self, fpath, exts = None):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(fpath):
            files.extend(filenames)
            break
        if exts:
            return([filename for filename in files if filename.upper().endswith(exts.upper())])
        else:
            return(files)

    def cfg_menu(self):

        mainscreen = self.get_widget_by_id('mainscreen')

        self.cfg_files = self.get_files(self.get_path(), 'cfg')

        if self.cfg_files:

            self.cfg_file_selected = self.cfg_files[0]
        
            lb = Label(text = 'Begin data entry with one of these CFG files or use File Open',
                        color = e5_colors.text_color,
                        size_hint_y = .1)
            mainscreen.add_widget(lb)

            mainscreen.add_widget(e5_scrollview_menu(self.cfg_files,
                                                     self.cfg_file_selected,
                                                     widget_id = 'cfg',
                                                     call_back = self.cfg_selected))
            self.scroll_menu = self.get_widget_by_id('cfg_scroll')
            self.scroll_menu.make_scroll_menu_item_visible()
            self.widget_with_focus = self.scroll_menu

        else:
            label_text = '\nBefore data entry can begin, you need to have a CFG file.\n\nThe current folder contains none.  Either use File Open to switch a folder that contains CFG files or create one.' 
            lb = e5_scrollview_label(text = label_text, id = 'label', colors = e5_colors)
            lb.halign = 'center'
            mainscreen.add_widget(lb)
            self.widget_with_focus = mainscreen

    def cfg_selected(self, value):
        if value.text:
            self.cfg_load(os.path.join(self.get_path(), value.text))
        
    def cfg_load(self, cfgfile_name):
        e4_cfg.load(cfgfile_name)
        if e4_cfg.filename:
            self.open_db()
        e4_ini.update()
        self.build_mainscreen()

    def open_db(self):
        database = locate_file(e4_cfg.get_value('E5','DATABASE'), e4_cfg.path)
        if not database:
            database = os.path.split(e4_cfg.filename)[1]
            if "." in database:
                database = database.split('.')[0]
            database = os.path.join(e4_cfg.path, database + '.json')
        e4_data.open(database)
        if e4_cfg.get_value('E5','TABLE'):    
            e4_data.table = e4_cfg.get_value('E5','TABLE')
        else:
            e4_data.table = '_default'
        e4_cfg.update_value('E5','DATABASE', e4_data.filename)
        e4_cfg.update_value('E5','TABLE', e4_data.table)
        e4_cfg.save()
        
    def show_popup_message(self, dt):
        self.event.cancel()
        if e4_cfg.has_errors or e4_cfg.has_warnings:
            if e4_cfg.has_errors:
                message_text = 'The following errors in the configuration file %s must be fixed before data entry can begin.\n\n' % e4_cfg.filename
                e4_cfg.filename = ''
                title = 'CFG File Errors'                
            elif e4_cfg.has_warnings:
                e4_cfg.has_warnings = False
                message_text = '\nThough data entry can start, there are the following warnings in the configuration file %s.\n\n' % e4_cfg.filename
                title = 'Warnings'
            message_text = message_text + '\n\n'.join(e4_cfg.errors)
        else:
            title = 'E5'
            message_text = SPLASH_HELP
        self.popup = MessageBox(title, message_text, call_back = self.close_popup)
        self.popup.open()
        self.popup_open = True

    def data_entry(self):

        mainscreen = self.get_widget_by_id('mainscreen')
        #inputbox.bind(minimum_height = inputbox.setter('height'))

        label = Label(text = e4_cfg.current_field.prompt,
                    size_hint = (1, .13),
                    color = e5_colors.text_color,
                    id = 'field_prompt',
                    halign = 'center',
                    font_size = e5_colors.text_font_size)
        mainscreen.add_widget(label)
        label.bind(texture_size = label.setter('size'))
        label.bind(size_hint_min_x = label.setter('width'))

        kb = TextInput(size_hint = (1, .07 if not e4_cfg.current_field.inputtype == 'NOTE' else .07 * 5),
                            multiline = (e4_cfg.current_field.inputtype == 'NOTE'),
                            write_tab = False,
                            id = 'field_data',
                            font_size = e5_colors.text_font_size)
        mainscreen.add_widget(kb)
        kb.bind(text = self.textbox_changed)
        self.widget_with_focus = kb
        self.scroll_menu = None
        kb.focus = True

        scroll_content = BoxLayout(orientation = 'horizontal',
                                    size_hint = (1, .6 if not e4_cfg.current_field.inputtype == 'NOTE' else .6 - .07 * 4),
                                    id = 'scroll_content',
                                    spacing = 20)
        self.add_scroll_content(scroll_content)
        mainscreen.add_widget(scroll_content)

        if e4_cfg.current_field.inputtype in ['BOOLEAN','MENU']:
            self.scroll_menu_setup()

        buttons = GridLayout(cols = 2, size_hint = (1, .2), spacing = 20)
        
        buttons.add_widget(e5_button('Back', id = 'back', selected = True, call_back = self.go_back, colors = e5_colors))
        
        buttons.add_widget(e5_button('Next', id = 'next', selected = True, call_back = self.go_next, colors = e5_colors))
        
        mainscreen.add_widget(buttons)
        
        #self.add_widget(mainscreen)

    def scroll_menu_setup(self):
        self.scroll_menu = self.get_widget_by_id('menu_scroll')
        if self.scroll_menu:
            self.scroll_menu.make_scroll_menu_item_visible()
        self.widget_with_focus = self.scroll_menu if self.scroll_menu else self

    def textbox_changed(self, instance, value):
        if e4_cfg.current_field.inputtype in ['BOOLEAN','MENU']:
            self.add_scroll_content(self.get_widget_by_id('scroll_content'), value)
            self.scroll_menu_setup()

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    def get_widget_by_id(self, id):
        for widget in self.walk():
            if widget.id == id:
                return(widget)
        return(None)

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        text_str = args[3]  
        print('INFO: The key %s has been pressed %s' % (ascii_code, text_str))
        if not self.popup_open:
            if ascii_code == 8:
                return False
            if ascii_code == 9:
                if self.widget_with_focus.id == 'menu_scroll':
                    self.widget_with_focus = self.get_widget_by_id('field_data')
                    self.widget_with_focus.focus = True
                elif self.widget_with_focus.id == 'field_data' and e4_cfg.current_field.inputtype in ['MENU','BOOLEAN']:
                    self.widget_with_focus.focus = False
                    self.widget_with_focus = self.get_widget_by_id('menu_scroll')
                return False
            if ascii_code == 27:
                if e4_cfg.filename:
                    self.go_back(None)
            if ascii_code == 13:
                if e4_cfg.filename:
                    if e4_cfg.current_field.inputtype in ['MENU','BOOLEAN']:
                        textbox = self.get_widget_by_id('field_data').text
                        menubox = self.scroll_menu.scroll_menu_get_selected().text if self.scroll_menu.scroll_menu_get_selected() else ''
                        if textbox == '' and not menubox == '':
                            self.get_widget_by_id('field_data').text = menubox
                        elif not textbox == '' and not menubox == '':
                            if not textbox.upper() == menubox.upper():
                                if textbox.upper() == menubox.upper()[0:len(textbox)]:
                                    self.get_widget_by_id('field_data').text = menubox
                    self.go_next(None)
                else:
                    self.cfg_selected(self.scroll_menu.scroll_menu_get_selected())
            if ascii_code == 51:
                return True 
            if ascii_code in [273, 274, 275, 276, 278, 279] and self.scroll_menu:
                self.scroll_menu.move_scroll_menu_item(ascii_code)
                return False 
            #if text_str:
            #    if text_str.upper() in ascii_uppercase:
            #        self.add_scroll_content(self.get_widget_by_id('scroll_content'), 
            #                                self.get_widget_by_id('field_data').text + text_str)
            #        return True
        else:
            if ascii_code == 13:
                self.close_popup(None)
                self.widget_with_focus.focus = True
                return False
        return True # return True to accept the key. Otherwise, it will be used by the system.

    def add_scroll_content(self, content_area, menu_filter = ''):
    
        content_area.clear_widgets()

        info_exists = e4_cfg.current_field.info or e4_cfg.current_field.infofile
        menu_exists = e4_cfg.current_field.inputtype == 'BOOLEAN' or (not e4_cfg.current_field.menu == [])
        camera_exists = e4_cfg.current_field.inputtype == 'CAMERA'

        if menu_exists or info_exists or camera_exists:

            if camera_exists:
                bx = BoxLayout(orientation = 'vertical')
                bx.add_widget(Camera(play=True, size_hint_y = .8,
                                         resolution = (320,160)))
                bx.add_widget(e5_button(text = "Snap",
                                        id = "snap", selected = True))                
                content_area.add_widget(bx)

            if menu_exists:
                if info_exists:
                    no_cols = int(content_area.width/2/150)
                else:
                    no_cols = int(content_area.width/150)
                if no_cols < 1:
                    no_cols = 1

                if e4_cfg.current_field.inputtype == 'BOOLEAN':
                    menu_list = ['True','False']
                else:
                    menu_list = e4_cfg.current_field.menu

                if menu_filter:
                    menu_list = [menu for menu in menu_list if menu.upper()[0:len(menu_filter)] == menu_filter.upper()]

                selected_menu = e4_cfg.get_field_data('')
                if not selected_menu and menu_list:
                    selected_menu = menu_list[0]

                if info_exists:
                    ncols = int(content_area.width / 400)
                else:
                    ncols = int(content_area.width / 200)
                if ncols < 1:
                    ncols = 1

                content_area.add_widget(e5_scrollview_menu(menu_list,
                                                           selected_menu,
                                                           widget_id = 'menu',
                                                           call_back = self.menu_selection,
                                                           ncols = ncols))

            if info_exists:
                content_area.add_widget(e5_scrollview_label(self.get_info(), colors = e5_colors))

    def get_info(self):
        if e4_cfg.current_field.infofile:
            fname = os.path.join(e4_cfg.path, e4_cfg.current_field.infofile)
            if os.path.exists(fname):
                try:
                    with open(fname, 'r') as f:
                        return(f.read())
                except:
                    return('Could not open file %s.' % fname)
            else:
                return('The file %s does not exist.' % fname)
        else:
            return(e4_cfg.current_field.info)

    def on_pre_enter(self):
        Window.bind(on_key_down = self._on_keyboard_down)
        if e5_colors.need_redraw:
            pass

    def exit_program(self):
        e4_ini.update_value('E5','TOP', Window.top)
        e4_ini.update_value('E5','LEFT', Window.left)
        e4_ini.update_value('E5','WIDTH', Window.width)
        e4_ini.update_value('E5','HEIGHT', Window.height)
        e4_ini.save()
        App.get_running_app().stop()

    def show_save_csvs(self):
        if e4_cfg.filename and e4_data.filename:
            content = SaveDialog(start_path = e4_cfg.path,
                                save = self.save_csvs, 
                                cancel = self.dismiss_popup,
                                button_color = e5_colors.button_color,
                                button_background = e5_colors.button_background)
            self.popup = Popup(title = "Select a folder for the  CSV files",
                                content = content,
                                size_hint = (0.9, 0.9))
        else:
            self.popup = MessageBox('E5', '\nOpen a CFG before exporting to CSV',
                                    call_back = self.dismiss_popup)
        self.popup.open()
        self.popup_open = True

    def save_csvs(self, path):

        self.popup.dismiss()

        filename = ntpath.split(e4_cfg.filename)[1].split(".")[0]
        filename = os.path.join(path, filename + '.csv' )

        table = e4_data.db.table('_default')

        errors = e4_cfg.write_csvs(filename, table)
        title = 'CSV Export'
        if errors:
            self.popup = MessageBox(title, errors, call_back = self.close_popup)
        else:
            self.popup = MessageBox(title, '%s successfully written.' % filename, call_back = self.close_popup)
        self.popup.open()
        self.popup_open = True

    def show_load_cfg(self):
        if e4_cfg.filename and e4_cfg.path:
            start_path = e4_cfg.path
        else:
            start_path = e4_ini.get_value('E5','APP_PATH')
        content = LoadDialog(load = self.load, 
                            cancel = self.dismiss_popup,
                            start_path = start_path,
                            button_color = e5_colors.button_color,
                            button_background = e5_colors.button_background)
        self.popup = Popup(title = "Load CFG file", content = content,
                            size_hint = (0.9, 0.9))
        self.popup.open()

    def load(self, path, filename):
        self.dismiss_popup()
        self.cfg_load(os.path.join(path, filename[0]))

    def dismiss_popup(self, *args):
        self.popup_open = False
        self.popup.dismiss()
        self.parent.current = 'MainScreen'

    def update_mainscreen(self):
        textbox_contents = ''
        for widget in self.walk():
            if widget.id=='field_prompt':
                widget.text = e4_cfg.current_field.name
            if widget.id == 'field_data':
                widget.text = e4_cfg.current_record[e4_cfg.current_field.name] if e4_cfg.current_field.name in e4_cfg.current_record.keys() else ''
                widget.multiline = (e4_cfg.current_field.inputtype == 'NOTE')
                widget.size_hint = (1, .07 if not e4_cfg.current_field.inputtype == 'NOTE' else .07 * 5)
                widget.select_all()
                self.widget_with_focus = widget
                self.scroll_menu = None
                textbox_contents = widget.text 
            if widget.id=='scroll_content':
                #widget.size_hint = (1, .6 if not e4_cfg.current_field.inputtype == 'NOTE' else .6 - .07 * 4),
                self.add_scroll_content(widget, textbox_contents)    
                self.scroll_menu_setup()
                break
        self.widget_with_focus.focus = True

    def save_field(self):
        widget = self.get_widget_by_id('field_data')
        e4_cfg.current_record[e4_cfg.current_field.name] = widget.text 
        widget.text = ''

    def go_back(self, *args):
        if e4_cfg.filename:
            self.save_field()
            e4_cfg.previous()
            if e4_cfg.BOF:
                e4_cfg.filename = ''
                self.build_mainscreen()
            else:
                self.update_mainscreen()

    def go_next(self, *args):
        self.save_field()
        valid_data = e4_cfg.data_is_valid()
        if valid_data == True:
            e4_cfg.next()
            if e4_cfg.EOF:
                self.save_record()
                e4_cfg.start()
            self.update_mainscreen()
        else:
            widget = self.get_widget_by_id('field_data')
            widget.text = e4_cfg.current_record[e4_cfg.current_field.name] 
            widget.focus = True
            self.popup = MessageBox(e4_cfg.current_field.name, valid_data, call_back = self.close_popup)
            self.popup.open()
            self.popup_open = True

    def menu_selection(self, value):
        self.get_widget_by_id('field_data').text = value.text
        self.go_next(value)

    def save_record(self):
        valid = e4_cfg.validate_current_record()
        if valid:
            e4_data.db.insert(e4_cfg.current_record)
            self.make_backup()
        else:
            self.popup = MessageBox('Save Error', valid, call_back = self.close_popup)
            self.popup.open()
            self.popup_open = True

    def make_backup(self):
        if e4_ini.backup_interval > 0:
            try:
                record_counter = int(e4_cfg.get_value('E5','RECORDS UNTIL BACKUP')) if e4_cfg.get_value('E5','RECORDS UNTIL BACKUP') else e4_ini.backup_interval
                record_counter -= 1
                if record_counter <= 0:
                    backup_path, backup_file = os.path.split(e4_data.filename)
                    backup_file, backup_file_ext = backup_file.split('.')
                    backup_file += self.time_stamp() if e4_ini.incremental_backups else '_backup'
                    backup_file += backup_file_ext
                    backup_file = os.path.join(backup_path, backup_file)
                    copyfile(e4_ini.filename, backup_file)
                    record_counter = e4_ini.backup_interval
                e4_cfg.update_value('E5','RECORDS UNTIL BACKUP',str(record_counter))
            except:
                self.popup = MessageBox('Backup Error', "An error occurred while attempting to make a backup.  Check the backup settings and that the disk has enough space for a backup.", call_back = self.close_popup)
                self.popup.open()
                self.popup_open = True

    def time_stamp(self):
        time_stamp = '%s' % datetime.now().replace(microsecond=0)
        time_stamp = time_stamp.replace('-','_')
        time_stamp = time_stamp.replace(' ','_')
        time_stamp = time_stamp.replace(':','_')
        return('_' + time_stamp)

    def close_popup(self, value):
        self.popup.dismiss()
        self.popup_open = False
        self.event = Clock.schedule_once(self.set_focus, 1)

    def set_focus(self, value):
        self.widget_with_focus.focus = True

#region Edit Screens

class EditPointsScreen(e5_DatagridScreen):

    def __init__(self,**kwargs):
        super(EditPointsScreen, self).__init__(**kwargs)
        if e4_data.db:
            self.datagrid.data = e4_data.db.table(e4_data.table)
            self.datagrid.fields = e4_cfg

    def on_pre_enter(self):
        if self.datagrid.data == None and not e4_data.db == None:
            self.datagrid.load_data(e4_data.db.table(e4_data.table), e4_cfg)
        elif not self.datagrid.data == None and not e4_data.db == None:
            if not self.datagrid.record_count() == len(e4_data.db):
                self.datagrid.reload_data()

class TextLabel(Label):
    def __init__(self, text, **kwargs):
        super(TextLabel, self).__init__(**kwargs)
        self.text = text
        self.color = e5_colors.text_color
        self.font_size = e5_colors.text_font_size
        self.size_hint_y = None

class EditCFGScreen(Screen):

    def on_pre_enter(self):
        #super(Screen, self).__init__(**kwargs)
        self.clear_widgets()

        layout = GridLayout(cols = 1,
                            size_hint_y = None, id = 'fields')
        layout.bind(minimum_height=layout.setter('height'))

        for field_name in e4_cfg.fields():
            f = e4_cfg.get(field_name)
            bx = GridLayout(cols = 1, size_hint_y = None)
            bx.add_widget(TextLabel("[" + f.name + "]"))
            layout.add_widget(bx)

            bx = GridLayout(cols = 2, size_hint_y = None)
            bx.add_widget(TextLabel("Prompt"))
            bx.add_widget(TextInput(text = f.prompt,
                                        multiline = False, size_hint_y = None))
            layout.add_widget(bx)

            bx = GridLayout(cols = 2, size_hint_y = None)
            bx.add_widget(TextLabel("Type"))
            bx.add_widget(Spinner(text="Text", values=("Text", "Numeric", "Menu"),
                                        #id = 'station',
                                        size_hint=(None, None),
                                        pos_hint={'center_x': .5, 'center_y': .5},
                                        color = e5_colors.optionbutton_color,
                                        background_color = e5_colors.optionbutton_background,
                                        background_normal = ''))
            #self.StationMenu.size_hint  = (0.3, 0.2)
            layout.add_widget(bx)

            bx = GridLayout(cols = 6, size_hint_y = None)
            
            bx.add_widget(TextLabel("Carry"))
            bx.add_widget(Switch(active = f.carry))

            bx.add_widget(TextLabel("Unique"))
            bx.add_widget(Switch(active = f.unique))

            bx.add_widget(TextLabel("Increment"))
            bx.add_widget(Switch(active = f.increment))

            layout.add_widget(bx)
            
            if f.inputtype == 'MENU':
                bx = GridLayout(cols = 1, size_hint_y = None)
                button1 = Button(text = 'Edit Menu', size_hint_y = None,
                                color = e5_colors.optionbutton_color,
                                background_color = e5_colors.optionbutton_background,
                                background_normal = '',
                                id = f.name)
                bx.add_widget(button1)
                button1.bind(on_press = self.show_menu)
                layout.add_widget(bx)

        root = ScrollView(size_hint=(1, .8))
        root.add_widget(layout)
        self.add_widget(root)

        buttons = GridLayout(cols = 2, spacing = 10, size_hint_y = None)

        button2 = Button(text = 'Back', size_hint_y = None,
                        color = e5_colors.button_color,
                        background_color = e5_colors.button_background,
                        background_normal = '')
        buttons.add_widget(button2)
        button2.bind(on_press = self.go_back)

        button3 = Button(text = 'Save Changes', size_hint_y = None,
                        color = e5_colors.button_color,
                        background_color = e5_colors.button_background,
                        background_normal = '')
        buttons.add_widget(button3)
        button3.bind(on_press = self.save)

        self.add_widget(buttons)

    def go_back(self, value):
        self.parent.current = 'MainScreen'

    def save(self, value):
        self.parent.current = 'MainScreen'

    def show_menu(self):
        pass

class E5SettingsScreen(Screen):
    def __init__(self,**kwargs):
        super(E5SettingsScreen, self).__init__(**kwargs)

        self.build_screen()

    def build_screen(self):
        self.clear_widgets()
        layout = GridLayout(cols = 1,
                                size_hint_y = 1,
                                id = 'settings_box',
                                spacing = 5, padding = 5)
        layout.bind(minimum_height = layout.setter('height'))

        darkmode = GridLayout(cols = 2, size_hint_y = .1, spacing = 5, padding = 5)
        darkmode.add_widget(e5_label('Dark Mode'))
        darkmode_switch = Switch(active = e5_colors.darkmode)
        darkmode_switch.bind(active = self.darkmode)
        darkmode.add_widget(darkmode_switch)
        layout.add_widget(darkmode)

        colorscheme = GridLayout(cols = 2, size_hint_y = .6, spacing = 5, padding = 5)
        colorscheme.add_widget(e5_label('Color Scheme'))
        colorscheme.add_widget(e5_scrollview_menu(e5_colors.color_names(),
                                                  menu_selected = '',
                                                  call_back = self.color_scheme_selected))
        current_scheme = e5_colors.color_scheme
        for widget in colorscheme.walk():
            if widget.id in e5_colors.color_names():
                e5_colors.set_to(widget.text)
                widget.background_color = e5_colors.button_background
        layout.add_widget(colorscheme)
        e5_colors.set_to(current_scheme)
        
        backups = GridLayout(cols = 2, size_hint_y = .3, spacing = 5, padding = 5)
        backups.add_widget(e5_label('Auto-backup after\nevery %s\nrecords entered.' % e4_ini.backup_interval,
                                    id = 'label_backup_interval'))
        slide = Slider(min = 0, max = 200,
                        value = e4_ini.backup_interval,
                        orientation = 'horizontal', id = 'backup_interval',
                        value_track = True, value_track_color= e5_colors.button_background)
        backups.add_widget(slide)
        slide.bind(value = self.update_backup_interval)
        backups.add_widget(e5_label('Use incremental backups?'))
        backups_switch = Switch(active = e4_ini.incremental_backups)
        backups_switch.bind(active = self.incremental_backups)
        backups.add_widget(backups_switch)
        layout.add_widget(backups)

        settings_layout = GridLayout(cols = 1, size_hint_y = 1, spacing = 5, padding = 5)
        scrollview = ScrollView(size_hint = (1, 1),
                                 bar_width = SCROLLBAR_WIDTH)
        scrollview.add_widget(layout)
        settings_layout.add_widget(scrollview)

        settings_layout.add_widget(e5_button('Back', selected = True, call_back = self.go_back))
        self.add_widget(settings_layout)

    def update_backup_interval(self, instance, value):
        e4_ini.backup_interval = int(value)
        for widget in self.walk():
            if widget.id == 'label_backup_interval':
                widget.text = 'Auto-backup after\nevery %s\nrecords entered.' % e4_ini.backup_interval
                break

    def incremental_backups(self, instance, value):
        e4_ini.incremental_backups = value

    def darkmode(self, instance, value):
        e5_colors.set_to_darkmode() if value else e5_colors.set_to_lightmode()
        self.build_screen()

    def color_scheme_selected(self, instance):
        e5_colors.set_to(instance.text)
        self.build_screen()

    def go_back(self, instance):
        e4_ini.update()
        self.parent.current = 'MainScreen'

### End Edit Screens
#endregion

#region Help Screens
### Help Screens
class InfoScreen(Screen):

    content = ObjectProperty(None)

    def __init__(self,**kwargs):
        super(InfoScreen, self).__init__(**kwargs)
        layout = GridLayout(cols = 1, size_hint_y = 1, spacing = 5, padding = 5)
        layout.add_widget(e5_scrollview_label(text = '', widget_id = 'content', colors = e5_colors))
        layout.add_widget(e5_button('Back', selected = True, call_back = self.go_back, colors = e5_colors))
        self.add_widget(layout)
        for widget in self.walk():
            if widget.id == 'content_label':
                self.content = widget

    def go_back(self, *args):
        self.parent.current = 'MainScreen'

class StatusScreen(InfoScreen):
    def on_pre_enter(self):
        txt = e4_data.status() if e4_data else 'A data file has not been initialized or opened.\n\n'
        txt += e4_cfg.status()
        txt += e4_ini.status()
        txt += '\nThe default user path is %s.\n' % e4_ini.get_value("E5","APP_PATH")
        txt += '\nThe operating system is %s.\n' % ['Windows','Linux','MacOSX','IOS','Unknown'][['win', 'linux', 'android', 'macosx', 'ios', 'unknown'].index(platform)]
        self.content.text = txt

class LogScreen(InfoScreen):
    def on_pre_enter(self):
        self.content.text = 'The last 150 lines:\n\n'
        try:
            with open(logger.handlers[0].baseFilename,'r') as f:
                content = f.readlines()
            self.content.text += ''.join(list(reversed(content))[0:150])
        except:
            self.content.text = "\nAn error occurred when reading the log file '%s'." % ('E5.log')

class AboutScreen(InfoScreen):
    def on_pre_enter(self):
        self.content.text = '\n\nE5 by Shannon P. McPherron\n\nVersion ' + __version__ + ' Alpha\nApple Pie\n\n'
        self.content.text += 'Build using Python 3.6, Kivy 1.10.1 and TinyDB 3.11.1\n\n'
        self.content.text += 'An OldStoneAge.Com Production\n\n' + __date__ 
        self.content.halign = 'center'
        self.content.valign = 'middle'

class CFGScreen(InfoScreen):
    def on_pre_enter(self):
        if e4_cfg.filename:
            try:
                with open(e4_cfg.filename,'r') as f:
                    self.content.text = f.read()
            except:
                self.content.text = "There was an error reading from the CFG file '%s'" % e4_cfg.filename
        else:
            self.content.text = '\nOpen a CFG file before trying to view it.'

class INIScreen(InfoScreen):
    def on_pre_enter(self):
        with open(e4_ini.filename, 'r') as f:
            self.content.text = f.read()

### End Help Screens
#endregion

class E5py(App):

    def __init__(self, **kwargs):
        super(E5py, self).__init__(**kwargs)

        app_path = self.user_data_dir

        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(os.path.join(app_path, 'E5.log'))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        e4_ini.open(os.path.join(app_path, 'E5.ini'))

        if not e4_ini.first_time:

            if e4_ini.get_value('E5','ColorScheme'):
                e5_colors.set_to(e4_ini.get_value('E5','ColorScheme'))
            if e4_ini.get_value('E5','DarkMode').upper() == 'TRUE':
                e5_colors.set_to_darkmode()

            if e4_ini.get_value("E5", "CFG"):
                e4_cfg.open(e4_ini.get_value("E5", "CFG"))
                if e4_cfg.filename:
                    if e4_cfg.get_value('E5','DATABASE'):
                        e4_data.open(e4_cfg.get_value('E5','DATABASE'))
                    else:
                        database = os.path.split(e4_cfg.filename)[1]
                        if "." in database:
                            database = database.split('.')[0]
                        database = database + '.json'
                        e4_data.open(os.path.join(e4_cfg.path, database))
                    if e4_cfg.get_value('E5','TABLE'):    
                        e4_data.table = e4_cfg.get_value('E5','TABLE')
                    else:
                        e4_data.table = '_default'
                    e4_cfg.update_value('E5','DATABASE', e4_data.filename)
                    e4_cfg.update_value('E5','TABLE', e4_data.table)
                    e4_cfg.save()
            e4_ini.update()
            e4_ini.save()
        e5_colors.need_redraw = False    
        e4_ini.update_value('E5','APP_PATH', self.user_data_dir)

    def build(self):

        Window.minimum_width = 450
        Window.minimum_height = 450
        if not e4_ini.get_value("E5","TOP") == '':
            temp = int(e4_ini.get_value("E5","TOP"))
            if temp < 0 : 
                temp = 0
            Window.top = temp
        if not e4_ini.get_value("E5","LEFT") == '':
            temp = int(e4_ini.get_value("E5","LEFT"))
            if temp < 0 : 
                temp = 0
            Window.left = temp
        window_width = None
        window_height = None
        if not e4_ini.get_value("E5","WIDTH") == '':
            window_width = int(e4_ini.get_value("E5","WIDTH"))
            if window_width < 450:
                window_width = 450
        if not e4_ini.get_value("E5","HEIGHT") == '':
            window_height = int(e4_ini.get_value("E5","HEIGHT"))
            if window_height < 450:
                window_height = 450
        if window_width and window_height:
            Window.size = (window_width, window_height)
        self.title = "E5 " + __version__

        logger.info('E5 started, logger initialized, and application built.')

Factory.register('E5', cls=E5py)

# See if the file as given can be found.
# If not, try to find it in the same folder as the CFG file.
# This can happen when a CFG and associated files are copied to a 
# new folder or computer or device.
def locate_file(filename, cfg_path = None):
    if os.path.isfile(filename):
        return(filename)
    if cfg_path:
        p, f = os.path.split(filename)
        if os.path.isfile(os.path.join(cfg_path, f)):
            return(os.path.join(cfg_path, f))
    return('')

if __name__ == '__main__':

    # Initialize a set of classes that are global
    logger = logging.getLogger('E5')
    e4_ini = ini()
    e4_cfg = cfg()
    e4_data = db()
    e5_colors = ColorScheme()

    E5py().run()