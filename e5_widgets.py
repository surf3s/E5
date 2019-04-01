from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.recycleview import RecycleView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty, ListProperty

from constants import BLACK, WHITE, SCROLLBAR_WIDTH, GOOGLE_COLORS
from colorscheme import ColorScheme, make_rgb

class e5_label(Label):
    def __init__(self, text, popup = False, colors = None, **kwargs):
        super(e5_label, self).__init__(**kwargs)
        self.text = text
        if not popup:
            self.color = colors.text_color if colors else make_rgb(BLACK)
        else:
            self.color = colors.popup_text_color if colors else make_rgb(WHITE)
        self.font_size = colors.text_font_size if colors else '15sp'

class e5_side_by_side_buttons(GridLayout):
    def __init__(self, text, id = ['',''], selected = [False, False],
                     call_back = [None,None], button_height = None, colors = None, **kwargs):
        super(e5_side_by_side_buttons, self).__init__(**kwargs)
        self.cols = 2
        self.spacing = 5
        self.size_hint_y = button_height
        self.add_widget(e5_button(text[0], id = id[0], selected = selected[0], call_back = call_back[0], button_height=button_height, colors = colors))
        self.add_widget(e5_button(text[1], id = id[1], selected = selected[1], call_back = call_back[1], button_height=button_height, colors = colors))

class e5_button(Button):
    def __init__(self, text, id = '', selected = False, call_back = None, button_height = None, colors = None, **kwargs):
        super(e5_button, self).__init__(**kwargs)
        self.text = text
        self.size_hint_y = button_height
        self.id = id
        self.font_size = colors.button_font_size if colors else '15sp'
        self.color = colors.button_color if colors else make_rgb(WHITE)
        if colors:
            self.background_color = colors.button_background if selected else colors.optionbutton_background
        else:
            self.background_color = make_rgb(GOOGLE_COLORS['light blue'][2 if selected else 0])  
        if call_back:
            self.bind(on_press = call_back)
        self.background_normal = ''

class e5_scrollview_menu(ScrollView):

    scrollbox = ObjectProperty(None)
    menu_selected_widget = None

    def __init__(self, menu_list, menu_selected, widget_id = '', call_back = None, ncols = 1, colors = None, **kwargs):
        super(e5_scrollview_menu, self).__init__(**kwargs)
        self.colors = colors
        self.scrollbox = GridLayout(cols = ncols,
                                size_hint_y = None,
                                id = widget_id + '_box',
                                spacing = 5)
        self.scrollbox.bind(minimum_height = self.scrollbox.setter('height'))
        
        self.menu_selected_widget = None
        if menu_list:
            for menu_item in menu_list:
                menu_button = e5_button(menu_item, menu_item,
                                        selected = (menu_item == menu_selected),
                                        call_back = call_back, colors = colors)
                self.scrollbox.add_widget(menu_button)
                if menu_item == menu_selected:
                    self.menu_selected_widget = menu_button
        else:
            self.scrollbox.add_widget(Button(text = '',
                                         background_normal = ''))
        self.size_hint = (1,1)
        self.id = widget_id + '_scroll'
        self.add_widget(self.scrollbox)

    def scroll_menu_clear_selected(self):
        if self.menu_selected_widget:
            self.menu_selected_widget.background_color = self.colors.optionbutton_background
            self.menu_selected_widget = None

    def scroll_menu_get_selected(self):
        return(self.menu_selected_widget)

    def scroll_menu_set_selected(self, text):
        self.scroll_menu_clear_selected()
        for widget in self.scrollbox.children:
            if widget.text == text:
                widget.background_color = self.colors.button_background
                self.menu_selected_widget = widget
                break

    def scroll_menu_list(self):
        menu_list = []
        for widget in self.scrollbox.children:
            menu_list.append(widget.text)
        menu_list.reverse()
        return(menu_list)
        # return([widget.text for widget in self.scroll_menu.children])

    def make_scroll_menu_item_visible(self):
        if self.menu_selected_widget:
            self.scroll_to(self.menu_selected_widget)

    def move_scroll_menu_item(self, ascii_code):
        menu_list = self.scroll_menu_list()
        if self.menu_selected_widget:
            index_no = menu_list.index(self.menu_selected_widget.text)
        else:
            index_no = 0

        if index_no >= 0:
            print (self.children[0].cols)
            new_index = -1
            if ascii_code == 279:
                new_index = len(menu_list) - 1
            elif ascii_code == 278:
                new_index = 0
            elif ascii_code == 273: # Up
                new_index = max([index_no - self.children[0].cols, 0])
            elif ascii_code == 276:
                new_index = max([index_no - 1, 0])
            elif ascii_code == 274: # Down
                new_index = min([index_no + self.children[0].cols, len(menu_list) - 1])
            elif ascii_code == 275:
                new_index = min([index_no + 1, len(menu_list) -1])
            if new_index >= 0:
                self.scroll_menu_set_selected(menu_list[new_index])
                self.make_scroll_menu_item_visible()
                #if self.get_widget_by_id('field_data'):
                #    self.get_widget_by_id('field_data').text = menu_list[new_index]

    def scroll_menu_char_match(self, match_str):
        menu_list = self.scroll_menu_list()
        if menu_list:
            index_no = menu_list.index(self.scroll_menu_get_selected().text)

            new_index = (index_no + 1) % len(menu_list)
            while not new_index == index_no:
                if menu_list[new_index].upper()[0] == match_str.upper():
                    self.scroll_menu_set_selected(menu_list[new_index])
                    self.make_scroll_menu_item_visible()
                    break
                else:
                    new_index = (new_index + 1) % len(menu_list)
                    # need new logic to auto select when only one case is available

class e5_scrollview_label(ScrollView):
    def __init__(self, text, widget_id = '', popup = False, colors = None, **kwargs):
        super(e5_scrollview_label, self).__init__(**kwargs)
        scrollbox = GridLayout(cols = 1,
                                size_hint_y = None,
                                id = widget_id + '_box',
                                spacing = 5)
        scrollbox.bind(minimum_height = scrollbox.setter('height'))

        info = Label(text = text, markup = True,
                    size_hint_y = None,
                    color = colors.text_color if not popup else colors.popup_text_color,
                    id = widget_id + '_label',
                    text_size = (self.width, None),
                    font_size = colors.text_font_size)

        info.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        info.bind(width=lambda instance, value: setattr(instance, 'text_size', (value * .95, None)))

        #info.bind(texture_size=lambda *x: info.setter('height')(info, info.texture_size[1]))
        scrollbox.add_widget(info)
        
        self.bar_width = SCROLLBAR_WIDTH
        self.size_hint = (1,1)
        self.id = widget_id + '_scroll'
        self.add_widget(scrollbox)

class e5_DatagridScreen(Screen):

    datagrid = ObjectProperty(None)

    def __init__(self, colors = None, **kwargs):
        super(e5_DatagridScreen, self).__init__(**kwargs)
        self.colors = colors if colors else ColorScheme()
        self.datagrid = DataGridWidget(colors = self.colors)
        self.add_widget(self.datagrid)

    def on_enter(self):
        Window.bind(on_key_down = self._on_keyboard_down)
        if self.datagrid:
            self.datagrid.switch_to(self.datagrid.tab_list[2])

    def _on_keyboard_down(self, *args):
        ascii_code = args[1]
        text_str = args[3]  
        if ascii_code in [273, 274, 275, 276, 278, 279] and self.datagrid.popup_scrollmenu:
            self.datagrid.popup_scrollmenu.move_scroll_menu_item(ascii_code)
            return False 
        if ascii_code == 13 and (self.datagrid.popup_scrollmenu or self.datagrid.popup_textbox):
            if self.datagrid.popup_textbox.focus:
                self.datagrid.popup_addbutton.trigger_action(0)
            else:
                self.datagrid.popup_scrollmenu.menu_selected_widget.trigger_action(0)
        if ascii_code == 8:
            return False
        if ascii_code == 27 and (self.datagrid.popup_scrollmenu or self.datagrid.popup_textbox):
            self.datagrid.popup_scrollmenu= None
            self.datagrid.popup_textbox = None
            self.datagrid.popup.dismiss()

        ### On key down, see if there is a current record,
        # get the next record in the db,
        # and then try to fire the highlight record stuff
        return True

    def on_leave(self):
        Window.unbind(on_key_down = self._on_keyboard_down)

#region Data Grid
#### Code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py

class DataGridMenuList(Popup):
    
    def __init__(self, title, menu_list, menu_selected = '', call_back = None, **kwargs):
        super(DataGridMenuList, self).__init__(**kwargs)
        
        pop_content = GridLayout(cols = 1, size_hint_y = 1, spacing = 5, padding = 5)

        new_item = GridLayout(cols = 2, spacing = 5, size_hint_y = .15)
        self.txt = TextInput(id = 'new_item', size_hint_y = .15)
        new_item.add_widget(self.txt)
        new_item.add_widget(e5_button('Add', id = 'add_button',
                                             selected = True,
                                             call_back = call_back,
                                             button_height = .15))
        pop_content.add_widget(new_item)

        ncols = int(Window.width / 200)
        if ncols < 1:
            ncols = 1

        menu = e5_scrollview_menu(menu_list, menu_selected,
                                                 widget_id = 'menu',
                                                 call_back = call_back, ncols = ncols)
        pop_content.add_widget(menu)
        menu.make_scroll_menu_item_visible()
        
        pop_content.add_widget(e5_button('Back', selected = True, call_back = self.dismiss))

        self.content = pop_content
        
        self.title = title
        self.size_hint = (.9, .9)
        self.auto_dismiss = True

    def on_open(self):
        self.txt.focus = True
        self.txt.select_all()

class DataGridTextBox(Popup):
    def __init__(self, title, text = '', multiline = False, call_back = None, **kwargs):
        super(DataGridTextBox, self).__init__(**kwargs)
        content = GridLayout(cols = 1, spacing = 5, padding = 10, size_hint_y = None)
        self.txt = TextInput(text = text, size_hint_y = .135, multiline = multiline, id = 'new_item')
        content.add_widget(self.txt)
        content.add_widget(e5_side_by_side_buttons(['Back','Save'],
                                                    button_height = .2,
                                                    id = [title, 'add_button'],
                                                    selected = [True, True],
                                                    call_back = [self.dismiss, call_back]))
        self.title = title
        self.content = content
        self.size_hint = (.8, .3)
        self.auto_dismiss = True
    
    def on_open(self):
        self.txt.focus = True
        self.txt.select_all()

class DataGridHeaderCell(Button):
    def __init__(self, text, colors, **kwargs):
        super(DataGridHeaderCell, self).__init__(**kwargs)
        self.background_color = colors.button_background
        self.background_normal = ''
        self.color = colors.button_color
        self.text = text

class DataGridTableHeader(ScrollView):
    """Fixed table header that scrolls x with the data table"""
    header = ObjectProperty(None)

    def __init__(self, titles = None, colors = None, *args, **kwargs):
        super(DataGridTableHeader, self).__init__(*args, **kwargs)

        for title in titles:
            self.header.add_widget(DataGridHeaderCell(title, colors))

class DataGridScrollCell(Button):
    text = StringProperty(None)
    is_even = BooleanProperty(None)
    datagrid_even = ListProperty(None)
    datagrid_odd = ListProperty(None)
    def __init__(self, **kwargs):
        super(DataGridScrollCell, self).__init__(**kwargs)
        self.background_normal = ''

class DataGridTableData(RecycleView):
    nrows = NumericProperty(None)
    ncols = NumericProperty(None)
    rgrid = ObjectProperty(None)
    
    datagrid_doc_id = None
    datagrid_background_color = None
    datagrid_widget_row = []

    datatable_widget = None

    popup = ObjectProperty(None)

    def __init__(self, list_dicts=[], column_names = None, tb = None, e5_cfg = None, colors = None, *args, **kwargs):
        self.nrows = len(list_dicts)
        self.ncols = len(column_names) 
        self.id = 'datatable'
        self.colors = colors if colors else ColorScheme()
        self.e5_cfg = e5_cfg

        super(DataGridTableData, self).__init__(*args, **kwargs)

        self.data = []
        for i, ord_dict in enumerate(list_dicts):
            is_even = i % 2 == 0
            for text, value in ord_dict.items():
                self.data.append({'text': value, 'is_even': is_even,
                                    'callback': self.editcell,
                                    'key': ord_dict['doc_id'], 'field': text,
                                    'db': tb, 'id': 'datacell',
                                    'datagrid_even': self.colors.datagrid_even,
                                    'datagrid_odd': self.colors.datagrid_odd ,
                                    'color': make_rgb(BLACK)})

    def clear_highlight_row(self):
        if self.datagrid_doc_id:
            for widget in self.get_editcell_row(self.datagrid_doc_id):
                widget.background_color = self.datagrid_background_color
            self.datagrid_doc_id = ''        
            self.datagrid_widget_row = []

    def set_highlight_row(self):
        if self.datagrid_doc_id:
            widget_row = self.get_editcell_row(self.datagrid_doc_id)
            for widget in widget_row:
                widget.background_color = self.colors.optionbutton_background
            self.datagrid_widget_row = widget_row

    def get_editcell_row(self, key):
        row_widgets = []
        for widget in self.walk():
            if widget.id == 'datacell':
                if widget.key == key:
                    row_widgets.append(widget)
        return(row_widgets)

    def get_editcell(self, key, field):
        for widget in self.walk():
            if widget.id == 'datacell':
                if widget.field == field and widget.key == key:
                    return(widget)
        return(None)

    def editcell(self, key, field, db):
        #self.key = key
        self.clear_highlight_row()
        self.datagrid_doc_id = key
        editcell_widget = self.get_editcell(key, field)
        self.datagrid_background_color = editcell_widget.background_color
        self.set_highlight_row()
        self.field = field
        self.tb = db
        cfg_field = self.e5_cfg.get(field)
        self.inputtype = cfg_field.inputtype
        if cfg_field.inputtype in ['MENU','BOOLEAN']:
            self.popup = DataGridMenuList(field, cfg_field.menu, editcell_widget.text, self.menu_selection)
            self.popup.open()
        if cfg_field.inputtype in ['TEXT','NUMERIC','NOTE']:
            self.popup = DataGridTextBox(field, editcell_widget.text, cfg_field.inputtype == 'NOTE', self.menu_selection)
            self.popup.open()
        self.datatable_widget.popup_scrollmenu = self.datatable_widget.get_widget_by_id(self.popup, 'menu_scroll')
        self.datatable_widget.popup_textbox = self.datatable_widget.get_widget_by_id(self.popup, 'new_item')
        self.datatable_widget.popup_addbutton = self.datatable_widget.get_widget_by_id(self.popup, 'add_button')
        self.datatable_widget.popup = self.popup

    def menu_selection(self, instance):
        ### need some data validation
        if self.inputtype in ['MENU','BOOLEAN']:
            new_data = {self.field: instance.text if not instance.text == 'Add' else self.datatable_widget.popup_textbox.text}
        else:
            new_data = {self.field: self.datatable_widget.popup_textbox.text}
        self.tb.update(new_data, doc_ids = [int(self.datagrid_doc_id)])
        for widget in self.walk():
            if widget.id=='datacell':
                if widget.key == self.datagrid_doc_id and widget.field == self.field:
                    widget.text = new_data[self.field]
        self.popup.dismiss()
        self.datatable_widget.popup_scrollmenu = None
        self.datatable_widget.popup_textbox = None

class DataGridTable(BoxLayout):

    def __init__(self, list_dicts=[], column_names = None, tb = None, e5_cfg = None, colors = None, *args, **kwargs):

        super(DataGridTable, self).__init__(*args, **kwargs)
        self.orientation = "vertical"

        self.header = DataGridTableHeader(column_names, colors)
        self.table_data = DataGridTableData(list_dicts = list_dicts, column_names = column_names,
                                            tb = tb, e5_cfg = e5_cfg, colors = colors)

        self.table_data.fbind('scroll_x', self.scroll_with_header)

        self.add_widget(self.header)
        self.add_widget(self.table_data)

    def scroll_with_header(self, obj, value):
        self.header.scroll_x = value

class DataGridGridPanel(BoxLayout):

    def populate_data(self, tb, tb_fields, colors = None):
        self.colors = colors if colors else ColorScheme()
        self.tb = tb
        self.sort_key = None
        self.column_names = ['doc_id'] + tb_fields.fields()
        self.tb_fields = tb_fields
        self._generate_table()

    def _generate_table(self, sort_key = None, disabled = None):
        self.clear_widgets()
        data = []
        for tb_row in self.tb:
            reformatted_row = {}
            reformatted_row['doc_id'] = str(tb_row.doc_id)
            for field in self.tb_fields.fields():
                reformatted_row[field] = tb_row[field] if field in tb_row else ''
            data.append(reformatted_row)
        data = sorted(data, key=lambda k: k['doc_id'], reverse = True) 
        self.add_widget(DataGridTable(list_dicts = data, column_names = self.column_names,
                                        tb = self.tb, e5_cfg = self.tb_fields, colors = self.colors))

class DataGridCasePanel(BoxLayout):
    
    def populate(self, data, fields, colors = None):
        self.colors = colors if colors else ColorScheme()
        self.addnew_list.bind(minimum_height = self.addnew_list.setter('height'))
        for col in fields.fields():
            self.addnew_list.add_widget(DataGridLabelAndField(col = col, colors = self.colors))

class DataGridLabelAndField(BoxLayout):

    popup = ObjectProperty(None)
    sorted_result = None

    def __init__(self, col, colors, **kwargs):
        super(DataGridLabelAndField, self).__init__(**kwargs)
        self.update_db = False
        self.widget_type = 'data'
        self.height = "30sp"
        self.size_hint = (0.9, None)
        self.spacing = 10
        label = e5_label(text = col)
        txt = TextInput(multiline = False,
                                size_hint=(0.75, None),
                                font_size= colors.text_font_size,
                                id = col)
        txt.bind(minimum_height=txt.setter('height'))
        self.add_widget(label)
        self.add_widget(txt)

class DataGridWidget(TabbedPanel):
    data = ObjectProperty(None)
    fields = ObjectProperty(None)
    colors = ObjectProperty(None)

    popup = None
    popup_scrollmenu = None
    popup_addbutton = None
    popup_textbox = None
    popup_field_widget = None

    def __init__(self, data = None, fields = None, colors = None, **kwargs):
        super(DataGridWidget, self).__init__(**kwargs)
        self.textboxes_will_update_db = False

        if data:
            self.data = data
        if fields:
            self.fields = fields

        if data and fields:
            self.populate_panels()

        self.colors = colors if colors else ColorScheme()
        self.color = self.colors.text_color 
        self.background_color = self.colors.window_background 
        self.background_image = ''

        for tab_no in [0,1,2]:
            self.tab_list[tab_no].color = self.colors.button_color
            self.tab_list[tab_no].background_color = self.colors.button_background

    def record_count(self):
        datatable = self.get_widget_by_id(self.tab_list[2].content, 'datatable')
        return(datatable.nrows if datatable else 0)

    def reload_data(self):
        self.populate_panels()

    def load_data(self, data, fields):
        self.data = data
        self.fields = fields
        self.populate_panels()

    def populate_panels(self):
        self.panel1.populate_data(tb = self.data, tb_fields = self.fields, colors = self.colors)
        self.panel2.populate(data = self.data, fields = self.fields, colors = self.colors)
        self.get_widget_by_id(self.tab_list[2].content, 'datatable').datatable_widget = self
        pass

    def open_panel1(self):
        self.textboxes_will_update_db = False

    def open_panel2(self):
        datatable = self.get_widget_by_id(self.tab_list[2].content, 'datatable')
        if datatable:
            if datatable.datagrid_doc_id:
                data_record = self.data.get(doc_id = int(datatable.datagrid_doc_id))
                for widget in self.ids.add_new_panel.children[0].walk():
                    if widget.id in self.fields.fields():
                        widget.text = data_record[widget.id] if widget.id in data_record else ''
                        widget.bind(text = self.update_db)
                        widget.bind(focus = self.show_menu)
                self.textboxes_will_update_db = True

    def show_menu(self, instance, value):
        if instance.focus:
            cfg_field = self.fields.get(instance.id)
            if cfg_field:
                self.popup_field_widget = instance
                if cfg_field.inputtype in ['MENU','BOOLEAN']:
                    self.popup = DataGridMenuList(instance.id, cfg_field.menu, instance.text, self.menu_selection)
                    self.popup.open()
                    self.popup_scrollmenu = self.get_widget_by_id(self.popup, 'menu_scroll')
                    self.popup_textbox = self.get_widget_by_id(self.popup, 'new_item')
                    self.popup_addbutton = self.get_widget_by_id(self.popup, 'add_button')

    def menu_selection(self, instance):
        self.popup.dismiss()
        self.popup_field_widget.text = instance.text if not instance.id == 'add_button' else self.popup_textbox.text
        self.popup_field_widget = None
        self.popup_scrollmenu = None

    def update_db(self, instance, value):
        if self.textboxes_will_update_db:
            datatable = self.get_widget_by_id(self.tab_list[2].content, 'datatable')
            if datatable:
                for widget in datatable.datagrid_widget_row:
                    if widget.field == instance.id and widget.key == datatable.datagrid_doc_id:
                        widget.text = value
                        update = {widget.field: value}
                        self.data.update(update, doc_ids = [int(datatable.datagrid_doc_id)])
                        break

    # repeats code above - could be put into a general functions package
    def get_widget_by_id(self, start = None, id = ''):
        if not start:
            start = self
        for widget in start.walk():
            if widget.id == id:
                return(widget)
        return(None)

    def close_panels(self):
        self.parent.parent.current = 'MainScreen'
        
    def cancel(self):
        pass

# End code from https://github.com/MichaelStott/DataframeGUIKivy/blob/master/dfguik.py
#endregion
