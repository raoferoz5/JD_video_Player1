from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

class MainPickerScreen(Screen):
    def filter_videos(self, text):
        app = MDApp.get_running_app()
        app.filter_and_render(text)
