# ## E5 by Shannon McPherron
#
#   This is a beta release.  I am still working on bugs and I am still implementing some features.
#   But it has been used to collect data and seems to work in most cases.  Caution should be exercised.
#   It should be backwards compatible with E4 and Entrer Trois (but there are still some issues).
#   A Windows version is available here, and has been tested on Windows 10.  Older versions of Windows
#   will likely experience issues.  This code also works on Mac and Linux.

# ToDo and Bugs:
#   If TYPE is missing from CFG provide a default of text
#   Fix box on icon
#   Make a loading icon
#   Set icon on program main screen
#   Add better formatted note and GPS fields to edit last record and data grid
#   Find a way to note when you are on the first field
#   Ask whether to add to menulist when new item is entered
#   Somehow show info from last record entered on first screen
#   Look into letting user set CSV file save name
#   Test species menu
#   Handle database and table names in the CFG and program better
#   On unique fields, give a warning but let data entry continue
#   then overwrite previous record
#   Implement 'sort' option on menus
#   Key press on boolean moves to right menu item but adds key press too
#   Add a CFG option to sort menus
#   Don't let it re-write the CFG if there are errors - can trash a cfg that is not an E5/E4 cfg

# Long term
#   Consider putting a dropdown menu into the grid view for sorting and maybe searching
#   Think about whether to allow editing of CFG in the program

# TODO Need to fix ASAP conditions in e4 not comma delimited

__version__ = '1.3.3'
__date__ = 'June, 2022'
__program__ = 'E5'

# region Imports
from kivy import resources
from kivy.clock import Clock, mainthread
from kivy.app import App
from kivy.uix.camera import Camera
from kivy.uix.switch import Switch
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy import __version__ as __kivy_version__

# The explicit mention of this package here
# triggers its inclusions in the pyinstaller spec file.
# It is needed for the filechooser widget.
try:
    import win32timezone
    win32timezone.TimeZoneInfo.local()
except ModuleNotFoundError:
    pass

import sys
from os import path
from datetime import datetime
import ntpath
from random import random
from platform import python_version

from plyer import gps
from plyer import __version__ as __plyer_version__

import logging

# My libraries for this project
from e5py.lib.blockdata import blockdata
from e5py.lib.dbs import dbs
from e5py.lib.e5_widgets import e5_MainScreen, e5_scrollview_menu, e5_scrollview_label, e5_button, e5_label, e5_side_by_side_buttons, e5_LoadDialog, e5_MessageBox, e5_textinput, e5_RecordEditScreen
from e5py.lib.e5_widgets import e5_DatagridScreen, e5_InfoScreen, e5_LogScreen, e5_CFGScreen, e5_INIScreen, e5_SettingsScreen
from e5py.lib.colorscheme import ColorScheme
from e5py.lib.misc import platform_name, restore_window_size_position, locate_file, filename_only

# The database - pure Python
# from tinydb import TinyDB, Query, where
from tinydb import __version__ as __tinydb_version__


# endregion

# region Data Classes

class db(dbs):
    MAX_FIELDS = 300
    datagrid_doc_id = None


class ini(blockdata):

    def __init__(self, filename = ''):
        if filename == '':
            filename = __program__ + '.ini'
        self.filename = filename
        self.incremental_backups = False
        self.backup_interval = 0
        self.first_time = True
        self.debug = False

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        self.blocks = self.read_blocks()
        self.first_time = (self.blocks == [])
        self.is_valid()
        self.incremental_backups = self.get_value(__program__, 'IncrementalBackups').upper() == 'TRUE'
        self.backup_interval = int(self.get_value(__program__, 'BackupInterval'))
        self.debug = self.get_value(__program__, 'Debug').upper() == 'TRUE'

    def is_valid(self):
        for field_option in ['DARKMODE', 'INCREMENTALBACKUPS']:
            if self.get_value(__program__, field_option):
                if self.get_value(__program__, field_option).upper() == 'YES':
                    self.update_value(__program__, field_option, 'TRUE')
            else:
                self.update_value(__program__, field_option, 'FALSE')

        if self.get_value(__program__, "BACKUPINTERVAL"):
            test = False
            try:
                test = int(self.get_value(__program__, "BACKUPINTERVAL"))
                if test < 0:
                    test = 0
                elif test > 200:
                    test = 200
                self.update_value(__program__, 'BACKUPINTERVAL', test)
            except:
                self.update_value(__program__, 'BACKUPINTERVAL', 0)
        else:
            self.update_value(__program__, 'BACKUPINTERVAL', 0)

    def update(self, e5_colors, e5_cfg):
        self.update_value(__program__, 'CFG', e5_cfg.filename)
        self.update_value(__program__, 'ColorScheme', e5_colors.color_scheme)
        self.update_value(__program__, 'DarkMode', 'TRUE' if e5_colors.darkmode else 'FALSE')
        self.update_value(__program__, 'IncrementalBackups', self.incremental_backups)
        self.update_value(__program__, 'BackupInterval', self.backup_interval)
        self.save()

    def save(self):
        self.write_blocks()

    def status(self):
        txt = '\nThe INI file is %s.\n' % self.filename
        return(txt)


class field:
    # Doing dataclasses the Python 3.6 way to maintain compatibity for now
    def __init__(self, name):
        self.name = name
        self.inputtype = ''
        self.prompt = ''
        self.length = 0
        self.menu = ''
        self.menufile = ''
        self.conditions = []
        self.conditions_clean = []
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
        self.link_fields = None     # Compatibility with E5

    def __str__(self):
        return(f'Field {self.name} of type {self.inputtype}.')

    def __repr__(self):
        return(f'Field {self.name} of type {self.inputtype}.')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            equality = self.name == other.name and self.inputtype == other.inputtype and self.prompt == other.prompt and self.length == other.length and self.menu == other.menu
            equality = equality and self.menufile == other.menufile and self.conditions == other.conditions and self.increment == other.increment and self.carry == other.carry
            equality = equality and self.unique == other.unique and self.info == other.info and self.infofile == other.infofile and self.data == other.data and self.key == other.key
            equality = equality and self.required == other.required and self.sorted == other.sorted and self.valid == other.valid and self.validfile == other.validfile
            equality = equality and self.invalid == other.invalid and self.invalidfile == other.invalidfile and self.lookupfile == other.lookupfile and self.lookupdb == other.lookupdb
            equality = equality and self.link_fields == other.link_fields
            return (equality)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class a_condition:
    match_list = []
    match_field = ''
    negate_it = False
    or_it = False


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
        self.gps = False

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
                except ValueError:
                    self.current_record[field_name] = '1'
        return(self.current_record)

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
            f.unique = self.get_value(field_name, "UNIQUE").upper() == 'TRUE'
            f.increment = self.get_value(field_name, "INCREMENT").upper() == 'TRUE'
            f.carry = self.get_value(field_name, "CARRY").upper() == 'TRUE'
            f.required = self.get_value(field_name, "REQUIRED").upper() == 'TRUE'
            f.sorted = self.get_value(field_name, "SORTED").upper() == 'TRUE'

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

            f.conditions_clean = self.get_value(field_name, "__CONDITIONS_CLEAN")

            return(f)

    def clean_menu(self, menulist):
        # Remove leading and trailing spaces
        menulist = [item.strip() for item in menulist]
        # and remove empty items.
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
        self.update_value(field_name, '__CONDITIONS_CLEAN', f.conditions_clean)

    def get_field_data(self, field_name = None):
        f = field_name
        if f is not None:
            if self.current_field:
                f = self.current_field.name
            else:
                return(None)
        return(self.current_record[f] if f in self.current_record.keys() else None)
        # if f in self.current_record.keys():
        #    return(self.current_record[f])
        # else:
        #    return(None)

    def data_is_valid(self, db = None):
        if self.current_field.required and self.current_record[self.current_field.name] == '':
            return('\nError: This field is marked as required.  Please provide a response.')
        if self.current_field.unique:
            if self.current_record[self.current_field.name] == '':
                return('\nError: This field is marked as unique.  Empty entries are not allowed in unique fields.')
            if db is not None:
                for data_row in db:
                    if self.current_field.name in data_row:
                        if data_row[self.current_field.name] == self.current_record[self.current_field.name]:
                            return('\nError: This field is marked as unique and you are trying to add a duplicate entry.')
        if self.current_field.valid:
            if not any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.valid):
                return("\nError: The entry '%s' does not appear in the list of valid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.validfile))
        if self.current_field.invalid:
            if any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.invalid):
                return("\nError: The entry '%s' appears in the list of invalid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.invalidfile))
        return(True)

    def convert_space_to_comma_delimited(self):
        for field in self.fields():
            menulist = self.get_value(field, 'MENU')
            if menulist:
                if ',' not in menulist:
                    menulist = menulist.replace(' ', ',')
                    self.update_value(field, 'MENU', menulist)

    def is_valid(self):
        logger = logging.getLogger(__name__)

        # Check to see that conditions are numbered
        self.has_errors = False
        self.has_warnings = False
        self.errors = []
        if len(self.fields()) == 0:
            self.errors.append('Error: No fields defined in the CFG file.')
            self.has_errors = True
        else:
            if 'E4' in self.names():
                self.rename_block('E4', 'E5')                # Convert E4 file to E5
                self.convert_space_to_comma_delimited()     # E4 allowed space delimited lists.

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
                                    # TODO What is this?
                                    # insert data into a data record
                                    # data_record = {}
                                    # for field in fieldnames:
                                    #    data_record[field] = data[field]
                                    # e5_data.db.insert(e5_cfg.current_record)

                        except:
                            pass
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the lookup file '%s' for the field %s." % (self.get_value(field_name, 'LOOKUP FILE'), field_name))

                for field_option in ['UNIQUE', 'CARRY', 'INCREMENT', 'REQUIRED', 'SORTED']:
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
                if f.inputtype not in ['TEXT', 'NOTE', 'NUMERIC', 'MENU', 'DATETIME', 'BOOLEAN', 'CAMERA', 'GPS', 'INSTRUMENT']:
                    self.errors.append("Error: The value '%s' for the field %s is not a valid TYPE.  Valid TYPES include Text, Note, Numeric, Instrument, Menu, Datetime, Boolean, Camera and GPS." % (f.inputtype, field_name))
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

                if f.inputtype in ['GPS']:
                    logger.info('About to start GPS in cfg.is_valid')
                    try:
                        gps.configure(on_location = self.gps_location)
                        self.gps = True
                        logger.info('GPS started in cfg.is_valid')
                    except (NotImplementedError, ImportError):
                        self.errors.append('Warning: GPS is not implimented for this platform.  You can still use this CFG but data will not be collected from a GPS.')
                        self.had_warnings = True
                        logger.info('GPS Errors in cfg.is_valid')

                if f.inputtype == 'MENU' and (len(f.menu) == 0 and f.menufile == ''):
                    self.errors.append('Error: The field %s is listed as a menu, but no menu list or menu file was provided with a MENU or MENUFILE option.' % field_name)
                    self.has_errors = True

                if f.menufile:
                    if locate_file(f.menufile, self.path):
                        f.menufile = locate_file(f.menufile, self.path)
                    else:
                        self.has_warnings = True
                        self.errors.append("Warning: Could not locate the menu file '%s' for the field %s." % (f.menufile, field_name))

                if any((c in set(r' !@#$%^&*()?/\{}<.,.|+=~`')) for c in field_name):
                    self.errors.append('Warning: The field %s has non-standard characters in it.  E5 will attempt to work with it, but it is highly recommended that you rename it as it will likely cause problems elsewhere.' % field_name)
                    self.has_warnings = True

                if len(f.conditions) > 0:
                    conditions = self.format_conditions(f.conditions)
                    n = 0
                    for condition in conditions:
                        n += 1
                        if condition.match_field == '' or not condition.match_list:
                            self.errors.append('Error: Condition number %s for the field %s is not correctly formatted.  A condition requires a target field and a matching value.' % (n, field_name))
                            self.has_errors = True
                        else:
                            if condition.match_field not in prior_fieldnames:
                                self.errors.append('Error: Condition number %s for the field %s references field %s which has not been defined prior to this.' % (n, field_name, condition.match_field))
                                self.has_errors = True
                            else:
                                condition_field = self.get(condition.match_field)
                                if condition_field.inputtype == 'MENU':
                                    condition_matches = list(filter(("''").__ne__, condition.match_list))
                                    condition_matches = list(filter(('""').__ne__, condition_matches))
                                    for condition_match in condition_matches:
                                        if condition_match.upper() not in [x.upper() for x in condition_field.menu]:
                                            self.errors.append('Warning: Condition number %s for the field %s tries to match the value "%s" to the menulist in field %s, but field %s does not contain this value.' % (n, field_name, condition_match, condition.match_field, condition.match_field))
                                            self.has_warnings = True
                                f.conditions_clean = conditions
                self.put(field_name, f)
                prior_fieldnames.append(field_name.upper())

        return(self.has_errors)

    # Pull the conditions appart into a list of objects
    # that make it easier to evaluate.
    def format_conditions(self, conditions):
        formatted_conditions = []
        for condition in conditions:
            condition_parsed = condition.split(' ')
            condition_parsed = self.clean_menu(condition_parsed)
            formatted_condition = a_condition()
            if len(condition_parsed) > 1:
                formatted_condition.match_field = condition_parsed[0].upper()
                if condition_parsed[1].upper() == 'NOT':
                    formatted_condition.negate_it = True
                    if len(condition_parsed) > 2:
                        formatted_condition.match_list = condition_parsed[2].upper().split(',')
                else:
                    formatted_condition.match_list = condition_parsed[1].upper().split(',')
                if formatted_condition.negate_it and len(condition_parsed) == 4:
                    if condition_parsed[3].upper() == 'OR':
                        formatted_condition.or_it = True
                elif not formatted_condition.negate_it and len(condition_parsed) == 3:
                    if condition_parsed[2].upper() == 'OR':
                        formatted_condition.or_it = True
                if formatted_condition.match_list:
                    formatted_condition.match_list = self.clean_menu(formatted_condition.match_list)
            formatted_conditions.append(formatted_condition)
        return(formatted_conditions)

    def gps_location(self):
        logger = logging.getLogger(__name__)
        logger.info('Have location in cfg.is_valid')

    def save(self):
        self.write_blocks()

    def load(self, filename = ''):
        if filename:
            self.filename = filename
        self.path = ntpath.split(self.filename)[0]

        self.blocks = []
        if path.isfile(self.filename):
            self.blocks = self.read_blocks()
        else:
            self.filename = ''
        self.BOF = True
        self.EOF = False if len(self.blocks) > 0 else True
        self.current_field = None
        self.is_valid()

    def status(self):
        if self.filename:
            txt = '\nThe CFG file is %s\n' % self.filename
            txt += 'and contains %s fields.\n' % len(self.blocks)
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
        if len(self.fields()) > 0 and not self.has_errors:
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
        if len(self.current_field.conditions_clean) > 0:
            condition_expression = ''
            for condition in self.current_field.conditions_clean:
                if condition.match_field in self.current_record.keys():
                    if self.current_record[condition.match_field].upper() in condition.match_list:
                        condition_value = 'True'
                    else:
                        condition_value = 'False'
                else:
                    condition_value = 'False'
                if condition.negate_it:
                    condition_value = 'False' if condition_value == 'True' else 'True'
                condition_expression += condition_value + ' and ' if not condition.or_it else condition_value + '  or '
            condition_expression = condition_expression[:-4]
            return(eval(condition_expression))
        else:
            return(True)

    def write_csvs(self, filename, table):
        try:
            cfg_fields = self.fields()
            f = open(filename, 'w')
            csv_row = ''
            for fieldname in cfg_fields:
                csv_row += ',"%s"' % fieldname if csv_row else '"%s"' % fieldname
            f.write(csv_row + '\n')
            for row in table:
                csv_row = ''
                for fieldname in cfg_fields:
                    if fieldname in row.keys():
                        if self.get(fieldname).inputtype in ['NUMERIC', 'INSTRUMENT']:
                            csv_row += ',%s' % row[fieldname] if csv_row else "%s" % row[fieldname]
                        else:
                            csv_row += ',"%s"' % row[fieldname] if csv_row else '"%s"' % row[fieldname]
                    else:
                        if self.get(fieldname).inputtype in ['NUMERIC', 'INSTRUMENT']:
                            if csv_row:
                                csv_row = csv_row + ','     # Not sure this works if there is an entirely empty row of numeric values
                        else:
                            if csv_row:
                                csv_row = csv_row + ',""'
                            else:
                                csv_row = '""'
                f.write(csv_row + '\n')
            f.close()
            return(None)
        except:
            return('\nCould not write data to %s.' % (filename))

    def write_geojson(self, filename, table):
        try:
            cfg_fields = self.fields()
            basename = path.basename(filename)
            basename = path.splitext(basename)[0]
            f = open(filename, 'w')
            geojson_header = '{\n'
            geojson_header += '"type": "FeatureCollection",\n'
            geojson_header += '"name": "%s",\n' % basename
            geojson_header += '"features": [\n'
            f.write(geojson_header)
            row_comma = ''
            for row in table:
                geojson_row = row_comma + '{ "type": "Feature", "properties": {'
                comma = ' '
                for fieldname in cfg_fields:
                    if fieldname in row.keys():
                        geojson_row += comma + '"%s": ' % fieldname
                        if self.get(fieldname).inputtype in ['NUMERIC', 'INSTRUMENT']:
                            geojson_row += '%s' % row[fieldname]
                        else:
                            geojson_row += '"%s"' % row[fieldname]
                    comma = ', '
                geojson_row += ' },\n'
                geojson_row += '"geometry": { "type": "Point", "coordinates": [ '
                geojson_row += '%s , %s' % self.get_XY(row)
                geojson_row += '] } }'
                f.write(geojson_row)
                row_comma = ',\n'
            f.write('\n]\n}')
            f.close()
            return(None)
        except:
            return('\nCould not write data to %s.' % (filename))

    def get_XY(self, row):
        cfg_fields = self.fields()
        if 'X' in cfg_fields and 'Y' in cfg_fields:
            return((row['X'], row['Y']))
        elif 'LATITUDE' in cfg_fields and 'LONGITUDE' in cfg_fields:
            return((row['LONGITUDE'], row['LATITUDE']))
        elif self.gps_field(row):
            gps_data = self.gps_to_dict(self.gps_field(row))
            return((gps_data['Lon'], gps_data['Lat']))
        else:
            return((0, 0))

    def gps_field(self, row):
        for fieldname in self.fields():
            field = self.get(fieldname)
            if field.inputtype in ['GPS']:
                return(row[fieldname])
        return('')

    def gps_to_dict(self, delimited_data):
        dict_data = {}
        for item in delimited_data.split(','):
            dict_item = item.split('=')
            dict_data[dict_item[0].strip()] = dict_item[1].strip()
        return(dict_data)

# endregion


class MainScreen(e5_MainScreen):

    gps_location = StringProperty(None)
    gps_location_widget = ObjectProperty(None)
    gps_status = StringProperty('Click Start to get GPS location updates')

    def __init__(self, user_data_dir, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        self.user_data_dir = user_data_dir
        self.colors = ColorScheme()
        self.ini = ini()
        self.cfg = cfg()
        self.data = db()

        self.setup_program()

        if platform_name() == 'Android':
            self.colors.button_font_size = "14sp"

        # Used for KV file settings
        self.text_color = self.colors.text_color
        self.button_color = self.colors.button_color
        self.button_background = self.colors.button_background

        self.fpath = ''

        if self.cfg.gps:
            logger = logging.getLogger(__name__)
            try:
                logger.info('Configuring GPS in mainscreen')
                gps.configure(on_location = self.on_gps_location,
                              on_status = self.on_gps_status)
            except (NotImplementedError, ModuleNotFoundError):
                logger.info('Error configuring GPS in mainscreen')
                self.gps_status = 'GPS is not implemented for your platform'

        self.mainscreen = BoxLayout(orientation = 'vertical',
                                    size_hint_y = .9,
                                    size_hint_x = .8,
                                    pos_hint={'center_x': .5},
                                    padding = 20,
                                    spacing = 20)
        self.add_widget(self.mainscreen)
        self.build_mainscreen()
        self.add_screens()
        restore_window_size_position(__program__, self.ini)
        self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(path.join(self.user_data_dir, __program__ + '.log'))
        fh.setLevel(logging.INFO)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info(__program__ + ' started, logger initialized, and application built.')

    def update_title(self):
        for widget in self.walk():
            if hasattr(widget, 'action_previous'):
                widget.action_previous.title = 'E5'
                if self.cfg is not None:
                    if self.cfg.filename:
                        widget.action_previous.title = filename_only(self.cfg.filename)

    def add_screens(self):
        sm.add_widget(StatusScreen(name = 'StatusScreen',
                                    colors = self.colors,
                                    e5_cfg = self.cfg,
                                    e5_ini = self.ini,
                                    e5_data = self.data))
        sm.add_widget(e5_LogScreen(name = 'LogScreen',
                                    colors = self.colors,
                                    logger = logging.getLogger(__name__)))
        sm.add_widget(e5_CFGScreen(name = 'CFGScreen',
                                    colors = self.colors,
                                    cfg = self.cfg))
        sm.add_widget(e5_INIScreen(name = 'INIScreen',
                                    colors = self.colors,
                                    ini = self.ini))
        sm.add_widget(AboutScreen(name = 'AboutScreen',
                                        colors = self.colors))
        sm.add_widget(EditLastRecordScreen(name = 'EditLastRecordScreen',
                                            data = self.data,
                                            doc_id = None,
                                            e5_cfg = self.cfg,
                                            colors = self.colors))
        sm.add_widget(EditPointsScreen(name = 'EditPointsScreen',
                                        colors = self.colors,
                                        main_data = self.data,
                                        main_tablename = self.data.table if self.data else '_default',
                                        main_cfg = self.cfg))
        sm.add_widget(EditCFGScreen(name = 'EditCFGScreen',
                                    colors = self.colors,
                                    e5_cfg = self.cfg))
        sm.add_widget(e5_SettingsScreen(name = 'E5SettingsScreen',
                                        colors = self.colors,
                                        ini = self.ini,
                                        cfg = self.cfg))

    @mainthread
    def on_gps_location(self, **kwargs):
        results, linefeed = '', ''
        for k, v in kwargs.items():
            results += linefeed + k.capitalize() + ' = '
            results += '%s' % (v if k != 'accuracy' else round(float(v), 3))
            linefeed = '\n'
        self.gps_location_widget.text = results

    @mainthread
    def on_gps_status(self, stype, status):
        logger = logging.getLogger(__name__)
        logger.info('GPS status updated.')
        self.gps_status = 'type={}\n{}'.format(stype, status)
        status = self.get_widget_by_id('gps_status')
        if status:
            status.text = self.gps_status

    def on_enter(self):
        self.build_mainscreen()

    def reset_screens(self):
        for screen in sm.screens[:]:
            if screen.name != 'MainScreen':
                sm.remove_widget(screen)
        self.add_screens()

    def build_mainscreen(self):

        self.mainscreen.clear_widgets()
        self.scroll_menu = None

        if self.cfg.filename:
            self.cfg.start()
            if not self.cfg.EOF or not self.cfg.BOF:
                self.data_entry()
                if self.cfg.has_warnings:
                    self.event = Clock.schedule_once(self.show_popup_message, 1)
            else:
                self.cfg_menu()
                self.event = Clock.schedule_once(self.show_popup_message, 1)

        else:
            if self.ini.first_time:
                self.ini.first_time = False
                self.event = Clock.schedule_once(self.show_popup_message, 1)
            self.cfg_menu()
        self.update_title()

    def cfg_menu(self):

        self.cfg_files = self.get_files(self.get_path(), 'cfg')

        if self.cfg_files:

            self.cfg_file_selected = self.cfg_files[0]

            lb = Label(text = 'Begin data entry with one of these CFG files or use File Open',
                        color = self.colors.text_color,
                        size_hint_y = .1)
            self.mainscreen.add_widget(lb)

            self.mainscreen.add_widget(e5_scrollview_menu(self.cfg_files,
                                                            self.cfg_file_selected,
                                                            widget_id = 'cfg',
                                                            call_back = [self.cfg_selected],
                                                            colors = self.colors))
            self.scroll_menu = self.get_widget_by_id('cfg_scroll')
            self.scroll_menu.make_scroll_menu_item_visible()
            self.widget_with_focus = self.scroll_menu

        else:
            label_text = '\nBefore data entry can begin, you need to have a CFG file.\n\nThe current folder %s contains none.  Either use File Open to switch a folder that contains CFG files or create a new one.' % self.get_path()
            lb = e5_scrollview_label(text = label_text, id = 'label', colors = self.colors)
            lb.halign = 'center'
            self.mainscreen.add_widget(lb)
            self.widget_with_focus = self.mainscreen

    def cfg_selected(self, value):
        if value.text:
            self.load_cfg(path.join(self.get_path(), value.text))

    def load_cfg(self, cfgfile_name):
        self.data.close()
        self.cfg.load(cfgfile_name)
        if self.cfg.filename:
            self.open_db()
            self.set_new_data_to_true()
        self.ini.update(self.colors, self.cfg)
        self.build_mainscreen()
        self.reset_screens()

    def set_new_data_to_true(self, table_name = None):
        if table_name is None:
            self.data.new_data[self.data.table] = True
        else:
            self.data.new_data[table_name] = True

    def data_entry(self):

        if platform_name() == 'Android':
            size_hints = {'field_label': .13,
                            'field_input': .07 if not self.cfg.current_field.inputtype == 'NOTE' else .07 * 5,
                            'scroll_content': .6 if not self.cfg.current_field.inputtype == 'NOTE' else .6 - .07 * 4,
                            'prev_next_buttons': .2}
        else:
            size_hints = {'field_label': .13,
                            'field_input': .07 if not self.cfg.current_field.inputtype == 'NOTE' else .07 * 5,
                            'scroll_content': .6 if not self.cfg.current_field.inputtype == 'NOTE' else .6 - .07 * 4,
                            'prev_next_buttons': .2}

        # mainscreen = self.get_widget_by_id('mainscreen')
        # inputbox.bind(minimum_height = inputbox.setter('height'))

        label = e5_label(text = self.cfg.current_field.prompt,
                            size_hint = (1, size_hints['field_label']),
                            color = self.colors.text_color,
                            id = 'field_prompt',
                            halign = 'center')
        if self.colors:
            if self.colors.text_font_size:
                label.font_size = self.colors.text_font_size
        self.mainscreen.add_widget(label)
        label.bind(texture_size = label.setter('size'))
        label.bind(size_hint_min_x = label.setter('width'))

        self.field_data = e5_textinput(text = self.cfg.current_record[self.cfg.current_field.name] if self.cfg.current_field.name in self.cfg.current_record.keys() else '',
                                        size_hint = (1, size_hints['field_input']),
                                        multiline = (self.cfg.current_field.inputtype == 'NOTE'),
                                        input_filter = None if self.cfg.current_field.inputtype not in ['NUMERIC', 'INSTRUMENT'] else 'float',
                                        write_tab = False,
                                        id = 'field_data')
        if self.colors:
            if self.colors.text_font_size:
                self.field_data.font_size = self.colors.text_font_size
        self.mainscreen.add_widget(self.field_data)
        self.field_data.bind(text = self.textbox_changed)
        self.widget_with_focus = self.field_data
        self.field_data.focus = True

        self.scroll_menu = None
        self.scroll_content = BoxLayout(orientation = 'horizontal',
                                        size_hint = (1, size_hints['scroll_content']),
                                        spacing = 20)
        self.add_scroll_content(self.scroll_content, self.field_data.text)

        if self.cfg.current_field.inputtype in ['BOOLEAN', 'MENU']:
            self.scroll_menu_setup()

        buttons = GridLayout(cols = 2, size_hint = (1, size_hints['prev_next_buttons']), spacing = 20)

        buttons.add_widget(e5_button('Back', id = 'back', selected = True,
                                     call_back = self.go_back, colors = self.colors))

        buttons.add_widget(e5_button('Next', id = 'next', selected = True,
                                     call_back = self.go_next, colors = self.colors))

        if platform_name() == 'Android':
            self.mainscreen.add_widget(buttons)
            self.mainscreen.add_widget(self.scroll_content)
        else:
            self.mainscreen.add_widget(self.scroll_content)
            self.mainscreen.add_widget(buttons)

        self.field_data.select_all()
        self.event = Clock.schedule_once(self.field_data_set_focus, .2)

    def field_data_set_focus(self, dt):
        self.field_data.focus = True
        self.field_data.select_all()

    def scroll_menu_setup(self):
        if self.scroll_menu is not None:
            self.scroll_menu.make_scroll_menu_item_visible()
        self.widget_with_focus = self.scroll_menu if self.scroll_menu else self

    def textbox_changed(self, instance, value):
        if self.cfg.current_field.inputtype in ['BOOLEAN', 'MENU']:
            self.add_scroll_content(self.scroll_content, value)
            self.scroll_menu_setup()

    # def _keyboard_closed(self):
    #    self._keyboard.unbind(on_key_down = self._on_keyboard_down)
    #    self._keyboard = None

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        text_str = args[3]
        # print('INFO: The key %s has been pressed %s' % (ascii_code, text_str))
        if not self.popup_open:
            if ascii_code in [8, 127]:
                return False
            if ascii_code == 9:
                if self.widget_with_focus.id == 'menu_scroll':
                    self.widget_with_focus = self.field_data
                    self.widget_with_focus.focus = True
                elif self.widget_with_focus.id == 'field_data' and self.cfg.current_field.inputtype in ['MENU', 'BOOLEAN']:
                    self.widget_with_focus.focus = False
                    self.widget_with_focus = self.get_widget_by_id('menu_scroll')
                return False
            if ascii_code == 27:
                if self.cfg.filename:
                    self.go_back(None)
            if ascii_code == 13:
                if self.cfg.filename:
                    self.go_next(None)
                elif self.cfg_files:
                    self.cfg_selected(self.scroll_menu.scroll_menu_get_selected())
            if ascii_code == 51:
                return True
            if ascii_code in [273, 274, 275, 276, 278, 279] and self.scroll_menu:
                self.scroll_menu.move_scroll_menu_item(ascii_code)
                return False
            if ascii_code in [276, 275, 278, 279] and not self.scroll_menu:
                return False
            # if text_str:
            #    if text_str.upper() in ascii_uppercase:
            #        self.add_scroll_content(self.get_widget_by_id('scroll_content'),
            #                                self.get_widget_by_id('field_data').text + text_str)
            #        return True
        else:
            if ascii_code == 13:
                self.close_popup(None)
                self.widget_with_focus.focus = True
                return False
            elif ascii_code in [275, 276]:
                return(False)
        return True  # return True to accept the key. Otherwise, it will be used by the system.

    def copy_from_menu_to_textbox(self):
        if self.cfg.current_field.inputtype in ['MENU', 'BOOLEAN']:
            textbox = self.field_data.text
            menubox = self.scroll_menu.scroll_menu_get_selected().text if self.scroll_menu.scroll_menu_get_selected() else ''
            if textbox == '' and not menubox == '':
                self.field_data.text = menubox
            elif not textbox == '' and not menubox == '':
                if not textbox.upper() == menubox.upper():
                    if textbox.upper() == menubox.upper()[0:len(textbox)]:
                        self.field_data.text = menubox

    def copy_from_gps_to_textbox(self):
        if self.cfg.current_field.inputtype in ['GPS']:
            textbox = self.field_data
            textbox.text = self.gps_location_widget.text.replace('\n', ',')

    def add_scroll_content(self, content_area, menu_filter = ''):

        content_area.clear_widgets()

        info_exists = self.cfg.current_field.info or self.cfg.current_field.infofile
        menu_exists = self.cfg.current_field.inputtype == 'BOOLEAN' or (not self.cfg.current_field.menu == [])
        camera_exists = self.cfg.current_field.inputtype == 'CAMERA'
        gps_exists = self.cfg.current_field.inputtype == 'GPS'

        if menu_exists or info_exists or camera_exists or gps_exists:

            if camera_exists:
                bx = BoxLayout(orientation = 'vertical')
                bx.add_widget(Camera(play = True, size_hint_y = .8,
                                         resolution = (320, 160)))
                bx.add_widget(e5_button(text = "Snap",
                                        id = "snap", selected = True,
                                        colors = self.colors,
                                        callback = self.take_photo))
                content_area.add_widget(bx)

            if gps_exists:
                bx = BoxLayout(orientation = 'vertical')
                if self.cfg.gps:
                    gps_label_text = 'Press start to begin.'
                elif self.ini.debug:
                    gps_label_text = 'Press start to begin [Debug mode].'
                else:
                    gps_label_text = 'No GPS available.'
                gps_label = e5_label(text = gps_label_text,
                                        id = 'gps_location')
                bx.add_widget(gps_label)
                bx.add_widget(e5_side_by_side_buttons(text = ['Start', 'Stop', 'Clear'],
                                                        id = [''] * 3,
                                                        selected = [False] * 3,
                                                        call_back = [self.gps_manage] * 3,
                                                        colors = self.colors))
                self.gps_location_widget = gps_label
                content_area.add_widget(bx)

            if menu_exists:
                menu_list = ['True', 'False'] if self.cfg.current_field.inputtype == 'BOOLEAN' else self.cfg.current_field.menu

                if menu_filter:
                    menu_list = [menu for menu in menu_list if menu.upper()[0:len(menu_filter)] == menu_filter.upper()]

                selected_menu = self.cfg.get_field_data('')
                if not selected_menu and menu_list:
                    selected_menu = menu_list[0]

                if platform_name() == 'Android':
                    ncols = 1 if info_exists else 2
                else:
                    ncols = int(content_area.width / 400) if info_exists else int(content_area.width / 200)
                    ncols = max(ncols, 1)

                self.scroll_menu = e5_scrollview_menu(menu_list,
                                                           selected_menu,
                                                           widget_id = 'menu',
                                                           call_back = [self.menu_selection],
                                                           ncols = ncols,
                                                           colors = self.colors)
                content_area.add_widget(self.scroll_menu)

            if info_exists:
                content_area.add_widget(e5_scrollview_label(self.get_info(), colors = self.colors))

    def gps_manage(self, value):
        logger = logging.getLogger(__name__)
        if self.cfg.gps:
            if value.text == 'Start':
                logger.info('GPS started')
                gps.start()
                self.gps_location_widget.text = "Waiting for GPS."
            elif value.text == 'Stop':
                logger.info('GPS stopped')
                gps.stop()
                self.gps_location_widget.text = "GPS stopped."
            elif value.text == 'Clear':
                self.gps_location_widget.text = ''
        elif self.ini.debug:
            if value.text == 'Start':
                self.gps_location_widget.text = self.gps_random_point()
            elif value.text == 'Stop':
                pass
            elif value.text == 'Clear':
                self.gps_location_widget.text = ''

    def gps_random_point(self):
        point = "Bearing = %s\n" % round(random() * 360, 2)
        point += "Altitude = %s\n" % round(random() * 10, 3)
        point += "Lon = %s\n" % round(12.3912015 + random() / 10, 3)
        point += "Lat = %s\n" % round(51.3220704 + random() / 10, 3)
        point += "Speed = %s\n" % round(random() * 10, 3)
        point += "Accuracy = %s" % round(random() * 5 + 3, 3)
        return(point)

    def take_photo(self):
        camera = self.get_widget_by_id('camera')
        if camera.play:
            try:
                camera.export_to_png("IMG_%s.png" % self.time_stamp())
            except:
                pass
                # print('camera file save error')
                # TODO Replace this with a popup message
        camera.play = not camera.play

    def on_pre_enter(self):
        Window.bind(on_key_down = self._on_keyboard_down)
        if self.colors.need_redraw:
            pass

    def show_load_cfg(self):
        if self.cfg.filename and self.cfg.path:
            start_path = self.cfg.path
        else:
            start_path = self.ini.get_value(__program__, 'APP_PATH')
        content = e5_LoadDialog(load = self.load,
                                cancel = self.dismiss_popup,
                                start_path = start_path,
                                button_color = self.colors.button_color,
                                button_background = self.colors.button_background)
        self.popup = Popup(title = "Load CFG file", content = content,
                            size_hint = (0.9, 0.9))
        self.popup.open()

    def load(self, path, filename):
        self.dismiss_popup()
        self.load_cfg(filename[0])

    def update_mainscreen(self):
        self.mainscreen.clear_widgets()
        self.data_entry()

    def save_field(self):
        widget = self.field_data
        self.cfg.current_record[self.cfg.current_field.name] = widget.text
        widget.text = ''

    def go_back(self, *args):
        if self.cfg.filename:
            self.save_field()
            self.cfg.previous()
            if self.cfg.BOF:
                self.cfg.filename = ''
                self.build_mainscreen()
            else:
                self.update_mainscreen()

    def go_next(self, *args):
        self.copy_from_menu_to_textbox()
        self.copy_from_gps_to_textbox()
        self.save_field()
        valid_data = self.cfg.data_is_valid(db = self.data.db)
        if valid_data is True:
            self.cfg.next()
            if self.cfg.EOF:
                self.save_record()
                self.cfg.start()
            self.update_mainscreen()
        else:
            widget = self.field_data
            widget.text = self.cfg.current_record[self.cfg.current_field.name]
            widget.focus = True
            self.popup = e5_MessageBox(self.cfg.current_field.name, valid_data, call_back = self.close_popup, colors = self.colors)
            self.popup.open()
            self.popup_open = True

    def menu_selection(self, value):
        self.field_data.text = value.text
        self.go_next(value)

    def exit_program(self):
        self.save_window_location()
        App.get_running_app().stop()

# region Edit Screens


class EditLastRecordScreen(e5_RecordEditScreen):
    pass


class EditPointsScreen(e5_DatagridScreen):
    pass


class EditCFGScreen(Screen):

    def __init__(self, e5_cfg = None, e5_ini = None, colors = None, **kwargs):
        super(EditCFGScreen, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()
        self.e5_ini = e5_ini
        self.e5_cfg = e5_cfg

    def on_pre_enter(self):
        # super(Screen, self).__init__(**kwargs)
        self.clear_widgets()

        layout = GridLayout(cols = 1,
                            # id = 'fields',
                            size_hint_y = None
                            )
        layout.bind(minimum_height=layout.setter('height'))

        for field_name in self.e5_cfg.fields():
            f = self.e5_cfg.get(field_name)
            bx = GridLayout(cols = 1, size_hint_y = None)
            bx.add_widget(e5_label("[" + f.name + "]", colors = self.colors))
            layout.add_widget(bx)

            bx = GridLayout(cols = 2, size_hint_y = None)
            bx.add_widget(e5_label("Prompt", colors = self.colors))
            bx.add_widget(TextInput(text = f.prompt,
                                        multiline = False, size_hint_y = None))
            layout.add_widget(bx)

            bx = GridLayout(cols = 2, size_hint_y = None)
            bx.add_widget(e5_label("Type", colors = self.colors))
            bx.add_widget(Spinner(text="Text", values=("Text", "Numeric", "Menu"),
                                        size_hint=(None, None),
                                        pos_hint={'center_x': .5, 'center_y': .5},
                                        color = self.colors.optionbutton_color,
                                        background_color = self.colors.optionbutton_background,
                                        background_normal = ''))
            # self.StationMenu.size_hint  = (0.3, 0.2)
            layout.add_widget(bx)

            bx = GridLayout(cols = 6, size_hint_y = None)

            bx.add_widget(e5_label("Carry", colors = self.colors))
            bx.add_widget(Switch(active = f.carry))

            bx.add_widget(e5_label("Unique", colors = self.colors))
            bx.add_widget(Switch(active = f.unique))

            bx.add_widget(e5_label("Increment", colors = self.colors))
            bx.add_widget(Switch(active = f.increment))

            layout.add_widget(bx)

            if f.inputtype == 'MENU':
                bx = GridLayout(cols = 1, size_hint_y = None)
                button1 = e5_button(text = 'Edit Menu', size_hint_y = None,
                                    color = self.colors.optionbutton_color,
                                    background_color = self.colors.optionbutton_background,
                                    background_normal = '',
                                    id = f.name)
                bx.add_widget(button1)
                button1.bind(on_press = self.show_menu)
                layout.add_widget(bx)

        root = ScrollView(size_hint=(1, .8))
        root.add_widget(layout)
        self.add_widget(root)

        buttons = GridLayout(cols = 2, spacing = 10, size_hint_y = None)

        button2 = e5_button(text = 'Back', size_hint_y = None,
                            color = self.colors.button_color,
                            background_color = self.colors.button_background,
                            background_normal = '')
        buttons.add_widget(button2)
        button2.bind(on_press = self.go_back)

        button3 = e5_button(text = 'Save Changes', size_hint_y = None,
                            color = self.colors.button_color,
                            background_color = self.colors.button_background,
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


# ## End Edit Screens
# endregion

# region Help Screens
# ## Help Screens

class StatusScreen(e5_InfoScreen):

    def __init__(self, e5_data = None, e5_ini = None, e5_cfg = None, **kwargs):
        super(StatusScreen, self).__init__(**kwargs)
        self.e5_data = e5_data
        self.e5_ini = e5_ini
        self.e5_cfg = e5_cfg

    def on_pre_enter(self):
        txt = self.e5_data.status() if self.e5_data else 'A data file has not been initialized or opened.\n\n'
        txt += self.e5_cfg.status() if self.e5_cfg else 'A CFG is not open.\n\n'
        txt += self.e5_ini.status() if self.e5_ini else 'An INI file is not available.\n\n'
        txt += '\nThe default user path is %s.\n' % self.e5_ini.get_value(__program__, "APP_PATH")
        txt += '\nThe operating system is %s.\n' % platform_name()
        txt += '\nPython buid is %s.\n' % (python_version())
        txt += '\nLibraries installed include Kivy %s, TinyDB %s and Plyer %s.\n' % (__kivy_version__, __tinydb_version__, __plyer_version__)
        txt += '\nE5 was tested and distributed on Python 3.6, Kivy 1.10.1, TinyDB 3.11.1 and Plyer 1.4.0.\n'
        if self.e5_ini.debug:
            txt += '\nProgram is running in debug mode.\n'
        self.content.text = txt
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color


class AboutScreen(e5_InfoScreen):
    def on_pre_enter(self):
        self.content.text = '\n\nE5 by Shannon P. McPherron\n\nVersion ' + __version__ + ' Beta\nBlueberry Pie\n\n'
        self.content.text += 'Built on Python 3.8, Kivy 2.0.0, TinyDB 4.4.0 and Plyer 2.0.0\n\n'
        self.content.text += 'An OldStoneAge.Com Production\n\n' + __date__
        self.content.text += '\n\nSpecial thanks to Marcel Weiss (debugging)\nand Jonathan Reeves (platform testing).\n\n'
        self.content.halign = 'center'
        self.content.valign = 'middle'
        self.content.color = self.colors.text_color
        self.back_button.background_color = self.colors.button_background
        self.back_button.color = self.colors.button_color

# ## End Help Screens
# endregion


sm = ScreenManager()


class E5App(App):

    def __init__(self, **kwargs):
        super(E5App, self).__init__(**kwargs)

        self.app_path = self.user_data_dir

    def build(self):
        sm.add_widget(MainScreen(user_data_dir = self.user_data_dir, name = 'MainScreen'))
        sm.current = 'MainScreen'
        self.title = __program__ + " " + __version__
        return(sm)


Factory.register(__program__, cls=E5App)


# From https://stackoverflow.com/questions/35952595/kivy-compiling-to-a-single-executable

def resourcePath():
    '''Returns path containing content - either locally or in pyinstaller tmp file'''
    if hasattr(sys, '_MEIPASS'):
        return path.join(sys._MEIPASS)

    return path.join(path.abspath("."))


if __name__ == '__main__':
    # This line goes with the function above
    resources.resource_add_path(resourcePath())  # add this line
    E5App().run()
