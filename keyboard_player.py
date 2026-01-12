import time
import keyboard
import threading
import mido

# Key mappings for 15-key and 22-key modes
NOTE_TO_KEY_15 = {
    ("C", 4): "a",
    ("D", 4): "s",
    ("E", 4): "d",
    ("F", 4): "f",
    ("G", 4): "g",
    ("A", 4): "h",
    ("B", 4): "j",

    ("C", 5): "q",
    ("D", 5): "w",
    ("E", 5): "e",
    ("F", 5): "r",
    ("G", 5): "t",
    ("A", 5): "y",
    ("B", 5): "u",

    ("C", 6): "i",
}

NOTE_TO_KEY_22 = {
    # Low octave for piano
    ("C", 3): "z",
    ("D", 3): "x",
    ("E", 3): "c",
    ("F", 3): "v",
    ("G", 3): "b",
    ("A", 3): "n",
    ("B", 3): "m",

    ("C", 4): "a",
    ("D", 4): "s",
    ("E", 4): "d",
    ("F", 4): "f",
    ("G", 4): "g",
    ("A", 4): "h",
    ("B", 4): "j",

    ("C", 5): "q",
    ("D", 5): "w",
    ("E", 5): "e",
    ("F", 5): "r",
    ("G", 5): "t",
    ("A", 5): "y",
    ("B", 5): "u",

    ("C", 6): "i",
}

MIN_OCTAVE = 1
MAX_OCTAVE = 6

# KeyboardPlayer: plays MIDI files
class KeyboardPlayer:
    def __init__(self, layout="15"):
        self.stop_flag = False
        self.thread = None
        self.set_layout(layout)

    def set_layout(self, layout):
        self.layout = layout
        self.note_map = NOTE_TO_KEY_22 if layout == "22" else NOTE_TO_KEY_15

    def stop(self):
        self.stop_flag = True

    def get_playable_key(self, note):
        name, octave = note
        # Adjust octave to match playable keys
        while (name, octave) not in self.note_map and octave < MAX_OCTAVE:
            octave += 1
        while (name, octave) not in self.note_map and octave > MIN_OCTAVE:
            octave -= 1
        return self.note_map.get((name, octave))

    def play(self, events, speed=1.0, on_key_press=None):
        self.stop_flag = False

        def run():
            for delay, notes in events:
                if self.stop_flag:
                    break
                time.sleep(delay / speed)
                keys = []
                for note in notes:
                    key = self.get_playable_key(note)
                    if key:
                        keys.append(key)
                for k in keys:
                    keyboard.press(k)
                if on_key_press:
                    on_key_press(keys)
                time.sleep(0.03)
                for k in keys:
                    keyboard.release(k)
                if on_key_press:
                    on_key_press([])

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

# MidiInputPlayer: live MIDI keyboard
class MidiInputPlayer:
    def __init__(self, note_to_key=None, on_key_press=None, transpose=0, tap_length=0.03):
        self.note_to_key = note_to_key if note_to_key else NOTE_TO_KEY_15
        self.on_key_press = on_key_press
        self.transpose = transpose
        self.tap_length = tap_length
        self.stop_flag = False
        self.thread = None

    def stop(self):
        self.stop_flag = True

    def start(self, port_name=None):
        self.stop_flag = False
        self.thread = threading.Thread(target=self.run, args=(port_name,), daemon=True)
        self.thread.start()

    def run(self, port_name):
        try:
            if port_name is None:
                ports = mido.get_input_names()
                if not ports:
                    print("No MIDI input found.")
                    return
                port_name = ports[0]

            with mido.open_input(port_name) as inport:
                for msg in inport:
                    if self.stop_flag:
                        break
                    if msg.type == 'note_on' and msg.velocity > 0:
                        key = self.get_playable_key(msg.note)
                        if key:
                            keyboard.press(key)
                            if self.on_key_press:
                                self.on_key_press([key])
                            keyboard.release(key)
                            if self.on_key_press:
                                self.on_key_press([])
        except Exception as e:
            print(f"MIDI input error: {e}")

    def get_playable_key(self, midi_note):
        NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
                      "F#", "G", "G#", "A", "A#", "B"]
        midi_note += self.transpose
        name = NOTE_NAMES[midi_note % 12]
        octave = midi_note // 12 - 1

        while (name, octave) not in self.note_to_key and octave < MAX_OCTAVE:
            octave += 1
        while (name, octave) not in self.note_to_key and octave > MIN_OCTAVE:
            octave -= 1
        return self.note_to_key.get((name, octave))
