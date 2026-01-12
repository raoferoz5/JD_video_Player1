[app]

# App title and package
title = DJ Video Player
package.name = djvideoplayer
package.domain = org.example

# Main source
source.dir = .
source.main = main.py

# Include python/kivy files
source.include_exts = py,kv,json

# Version
version = 1.2

# Android settings
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.ndk_api = 24
android.arch = arm64-v8a
p4a.python_version = 3.11

# Requirements
requirements = python3,kivy==2.3.1,kivymd==1.2.0,ffpyplayer,plyer

# Permissions (reading video files)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# Orientation
orientation = portrait

# Logging and debugging
log_level = 2
android.logcat = True

# Clean build each time
clean_build = True

[buildozer]

build_dir = .buildozer
bin_dir = bin
jobs = 4
verbose = 1
