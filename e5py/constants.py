'''
As the lib folder is shared between EDM and E5, I place here the only things that are specific to each program.
In this way I can copy the other library code between programs without modifying it.
'''

__SPLASH_HELP__ = "\nE5 is a generalized data entry program intended "
__SPLASH_HELP__ += "for archaeologists but likely useful for others as well.  It works with a "
__SPLASH_HELP__ += "configuration file where the data entry fields are defined.  Importantly, E5 "
__SPLASH_HELP__ += "makes it simple to make entry in one field conditional on values previously "
__SPLASH_HELP__ += "entered for other fields.  The goal is to make data entry fast, efficient "
__SPLASH_HELP__ += "and error free.\n\n"
__SPLASH_HELP__ += "E5 is a complete, from scratch re-write of E4.  It is backwards compatible "
__SPLASH_HELP__ += "with E4 configuration files, but it supports a great many new features. "
__SPLASH_HELP__ += "For one, it is now built on Python to be cross-platform compatible, and the "
__SPLASH_HELP__ += "source code is available at GitHub.  E5 will run on Windows, Mac OS, Linux "
__SPLASH_HELP__ += "and Android tablets and phones.  For this reason and others, E5 now uses an "
__SPLASH_HELP__ += "open database format.  All data are stored in human readable, ASCII formatted "
__SPLASH_HELP__ += "JSON files.  Data can also be exported to CSV files for easy import into any "
__SPLASH_HELP__ += "database, statistics or spreadsheet software.\n\n"
__SPLASH_HELP__ += "To start using this program, you will need to open a CFG file.  Example CFG files "
__SPLASH_HELP__ += "and documentation on writing your own CFG file can be found at the E5 GitHub site."

APP_NAME = 'E5'
