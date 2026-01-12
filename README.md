# Heartopia MIDI Player

A Python script that allows you to play music inside **Heartopia** (PC only).

⚠️ **Warning:** According to the Heartopia Discord mods, any third-party software is against the ToS. Use this at your own risk there’s a chance you could get banned.

Personally, I believe this tool is harmless and mainly helps players enjoy the game.. It does **not** give any in-game advantage. Tools like this are common in social games with instrument systems.

---

## Features

* Play **MIDI files** directly in the game
* Use a **physical MIDI keyboard** (currently only white keys supported)
* Supports **15-key** and **22-key** layouts
* Playlist persistence (remembers loaded MIDI files between sessions)
* Visual keyboard display
* Simple GUI with playback controls

---

## Requirements

* Python **3.10+**
* Packages (install via pip):

```bash
pip install mido python-rtmidi keyboard
```

> `python-rtmidi` is required to use a physical MIDI keyboard.

---

## How to Run

1. Clone or download this repository:

```bash
git clone https://github.com/yourusername/Heartopia-Midi-Player.git
cd Heartopia-Midi-Player
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

4. **Using the app:**

* **Load MIDI files:** Click `Load MIDI` and select `.mid` or `.midi` files.
* **Delete:** Remove selected MIDI files from the playlist.
* **Play Selected:** Plays the selected MIDI file.
* **Play Playlist:** Plays all MIDI files in order.
* **MIDI Keyboard:** Connect a MIDI keyboard and select it from the dropdown to play live.
* **Stop:** Stops playback or live MIDI input.
* **Layout:** Choose between 15-key or 22-key layouts to match your instrument.

> The app will remember loaded MIDI files and the selected layout between sessions.

---

## Notes

* 22-key layout adds an extra low octave to match certain pianos.
* The app is intended for fun and personal use in **Heartopia** use responsibly.

---

## Contributing

Feel free to contribute! I built this in a few days, so there’s plenty of room for improvement:

* Improve the visual keyboard mapping
* Add more playback options (speed, looping, etc.)

---

## License

This project is **open-source** and free to use.
