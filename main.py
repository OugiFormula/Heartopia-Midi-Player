import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import webbrowser
import mido

from midi_parser import parse_midi
from keyboard_player import KeyboardPlayer, MidiInputPlayer

# Paths
PLAYLIST_FILE = "playlist.json"
LAYOUT_FILE = "layout.json"

# App state
player = None
midi_input = None
playlist = []
current_index = None
midi_mode = False
current_layout = "22"

# Tk setup
root = tk.Tk()
root.title("Heartopia MIDI Player")
root.geometry("720x700")
root.configure(bg="#1e1e1e")

# Helpers
def set_status(text):
    status_label.config(text=text)

# Title
title_frame = tk.Frame(root, bg="#1e1e1e")
title_frame.pack(pady=(10, 2))

tk.Label(title_frame, text="Heartopia MIDI Player", fg="white",
         bg="#1e1e1e", font=("Arial", 20, "bold")).pack()
tk.Label(title_frame, text="by yukiokoito", fg="#bbbbbb",
         bg="#1e1e1e", font=("Arial", 10)).pack()

# Playlist
playlist_box = tk.Listbox(root, bg="#2e2e2e", fg="white",
                          selectbackground="#555555", font=("Arial", 12))
playlist_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

def on_playlist_select(event):
    global current_index
    sel = playlist_box.curselection()
    if sel:
        current_index = sel[0]

playlist_box.bind("<<ListboxSelect>>", on_playlist_select)

# Status
status_label = tk.Label(root, text="No files loaded", bg="#1e1e1e",
                        fg="white", font=("Arial", 12))
status_label.pack(pady=(0, 10))

# Visual keyboard
keyboard_frame = tk.LabelFrame(root, text="Visual Keyboard", bg="#1e1e1e", fg="white")
keyboard_frame.pack(fill=tk.X, padx=10, pady=5)

key_labels = {}

def build_visual_keyboard(layout):
    for w in keyboard_frame.winfo_children():
        w.destroy()
    key_labels.clear()

    if layout == "22":
        keys = ["z","x","c","v","b","n","m",
                "a","s","d","f","g","h","j",
                "q","w","e","r","t","y","u","i"]
    else:
        keys = ["a","s","d","f","g","h","j",
                "q","w","e","r","t","y","u","i"]

    for i, key in enumerate(keys):
        lbl = tk.Label(keyboard_frame, text=key.upper(), width=4, height=2,
                       bg="#2e2e2e", fg="white", relief=tk.RAISED, font=("Arial", 12))
        lbl.grid(row=0, column=i, padx=2, pady=2)
        key_labels[key] = lbl

def highlight_keys(keys):
    for lbl in key_labels.values():
        lbl.config(bg="#2e2e2e")
    for k in keys:
        if k in key_labels:
            key_labels[k].config(bg="#ff9900")

# Playback controls
def stop():
    global midi_mode
    if player:
        player.stop()
    if midi_mode and midi_input:
        midi_input.stop()
    midi_mode = False
    set_status("Stopped")
    highlight_keys([])

def load_midi():
    files = filedialog.askopenfilenames(filetypes=[("MIDI Files", "*.mid *.midi")])
    if not files:
        return
    for path in files:
        playlist.append({"name": os.path.basename(path), "path": path})
        playlist_box.insert(tk.END, os.path.basename(path))
    set_status(f"{len(playlist)} files loaded")
    save_playlist()

def delete_selected():
    global current_index
    sel = playlist_box.curselection()
    if not sel:
        return
    idx = sel[0]
    playlist_box.delete(idx)
    playlist.pop(idx)
    if playlist:
        current_index = min(idx, len(playlist)-1)
        playlist_box.select_set(current_index)
    else:
        current_index = None
        set_status("No files loaded")
    save_playlist()

def play_selected():
    global midi_mode
    stop()
    midi_mode = False
    if current_index is None:
        messagebox.showwarning("Play", "Select a MIDI file first")
        return
    try:
        events = parse_midi(playlist[current_index]["path"])
    except Exception as e:
        messagebox.showerror("MIDI Error", str(e))
        return
    set_status(f"Playing: {playlist[current_index]['name']}")
    player.play(events, on_key_press=highlight_keys)

def play_playlist():
    global midi_mode
    stop()
    midi_mode = False
    def play_next(idx):
        if idx >= len(playlist):
            set_status("Playlist finished")
            return
        playlist_box.select_clear(0, tk.END)
        playlist_box.select_set(idx)
        playlist_box.activate(idx)
        try:
            events = parse_midi(playlist[idx]["path"])
        except Exception as e:
            messagebox.showerror("MIDI Error", str(e))
            play_next(idx+1)
            return
        set_status(f"Playing: {playlist[idx]['name']}")
        player.play(events, on_key_press=highlight_keys)
        # approximate next
        root.after(int(sum(d[0] for d in events)*1000)+50, lambda: play_next(idx+1))
    play_next(current_index or 0)

# MIDI keyboard
device_frame = tk.Frame(root, bg="#1e1e1e")
device_frame.pack(pady=5)

tk.Label(device_frame, text="MIDI Device:", bg="#1e1e1e", fg="white").grid(row=0, column=0, padx=5)

midi_device_var = tk.StringVar()
device_box = ttk.Combobox(device_frame, textvariable=midi_device_var, width=45)
device_box.grid(row=0, column=1, padx=5)

def refresh_devices():
    try:
        ports = mido.get_input_names()
    except Exception:
        ports = []
    if not ports:
        ports = ["No MIDI devices"]
    device_box["values"] = ports
    midi_device_var.set(ports[0])

def start_midi_keyboard():
    global midi_input, midi_mode
    stop()
    midi_mode = True
    port = midi_device_var.get()
    if not port or port == "No MIDI devices":
        messagebox.showerror("MIDI", "No MIDI device available")
        return
    midi_input = MidiInputPlayer(layout=current_layout, on_key_press=highlight_keys)
    midi_input.start(port)
    set_status(f"MIDI Keyboard: {port}")

refresh_devices()

# Layout switch
layout_var = tk.StringVar(value="22 Keys")

def apply_layout():
    global player, current_layout
    # safe stop
    if player:
        stop()
    current_layout = "22" if "22" in layout_var.get() else "15"
    player = KeyboardPlayer(layout=current_layout)
    build_visual_keyboard(current_layout)
    save_layout()

layout_menu = ttk.Combobox(root, textvariable=layout_var,
                           values=["15 Keys","22 Keys"], state="readonly", width=10)
layout_menu.pack(pady=5)
layout_menu.bind("<<ComboboxSelected>>", lambda e: apply_layout())

# Buttons
btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=5)

buttons = [
    ("Load MIDI", load_midi),
    ("Delete", delete_selected),
    ("Play Selected", play_selected),
    ("Play Playlist", play_playlist),
    ("MIDI Keyboard", start_midi_keyboard),
    ("Stop", stop)
]

for i, (text, cmd) in enumerate(buttons):
    tk.Button(btn_frame, text=text, command=cmd, bg="#333333", fg="white", width=12).grid(row=0, column=i, padx=4)

# Footer
tk.Frame(root, bg="#444444", height=1).pack(fill=tk.X, pady=10)

footer = tk.Frame(root, bg="#1e1e1e")
footer.pack(fill=tk.X, padx=10)

tk.Label(footer, text="v0.1.1", fg="#aaaaaa", bg="#1e1e1e").pack(side=tk.LEFT)
tk.Button(footer, text="Ko-fi", command=lambda: webbrowser.open("https://ko-fi.com/yukiokoito"),
          bg="#333333", fg="white").pack(side=tk.RIGHT)

# Saving songs
def save_playlist():
    with open(PLAYLIST_FILE, "w") as f:
        json.dump([p["path"] for p in playlist], f)

def load_saved_playlist():
    if os.path.exists(PLAYLIST_FILE):
        try:
            with open(PLAYLIST_FILE, "r") as f:
                paths = json.load(f)
            for path in paths:
                if os.path.exists(path):
                    playlist.append({"name": os.path.basename(path), "path": path})
                    playlist_box.insert(tk.END, os.path.basename(path))
            if playlist:
                set_status(f"{len(playlist)} files loaded")
        except Exception:
            pass

def save_layout():
    with open(LAYOUT_FILE, "w") as f:
        json.dump({"layout": current_layout}, f)

def load_layout():
    global current_layout
    if os.path.exists(LAYOUT_FILE):
        try:
            with open(LAYOUT_FILE, "r") as f:
                data = json.load(f)
                current_layout = data.get("layout", "22")
        except Exception:
            pass

# Init
load_layout()
player = KeyboardPlayer(layout=current_layout)
build_visual_keyboard(current_layout)
load_saved_playlist()

root.mainloop()
