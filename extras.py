class KeyboardInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        if e4_cfg.current_field.inputtype == 'NUMERIC':
            if not substring in "0123456789,.-+":
                s = ''
            else:
                s = substring
        else:
            s = substring 
        return super(KeyboardInput, self).insert_text(s, from_undo = from_undo)



        bx = GridLayout(cols = 2, size_hint_y = .8)

        bx.add_widget(Label(text='Field 1'))    
        tx1 = TextInput(multiline = False)
        bx.add_widget(tx1)

        bx.add_widget(Label(text='Field 2'))    
        tx2 = TextInput()
        bx.add_widget(tx2)

        bx.add_widget(Label(text='Field 3'))    
        tx3 = TextInput()
        bx.add_widget(tx3)

        self.add_widget(bx)
        tx1.focus = True


 textinput.bind(on_text_validate=on_enter)