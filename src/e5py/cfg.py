from tinydb import where
import logging
from datetime import datetime
from os import path
import ntpath

from plyer import gps
# from plyer import camera

from e5py.lib.misc import locate_file

from e5py.lib.blockdata import blockdata

__DEFAULT_FIELDS__ = []
__DEFAULT_FIELDS_NUMERIC__ = []


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
        return f'Field {self.name} of type {self.inputtype}.'

    def __repr__(self):
        return f'Field {self.name} of type {self.inputtype}.'

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

    def __init__(self, filename=''):
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
        self.errors = []
        self.unique_together = []

    def open(self, filename=''):
        if filename:
            self.filename = filename
        return self.load()

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
        return self.current_record

    def validate_current_record(self):
        return True

    def camera_in_cfg(self):
        for field in self.fields():
            f = self.get(field)
            if f.inputtype == 'CAMERA':
                return True
        return False

    def validate_datafield(self, data_to_insert, data_table):
        # This just validates one field (e.g. when an existing record is edit)
        if data_to_insert and data_table and len(data_to_insert) == 1:
            for field, value in data_to_insert.items():
                f = self.get(field)
                if f.required and str(value).strip() == "":
                    error_message = f'\nThe field {field} is set to unique or required.  Enter a value to save this record.'
                    return error_message
                if f.inputtype == 'NUMERIC':
                    try:
                        float(value)
                    except ValueError:
                        error_message = f'\nThe field {field} requires a valid number.  Correct to save this record.'
                        return error_message
                if f.unique:
                    result = data_table.search(where(field) == value)
                    if result:
                        error_message = f'\nThe field {field} is set to unique and the value {value} already exists for this field in this data table.'
                        return error_message
        return True

    def validate_datarecord(self, data_to_insert, data_table):
        # This validates one record (e.g. one a record is about to be inserted)
        for field in self.fields():
            f = self.get(field)
            if f.required:
                if field in data_to_insert.keys():
                    if data_to_insert[field].strip() == '':
                        error_message = f'\nThe field {field} is set to unique or required.  Enter a value to save this record.'
                        return error_message
                else:
                    error_message = f'\nThe field {field} is set to unique or required.  Enter a value to save this record.'
                    return error_message
            if f.inputtype == 'NUMERIC':
                if field in data_to_insert.keys():
                    try:
                        float(data_to_insert[field])
                    except ValueError:
                        error_message = f'\nThe field {field} requires a valid number.  Correct to save this record.'
                        return error_message
            if f.unique:
                if field in data_to_insert.keys():
                    result = data_table.search(where(field) == data_to_insert[field])
                    if result:
                        error_message = f'\nThe field {field} is set to unique and the value {data_to_insert[field]} already exists for this field in this data table.'
                        return error_message
                else:
                    error_message = f'\nThe field {field} is set to unique and a value was not provided for this field.  Unique fields require a value.'
                    return error_message

        # TODO test to see if it is units, prisms or datums
        # TODO create a unit, prism or datum from the dictionary using *data_to_insert
        # TODO run the validator in whichever
        # TODO and return results
        return True

    def get(self, field_name):
        if not field_name:
            return ''
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

            return f

    def clean_menu(self, menulist):
        # Remove leading and trailing spaces
        menulist = [item.strip() for item in menulist]
        # and remove empty items.
        menulist = list(filter(('').__ne__, menulist))
        return menulist

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

    def get_field_data(self, field_name=None):
        f = field_name
        if f is not None:
            if self.current_field:
                f = self.current_field.name
            else:
                return None
        return self.current_record[f] if f in self.current_record.keys() else None
        # if f in self.current_record.keys():
        #    return(self.current_record[f])
        # else:
        #    return(None)

    def data_is_valid(self, db=None):
        if self.current_field.required and self.current_record[self.current_field.name] == '':
            return '\nError: This field is marked as required.  Please provide a response.'
        if self.current_field.unique:
            if self.current_record[self.current_field.name] == '':
                return '\nError: This field is marked as unique.  Empty entries are not allowed in unique fields.'
            if db is not None:
                for data_row in db:
                    if self.current_field.name in data_row:
                        if data_row[self.current_field.name] == self.current_record[self.current_field.name]:
                            return '\nError: This field is marked as unique and you are trying to add a duplicate entry.'
        if self.current_field.valid:
            if not any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.valid):
                return ("\nError: The entry '%s' does not appear in the list of valid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.validfile))
        if self.current_field.invalid:
            if any(s.upper() == self.current_record[self.current_field.name].upper() for s in self.current_field.invalid):
                return ("\nError: The entry '%s' appears in the list of invalid entries found in '%s'." %
                             (self.current_record[self.current_field.name], self.current_field.invalidfile))
        return True

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
                        gps.configure(on_location=self.gps_location)
                        self.gps = True
                        logger.info('GPS started in cfg.is_valid')
                    except (NotImplementedError, ImportError):
                        self.errors.append('Warning: GPS is not implimented for this platform.  You can still use this CFG but data will not be collected from a GPS.')
                        self.has_warnings = True
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

        return (self.has_errors, self.errors)

    # Pull the conditions appart into a list of objects
    # that make it easier to evaluate.
    def format_conditions(self, conditions):
        formatted_conditions = []
        for condition in conditions:
            condition_parsed = []
            if ' ' in condition:
                condition_parsed.append(condition[:condition.find(' ')])
                condition = condition[condition.find(' '):].strip()
                if condition[:4].upper() == 'NOT ':
                    condition_parsed.append('NOT')
                    condition = condition[4:]
                if condition.upper().endswith(' OR'):
                    condition = condition[:-3]
                    condition_parsed.append(condition.strip())
                    condition_parsed.append('OR')
                if condition.upper().endswith(' AND'):
                    condition = condition[:-4]
                    condition_parsed.append(condition.strip())
                else:
                    condition_parsed.append(condition.strip())
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
        return formatted_conditions

    def gps_location(self):
        logger = logging.getLogger(__name__)
        logger.info('Have location in cfg.is_valid')

    def save(self):
        self.write_blocks()

    def load(self, filename=''):
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
        return self.is_valid()

    def status(self):
        if self.filename:
            txt = '\nThe CFG file is %s\n' % self.filename
            txt += 'and contains %s fields.\n' % len(self.blocks)
        else:
            txt = 'A CFG file has not been opened.\n'
        return txt

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
        return self.current_field

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
        return self.current_field

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
        return self.current_field

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
            return eval(condition_expression)
        else:
            return True

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
                        if row[fieldname] is not None:
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
            return None
        except OSError:
            return '\nCould not write data to %s.' % (filename)

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
                        if row[fieldname] != '':
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
            return None
        except:
            return '\nCould not write data to %s.' % (filename)

    def get_XY(self, row):
        cfg_fields = self.fields()
        if 'X' in cfg_fields and 'Y' in cfg_fields:
            return ((row['X'], row['Y']))
        elif 'LATITUDE' in cfg_fields and 'LONGITUDE' in cfg_fields:
            return ((row['LONGITUDE'], row['LATITUDE']))
        elif self.gps_field(row):
            gps_data = self.gps_to_dict(self.gps_field(row))
            return ((gps_data['Lon'], gps_data['Lat']))
        else:
            return ((0, 0))

    def gps_field(self, row):
        for fieldname in self.fields():
            field = self.get(fieldname)
            if field.inputtype in ['GPS']:
                return row[fieldname]
        return ''

    def gps_to_dict(self, delimited_data):
        dict_data = {}
        for item in delimited_data.split(','):
            dict_item = item.split('=')
            dict_data[dict_item[0].strip()] = dict_item[1].strip()
        return dict_data

    def save_as_numeric_field(self, field_name):
        if field_name in ['HANGLE', 'VANGLE']:
            return False
        if field_name in __DEFAULT_FIELDS_NUMERIC__:
            return True
        return self.get_value(field_name, 'TYPE').upper() == 'NUMERIC'

    def edit_as_numeric_field(self, field_name):
        if field_name in __DEFAULT_FIELDS_NUMERIC__:
            return True
        return self.get_value(field_name, 'TYPE').upper() == 'NUMERIC'
