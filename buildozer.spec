[app]

# (str) Title of your application
title = LWUP

# (str) Package name
package.name = lwup

# (str) Application version
version = 1.0.0

# (str) Package domain (unique identifier)
package.domain = org.zsy

# (str) Source code directory
source.dir = .

# (list) Source file extensions to include
source.include_exts = py,png,jpg,jpeg,gif,wav,ttf,ico,txt

# (list) Requirements (Python packages for Android)
requirements = python3,kivy==2.3.1,kivymd==1.2.0,requests,Pillow

# (str) Application icon
icon.filename = assets/icon.png

# (str) Splash screen
presplash.filename = assets/icon.png

# (str) Orientation
orientation = portrait

# (list) Android permissions
android.permissions = INTERNET

# (int) Android API level
android.api = 34

# (int) Minimum API level
android.minapi = 21

# (int) Android SDK version
android.sdk = 34

# (str) Android NDK version
android.ndk = 27c

# (bool) Enable AndroidX
android.enable_androidx = True

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Target architecture
android.archs = arm64-v8a

# (bool) GStreamer support
android.gstreamer = False

# (int) Log level (0=error, 1=warning, 2=info, 3=debug)
log_level = 2

[buildozer]

# (int) Log level
log_level = 2

# (int) Max build threads
build_max = 4
