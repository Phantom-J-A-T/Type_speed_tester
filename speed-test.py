"""
Typing Speed Test App using Tkinter
- Light/Dark theme toggle
- Modern UI layout
- Rounded typing input boxes (simulated using Canvas)
- Starts directly into the test interface, filtering sentences only by difficulty (Easy/Medium/Hard).
- Implements a fixed 5-minute (300 seconds) timer for the test duration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import os

# Define the fixed test duration in seconds (5 minutes)
TEST_DURATION_SECONDS = 300

# -----------------------------
# Load and Structure Sentences
# -----------------------------
def load_sentences(file_path="sample.txt"):
    """
    Loads sentences from the text file, grouping them only by Difficulty.
    
    Returns: 
        dict: {Difficulty: [sentences]}
    """
    # Initialize structure to store sentences by difficulty
    all_sentences = {"EASY": [], "MEDIUM": [], "HARD": []}
    current_level = None

    # --- FIX: Ensure file path is relative to the script location ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)
    # -----------------------------------------------------------------

    try:
        with open(full_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # Check for Difficulty header [EASY], [MEDIUM], [HARD]
                # Note: The provided file uses "[Easy]." but we check for the uppercase bracketed keyword
                if line.upper().startswith("[EASY]"):
                    current_level = "EASY"
                elif line.upper().startswith("[MEDIUM]"):
                    current_level = "MEDIUM"
                elif line.upper().startswith("[HARD]"):
                    current_level = "HARD"
                
                # If a level is active and the line is not the header itself, add it as a sentence
                elif current_level and line:
                    # Clean up any potential leading periods from the user's formatting "[Easy]."
                    if line.startswith('.') and len(line) > 1:
                         line = line[1:].strip()
                    if line: # Ensure line is not empty after stripping
                        all_sentences[current_level].append(line)

    except FileNotFoundError:
        messagebox.showerror("Error", f"File not found! Expected path: {full_path}")
        return {} # Return empty dict to prevent app crash
    except Exception as e:
        messagebox.showerror("Error", f"Error processing sample.txt: {e}")
        return {}
    
    # Final check for data
    if not any(all_sentences.values()):
        messagebox.showerror("Error", "No sentences found in sample.txt under [EASY], [MEDIUM], or [HARD] headings.")
        return {}

    return all_sentences

# -----------------------------
# Rounded Entry / Text creators
# -----------------------------

def create_rounded_textbox(parent, width=80, height=6, bg="#ffffff", radius=25):
    canvas = tk.Canvas(parent, highlightthickness=0)
    canvas.grid(pady=10, padx=20, sticky="nsew")

    w = (width * 8) + 120 
    h = (height * 18) + 120 
    
    canvas.config(width=w, height=h)

    # Rounded box drawing
    canvas.create_arc((0, 0, radius*2, radius*2), start=90, extent=90, fill=bg, outline=bg)
    canvas.create_arc((w - radius*2, 0, w, radius*2), start=0, extent=90, fill=bg, outline=bg)
    canvas.create_arc((0, h - radius*2, radius*2, h), start=180, extent=90, fill=bg, outline=bg)
    canvas.create_arc((w - radius*2, h - radius*2, w, h), start=270, extent=90, fill=bg, outline=bg)
    
    # Create rectangles to fill the flat edges
    canvas.create_rectangle((radius, 0, w - radius, h), fill=bg, outline=bg)
    canvas.create_rectangle((0, radius, w, h - radius), fill=bg, outline=bg)

    text_widget = tk.Text(canvas, width=width, height=height, bg=bg, bd=0, highlightthickness=0, font=("Arial", 12), wrap="word", relief="flat", padx=20, pady=20)
    
    canvas.create_window(w/2, h/2, window=text_widget)

    return text_widget

# -----------------------------
# Main App Class
# -----------------------------

class TypingTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Test App")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Load all data upfront (only by difficulty now)
        self.all_sentences = load_sentences()
        
        if not any(self.all_sentences.values()):
            self.root.destroy()
            return

        # Test state variables
        self.target_sentence = ""
        self.start_time = None
        self.timer_id = None # Reference to the scheduled timer function
        self.start_timer_binding = None
        self.is_running = False # Flag to track if the test is active
        
        # Theme variables
        self.theme_var = tk.StringVar(value="light")
        self.correct_color = "#1E8449" 
        self.incorrect_color = "#C0392B"

        self.setup_test_ui()
        self.apply_theme()
        
        if hasattr(self, 'input_box'):
            text_widget = self.input_box.master.winfo_children()[0]
            self.start_timer_binding = text_widget.bind("<KeyPress>", self._start_timer_on_key)
            self.root.title("Typing Test App - Ready")

    def setup_test_ui(self):
        """Creates the main typing test interface elements."""
        
        # Configure root grid for the main test UI
        self.root.grid_rowconfigure(0, weight=0) # Top Bar
        self.root.grid_rowconfigure(1, weight=1) # Main Content (text boxes)
        self.root.grid_rowconfigure(2, weight=0) # Bottom Bar
        self.root.grid_columnconfigure(0, weight=1)
        
        # --- Top Bar ---
        self.top_bar = tk.Frame(self.root)
        self.top_bar.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)
        self.top_bar.grid_columnconfigure(0, weight=1) # Theme
        self.top_bar.grid_columnconfigure(1, weight=1) # Difficulty/Timer
        self.top_bar.grid_columnconfigure(2, weight=1) # WPM

        # Theme Toggle (Left)
        self.theme_frame = tk.Frame(self.top_bar)
        self.theme_frame.grid(row=0, column=0, sticky="w")
        self.light_button = ttk.Radiobutton(self.theme_frame, text="Light", variable=self.theme_var, value="light", command=self.apply_theme, style="Theme.TRadiobutton")
        self.dark_button = ttk.Radiobutton(self.theme_frame, text="Dark", variable=self.theme_var, value="dark", command=self.apply_theme, style="Theme.TRadiobutton")
        self.light_button.pack(side="left", padx=5)
        self.dark_button.pack(side="left", padx=5)

        # Difficulty and Timer Frame (Center)
        self.center_frame = tk.Frame(self.top_bar)
        self.center_frame.grid(row=0, column=1, sticky="n")

        # Difficulty Menu
        self.difficulty_levels = ["EASY", "MEDIUM", "HARD"]
        self.difficulty_var = tk.StringVar(value="EASY")
        self.difficulty_menu = ttk.Combobox(self.center_frame, textvariable=self.difficulty_var,
                                            values=self.difficulty_levels, state="readonly", width=15,
                                            font=("Arial", 12, "bold"), style="Black.TCombobox")
        self.difficulty_menu.pack(pady=5) # pack inside center_frame

        # Timer Label (Below Difficulty)
        self.timer_label = ttk.Label(self.center_frame, text="Time: 5:00", font=("Arial", 14, "bold"), style="WPM.TLabel")
        self.timer_label.pack(pady=5)

        # WPM Box (Right)
        self.wpm_frame = tk.Frame(self.top_bar)
        self.wpm_frame.grid(row=0, column=2, sticky="e")
        ttk.Label(self.wpm_frame, text="WPM", font=("Arial", 10, "bold"), style="WPM.TLabel").pack()
        self.wpm_value_label = ttk.Label(self.wpm_frame, text="0", font=("Arial", 14, "bold"), style="WPM.TLabel")
        self.wpm_value_label.pack()
        
        # --- Main Content Frame ---
        self.main_content = tk.Frame(self.root)
        self.main_content.grid(row=1, column=0, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        
        self.sentence_box = create_rounded_textbox(self.main_content, bg="#ffffff")
        self.sentence_box.config(state="disabled")
        
        self.input_box = create_rounded_textbox(self.main_content, bg="#ffffff")

        # --- Bottom Bar ---
        self.bottom_bar = tk.Frame(self.root)
        self.bottom_bar.grid(row=2, column=0, sticky="nsew", pady=20)
        self.bottom_bar.grid_columnconfigure(0, weight=1)

        self.start_button = ttk.Button(self.bottom_bar, text="Start Test", command=self.start_test, style="Black.TButton")
        self.start_button.grid(row=0, column=0) 


    def apply_theme(self):
        theme = self.theme_var.get()
        
        bg_color = "#F0F0F0" if theme == "light" else "#333333"
        text_bg_color = "#FFFFFF" if theme == "light" else "#555555"
        fg_color = "#000000" if theme == "light" else "#FFFFFF"
        
        inv_bg_color = "#222222" if theme == "light" else "#DDDDDD"
        inv_fg_color = "#FFFFFF" if theme == "light" else "#000000"
        
        if theme == "light":
            self.correct_color = "#1E8449"  
            self.incorrect_color = "#C0392B" 
            self.extra_color = "#888888" 
        else:
            self.correct_color = "#34eb55"  
            self.incorrect_color = "#FF4500" 
            self.extra_color = "#AAAAAA" 

        self.root.configure(bg=bg_color)
        
        frames_to_style = []
        if hasattr(self, 'top_bar'):
            frames_to_style.extend([self.top_bar, self.main_content, self.bottom_bar, self.theme_frame, self.wpm_frame, self.center_frame])
        
        for frame in frames_to_style:
            frame.configure(bg=bg_color)

        style = ttk.Style()
        style.theme_use('clam') 

        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Arial", 12))

        style.configure("Theme.TRadiobutton",
                        background=bg_color,
                        foreground=fg_color,
                        font=("Arial", 10, "bold"),
                        padding=10,
                        anchor="center")
        style.map("Theme.TRadiobutton",
            background=[('active', bg_color),
                        ('selected', inv_bg_color)],
            foreground=[('active', fg_color),
                        ('selected', inv_fg_color)]
        )

        style.configure("Black.TCombobox",
                        fieldbackground=inv_bg_color,
                        foreground=inv_fg_color,
                        background=inv_bg_color,
                        arrowcolor=inv_fg_color,
                        selectbackground=inv_bg_color, 
                        selectforeground=inv_fg_color, 
                        bordercolor=inv_bg_color,
                        lightcolor=inv_bg_color,
                        darkcolor=inv_bg_color)
        style.map('Black.TCombobox',
                  fieldbackground=[('readonly', inv_bg_color)],
                  foreground=[('readonly', inv_fg_color)],
                  selectbackground=[('readonly', inv_bg_color)],
                  selectforeground=[('readonly', inv_fg_color)])

        if hasattr(self, 'wpm_frame') and self.wpm_frame.winfo_exists():
            # Apply WPM style to both WPM frame and Timer label
            style.configure("WPM.TLabel",
                            background=inv_bg_color,
                            foreground=inv_fg_color,
                            padding=(10, 5))
            self.wpm_frame.configure(bg=inv_bg_color)
            self.timer_label.configure(style="WPM.TLabel", background=inv_bg_color) # Ensure timer label gets styled correctly

        style.configure("Black.TButton",
                        background=inv_bg_color,
                        foreground=inv_fg_color,
                        font=("Arial", 12, "bold"),
                        padding=15,
                        relief="flat",
                        bordercolor=inv_bg_color)
        style.map("Black.TButton",
            background=[('active', bg_color)],
            foreground=[('active', fg_color)]
        )

        if hasattr(self, 'input_box'):
            for canvas in [self.sentence_box.master, self.input_box.master]:
                canvas.config(bg=bg_color) 
                
                text_widget = canvas.winfo_children()[0] 
                text_widget.config(bg=text_bg_color, fg=fg_color, 
                                   insertbackground=fg_color)
                
                items = canvas.find_all()
                for item in items:
                    if canvas.type(item) in ["arc", "rectangle"]:
                        canvas.itemconfig(item, fill=text_bg_color, outline=text_bg_color)
                        
            text_widget = self.input_box.master.winfo_children()[0]
            text_widget.tag_delete("correct")
            text_widget.tag_delete("incorrect")
            text_widget.tag_delete("extra")
            
            text_widget.tag_config("correct", foreground=self.correct_color)
            text_widget.tag_config("incorrect", foreground=self.incorrect_color)
            text_widget.tag_config("extra", foreground=self.extra_color)


    def start_test(self):
        # Stop any existing timer or process before starting a new one
        self.stop_timer() 
        self.is_running = False

        difficulty = self.difficulty_var.get()
        
        if difficulty not in self.all_sentences or not self.all_sentences[difficulty]:
            messagebox.showerror("Error", f"No sentences available for difficulty: {difficulty}!")
            return

        # Use a new random sentence for a fresh start
        self.target_sentence = random.choice(self.all_sentences[difficulty])
        self.sentence_len = len(self.target_sentence)
        text_widget = self.input_box.master.winfo_children()[0]
        
        # Display target sentence
        self.sentence_box.config(state="normal")
        self.sentence_box.delete("1.0", tk.END)
        self.sentence_box.insert(tk.END, self.target_sentence)
        self.sentence_box.config(state="disabled")

        # Prepare input box
        self.input_box.config(state="normal")
        self.input_box.delete("1.0", tk.END)
        self.input_box.focus_set() 
        
        # Reset visual state
        self.start_time = None
        self.wpm_value_label.config(text="0") 
        self.timer_label.config(text=f"Time: {TEST_DURATION_SECONDS // 60}:00")
        self.start_button.config(text="Reset Test")
        
        # Clear tags
        text_widget.tag_remove("correct", "1.0", tk.END)
        text_widget.tag_remove("incorrect", "1.0", tk.END)
        text_widget.tag_remove("extra", "1.0", tk.END)

        # Re-bind only the key listener to START the timer
        text_widget.bind("<KeyPress>", self._start_timer_on_key)
        # Bind the key release for live WPM/coloring, but it will be guarded by self.is_running
        text_widget.bind("<KeyRelease>", self._key_release_handler)
        self.start_timer_binding = text_widget.bind("<KeyPress>", self._start_timer_on_key)
        
        self.root.title(f"Typing Test App - {difficulty}")

    def _start_timer_on_key(self, event):
        """Starts the timer and unbinds itself on the first relevant key press."""
        # Check if it's a key we should care about (i.e., not just a modifier key)
        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock", "Scroll_Lock", "Super_L", "Super_R", "Tab", "Up", "Down", "Left", "Right"):
            return
        
        if self.start_time is None and self.target_sentence:
            self.start_time = time.time()
            self.is_running = True
            self.update_timer() # Start the recurring timer update
            
            # Unbind this startup function
            text_widget = self.input_box.master.winfo_children()[0]
            if self.start_timer_binding:
                text_widget.unbind("<KeyPress>", self.start_timer_binding)
            self.start_timer_binding = None


    def update_timer(self):
        """Updates the timer label and checks for time expiry."""
        if not self.is_running or self.start_time is None:
            return

        time_elapsed = time.time() - self.start_time
        time_remaining = TEST_DURATION_SECONDS - time_elapsed

        if time_remaining <= 0:
            self.end_test(time_taken=TEST_DURATION_SECONDS)
            return

        # Format and update the timer display
        minutes = int(time_remaining // 60)
        seconds = int(time_remaining % 60)
        self.timer_label.config(text=f"Time: {minutes:01d}:{seconds:02d}")

        # Schedule the next update in 1 second
        self.timer_id = self.root.after(1000, self.update_timer)


    def stop_timer(self):
        """Cancels the scheduled timer updates."""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
            
        # Ensure the test is marked as stopped
        self.is_running = False
        self.start_time = None
        text_widget = self.input_box.master.winfo_children()[0]
        text_widget.unbind("<KeyRelease>")
        
        # Reset the timer label visually
        self.timer_label.config(text=f"Time: {TEST_DURATION_SECONDS // 60}:00")


    def _key_release_handler(self, event):
        """Called on every key release to check live WPM, coloring, and sentence completion."""
        if not self.is_running or not self.target_sentence:
            return

        text_widget = self.input_box.master.winfo_children()[0]
        # Get the text actually typed, up to the length of the target sentence, and remove the trailing newline
        user_text = text_widget.get("1.0", tk.END + "-1c")
        
        target = self.target_sentence
        target_len = self.sentence_len
        
        # 1. Clear previous tags
        text_widget.tag_remove("correct", "1.0", tk.END)
        text_widget.tag_remove("incorrect", "1.0", tk.END)
        text_widget.tag_remove("extra", "1.0", tk.END)

        # 2. Apply coloring and calculate errors live
        error_count = 0
        
        for i in range(len(user_text)):
            char = user_text[i]
            start_index = f"1.{i}"
            end_index = f"1.{i+1}"

            if i < target_len:
                # Character within target length
                if char == target[i]:
                    text_widget.tag_add("correct", start_index, end_index)
                else:
                    text_widget.tag_add("incorrect", start_index, end_index)
                    error_count += 1
            else:
                # Extra characters typed beyond the target sentence length
                text_widget.tag_add("extra", start_index, end_index)

        # --- Live WPM Update ---
        time_elapsed = time.time() - self.start_time
        if time_elapsed > 1 and len(user_text) > 0:
            # WPM based on total characters typed
            cpm = (len(user_text) / time_elapsed) * 60
            live_wpm = max(0, (cpm / 5) - (error_count / 5)) 
            self.wpm_value_label.config(text=f"{live_wpm:.0f}")

        # --- Manual Sentence Completion Check (Optional End) ---
        # The user has successfully typed the entire required sentence
        if user_text == target:
            time_taken = time.time() - self.start_time
            self.end_test(time_taken=time_taken, reason="Sentence Completed")


    def end_test(self, time_taken, reason="Time Expired"):
        """Finalizes the test, calculates results, and shows the popup."""
        
        # Stop all processes and input
        self.stop_timer()
        self.input_box.config(state="disabled") 
        self.is_running = False

        text_widget = self.input_box.master.winfo_children()[0]
        # Get the typed text up to the length of the current target sentence
        final_typed_text = text_widget.get("1.0", f"1.{self.sentence_len}")
        
        # 1. Calculate Errors (only against the target sentence)
        error_count = 0
        target = self.target_sentence
        
        for i, char in enumerate(final_typed_text):
            if i < len(target) and char != target[i]:
                error_count += 1
        
        # 2. Calculate Final WPM (Net WPM)
        # Net WPM = (Total Correct Characters / 5) / Time (in minutes)
        
        total_correct_chars = len(final_typed_text) - error_count
        time_in_minutes = time_taken / 60
        
        if time_in_minutes > 0:
            # Calculate WPM based on the actual time taken, even if it's less than 5 minutes
            net_wpm = max(0, (total_correct_chars / 5) / time_in_minutes)
        else:
            net_wpm = 0.0

        # 3. Update UI and Show Popup
        self.wpm_value_label.config(text=f"{net_wpm:.0f}")
        
        difficulty = self.difficulty_var.get()
        
        # Determine the status message based on how the test ended
        status_message = "Test Completed (Sentence Match)" if reason == "Sentence Completed" else "Test Completed (Time Expired)"
        
        messagebox.showinfo(status_message, 
                            f"**Difficulty: {difficulty}**\n\n"
                            f"Duration: {time_taken:.2f} seconds\n"
                            f"Net WPM: {net_wpm:.0f}\n"
                            f"Character Errors: {error_count}")
        
        self.start_button.config(text="Start Test")


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTestApp(root)
    root.mainloop()