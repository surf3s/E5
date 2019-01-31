class dbs:
    def status(self):
        txt = '%s %s are defined\n' % (self.db_name, len(self.db))
        return(txt)

    def save(self):
        self.prisms.to_csv(self.filename, index=False)

    def __len__(self):
        return(len(self.db))

    def names(self):
        return([row['name'] for row in self.db])

    def replace(self, data_record):
        ###
        pass

    def duplicate(self, data_record):
        ###
        pass