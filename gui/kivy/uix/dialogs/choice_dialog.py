from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.widget import Widget

Builder.load_string('''
<ChoiceDialog@Popup>
    id: popup
    title: ''
    size_hint: 0.8, 0.8
    pos_hint: {'top':0.9}
    BoxLayout:
        orientation: 'vertical'
        Widget:
            size_hint: 1, 0.1
        ScrollView:
            orientation: 'vertical'
            size_hint: 1, 0.8
            GridLayout:
                row_default_height: '48dp'
                orientation: 'vertical'
                id: choices
                cols: 2
                size_hint: 1, None
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 0.2
            Button:
                text: _('Cancel')
                size_hint: 0.5, None
                height: '48dp'
                on_release: popup.dismiss()
            Button:
                text: _('OK')
                size_hint: 0.5, None
                height: '48dp'
                on_release:
                    root.callback(popup.value)
                    root.refresh()
                    popup.dismiss()
''')


class ChoiceDialog(Factory.Popup):

    def __init__(self, title, choices, key, callback):
        Factory.Popup.__init__(self)
        print(choices, type(choices))
        if type(choices) is list:
            choices = dict(map(lambda x: (x, x), choices))
        layout = self.ids.choices
        layout.bind(minimum_height=layout.setter('height'))
        for k, v in sorted(choices.items()):
            l = Label(text=v)
            l.height = '48dp'
            l.size_hint_x = 4
            cb = CheckBox(group='choices')
            cb.value = k
            cb.height = '48dp'
            cb.size_hint_x = 1

            def f(cb, x):
                if x: self.value = cb.value

            cb.bind(active=f)
            if k == key:
                cb.active = True
            layout.add_widget(l)
            layout.add_widget(cb)
        layout.add_widget(Widget(size_hint_y=1))
        self.callback = callback
        self.title = title
        self.value = key
        self.app = App.get_running_app()

    def refresh(self):
        if 'Language' == self.title:
            app = App.get_running_app()
            path = app.electrum_config.get_wallet_path()
            app.load_wallet_by_name(path)
