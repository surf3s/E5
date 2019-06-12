from tinydb import TinyDB, Query, where

class dbs:
    
    db = None
    filename = None
    db_name = 'data'
    table = '_default'
    new_data = False

    def __init__(self, filename = None):
        if filename:
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
        fieldnames = []
        for row in self.db.table(tablename if tablename else self.table):
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

    #def __len__(self):
    #    return(len(self.db) if self.db else 0)

    def names(self, fieldname):
        return([row[fieldname] for row in self.db.table(self.table)])

    def replace(self, data_record):
        pass

    def duplicate(self, data_record):
        pass

    def delete(self, doc_id):
        self.db.table(self.table).remove(doc_ids = [doc_id])
        self.new_data = True

    def delete_all(self):
        self.db.table(self.table).purge()
        self.new_data = True
        
    def get_unitid(self, name):
        unit, idno = name.split('-')
        p = self.db.table(self.table).search( (where('unit') == unit.strip()) & (where('id') == idno.strip()) )
        if p:
            return(p)
        else:
            return(None)

    def last_record(self):
        try:
            last = self.db.table(self.table).all()[-1]
        except:
            last = None
        return(last)
