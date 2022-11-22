from tinydb import TinyDB, where
from typing import Dict
import json
from os import path


class dbs:

    db = None
    filename = None
    db_name = 'data'
    table = '_default'
    new_data = {}  # type: Dict[str, bool]

    def __init__(self, filename = None):
        if filename:
            self.filename = filename

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        try:
            self.db = TinyDB(self.filename)
            self.new_data[self.table] = True
        except FileNotFoundError:
            self.db = None
            self.filename = ''

    def valid_format(self, filename):
        try:
            if path.getsize(filename) == 0:
                return(True)
            with open(filename) as f:
                json.load(f)
            return True
        except ValueError:
            return False
        except FileNotFoundError:
            return True

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
            self.filename = None

    def status(self):
        if self.filename:
            txt = '\nThe JSON data file is %s.\n\n' % self.filename
            if self.db is not None:
                if len(self.db.tables()) > 0:
                    txt += 'There are %s tables in this data file as follows:\n' % len(self.db.tables())
                    total_records = 0
                    for table_name in self.db.tables():
                        total_records += len(self.db.table(table_name))
                        txt += "  A table named '%s' with %s records.\n" % (table_name, len(self.db.table(table_name)))
                    txt += '  In total there are %s records in the data file.\n' % total_records
                    txt += "The current table is '%s'.\n" % self.table
                else:
                    txt += 'There are no tables in this data file.\n'
            else:
                txt += 'The data file is empty or has not been initialized.\n'
        else:
            txt = '\nA data file has not been opened.\n'
        return(txt)

    def fields(self, tablename = ''):
        fieldnames = []
        for row in self.db.table(tablename if tablename else self.table):
            for fieldname in row.keys():
                if fieldname not in fieldnames:
                    fieldnames.append(fieldname)
        return(fieldnames)

    def save(self, data_record):
        self.db.table(self.table).insert(data_record)
        self.new_data[self.table] = True
        return(True)

    # def __len__(self):
    #    return(len(self.db) if self.db else 0)

    def names(self, fieldname):
        return([row[fieldname] for row in self.db.table(self.table)])

    def replace(self, data_record):
        pass

    def duplicate(self, data_record):
        pass

    def delete(self, doc_id):
        self.db.table(self.table).remove(doc_ids = [doc_id])
        self.new_data[self.table] = True

    def delete_all(self, table_name = None):
        if self.db is not None:
            if table_name is None:
                self.db.drop_tables()
            else:
                self.db.table(table_name).truncate()

    def get_unitid(self, name):
        unit, idno = name.split('-')
        p = self.db.table(self.table).search((where('unit') == unit.strip()) & (where('id') == idno.strip()))
        if p:
            return(p)
        else:
            return(None)

    def last_record(self):
        try:
            last = self.db.table(self.table).all()[-1]
        except (IndexError, AttributeError):
            last = None
        return(last)

    def doc_ids(self):
        return([r.doc_id for r in self.db.table(self.table).all()])
