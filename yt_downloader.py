#!/usr/bin/env python3
import sys
import os
import threading
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Atk

class MediaDownloaderApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="YouTube Media Downloader")
        self.set_default_size(550, 450)
        self.set_border_width(15)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.add(main_box)

        url_label = Gtk.Label(label="YouTube URL (Video, Playlist or Channel):")
        url_label.set_halign(Gtk.Align.START)
        main_box.pack_start(url_label, False, False, 0)

        self.url_entry = Gtk.Entry()
        self.url_entry.set_placeholder_text("https://www.youtube.com/...")
        main_box.pack_start(self.url_entry, False, False, 0)

        url_accessible = self.url_entry.get_accessible()
        url_accessible.set_name("YouTube URL Entry")
        url_accessible.set_description("Enter YouTube video, playlist, or channel URL")

        target_label = Gtk.Label(label="Download Target:")
        target_label.set_halign(Gtk.Align.START)
        main_box.pack_start(target_label, False, False, 0)

        target_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(target_box, False, False, 0)

        self.radio_single = Gtk.RadioButton.new_with_label(None, "Single Video")
        target_box.pack_start(self.radio_single, False, False, 0)

        self.radio_playlist = Gtk.RadioButton.new_with_label_from_widget(self.radio_single, "Entire Playlist")
        target_box.pack_start(self.radio_playlist, False, False, 0)

        self.radio_channel = Gtk.RadioButton.new_with_label_from_widget(self.radio_single, "Entire Channel")
        target_box.pack_start(self.radio_channel, False, False, 0)

        format_label = Gtk.Label(label="Download Format:")
        format_label.set_halign(Gtk.Align.START)
        main_box.pack_start(format_label, False, False, 0)

        format_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.pack_start(format_box, False, False, 0)

        self.radio_mp4 = Gtk.RadioButton.new_with_label(None, "Video (MP4)")
        format_box.pack_start(self.radio_mp4, False, False, 0)

        self.radio_mp3 = Gtk.RadioButton.new_with_label_from_widget(self.radio_mp4, "Audio (MP3)")
        format_box.pack_start(self.radio_mp3, False, False, 0)

        self.status_label = Gtk.Label(label="Status: Ready")
        self.status_label.set_halign(Gtk.Align.START)
        main_box.pack_start(self.status_label, False, False, 0)

        status_accessible = self.status_label.get_accessible()
        status_accessible.set_name("Status Indicator")

        self.download_btn = Gtk.Button(label="Start Download")
        self.download_btn.connect("clicked", self.on_download_clicked)
        main_box.pack_start(self.download_btn, False, False, 0)

        btn_accessible = self.download_btn.get_accessible()
        btn_accessible.set_name("Start Download Button")

    def on_download_clicked(self, widget):
        url = self.url_entry.get_text().strip()
        if not url:
            self.show_message_dialog(Gtk.MessageType.WARNING, "Warning", "Please enter a valid URL.")
            return

        self.download_btn.set_sensitive(False)
        self.update_status("Status: Initializing download...")

        fmt = "mp3" if self.radio_mp3.get_active() else "mp4"

        if self.radio_single.get_active():
            target_type = "single"
        elif self.radio_playlist.get_active():
            target_type = "playlist"
        else:
            target_type = "channel"

        thread = threading.Thread(target=self.download_process, args=(url, fmt, target_type))
        thread.daemon = True
        thread.start()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            GLib.idle_add(self.update_status, f"Status: Downloading... {percent}")
        elif d['status'] == 'finished':
            GLib.idle_add(self.update_status, "Status: Processing media conversion...")

    def update_status(self, text):
        self.status_label.set_text(text)
        acc = self.status_label.get_accessible()
        acc.notify_state_change(Atk.StateType.SHOWING, True)

    def download_process(self, url, fmt, target_type):
        import yt_dlp
        download_path = os.path.expanduser("~/Downloads")

        ydl_opts = {
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'quiet': False,
            'no_warnings': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        if target_type == "single":
            ydl_opts['noplaylist'] = True
            ydl_opts['outtmpl'] = os.path.join(download_path, '%(title)s.%(ext)s')
        elif target_type == "playlist":
            ydl_opts['outtmpl'] = os.path.join(download_path, 'Playlists/%(playlist_title)s/%(title)s.%(ext)s')
        else:
            ydl_opts['outtmpl'] = os.path.join(download_path, 'Channels/%(uploader)s/%(title)s.%(ext)s')

        if fmt == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            GLib.idle_add(self.download_complete, True, "Download completed successfully. Saved to Downloads folder.")
        except Exception as e:
            GLib.idle_add(self.download_complete, False, str(e))

    def download_complete(self, success, message):
        self.download_btn.set_sensitive(True)
        if success:
            self.update_status("Status: Download Complete")
            self.show_message_dialog(Gtk.MessageType.INFO, "Success", message)
        else:
            self.update_status("Status: Error Occurred")
            self.show_message_dialog(Gtk.MessageType.ERROR, "Error", f"Download failed: {message}")

    def show_message_dialog(self, message_type, title, text):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()

if __name__ == "__main__":
    app = MediaDownloaderApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()
