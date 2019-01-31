import logging
import os

class blockdata:
    def update_value(self, blockname, varname, vardata, append = False):
        block_exists = False
        for block in self.blocks:
            if block['BLOCKNAME']==blockname:
                block_exists = True
                if (varname in block.keys()) and append:
                    block[varname] = [block[varname] , vardata]
                else:
                    block[varname] = vardata 
                return(True)
        if not block_exists:
            temp = {}
            temp['BLOCKNAME'] = blockname
            temp[varname] = vardata
            self.blocks.append(temp)
            return(True)
        return(False)

    def read_blocks(self):
        self.blocks = []
        print(self.filename)
        try:
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
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.exception(message)
            print(message)
            return([])
        return(self.blocks)

    def names(self):
        name_list = []
        for block in self.blocks:
            name_list.append(block['BLOCKNAME'])
        return(name_list)
        
    def get_value(self, blockname, varname):
        for block in self.blocks:
            if block['BLOCKNAME'] == blockname:
                if varname in block.keys():
                    return(block[varname])
                else:
                    return('')
        return('')                

    def write_blocks(self):
        try:
            with open(self.filename, mode = 'w') as f:
                for block in self.blocks:
                    f.write("[%s]\n" % block['BLOCKNAME'])
                    for item in block.keys():
                        f.write(item + "=%s\n" % block[item])
                    f.write("\n")
            return(True)
        except:
            return(False)

    def __len__(self):
        return(len(self.blocks))