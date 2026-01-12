from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp

class VideoPlayerScreen(Screen):
    short_name = StringProperty('')
    player_video = ObjectProperty(None)

    def on_pre_enter(self):
        self.ids.v_container.clear_widgets()
        if self.player_video:
            self.ids.v_container.add_widget(self.player_video)

    def set_video_widget(self, widget, title):
        self.player_video = widget
        self.short_name = title

    def toggle_play(self):
        if not self.player_video: return
        try:
            if getattr(self.player_video, 'state', '') == 'play':
                self.player_video.state = 'pause'
                self.ids.play_btn.icon = 'play'
            else:
                self.player_video.state = 'play'
                self.ids.play_btn.icon = 'pause'
        except Exception:
            pass

    def play_next(self):
        MDApp.get_running_app().player_next()

    def play_prev(self):
        MDApp.get_running_app().player_prev()

    def close_player(self):
        MDApp.get_running_app().close_player()

    def on_touch_move(self, touch):
        if touch.dx < -40:
            self.play_next()
        elif touch.dx > 40:
            self.play_prev()
        return super().on_touch_move(touch)
