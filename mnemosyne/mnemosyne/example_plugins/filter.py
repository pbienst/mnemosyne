#
# filter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin


class Uppercase(Filter):

    def run(self, text, **render_args):
        # Note: if you need access to the current card in your filter, use
        # 'self.review_controller().card'
        return text.upper()


class UppercasePlugin(Plugin):
    
    name = "Uppercase"
    description = "Make all your card text uppercase"   
    components = [Uppercase]
    
    def activate(self):
        Plugin.activate(self)
        self.render_chain("default").\
            register_filter(Uppercase, in_front=False)
        # Other chain you might want to add to is e.g. "card_browser".
        
    def deactivate(self):
        Plugin.deactivate(self)
        self.render_chain("default").\
            unregister_filter(Uppercase)      

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(UppercasePlugin)
