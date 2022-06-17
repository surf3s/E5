from kivy.core.window import Window
from e5py.lib.misc import platform_name

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


def make_rgb(hex_color):
    return([((hex_color >> 16) & 0xFF) / 255.0,
            ((hex_color >> 8) & 0xFF) / 255.0,
            (hex_color & 0xFF) / 255.0,
            1])


class ColorScheme:

    def __init__(self, color_name = 'light blue'):

        if platform_name() == 'Android':
            self.optionbutton_font_size = "10sp"
            self.button_font_size = "5dp"
            self.text_font_size = "15sp"
            self.datagrid_font_size = "10sp"
        if platform_name() == 'Linux':
            self.optionbutton_font_size = "15sp"
            self.button_font_size = "15sp"
            self.text_font_size = "15sp"
            self.datagrid_font_size = "15sp"
        else:
            self.optionbutton_font_size = None
            self.button_font_size = '23sp'
            self.text_font_size = None
            self.datagrid_font_size = None

        self.popup_background = (0, 0, 0, 1)
        self.popup_text_color = (1, 1, 1, 1)

        self.datagrid_odd = (224.0 / 255, 224.0 / 255, 224.0 / 255, 1)
        self.datagrid_even = (189.0 / 255, 189.0 / 255, 189.0 / 255, 1)

        self.valid_colors = GOOGLE_COLORS

        if color_name.lower() in self.valid_colors:
            self.set_to(color_name)
        else:
            self.set_to('light blue')

        self.window_background = (1, 1, 1, 1)
        self.text_color = (0, 0, 0, 1)
        self.darkmode = False
        self.need_redraw = False

    def set_colormode(self):
        if self.darkmode:
            self.set_to_darkmode()
        else:
            self.set_to_lightmode()

    def set_to_darkmode(self):
        self.need_redraw = True
        self.window_background = (0, 0, 0, 1)
        self.text_color = (1, 1, 1, 1)
        self.darkmode = True
        Window.clearcolor = self.window_background

    def set_to_lightmode(self):
        self.need_redraw = True
        self.window_background = (1, 1, 1, 1)
        self.text_color = (0, 0, 0, 1)
        self.darkmode = False
        Window.clearcolor = self.window_background

    def color_names(self):
        return(list(self.valid_colors.keys()))

    def set_to(self, name):
        self.need_redraw = True
        if name in self.valid_colors:
            self.optionbutton_background = make_rgb(self.valid_colors[name][0])
            self.optionbutton_color = make_rgb(self.valid_colors[name][1])
            self.button_background = make_rgb(self.valid_colors[name][2])
            self.button_color = make_rgb(self.valid_colors[name][3])
            self.color_scheme = name
        else:
            return('Error: %s is not a valid color scheme.' % (name))
