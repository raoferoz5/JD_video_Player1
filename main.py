import os
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.video import Video
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.slider import Slider
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.app import App
# For volume control
from kivy.core.audio import SoundLoader
from plyer import brightness

# ---------- Screens ----------

class MainPickerScreen(Screen):
    video_files = []
    current_index = NumericProperty(0)

    def on_enter(self):
        Clock.schedule_once(self.load_videos, 0.1)

    def load_videos(self, dt):
        self.video_folder = os.path.join(os.getcwd(), "Videos")
        if not os.path.exists(self.video_folder):
            os.makedirs(self.video_folder)

        self.video_files = [f for f in os.listdir(self.video_folder) if f.endswith(('.mp4', '.mov', '.avi'))]

        grid = self.ids.grid_videos
        grid.clear_widgets()

        for idx, filename in enumerate(self.video_files):
            thumb_path = f"thumbnails/{os.path.splitext(filename)[0]}.png"
            if not os.path.exists(thumb_path):
                thumb_path = "thumbnails/default.png"

            btn = VideoThumbButton(
                title_text=filename,
                thumb_source=thumb_path,
                video_path=os.path.join(self.video_folder, filename),
                index=idx
            )
            grid.add_widget(btn)

    def filter_videos(self, text):
        for child in self.ids.grid_videos.children:
            child.opacity = 1 if text.lower() in child.title_text.lower() else 0
            child.disabled = False if text.lower() in child.title_text.lower() else True


class VideoPlayerScreen(Screen):
    short_name = StringProperty("Video Player")
    video_widget = None
    current_index = NumericProperty(0)
    video_files = []
    is_fullscreen = BooleanProperty(False)
    overlay_visible = BooleanProperty(True)
    touch_start_x = NumericProperty(0)
    touch_start_y = NumericProperty(0)
    initial_volume = NumericProperty(50)
    initial_brightness = NumericProperty(50)

    def load_video(self, video_path, title="Video Player", index=0, all_videos=[]):
        self.short_name = title
        self.ids.v_container.clear_widgets()
        self.video_files = all_videos
        self.current_index = index

        # FloatLayout to allow overlay controls
        layout = FloatLayout()
        self.video_widget = Video(source=video_path, state='play', options={'eos': 'stop'})
        layout.add_widget(self.video_widget)

        # Overlay controls
        overlay = self.create_overlay()
        layout.add_widget(overlay)
        self.overlay = overlay
        layout.bind(on_touch_down=self.on_video_touch, on_touch_move=self.on_video_move, on_touch_up=self.on_video_up)

        self.ids.v_container.add_widget(layout)
        self.show_overlay(True)

    # ---------- Overlay Controls ----------
    def create_overlay(self):
        from kivy.uix.boxlayout import BoxLayout
        from kivymd.uix.button import MDIconButton
        from kivymd.uix.slider import MDSlider

        overlay = BoxLayout(
            size_hint=(1, None),
            height=80,
            orientation='horizontal',
            padding=8,
            spacing=8,
            pos_hint={'top': 1}
        )

        self.play_btn = MDIconButton(icon='play', on_release=lambda x: self.toggle_play())
        prev_btn = MDIconButton(icon='skip-previous', on_release=lambda x: self.play_prev())
        next_btn = MDIconButton(icon='skip-next', on_release=lambda x: self.play_next())
        self.seek_slider = MDSlider(min=0, max=100, value=0)
        self.seek_slider.bind(on_touch_up=lambda s, touch: self.seek_video(s.value) if s.collide_point(*touch.pos) else None)
        fullscreen_btn = MDIconButton(icon='fullscreen', on_release=lambda x: self.toggle_fullscreen())

        overlay.add_widget(prev_btn)
        overlay.add_widget(self.play_btn)
        overlay.add_widget(next_btn)
        overlay.add_widget(self.seek_slider)
        overlay.add_widget(fullscreen_btn)

        return overlay

    def show_overlay(self, show=True):
        self.overlay_visible = show
        self.overlay.opacity = 1 if show else 0
        self.overlay.disabled = not show
        if show:
            Clock.unschedule(self.hide_overlay)
            Clock.schedule_once(self.hide_overlay, 4)  # auto-hide after 4 seconds

    def hide_overlay(self, dt=None):
        self.overlay.opacity = 0
        self.overlay.disabled = True
        self.overlay_visible = False

    # ---------- Video Control ----------
    def toggle_play(self):
        if self.video_widget:
            self.video_widget.state = 'pause' if self.video_widget.state == 'play' else 'play'
            self.play_btn.icon = 'play' if self.video_widget.state == 'pause' else 'pause'

    def play_next(self):
        if self.current_index + 1 < len(self.video_files):
            self.current_index += 1
            self.load_video(
                self.video_files[self.current_index],
                os.path.basename(self.video_files[self.current_index]),
                self.current_index,
                self.video_files
            )

    def play_prev(self):
        if self.current_index - 1 >= 0:
            self.current_index -= 1
            self.load_video(
                self.video_files[self.current_index],
                os.path.basename(self.video_files[self.current_index]),
                self.current_index,
                self.video_files
            )

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        Window.fullscreen = 'auto' if self.is_fullscreen else False

    def seek_video(self, value):
        if self.video_widget and self.video_widget.duration > 0:
            self.video_widget.position = (value / 100) * self.video_widget.duration

    def close_player(self):
        if self.video_widget:
            self.video_widget.state = 'stop'
        if self.is_fullscreen:
            self.toggle_fullscreen()
        self.manager.current = "picker"

    # ---------- Gesture Handling ----------
    def on_video_touch(self, instance, touch):
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        touch.ud['volume_brightness'] = None
        touch.ud['time'] = touch.time_start
        return False

    def on_video_move(self, instance, touch):
        dx = touch.x - self.touch_start_x
        dy = touch.y - self.touch_start_y

        # Vertical swipe for volume/brightness
        if abs(dy) > abs(dx):
            if touch.x > Window.width / 2:  # right side -> volume
                change = dy / Window.height * 100
                self.set_volume(self.initial_volume + change)
                touch.ud['volume_brightness'] = 'volume'
            else:  # left side -> brightness
                change = dy / Window.height * 100
                self.set_brightness(self.initial_brightness + change)
                touch.ud['volume_brightness'] = 'brightness'

    def on_video_up(self, instance, touch):
        # Save initial volume/brightness for next gesture
        if touch.ud.get('volume_brightness') == 'volume':
            self.initial_volume = Window.volume if hasattr(Window, 'volume') else self.initial_volume
        elif touch.ud.get('volume_brightness') == 'brightness':
            self.initial_brightness = brightness.brightness if hasattr(brightness, 'brightness') else self.initial_brightness

        # Tap detection
        dx = touch.x - self.touch_start_x
        dy = touch.y - self.touch_start_y
        dt = touch.time_end - touch.ud.get('time', 0.01)

        if abs(dx) < 10 and abs(dy) < 10:
            self.show_overlay(not self.overlay_visible)

        # Double-tap
        if dt < 0.3 and abs(dx) < 10 and abs(dy) < 10:
            self.toggle_fullscreen()

        # Horizontal swipe for next/prev video
        if abs(dx) > 50 and abs(dy) < 100:
            if dx > 0:
                self.play_prev()
            else:
                self.play_next()

    # ---------- Volume/Brightness ----------
    def set_volume(self, value):
        value = max(0, min(100, value))
        # If you use plyer audio or custom volume handler, implement here
        # Placeholder: print
        print(f"Volume: {value}%")

    def set_brightness(self, value):
        value = max(0, min(100, value))
        try:
            brightness.brightness = value / 100.0
        except Exception:
            pass
        print(f"Brightness: {value}%")

# ---------- Video Thumb ----------
class VideoThumbButton(ButtonBehavior, BoxLayout):
    title_text = StringProperty("")
    thumb_source = StringProperty("")
    video_path = StringProperty("")
    index = NumericProperty(0)

    def on_release(self):
        app = App.get_running_app()
        player = app.root.get_screen("player")  # Safe way to get VideoPlayerScreen
        all_videos = [child.video_path for child in self.parent.children[::-1]]
        player.load_video(self.video_path, self.title_text, self.index, all_videos)
        app.root.current = "player"


# ---------- App ----------
class DJVideoPlayerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "DeepPurple"
        return Builder.load_file("main.kv")


if __name__ == "__main__":
    DJVideoPlayerApp().run()
