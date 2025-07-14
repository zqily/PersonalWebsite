import tkinter as tk
import keyboard  # For capturing global key presses

class OBSStatusOverlay:
    def __init__(self, root):
        self.root = root
        root.overrideredirect(True)  # Remove window decorations (borders, title bar)
        root.attributes('-topmost', True)  # Keep window on top
        root.attributes('-transparentcolor', 'white') # Make 'white' color transparent
        # For click-through, we need to bind mouse events and stop propagation
        root.bind("<Button-1>", lambda event: "break")
        root.bind("<ButtonRelease-1>", lambda event: "break")
        root.bind("<Motion>", lambda event: "break")

        self.canvas = tk.Canvas(root, width=30, height=30, highlightthickness=0, background='white') # White background will be transparent
        self.canvas.pack()

        self.status = "not_recording"  # Initial status
        self.dot = self.canvas.create_oval(5, 5, 25, 25, fill="deep pink", outline="")
        self.update_position() # Initial position

        self.is_recording = False
        self.is_paused = False

        self.setup_keybinds()
        self.keep_on_top() # Start the loop to keep window on top

    def update_position(self):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 30
        window_height = 30
        x = screen_width - window_width - 10  # 10 pixels from right edge
        y = screen_height - window_height - 50 # 10 pixels from bottom edge
        root.geometry(f"+{x}+{y}")

    def update_dot_color(self):
        if not self.is_recording:
            color = "deep pink"
        elif self.is_paused:
            color = "yellow"
        else:
            color = "red"
        self.canvas.itemconfig(self.dot, fill=color)

    def toggle_recording(self):
        if self.is_paused: # Stopping from paused state
            self.is_recording = False
            self.is_paused = False
        elif self.is_recording:
            self.is_recording = False
            self.is_paused = False
        else:
            self.is_recording = True
            self.is_paused = False
        self.update_dot_color()

    def toggle_pause(self):
        if self.is_recording:
            if not self.is_paused:
                self.is_paused = True
            else:
                self.is_paused = False
            self.update_dot_color()

    def setup_keybinds(self):
        keyboard.add_hotkey('F7', self.toggle_recording)
        keyboard.add_hotkey('F8', self.toggle_pause)

    def keep_on_top(self):
        self.root.attributes('-topmost', True)
        self.root.after(100, self.keep_on_top) # Re-run this every 100 milliseconds

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    overlay = OBSStatusOverlay(root)
    overlay.run()
