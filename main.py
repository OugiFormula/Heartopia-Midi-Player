import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import mido

from midi_parser import parse_midi
from keyboard_player import KeyboardPlayer, MidiInputPlayer

player = KeyboardPlayer()
midi_input = None
playlist = []
current_index = None
midi_mode = False

root = tk.Tk()
root.title("Heartopia MIDI Player")
root.geometry("720x650")
root.configure(bg="#1e1e1e")

def set_status(text):
    status_label.config(text=text)

# Playlist box
playlist_box = tk.Listbox(root, bg="#2e2e2e", fg="white",
                          selectbackground="#555555", font=("Arial", 12))
playlist_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,5))

# Bind selection to update current_index
def on_playlist_select(event):
    global current_index
    selected = playlist_box.curselection()
    if selected:
        current_index = selected[0]

playlist_box.bind('<<ListboxSelect>>', on_playlist_select)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=10, pady=(0,10))

# Status label
status_label = tk.Label(root, text="No files loaded", bg="#1e1e1e",
                        fg="white", font=("Arial", 12))
status_label.pack(pady=(0,10))

# Visual keyboard
keyboard_frame = tk.LabelFrame(root, text="Visual Keyboard", bg="#1e1e1e", fg="white")
keyboard_frame.pack(fill=tk.X, padx=10, pady=5)

GAME_KEYS = ["q","w","e","r","t","y","u","i","a","s","d","f","g","h","j"]
key_labels = {}
for i, key in enumerate(GAME_KEYS):
    lbl = tk.Label(keyboard_frame, text=key.upper(), width=4, height=2,
                   bg="#2e2e2e", fg="white", relief=tk.RAISED, font=("Arial",12))
    lbl.grid(row=0, column=i, padx=2, pady=2)
    key_labels[key] = lbl

def highlight_keys(keys):
    for lbl in key_labels.values():
        lbl.config(bg="#2e2e2e")
    for k in keys:
        lbl = key_labels.get(k)
        if lbl:
            lbl.config(bg="#ff9900")

# Load / Delete / Play
def load_midi():
    files = filedialog.askopenfilenames(filetypes=[("MIDI Files", "*.mid *.midi")])
    if not files:
        return
    for path in files:
        playlist.append({
            "name": os.path.basename(path),
            "path": path,
            "events": []
        })
        playlist_box.insert(tk.END, os.path.basename(path))
    if playlist:
        set_status(f"{len(playlist)} files loaded")
        playlist_box.select_clear(0, tk.END)
        playlist_box.select_set(0)
        playlist_box.activate(0)
        global current_index
        current_index = 0

def delete_selected():
    global current_index
    selected = playlist_box.curselection()
    if not selected:
        messagebox.showwarning("Delete file", "Please select a file to delete")
        return
    idx = selected[0]
    playlist_box.delete(idx)
    playlist.pop(idx)
    if playlist:
        current_index = min(idx, len(playlist)-1)
        playlist_box.select_set(current_index)
        playlist_box.activate(current_index)
    else:
        current_index = None
        set_status("No files loaded")
        progress_var.set(0)

def play_selected():
    global midi_mode
    stop()
    midi_mode = False
    if current_index is None:
        messagebox.showwarning("Select file", "Please select a file to play")
        return
    idx = current_index
    events = parse_midi(playlist[idx]["path"])
    playlist[idx]["events"] = events
    play_file(idx)

def play_playlist():
    global midi_mode
    stop()
    midi_mode = False
    def play_next(idx):
        if idx >= len(playlist):
            set_status("Playlist finished")
            progress_var.set(0)
            return
        playlist_box.select_clear(0, tk.END)
        playlist_box.select_set(idx)
        playlist_box.activate(idx)
        events = parse_midi(playlist[idx]["path"])
        playlist[idx]["events"] = events
        play_file(idx, on_finished=lambda: play_next(idx + 1))
    start_idx = current_index if current_index is not None else 0
    play_next(start_idx)

def play_file(idx, on_finished=None):
    set_status(f"Playing: {playlist[idx]['name']}")
    player.play(
        playlist[idx]["events"],
        speed=1.0,
        on_key_press=highlight_keys
    )

def stop():
    global midi_mode
    player.stop()
    if midi_mode and midi_input:
        midi_input.stop()
    set_status("Stopped")
    progress_var.set(0)

device_frame = tk.Frame(root, bg="#1e1e1e")
device_frame.pack(pady=5)

tk.Label(device_frame, text="Select MIDI Device:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)

midi_device_var = tk.StringVar()
midi_device_dropdown = ttk.Combobox(device_frame, textvariable=midi_device_var, width=50)
midi_device_dropdown.grid(row=0, column=1, padx=5)

def refresh_midi_devices():
    try:
        ports = mido.get_input_names()
    except Exception:
        ports = []
    if not ports:
        ports = ["No MIDI input found"]
    midi_device_dropdown['values'] = ports
    midi_device_var.set(ports[0])

refresh_midi_devices()

tk.Button(device_frame, text="Refresh Devices", command=refresh_midi_devices,
          bg="#333333", fg="white").grid(row=0, column=2, padx=5)

def start_midi_keyboard():
    global midi_input, midi_mode
    stop()
    midi_mode = True
    port_name = midi_device_var.get()
    if port_name == "No MIDI input found":
        messagebox.showerror("MIDI Keyboard", "No MIDI device available.")
        return
    midi_input = MidiInputPlayer(on_key_press=highlight_keys)
    midi_input.start(port_name=port_name)
    set_status(f"MIDI Keyboard Mode Active ({port_name})")

# --- Buttons ---
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=5)

tk.Button(button_frame, text="Load MIDI", command=load_midi, bg="#333333", fg="white", width=12).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Delete Selected", command=delete_selected, bg="#333333", fg="white", width=12).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Play Selected", command=play_selected, bg="#333333", fg="white", width=12).grid(row=0, column=2, padx=5)
tk.Button(button_frame, text="Play Playlist", command=play_playlist, bg="#333333", fg="white", width=12).grid(row=0, column=3, padx=5)
tk.Button(button_frame, text="MIDI Keyboard", command=start_midi_keyboard, bg="#333333", fg="white", width=12).grid(row=0, column=4, padx=5)
tk.Button(button_frame, text="Stop", command=stop, bg="#333333", fg="white", width=12).grid(row=0, column=5, padx=5)

root.mainloop()
