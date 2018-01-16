from .labels import LabelsPlugin
from bitcoinnano.plugins import hook

class Plugin(LabelsPlugin):

    @hook
    def load_wallet(self, wallet, window):
        self.window = window
        self.start_wallet(wallet)

    def on_pulled(self, wallet):
        self.print_error('on pulled')
        self.window._trigger_update_history()

