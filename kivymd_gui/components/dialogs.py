"""
Custom dialog components for the KivyMD GUI
"""

from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

class ConfirmDialog(MDDialog):
    """Confirmation dialog component"""
    
    def __init__(self, title="Confirm", text="Are you sure?", **kwargs):
        super().__init__(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    on_release=self.dismiss
                ),
                MDRaisedButton(
                    text="CONFIRM",
                    on_release=self.confirm_action
                ),
            ],
            **kwargs
        )
    
    def confirm_action(self, *args):
        """Override this method to handle confirmation"""
        self.dismiss()