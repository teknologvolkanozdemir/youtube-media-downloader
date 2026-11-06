# YouTube Media Downloader

An accessible, lightweight YouTube video, playlist, and channel downloader built with Python and GTK 3, specifically designed for Raspberry Pi OS with full Orca screen reader (ATK/AT-SPI2) support.

Raspberry Pi OS için geliştirilmiş; tek video, oynatma listesi (playlist) ve kanal indirme özelliklerine sahip, Orca ekran okuyucusuyla %100 erişilebilir Python ve GTK 3 tabanlı indirme uygulaması.

---

## Features / Özellikler

* **Full Accessibility (Tam Erişilebilirlik):** Built with native GTK 3 widgets and ATK hooks for seamless Orca screen reader navigation.
* **Multiple Download Targets (Çeşitli İndirme Hedefleri):** Download single videos, entire playlists, or full channels.
* **Format Options (Format Seçenekleri):** Extract audio as MP3 or download video in MP4 format.
* **Raspberry Pi OS Integration:** Fully compatible with Pi-Apps and Debian packaging standards (`.deb`).

---

## Dependencies / Gereksinimler

* `python3`
* `python3-gi` (PyGObject)
* `yt-dlp`
* `ffmpeg`
* `at-spi2-core`

---

## Installation / Kurulum

### Installing via `.deb` package
Download the latest `.deb` package from the repository or build it locally, then run:

```bash
sudo apt update
sudo apt install ./yt-downloader_1.0.0_all.deb