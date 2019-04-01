import logging
import os

class blockdata:

    filename = ''
    blocks = []
    
    def update_value(self, blockname, varname, vardata, append = False):
        block_exists = False
        for block in self.blocks:
            if block['BLOCKNAME']==blockname.upper():
                block_exists = True
                if (varname.upper() in block.keys()) and append:
                    block[varname.upper()] = [block[varname.upper()] , vardata]
                else:
                    block[varname.upper()] = vardata 
                return(self.write_blocks())
        if not block_exists:
            temp = {}
            temp['BLOCKNAME'] = blockname.upper()
            temp[varname.upper()] = vardata
            self.blocks.append(temp)
            return(self.write_blocks())
        return(False)

    def read_blocks(self):
        self.blocks = []
        try:
            if os.path.isfile(self.filename):
                with open(self.filename) as f:
                    for line in f:
                        if len(line) > 2:
                            if line.strip()[0]=="[":
                                blockname = line.strip()[1:-1].upper()
                            else:
                                if '=' in line:
                                    varname = line.split("=")[0].strip().upper()
                                    vardata = line.split("=")[1].strip()
                                    self.update_value(blockname, varname, vardata)
            else:
                f = open(self.filename, mode = 'w')
                f.close()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.exception(message)
            print(message)
        return(self.blocks)

    def names(self):
        name_list = []
        for block in self.blocks:
            name_list.append(block['BLOCKNAME'])
        return(name_list)
        
    def get_value(self, blockname, varname):
        if self.blocks:
            for block in self.blocks:
                if block['BLOCKNAME'] == blockname.upper():
                    if varname.upper() in block.keys():
                        return(block[varname.upper()])
                    else:
                        return('')
        return('')                

    def rename_block(self, oldname, newname):
        for block in self.blocks:
            if block['BLOCKNAME'] == oldname.upper():
                block['BLOCKNAME'] = newname.upper()
                return

    def rename_key(self, blockname, old_key, new_key):
        for block in self.blocks:
            if block['BLOCKNAME'] == blockname.upper():
                block[new_key] = block.pop(old_key)
                return
        
    def write_blocks(self):
        try:
            with open(self.filename, mode = 'w') as f:
                for block in self.blocks:
                    f.write("[%s]\n" % block['BLOCKNAME'])
                    for item in block.keys():
                        if not item=='BLOCKNAME':
                            if block[item]:
                                f.write(item + "=%s\n" % block[item])
                    f.write("\n")
            return(True)
        except:
            return(False)

    def __len__(self):
        return(len(self.blocks))