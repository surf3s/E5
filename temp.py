    delete_list: delete_list
    orientation: 'vertical'
    ScrollView:
        do_scroll_x: False
        do_scroll_y: True
        size_hint: 1, 1
        scroll_timeout: 150
        GridLayout:
            id: delete_list
            padding: "10sp"
            spacing: "5sp"
            cols:1
            row_default_height: '35dp'
            row_force_default: True
            size_hint_y: None
