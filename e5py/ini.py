from blockdata import blockdata
from constants import APP_NAME


class ini(blockdata):

    def __init__(self, filename=''):
        if filename == '':
            filename = APP_NAME + '.ini'
        self.filename = filename
        self.incremental_backups = False
        self.backup_interval = 0
        self.first_time = True
        self.debug = False

    def open(self, filename=''):
        if filename:
            self.filename = filename
        self.blocks = self.read_blocks()
        self.first_time = (self.blocks == [])
        self.is_valid()
        self.incremental_backups = self.get_value(APP_NAME, 'IncrementalBackups').upper() == 'TRUE'
        self.backup_interval = int(self.get_value(APP_NAME, 'BackupInterval'))
        self.debug = self.get_value(APP_NAME, 'Debug').upper() == 'TRUE'

    def is_valid(self):
        for field_option in ['DARKMODE', 'INCREMENTALBACKUPS']:
            if self.get_value(APP_NAME, field_option):
                if self.get_value(APP_NAME, field_option).upper() == 'YES':
                    self.update_value(APP_NAME, field_option, 'TRUE')
            else:
                self.update_value(APP_NAME, field_option, 'FALSE')

        if self.get_value(APP_NAME, "BACKUPINTERVAL"):
            test = False
            try:
                test = int(self.get_value(APP_NAME, "BACKUPINTERVAL"))
                if test < 0:
                    test = 0
                elif test > 200:
                    test = 200
                self.update_value(APP_NAME, 'BACKUPINTERVAL', test)
            except ValueError:
                self.update_value(APP_NAME, 'BACKUPINTERVAL', 0)
        else:
            self.update_value(APP_NAME, 'BACKUPINTERVAL', 0)

    def update(self, e5_colors, e5_cfg):
        self.update_value(APP_NAME, 'CFG', e5_cfg.filename)
        self.update_value(APP_NAME, 'ColorScheme', e5_colors.color_scheme)
        self.update_value(APP_NAME, 'ButtonFontSize', e5_colors.button_font_size)
        self.update_value(APP_NAME, 'TextFontSize', e5_colors.text_font_size)
        self.update_value(APP_NAME, 'DarkMode', 'TRUE' if e5_colors.darkmode else 'FALSE')
        self.update_value(APP_NAME, 'IncrementalBackups', self.incremental_backups)
        self.update_value(APP_NAME, 'BackupInterval', self.backup_interval)
        return self.save()

    def save(self):
        return self.write_blocks()

    def status(self):
        txt = '\nThe INI file is %s.\n' % self.filename
        return txt
