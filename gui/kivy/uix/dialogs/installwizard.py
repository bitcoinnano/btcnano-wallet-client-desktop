import os

from functools import partial
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, OptionProperty
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.utils import platform
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform

from .choice_dialog import ChoiceDialog
from bitcoinnano.i18n import languages
from bitcoinnano_gui.kivy.i18n import _
from lib.wallet import wallet_types
from lib import keystore,bitcoin
from lib.keystore import bip44_derivation, bip44_derivation_145


from bitcoinnano.base_wizard import BaseWizard

from . import EventsDialog
# from ...i18n import _
from .password_dialog import PasswordDialog

# global Variables
is_test = (platform == "linux")
test_seed = "time taxi field recycle tiny license olive virus report rare steel portion achieve"
test_xpub = "xpub661MyMwAqRbcEbvVtRRSjqxVnaWVUMewVzMiURAKyYratih4TtBpMypzzefmv8zUNebmNVzB3PojdC5sV2P9bDgMoo9B3SARw1MXUUfU1GL"

Builder.load_string('''
#:import Window kivy.core.window.Window
#:import _ bitcoinnano_gui.kivy.i18n._


<WizardTextInput@TextInput>
    border: 4, 4, 4, 4
    font_size: '15sp'
    padding: '15dp', '15dp'
    background_color: (1, 1, 1, 1) if self.focus else (0.454, 0.698, 0.909, 1)
    foreground_color: (0.31, 0.31, 0.31, 1) if self.focus else (0.835, 0.909, 0.972, 1)
    hint_text_color: self.foreground_color
    background_active: 'atlas://gui/kivy/theming/light/create_act_text_active'
    background_normal: 'atlas://gui/kivy/theming/light/create_act_text_active'
    size_hint_y: None
    height: '48sp'

<WizardButton@Button>:
    root: None
    size_hint: 1, None
    height: '48sp'
    on_press: if self.root: self.root.dispatch('on_press', self)
    on_release: if self.root: self.root.dispatch('on_release', self)

<BigLabel@Label>
    color: .854, .925, .984, 1
    size_hint: 1, None
    text_size: self.width, None
    height: self.texture_size[1]
    bold: True

<-WizardDialog>
    text_color: .854, .925, .984, 1
    value: ''
    #auto_dismiss: False
    size_hint: None, None
    canvas.before:
        Color:
            rgba: 0, 0, 0, .9
        Rectangle:
            size: Window.size
        Color:
            rgba: .239, .588, .882, 1
        Rectangle:
            size: Window.size

    crcontent: crcontent
    # add electrum icon
    BoxLayout:
        orientation: 'vertical' if self.width < self.height else 'horizontal'
        padding:
            min(dp(27), self.width/32), min(dp(27), self.height/32),\
            min(dp(27), self.width/32), min(dp(27), self.height/32)
        spacing: '10dp'
        GridLayout:
            id: grid_logo
            cols: 1
            pos_hint: {'center_y': .5}
            size_hint: 1, None
            height: self.minimum_height
            Label:
                color: root.text_color
                text: 'BitCoin Nano'
                size_hint: 1, None
                height: self.texture_size[1] if self.opacity else 0
                font_size: '33sp'
                font_name: 'gui/kivy/data/fonts/tron/Tr2n.ttf'
        Button:
            text: 'Language'
            font_size: '13sp'
            size_hint: None, None
            size: 150, 44
            size_hint: None, None
            background_color: 0, 0, 0, 0
            pos_hint: {'center_x': .9}
            on_release: root.language_dialog_first()
        GridLayout:
            cols: 1
            id: crcontent
            spacing: '1dp'
        Widget:
            size_hint: 1, 0.3
        GridLayout:
            rows: 1
            spacing: '12dp'
            size_hint: 1, None
            height: self.minimum_height
            WizardButton:
                id: back
                text: _('Back')
                root: root
            WizardButton:
                id: next
                text: _('Next')
                root: root
                disabled: root.value == ''


<WizardMultisigDialog>
    value: 'next'
    Widget
        size_hint: 1, 1
    Label:
        color: root.text_color
        size_hint: 1, None
        text_size: self.width, None
        height: self.texture_size[1]
        text: _("Choose the number of signatures needed to unlock funds in your wallet")
    Widget
        size_hint: 1, 1
    GridLayout:
        orientation: 'vertical'
        cols: 2
        spacing: '14dp'
        size_hint: 1, 1
        height: self.minimum_height
        Label:
            color: root.text_color
            text: _('From %d cosigners')%n.value
        Slider:
            id: n
            range: 2, 5
            step: 1
            value: 2
        Label:
            color: root.text_color
            text: _('Require %d signatures')%m.value
        Slider:
            id: m
            range: 1, n.value
            step: 1
            value: 2


<WizardChoiceDialog>
    message : ''
    Widget:
        size_hint: 1, 1
    Label:
        color: root.text_color
        size_hint: 1, None
        text_size: self.width, None
        height: self.texture_size[1]
        text: root.message
    Widget
        size_hint: 1, 1
    GridLayout:
        row_default_height: '48dp'
        orientation: 'vertical'
        id: choices
        cols: 1
        spacing: '14dp'
        size_hint: 1, None

<MButton@Button>:
    size_hint: 1, None
    height: '40dp'
    on_release:
        self.parent.update_amount(self.text)

<WordButton@Button>:
    size_hint: None, None
    padding: '5dp', '5dp'
    text_size: None, self.height
    width: self.texture_size[0]
    height: '30dp'
    on_release:
        self.parent.new_word(self.text)


<SeedButton@Button>:
    height: dp(100)
    border: 4, 4, 4, 4
    halign: 'justify'
    valign: 'top'
    font_size: '18dp'
    text_size: self.width - dp(24), self.height - dp(12)
    color: .1, .1, .1, 1
    background_normal: 'atlas://gui/kivy/theming/light/white_bg_round_top'
    background_down: self.background_normal
    size_hint_y: None


<SeedLabel@Label>:
    font_size: '12sp'
    text_size: self.width, None
    size_hint: 1, None
    height: self.texture_size[1]
    halign: 'justify'
    valign: 'middle'
    border: 4, 4, 4, 4


<RestoreSeedDialog>
    message: ''
    word: ''
    BigLabel:
        text: _("ENTER YOUR SEED PHRASE")
    GridLayout
        cols: 1
        padding: 0, '12dp'
        orientation: 'vertical'
        spacing: '12dp'
        size_hint: 1, None
        height: self.minimum_height
        SeedButton:
            id: text_input_seed
            text: ''
            on_text: Clock.schedule_once(root.on_text)
            on_release: root.options_dialog()
        SeedLabel:
            text: root.message
        BoxLayout:
            id: suggestions
            height: '35dp'
            size_hint: 1, None
            new_word: root.on_word
        BoxLayout:
            id: line1
            spacing:'2dp'
            update_amount: root.update_text
            size_hint: 1, None
            height: '40dp'
            MButton:
                text: 'Q'
            MButton:
                text: 'W'
            MButton:
                text: 'E'
            MButton:
                text: 'R'
            MButton:
                text: 'T'
            MButton:
                text: 'Y'
            MButton:
                text: 'U'
            MButton:
                text: 'I'
            MButton:
                text: 'O'
            MButton:
                text: 'P'
        BoxLayout:
            id: line2
            update_amount: root.update_text
            size_hint: 1, None
            height: '40dp'
            spacing:'2dp'
            Widget:
                size_hint: 0.5, None
                height: '40dp'
            MButton:
                text: 'A'
            MButton:
                text: 'S'
            MButton:
                text: 'D'
            MButton:
                text: 'F'
            MButton:
                text: 'G'
            MButton:
                text: 'H'
            MButton:
                text: 'J'
            MButton:
                text: 'K'
            MButton:
                text: 'L'
            Widget:
                size_hint: 0.5, None
                height: '40dp'
        BoxLayout:
            id: line3
            update_amount: root.update_text
            size_hint: 1, None
            height: '40dp'
            spacing:'2dp'
            Widget:
                size_hint: 1, None
            MButton:
                text: 'Z'
            MButton:
                text: 'X'
            MButton:
                text: 'C'
            MButton:
                text: 'V'
            MButton:
                text: 'B'
            MButton:
                text: 'N'
            MButton:
                text: 'M'
            MButton:
                text: '<'
            Widget:
                size_hint: 1, None
                height: '40dp'

<AddXpubDialog>
    title: ''
    message: ''
    BigLabel:
        text: root.title
    GridLayout
        cols: 1
        padding: 0, '12dp'
        orientation: 'vertical'
        spacing: '12dp'
        size_hint: 1, None
        height: self.minimum_height
        SeedButton:
            id: text_input
            text: ''
            on_text: Clock.schedule_once(root.check_text)
        SeedLabel:
            text: root.message
    GridLayout
        rows: 1
        spacing: '12dp'
        size_hint: 1, None
        height: self.minimum_height
        IconButton:
            id: scan
            height: '48sp'
            on_release: root.scan_xpub()
            icon: 'atlas://gui/kivy/theming/light/camera'
            size_hint: 1, None
        WizardButton:
            text: _('Paste')
            on_release: root.do_paste()
        WizardButton:
            text: _('Clear')
            on_release: root.do_clear()


<ShowXpubDialog>
    xpub: ''
    message: _('Here is your master public key. Share it with your cosigners.')
    BigLabel:
        text: _("MASTER PUBLIC KEY")
    GridLayout
        cols: 1
        padding: 0, '12dp'
        orientation: 'vertical'
        spacing: '12dp'
        size_hint: 1, None
        height: self.minimum_height
        SeedButton:
            id: text_input
            text: root.xpub
        SeedLabel:
            text: root.message
    GridLayout
        rows: 1
        spacing: '12dp'
        size_hint: 1, None
        height: self.minimum_height
        WizardButton:
            text: _('QR code')
            on_release: root.do_qr()
        WizardButton:
            text: _('Copy')
            on_release: root.do_copy()
        WizardButton:
            text: _('Share')
            on_release: root.do_share()


<ShowSeedDialog>
    spacing: '12dp'
    value: 'next'
    BigLabel:
        text: _("PLEASE WRITE DOWN YOUR SEED PHRASE")
    GridLayout:
        id: grid
        cols: 1
        pos_hint: {'center_y': .5}
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
        spacing: '12dp'
        SeedButton:
            text: root.seed_text
            on_release: root.options_dialog()
        SeedLabel:
            text: _("If you forget your PIN or lose your device, your seed phrase will be the only way to recover your funds.")


<LineDialog>

    BigLabel:
        text: root.title
    SeedLabel:
        text: root.message
    TextInput:
        id: passphrase_input
        multiline: False
        size_hint: 1, None
        height: '27dp'
    SeedLabel:
        text: root.warning

''')


class WizardDialog(EventsDialog):
    ''' Abstract dialog to be used as the base for all Create Account Dialogs
    '''
    crcontent = ObjectProperty(None)

    def __init__(self, wizard, **kwargs):
        super(WizardDialog, self).__init__()
        self.wizard = wizard
        self.ids.back.disabled = not wizard.can_go_back()
        self.app = App.get_running_app()
        self.run_next = kwargs['run_next']
        _trigger_size_dialog = Clock.create_trigger(self._size_dialog)
        Window.bind(size=_trigger_size_dialog,
                    rotation=_trigger_size_dialog)
        _trigger_size_dialog()
        self._on_release = False

    def _size_dialog(self, dt):
        app = App.get_running_app()
        if app.ui_mode[0] == 'p':
            self.size = Window.size
        else:
            # tablet
            if app.orientation[0] == 'p':
                # portrait
                self.size = Window.size[0] / 1.67, Window.size[1] / 1.4
            else:
                self.size = Window.size[0] / 2.5, Window.size[1]

    def add_widget(self, widget, index=0):
        if not self.crcontent:
            super(WizardDialog, self).add_widget(widget)
        else:
            self.crcontent.add_widget(widget, index=index)

    def on_dismiss(self):
        app = App.get_running_app()
        if app.wallet is None and not self._on_release:
            app.stop()

    def get_params(self, button):
        return (None,)

    def on_release(self, button):
        self._on_release = True
        self.close()
        if not button:
            self.parent.dispatch('on_wizard_complete', None)
            return
        if button is self.ids.back:
            self.wizard.go_back()
            return
        params = self.get_params(button)
        print(params)
        print(self.run_next, type(self.run_next))
        self.run_next(*params)

    def language_dialog_first(self):
        l = self.app.electrum_config.get('language', 'en')

        def cb(key):
            self.app.electrum_config.set_key("language", key, True)
            # item.lang = self.get_language_name()
            self.app.language = key

        language_dialog_first = ChoiceDialog('Language', languages, l, cb)
        language_dialog_first.open()

class WizardMultisigDialog(WizardDialog):

    def get_params(self, button):
        m = self.ids.m.value
        n = self.ids.n.value
        return m, n


class WizardChoiceDialog(WizardDialog):

    def __init__(self, wizard, **kwargs):
        super(WizardChoiceDialog, self).__init__(wizard, **kwargs)
        self.message = kwargs.get('message', '')
        choices = kwargs.get('choices', [])
        layout = self.ids.choices
        layout.bind(minimum_height=layout.setter('height'))
        for action, text in choices:
            l = WizardButton(text=text)
            l.action = action
            l.height = '48dp'
            l.root = self
            layout.add_widget(l)

    def on_parent(self, instance, value):
        if value:
            app = App.get_running_app()
            self._back = _back = partial(app.dispatch, 'on_back')

    def get_params(self, button):
        return (button.action,)


class LineDialog(WizardDialog):
    title = StringProperty('')
    message = StringProperty('')
    warning = StringProperty('')

    def __init__(self, wizard, **kwargs):
        WizardDialog.__init__(self, wizard, **kwargs)
        self.ids.next.disabled = False

    def get_params(self, b):
        return (self.ids.passphrase_input.text,)


class ShowSeedDialog(WizardDialog):
    seed_text = StringProperty('')
    ext = False
    message = _("If you forget your PIN or lose your device, your seed phrase will be the only way to recover your funds.")

    def __init__(self, wizard, **kwargs):
        super(ShowSeedDialog, self).__init__(wizard, **kwargs)
        self.seed_text = kwargs['seed_text']

    def on_parent(self, instance, value):
        if value:
            app = App.get_running_app()
            self._back = _back = partial(self.ids.back.dispatch, 'on_release')

    def options_dialog(self):
        from .seed_options import SeedOptionsDialog
        def callback(status):
            self.ext = status

        d = SeedOptionsDialog(self.ext, callback)
        d.open()

    def get_params(self, b):
        return (self.ext,)


class WordButton(Button):
    pass


class WizardButton(Button):
    pass


class RestoreSeedDialog(WizardDialog):

    def __init__(self, wizard, **kwargs):
        super(RestoreSeedDialog, self).__init__(wizard, **kwargs)
        self._test = kwargs['test']
        from bitcoinnano.mnemonic import Mnemonic
        from bitcoinnano.old_mnemonic import words as old_wordlist
        self.words = set(Mnemonic('en').wordlist).union(set(old_wordlist))
        self.ids.text_input_seed.text = test_seed if is_test else ''
        self.message = _('Please type your seed phrase using the virtual keyboard.')
        self.title = _('Enter Seed')
        self.ext = False

        # Modifying the style of the input method
        for line in [self.ids.line1, self.ids.line2, self.ids.line3]:
            for c in line.children:
                if isinstance(c, Button):
                    c.font_size = '20sp'
                    c.font_name = 'gui/kivy/data/fonts/SourceHanSansK-Bold.ttf'

    def options_dialog(self):
        from .seed_options import SeedOptionsDialog
        def callback(status):
            self.ext = status

        d = SeedOptionsDialog(self.ext, callback)
        d.open()

    def get_suggestions(self, prefix):
        for w in self.words:
            if w.startswith(prefix):
                yield w

    def on_text(self, dt):
        self.ids.next.disabled = not bool(self._test(self.get_text()))

        text = self.ids.text_input_seed.text
        if not text:
            last_word = ''
        elif text[-1] == ' ':
            last_word = ''
        else:
            last_word = text.split(' ')[-1]

        enable_space = False
        self.ids.suggestions.clear_widgets()
        suggestions = [x for x in self.get_suggestions(last_word)]

        if last_word in suggestions:
            b = WordButton(text=last_word)
            self.ids.suggestions.add_widget(b)
            enable_space = True

        for w in suggestions:
            if w != last_word and len(suggestions) < 10:
                b = WordButton(text=w)
                self.ids.suggestions.add_widget(b)

        i = len(last_word)
        p = set()
        for x in suggestions:
            if len(x) > i: p.add(x[i])

        for line in [self.ids.line1, self.ids.line2, self.ids.line3]:
            for c in line.children:
                if isinstance(c, Button):
                    if c.text in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                        c.disabled = (c.text.lower() not in p) and last_word
                    elif c.text == ' ':
                        c.disabled = not enable_space

    def on_word(self, w):
        text = self.get_text()
        words = text.split(' ')
        words[-1] = w
        text = ' '.join(words)
        self.ids.text_input_seed.text = text + ' '
        self.ids.suggestions.clear_widgets()

    def get_text(self):
        ti = self.ids.text_input_seed
        return ' '.join(ti.text.strip().split())

    def update_text(self, c):
        c = c.lower()
        text = self.ids.text_input_seed.text
        if c == '<':
            text = text[:-1]
        else:
            text += c
        self.ids.text_input_seed.text = text

    def on_parent(self, instance, value):
        if value:
            tis = self.ids.text_input_seed
            tis.focus = True
            # tis._keyboard.bind(on_key_down=self.on_key_down)
            self._back = _back = partial(self.ids.back.dispatch,
                                         'on_release')
            app = App.get_running_app()

    def on_key_down(self, keyboard, keycode, key, modifiers):
        if keycode[0] in (13, 271):
            self.on_enter()
            return True

    def on_enter(self):
        # self._remove_keyboard()
        # press next
        next = self.ids.next
        if not next.disabled:
            next.dispatch('on_release')

    def _remove_keyboard(self):
        tis = self.ids.text_input_seed
        if tis._keyboard:
            tis._keyboard.unbind(on_key_down=self.on_key_down)
            tis.focus = False

    def get_params(self, b):
        return (self.get_text(), False, self.ext)


class ConfirmSeedDialog(RestoreSeedDialog):
    def get_params(self, b):
        return (self.get_text(),)

    def options_dialog(self):
        pass


class ShowXpubDialog(WizardDialog):

    def __init__(self, wizard, **kwargs):
        WizardDialog.__init__(self, wizard, **kwargs)
        self.xpub = kwargs['xpub']
        self.ids.next.disabled = False

    def do_copy(self):
        self.app._clipboard.copy(self.xpub)

    def do_share(self):
        self.app.do_share(self.xpub, _("Master Public Key"))

    def do_qr(self):
        from .qr_dialog import QRDialog
        popup = QRDialog(_("Master Public Key"), self.xpub, True)
        popup.open()


class AddXpubDialog(WizardDialog):

    def __init__(self, wizard, **kwargs):
        WizardDialog.__init__(self, wizard, **kwargs)
        self.is_valid = kwargs['is_valid']
        self.title = kwargs['title']
        self.message = kwargs['message']

    def check_text(self, dt):
        self.ids.next.disabled = not bool(self.is_valid(self.get_text()))

    def get_text(self):
        ti = self.ids.text_input
        return ti.text.strip()

    def get_params(self, button):
        return (self.get_text(),)

    def scan_xpub(self):
        def on_complete(text):
            self.ids.text_input.text = text

        self.app.scan_qr(on_complete)

    def do_paste(self):
        self.ids.text_input.text = test_xpub if is_test else self.app._clipboard.paste()

    def do_clear(self):
        self.ids.text_input.text = ''


class InstallWizard(BaseWizard, Widget):
    '''
    events::
        `on_wizard_complete` Fired when the wizard is done creating/ restoring
        wallet/s.
    '''

    __events__ = ('on_wizard_complete',)

    def on_wizard_complete(self, wallet):
        """overriden by main_window"""
        pass

    def waiting_dialog(self, task, msg):
        '''Perform a blocking task in the background by running the passed
        method in a thread.
        '''

        def target():
            # run your threaded function
            try:
                task()
            except Exception as err:
                self.show_error(str(err))
            # on  completion hide message
            Clock.schedule_once(lambda dt: app.info_bubble.hide(now=True), -1)

        app = App.get_running_app()
        app.show_info_bubble(
            text=msg, icon='atlas://gui/kivy/theming/light/important',
            pos=Window.center, width='200sp', arrow_pos=None, modal=True)
        t = threading.Thread(target=target)
        t.start()

    def terminate(self, **kwargs):
        self.dispatch('on_wizard_complete', self.wallet)

    def choice_dialog(self, **kwargs):
        choices = kwargs['choices']
        if len(choices) > 1:
            WizardChoiceDialog(self, **kwargs).open()
        else:
            f = kwargs['run_next']
            f(choices[0][0])

    def multisig_dialog(self, **kwargs):
        WizardMultisigDialog(self, **kwargs).open()

    def show_seed_dialog(self, **kwargs):
        ShowSeedDialog(self, **kwargs).open()

    def line_dialog(self, **kwargs):
        LineDialog(self, **kwargs).open()

    def confirm_seed_dialog(self, **kwargs):
        kwargs['title'] = _('Confirm Seed')
        kwargs['message'] = _('Please retype your seed phrase, to confirm that you properly saved it')
        ConfirmSeedDialog(self, **kwargs).open()

    def restore_seed_dialog(self, **kwargs):
        RestoreSeedDialog(self, **kwargs).open()

    def add_xpub_dialog(self, **kwargs):
        kwargs['message'] += ' ' + _('Use the camera button to scan a QR code.')
        AddXpubDialog(self, **kwargs).open()

    def add_cosigner_dialog(self, **kwargs):
        kwargs['title'] = _("Add Cosigner") + " %d" % kwargs['index']
        kwargs['message'] = _('Please paste your cosigners master public key, or scan it using the camera button.')
        AddXpubDialog(self, **kwargs).open()

    def show_xpub_dialog(self, **kwargs):
        ShowXpubDialog(self, **kwargs).open()

    def show_error(self, msg):
        app = App.get_running_app()
        Clock.schedule_once(lambda dt: app.show_error(msg))

    def password_dialog(self, message, callback):
        popup = PasswordDialog()
        popup.init(message, callback)
        popup.open()

    def request_password(self, run_next):
        def callback(pin):
            if pin:
                self.run('confirm_password', pin, run_next)
            else:
                run_next(None, None)

        self.password_dialog(_('Choose a PIN code'), callback)

    def confirm_password(self, pin, run_next):
        def callback(conf):
            if conf == pin:
                run_next(pin, False)
            else:
                self.show_error(_('PIN mismatch'))
                self.run('request_password', run_next)

        self.password_dialog(_('Confirm your PIN code'), callback)

    def action_dialog(self, action, run_next):
        f = getattr(self, action)
        f()

    def new(self):
        name = os.path.basename(self.storage.path)
        title = _("Create") + ' ' + name
        message = '\n'.join([
            _("What kind of wallet do you want to create ?")
        ])
        wallet_kinds = [
            ('standard', _("Standard wallet")),
            ('multisig', _("Multi-signature wallet")),
            ('imported', _("Import Bitcoin addresses or private keys")),
        ]
        choices = [pair for pair in wallet_kinds if pair[0] in wallet_types]
        self.choice_dialog(title=title, message=message, choices=choices, run_next=self.on_wallet_type)

    def choose_keystore(self):
        assert self.wallet_type in ['standard', 'multisig']
        i = len(self.keystores)
        title = _('Add cosigner') + ' (%d of %d)' % (i + 1, self.n) if self.wallet_type == 'multisig' else _('Keystore')
        if self.wallet_type == 'standard' or i == 0:
            message = _('Do you want to create a new seed, or to restore a wallet using an existing seed?')
            choices = [
                ('create_standard_seed', _('Create a new seed')),
                ('restore_from_seed', _('I already have a seed')),
                ('restore_from_key', _('Use public or private keys')),
            ]
            if not self.is_kivy:
                choices.append(('choose_hw_device', _('Use a hardware device')))
        else:
            message = _('Add a cosigner to your multi-sig wallet')
            choices = [
                ('restore_from_key', _('Enter cosigner key')),
                ('restore_from_seed', _('Enter cosigner seed')),
            ]
            if not self.is_kivy:
                choices.append(('choose_hw_device', _('Cosign with hardware device')))

        self.choice_dialog(title=title, message=message, choices=choices, run_next=self.run)

    def import_addresses_or_keys(self):
        v = lambda x: keystore.is_address_list(x) or keystore.is_private_key_list(x)
        title = _("Import Bitcoin Addresses")
        message = _(
            "Enter a list of Bitcoin addresses (this will create a watching-only wallet), or a list of private keys.")
        self.add_xpub_dialog(title=title, message=message, run_next=self.on_import, is_valid=v)

    def restore_from_key(self):
        if self.wallet_type == 'standard':
            v = keystore.is_master_key
            title = _("Create keystore from a master key")
            message = ' '.join([
                _("To create a watching-only wallet, please enter your master public key (xpub/ypub/zpub)."),
                _("To create a spending wallet, please enter a master private key (xprv/yprv/zprv).")
            ])
            self.add_xpub_dialog(title=title, message=message, run_next=self.on_restore_from_key, is_valid=v)
        else:
            i = len(self.keystores) + 1
            self.add_cosigner_dialog(index=i, run_next=self.on_restore_from_key, is_valid=keystore.is_bip32_key)

    def choose_hw_device(self):
        title = _('Hardware Keystore')
        # check available plugins
        support = self.plugins.get_hardware_support()
        if not support:
            msg = '\n'.join([
                _('No hardware wallet support found on your system.'),
                _('Please install the relevant libraries (eg python-trezor for Trezor).'),
            ])
            self.confirm_dialog(title=title, message=msg, run_next=lambda x: self.choose_hw_device())
            return
        # scan devices
        devices = []
        devmgr = self.plugins.device_manager
        for name, description, plugin in support:
            try:
                # FIXME: side-effect: unpaired_device_info sets client.handler
                u = devmgr.unpaired_device_infos(None, plugin)
            except:
                devmgr.print_error("error", name)
                continue
            devices += list(map(lambda x: (name, x), u))
        if not devices:
            msg = ''.join([
                _('No hardware device detected.') + '\n',
                _('To trigger a rescan, press \'Next\'.') + '\n\n',
                _(
                    'If your device is not detected on Windows, go to "Settings", "Devices", "Connected devices", and do "Remove device". Then, plug your device again.') + ' ',
                _('On Linux, you might have to add a new permission to your udev rules.'),
            ])
            self.confirm_dialog(title=title, message=msg, run_next=lambda x: self.choose_hw_device())
            return
        # select device
        self.devices = devices
        choices = []
        for name, info in devices:
            state = _("initialized") if info.initialized else _("wiped")
            label = info.label or _("An unnamed %s") % name
            descr = "%s [%s, %s]" % (label, name, state)
            choices.append(((name, info), descr))
        msg = _('Select a device') + ':'
        self.choice_dialog(title=title, message=msg, choices=choices, run_next=self.on_device)

    def derivation_dialog(self, f):
        default = bip44_derivation(0)
        message = '\n'.join([
            _('Enter your wallet derivation here.'),
            _('If you are not sure what this is, leave this field unchanged.'),
            _("If you want the wallet to use legacy Bitcoin addresses use m/44'/0'/0'"),
            _("If you want the wallet to use Bitcoin Cash addresses use m/44'/145'/0'")
        ])
        self.line_dialog(run_next=f, title=_('Derivation'), message=message, default=default,
                         test=bitcoin.is_bip32_derivation)

    def derivation_dialog_other(self, f, default_derivation):
        message = '\n'.join([
            _('Enter your wallet derivation here.'),
            _('If you are not sure what this is, leave this field unchanged.')
        ])
        self.line_dialog(run_next=f, title=_('Derivation'), message=message,
                         default=default_derivation,
                         test=bitcoin.is_bip32_derivation)

    def passphrase_dialog(self, run_next):
        title = _('Seed extension')
        message = '\n'.join([
            _('You may extend your seed with custom words.'),
            _('Your seed extension must be saved together with your seed.'),
        ])
        warning = '\n'.join([
            _('Note that this is NOT your encryption password.'),
            _('If you do not know what this is, leave this field empty.'),
        ])
        self.line_dialog(title=title, message=message, warning=warning, default='', test=lambda x: True,
                         run_next=run_next)

    def on_keystore(self, k):
        has_xpub = isinstance(k, keystore.Xpub)
        if has_xpub:
            from lib.bitcoin import xpub_type
            t1 = xpub_type(k.xpub)
        if self.wallet_type == 'standard':
            if has_xpub and t1 not in ['standard']:
                self.show_error(_('Wrong key type') + ' %s' % t1)
                self.run('choose_keystore')
                return
            self.keystores.append(k)
            self.run('create_wallet')
        elif self.wallet_type == 'multisig':
            assert has_xpub
            if t1 not in ['standard']:
                self.show_error(_('Wrong key type') + ' %s' % t1)
                self.run('choose_keystore')
                return
            if k.xpub in map(lambda x: x.xpub, self.keystores):
                self.show_error(_('Error: duplicate master public key'))
                self.run('choose_keystore')
                return
            if len(self.keystores) > 0:
                t2 = xpub_type(self.keystores[0].xpub)
                if t1 != t2:
                    self.show_error(
                        _('Cannot add this cosigner:') + '\n' + "Their key type is '%s', we are '%s'" % (t1, t2))
                    self.run('choose_keystore')
                    return
            self.keystores.append(k)
            if len(self.keystores) == 1:
                xpub = k.get_master_public_key()
                self.stack = []
                self.run('show_xpub_and_add_cosigners', xpub)
            elif len(self.keystores) < self.n:
                self.run('choose_keystore')
            else:
                self.run('create_wallet')

    def confirm_passphrase(self, seed, passphrase):
        f = lambda x: self.run('create_keystore', seed, x)
        if passphrase:
            title = _('Confirm Seed Extension')
            message = '\n'.join([
                _('Your seed extension must be saved together with your seed.'),
                _('Please type it here.'),
            ])
            self.line_dialog(run_next=f, title=title, message=message, default='', test=lambda x: x == passphrase)
        else:
            f('')

    def create_addresses(self):
        def task():
            self.wallet.synchronize()
            self.wallet.storage.write()
            self.terminate()

        msg = _("Bitcoin Nano wallet is generating your addresses, please wait.")
        self.waiting_dialog(task, msg)
