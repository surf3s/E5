SCROLLBAR_WIDTH = 5
BLACK = 0x000000
WHITE = 0xFFFFFF

# Color from Google material design
# https://material.io/design/color/the-color-system.html#tools-for-picking-colors
GOOGLE_COLORS = {'red': [0xFF8A80, BLACK, 0xFF1744, WHITE],
                                'pink': [0xFF80AB, BLACK, 0xF50057, WHITE],
                                'purple': [0xEA80FC, BLACK, 0xD500F9, WHITE],
                                'deep purple': [0xB388FF, BLACK, 0x651FFF, WHITE],
                                'indigo': [0x8C9EFF, BLACK, 0x3D5AFE, WHITE],
                                'blue': [0x82B1FF, BLACK, 0x2979FF, WHITE],
                                'light blue': [0x80D8FF, BLACK, 0x00B0FF, BLACK],
                                'cyan': [0x84FFFF, BLACK, 0x00E5FF, BLACK],
                                'teal': [0xA7FFEB, BLACK, 0x1DE9B6, BLACK],
                                'green': [0xB9F6CA, BLACK, 0x00E676, BLACK],
                                'light green': [0xCCFF90, BLACK, 0x76FF03, BLACK],
                                'lime': [0xF4FF81, BLACK, 0xC6FF00, BLACK],
                                'yellow': [0xFFFF8D, BLACK, 0xFFEA00, BLACK],
                                'amber': [0xFFE57F, BLACK, 0xFFC400, BLACK],
                                'orange': [0xFFD180, BLACK, 0xFF9100, BLACK],
                                'deep orange': [0xFF9E80, BLACK, 0xFF3D00, WHITE],
                                'brown': [0x8D6E63, WHITE, 0x6D4C41, WHITE]}

SPLASH_HELP = "\nE5 is a generalized data entry program intended "
SPLASH_HELP += "for archaeologists but likely useful for others as well.  It works with a "
SPLASH_HELP += "configuration file where the data entry fields are defined.  Importantly, E5 "
SPLASH_HELP += "makes it simple to make entry in one field conditional on values previously "
SPLASH_HELP += "entered for other fields.  The goal is to make data entry fast, efficient "
SPLASH_HELP += "and error free.\n\n"
SPLASH_HELP += "E5 is a complete, from scratch re-write of E4.  It is backwards compatible "
SPLASH_HELP += "with E4 configuration files, but it supports a great many new features. "
SPLASH_HELP += "For one, it is now built on Python to be cross-platform compatible, and the "
SPLASH_HELP += "source code is available at GitHub.  E5 will run on Windows, Mac OS, Linux "
SPLASH_HELP += "and Android tablets and phones.  For this reason and others, E5 now uses an "
SPLASH_HELP += "open database format.  All data are stored in human readable, ASCII formatted "
SPLASH_HELP += "JSON files.  Data can also be exported to CSV files for easy import into any "
SPLASH_HELP += "database, statistics or spreadsheet software.\n\n"
SPLASH_HELP += "To start using this program, you will need to open CFG file.  Example CFG files "
SPLASH_HELP += "and documentation on writing your own CFG file can be found at the E5 GitHub site."
