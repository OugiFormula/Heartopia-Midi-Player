import mido
from collections import defaultdict

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]

def midi_to_note(midi_note: int):
    name = NOTE_NAMES[midi_note % 12]
    octave = midi_note // 12 - 1
    return name, octave

def snap_to_scale(note_name: str):
    """Convert sharps/flats to nearest diatonic note"""
    mapping = {
        "C#": "D",
        "D#": "E",
        "F#": "G",
        "G#": "A",
        "A#": "B"
    }
    return mapping.get(note_name, note_name)

def parse_midi(path: str):
    """
    Returns a list of (delay_seconds, [ (note_name, octave), ... ])
    """
    mid = mido.MidiFile(path)
    events = []
    current_time = 0.0

    buffer = defaultdict(list)

    for msg in mid:
        current_time += msg.time

        if msg.type == "note_on" and msg.velocity > 0:
            name, octave = midi_to_note(msg.note)
            name = snap_to_scale(name)
            buffer[current_time].append((name, octave))

    last_time = 0.0
    for t in sorted(buffer.keys()):
        delay = t - last_time
        events.append((delay, buffer[t]))
        last_time = t

    return events
