from tinydb import TinyDB, Query, where

class dbs:
    
    db = None
    filename = None
    db_name = 'data'
    table = '_default'
    new_data = False

    def __init__(self, filename = ''):
        if filename:
            self.filename = filename
        self.filename = filename

    def open(self, filename = ''):
        if filename:
            self.filename = filename
        try:
            self.db = TinyDB(self.filename)
            self.new_data = True
        except:
            self.db = None
            self.filename = ''

    def status(self):
        if self.filename:
            txt = '\nThe JSON data file is %s.\n\n' % self.filename
            if self.db:
                if len(self.db.tables()) > 0:
                    txt += 'There are %s tables in this data file as follows:\n' % len(self.db.tables())
                    total_records = 0
                    for table_name in self.db.tables():
                        total_records += len(self.db.table(table_name))
                        txt += "  A table named '%s' with %s records.\n" % (table_name, len(self.db.table(table_name)))
                    txt += '\nIn total there are %s records in the data file.\n' % total_records
                    txt += "The current table is '%s'.\n" % self.table
                else:
                    txt += 'There are no tables in this data file.\n'
            else:
                txt += 'The data file is empty or has not been initialized.\n'
        else:
            txt = '\nA data file has not been opened.\n'
        return(txt)

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

    def save(self, data_record):
        try:
            self.db.table(self.table).insert(data_record)
            return(True)
        except:
            return(False)

    def __len__(self):
        return(len(self.db) if self.db else 0)

    def names(self):
        return([row['name'] for row in self.db])

    def replace(self, data_record):
        pass

    def duplicate(self, data_record):
        pass

    def delete_all(self):
        self.db.purge()
