# To Do
#   Consider implications of not writing the block data after each update

import logging
import os

from e5py.constants import APP_NAME


class blockdata:

    filename = ''
    blocks = {}

    def update_value(self, blockname, varname, vardata, append=False):
        var = varname.upper()
        block = blockname.upper()
        if block in self.blocks.keys():
            if (var in self.blocks[block].keys()) and append:
                self.blocks[block][var] = [self.blocks[block][var], vardata]
            else:
                self.blocks[block][var] = vardata
            return True
        else:
            self.blocks[block] = {var: vardata}
            return True
        return False

    def get_block(self, blockname):
        if self.blocks:
            if blockname.upper() in self.blocks.keys():
                return self.block[blockname.upper()]
        return ''

    def read_blocks(self):
        self.blocks = {}
        try:
            if os.path.isfile(self.filename):
                with open(self.filename, 'r', encoding="latin1") as f:
                    for line in f:
                        if len(line) > 2:
                            if line.strip()[0] == "[":
                                blockname = line.strip()[1:-1].upper()
                            else:
                                if '=' in line:
                                    varname = line.split("=")[0].strip().upper()
                                    vardata = line.split("=")[1].strip()
                                    self.update_value(blockname, varname, vardata)
            else:
                f = open(self.filename, mode='w')
                f.close()
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logging.exception(message)
            print(message)
        return self.blocks

    def names(self):
        return list(self.blocks.keys())

    def fields(self):
        fieldnames = self.names()
        if APP_NAME in fieldnames:
            fieldnames.remove(APP_NAME)
        return fieldnames

    def get_value(self, blockname, varname):
        if blockname.upper() in self.blocks.keys():
            if varname.upper() in self.blocks[blockname.upper()].keys():
                return self.blocks[blockname.upper()][varname.upper()]
        return ''

    def delete_key(self, blockname, key):
        if blockname.upper() in self.blocks:
            self.blocks[blockname.upper()].pop(key, None)

    def rename_block(self, oldname, newname):
        if oldname.upper() in self.blocks:
            self.blocks[newname.upper()] = self.blocks.pop(oldname.upper(), None)

    def rename_key(self, blockname, old_key, new_key):
        blockname = blockname.upper()
        old_key = old_key.upper()
        new_key = new_key.upper()
        
        if blockname in self.blocks:
            block = self.blocks[blockname]
            if old_key in block:
                block[new_key] = block.pop(old_key)

    def write_blocks(self):
        try:
            with open(self.filename, mode='w') as f:
                for block, values in self.blocks.items():
                    f.write(f"[{block}]\n")
                    for item, value in values.items():
                        if not item[:2] == "__":
                            if value != '' and value is not None:
                                f.write(f"{item}={value}\n")
                    f.write("\n")
            return True
        except OSError:
            return False

    def save(self):
        self.write_blocks()

    def __len__(self):
        return len(self.blocks)
