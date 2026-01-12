import os
from kivy.lang import Builder
from kivy.uix.video import Video
from kivymd.app import MDApp
from widgets.video_thumb import VideoThumbButton

class DJVideoPlayerApp(MDApp):
    video_dir = os.path.join(os.getcwd(), "Videos")

    def build(self):
        self.root = Builder.load_file("main.kv")
        self.load_videos()
        return self.root

    def load_videos(self):
        # List all video files in the Videos folder
        video_files = [f for f in os.listdir(self.video_dir)
                       if f.endswith(('.mp4', '.mov', '.avi'))]

        if not video_files:
            print("🎥 No videos found!")
            return
        print(f"🎞️ Found {len(video_files)} videos")

        # Create a VideoThumbButton for each video
        for video in video_files:
            video_path = os.path.join(self.video_dir, video)
            thumb = VideoThumbButton(video_path)
            thumb.bind(on_release=lambda btn, path=video_path: self.play_video(path))
            self.root.ids.video_list.add_widget(thumb)

    def play_video(self, path):
        video_player = self.root.ids.video_player
        video_player.source = path
        video_player.state = 'play'

if __name__ == "__main__":
    DJVideoPlayerApp().run()
