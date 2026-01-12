from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivymd.uix.snackbar import Snackbar
from kivy.uix.label import Label
import os
from kivy.uix.video import Video
from kivy.logger import Logger

class VideoCard(MDCard):
    video_path = StringProperty('')
    short_name = StringProperty('')
    is_paused = BooleanProperty(True)
    seek_value = NumericProperty(0)
    card_height = NumericProperty(260)

    def __init__(self, video_path, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.video_path = video_path
        self.short_name = os.path.basename(video_path)
        self.app = app_ref
        self.video = None
        self._duration = 0
        self._seek_updating = False
        Clock.schedule_once(lambda dt: self._maybe_create_placeholder(), 0)

    def _maybe_create_placeholder(self):
        try:
            videobox = self.ids.videobox
        except Exception:
            return
        if not self.video and not any(getattr(w, 'is_placeholder', False) for w in videobox.children):
            placeholder = Label(text='Tap to play', halign='center')
            placeholder.is_placeholder = True
            videobox.clear_widgets()
            videobox.add_widget(placeholder)
            placeholder.bind(on_touch_down=self._on_placeholder_touch)

    def _on_placeholder_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.start_video()
            return True
        return False

    # Remaining methods (start_video, toggle_play, toggle_mute, on_seek_touch_up, stop_and_remove)
    # can be copied as-is from your main.py VideoCard class
