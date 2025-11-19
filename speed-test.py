"""
Typing Speed Test App using Tkinter
- Light/Dark theme toggle
- Modern UI layout
- Rounded typing input boxes (simulated using Canvas)
- Initial startup screen to collect user name and subject
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import random

# -----------------------------
# Load and Structure Sentences
# -----------------------------
def load_sentences(file_path="sample.txt"):
    """
    Loads sentences from the text file, grouping them by Subject and then by Difficulty.
    
    Returns: 
        dict: {Subject: {Difficulty: [sentences]}}
    """
    all_subjects = {}
    current_subject = None
    current_level = None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                # Check for Subject marker (e.g., [PHYSICS])
                if line.startswith("[") and line.endswith("]"):
                    subject = line[1:-1]
                    current_subject = subject
                    all_subjects[current_subject] = {"EASY": [], "MEDIUM": [], "HARD": []}
                    current_level = None # Reset level when subject changes
                
                # Check for Difficulty level within a Subject block
                elif current_subject and line.upper().startswith(("EASY:", "MEDIUM:", "HARD:")):
                    parts = line.split(":", 1)
                    level = parts[0].strip().upper()
                    sentence_text = parts[1].strip()
                    
                    if level in all_subjects[current_subject]:
                        current_level = level
                        # Split by period and filter out short empty strings, then re-join with a period
                        sentences = [s.strip() for s in sentence_text.split('.') if s.strip()]
                        for sentence in sentences:
                            # Add back the period if it was removed
                            all_subjects[current_subject][current_level].append(sentence + '.')

    except FileNotFoundError:
        messagebox.showerror("Error", "sample.txt not found!")
    except Exception as e:
        messagebox.showerror("Error", f"Error processing sample.txt: {e}")

    return all_subjects

# -----------------------------
# Rounded Entry / Text creators
# -----------------------------

def create_rounded_textbox(parent, width=80, height=6, bg="#ffffff", radius=25):
    # Remove bg=bg from canvas creation to allow parent bg to show
    canvas = tk.Canvas(parent, highlightthickness=0)
    # Use grid instead of pack for more control
    canvas.grid(pady=10, padx=20, sticky="nsew")

    # Adjust dimensions for the canvas based on text widget size
    # Increased padding (120) to give more margin around the text widget (padx=20, pady=20)
    w = (width * 8) + 120 # Approx width in pixels + larger padding
    h = (height * 18) + 120 # Approx height in pixels + larger padding
    
    # Configure canvas size
    canvas.config(width=w, height=h)

    # Rounded box drawing
    # Use the bg color for both fill and outline to blend
    canvas.create_arc((0, 0, radius*2, radius*2), start=90, extent=90, fill=bg, outline=bg)
    canvas.create_arc((w - radius*2, 0, w, radius*2), start=0, extent=90, fill=bg, outline=bg)
    canvas.create_arc((0, h - radius*2, radius*2, h), start=180, extent=90, fill=bg, outline=bg)
    canvas.create_arc((w - radius*2, h - radius*2, w, h), start=270, extent=90, fill=bg, outline=bg)
    
    # Create rectangles to fill the flat edges
    canvas.create_rectangle((radius, 0, w - radius, h), fill=bg, outline=bg)
    canvas.create_rectangle((0, radius, w, h - radius), fill=bg, outline=bg)

    # Note: Text widget has internal padding (padx=20, pady=20)
    text_widget = tk.Text(canvas, width=width, height=height, bg=bg, bd=0, highlightthickness=0, font=("Arial", 12), wrap="word", relief="flat", padx=20, pady=20)
    
    # Place text widget centered inside the canvas
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
        
        # Load all data upfront
        self.all_sentences = load_sentences()
        self.subjects = list(self.all_sentences.keys())
        
        # Check if any data exists
        if not self.subjects:
            messagebox.showerror("Error", "No subjects or sentences found in sample.txt!")
            self.root.destroy()
            return

        # State variables for user info (initialized in setup_login_ui)
        self.user_name = None
        self.selected_subject = None
        self.sentences = {}
        
        # Test state variables
        self.target_sentence = ""
        self.start_time = None
        self.start_timer_binding = None
        
        # Theme variables
        self.theme_var = tk.StringVar(value="light")
        self.correct_color = "#1E8449" 
        self.incorrect_color = "#C0392B"

        # Start by setting up the login screen
        self.setup_login_ui()
        # Apply the default theme to the root window (important for the login screen background)
        self.apply_theme() 

    def setup_login_ui(self):
        """Creates and displays the login input elements on the main window."""
        
        # Configure root grid for the login frame to be centered
        self.root.grid_rowconfigure(0, weight=1) 
        self.root.grid_rowconfigure(1, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create a central frame for the login UI
        self.login_frame = ttk.Frame(self.root, padding="40 40 40 40")
        self.login_frame.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=1)
        
        # Center contents within the login frame
        self.login_frame.grid_columnconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(0, weight=1)
        self.login_frame.grid_rowconfigure(5, weight=1)
        
        login_inner_frame = ttk.Frame(self.login_frame)
        login_inner_frame.grid(row=1, column=0)
        
        # Variables to hold user input
        self.user_name_var = tk.StringVar(value="")
        self.selected_subject_var = tk.StringVar(value=self.subjects[0])
        
        # 1. Title
        ttk.Label(login_inner_frame, text="Welcome to the Typing Test", font=("Arial", 16, "bold")).pack(pady=20)

        # 2. Name Input
        ttk.Label(login_inner_frame, text="Enter Your Name:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        name_entry = ttk.Entry(login_inner_frame, textvariable=self.user_name_var, width=30, font=("Arial", 12))
        name_entry.pack(pady=5)
        name_entry.focus_set()

        # 3. Subject Selection
        ttk.Label(login_inner_frame, text="Choose Subject:", font=("Arial", 12, "bold")).pack(pady=5, anchor="w")
        subject_menu = ttk.Combobox(login_inner_frame, textvariable=self.selected_subject_var,
                                    values=self.subjects, state="readonly", width=28,
                                    font=("Arial", 12))
        subject_menu.pack(pady=5)
        subject_menu.set(self.subjects[0])

        # 4. Start Button
        ttk.Button(login_inner_frame, text="Continue to Test", command=self.start_test_app, 
                   style="Black.TButton").pack(pady=20, ipadx=10, ipady=5)

    def start_test_app(self):
        """Validates login details and transitions the UI to the main test view."""
        
        name = self.user_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter your name.")
            return

        self.user_name = name
        self.selected_subject = self.selected_subject_var.get()
        self.sentences = self.all_sentences.get(self.selected_subject, {})

        if not any(self.sentences.values()):
            messagebox.showerror("Error", f"No sentences available for the subject: {self.selected_subject}")
            return

        # Destroy the login UI
        self.login_frame.destroy()
        
        # Update the main window title
        self.root.title(f"{self.user_name}'s Typing Test - {self.selected_subject}")

        # Reconfigure root grid for the main test UI
        self.root.grid_rowconfigure(0, weight=0) # Top Bar
        self.root.grid_rowconfigure(1, weight=1) # Main Content (text boxes)
        self.root.grid_rowconfigure(2, weight=0) # Bottom Bar
        self.root.grid_columnconfigure(0, weight=1)
        
        # Setup and initialize the main test UI
        self.setup_test_ui()
        self.apply_theme()
        
        # Initial binding setup (can only be done after input_box is created)
        if hasattr(self, 'input_box'):
            self.start_timer_binding = self.input_box.bind("<KeyPress>", self.start_timer)


    def setup_test_ui(self):
        """Creates the main typing test interface elements."""
        
        # --- Top Bar ---
        self.top_bar = tk.Frame(self.root)
        self.top_bar.grid(row=0, column=0, sticky="nsew", pady=10, padx=20)
        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(2, weight=1)

        # Theme Toggle (Left)
        self.theme_frame = tk.Frame(self.top_bar)
        self.theme_frame.grid(row=0, column=0, sticky="w")
        self.light_button = ttk.Radiobutton(self.theme_frame, text="Light", variable=self.theme_var, value="light", command=self.apply_theme, style="Theme.TRadiobutton")
        self.dark_button = ttk.Radiobutton(self.theme_frame, text="Dark", variable=self.theme_var, value="dark", command=self.apply_theme, style="Theme.TRadiobutton")
        self.light_button.pack(side="left", padx=5)
        self.dark_button.pack(side="left", padx=5)

        # Difficulty Menu (Center)
        self.difficulty_levels = ["EASY", "MEDIUM", "HARD"]
        self.difficulty_var = tk.StringVar(value="EASY")
        self.difficulty_menu = ttk.Combobox(self.top_bar, textvariable=self.difficulty_var,
                                            values=self.difficulty_levels, state="readonly", width=15,
                                            font=("Arial", 12, "bold"), style="Black.TCombobox")
        self.difficulty_menu.grid(row=0, column=1, sticky="n")

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
        # Bindings are set in start_test_app() now

        # --- Bottom Bar ---
        self.bottom_bar = tk.Frame(self.root)
        self.bottom_bar.grid(row=2, column=0, sticky="nsew", pady=20)
        self.bottom_bar.grid_columnconfigure(0, weight=1)

        self.start_button = ttk.Button(self.bottom_bar, text="Start Test", command=self.start_test, style="Black.TButton")
        self.start_button.grid(row=0, column=0) # Centered by default in single-column grid


    def apply_theme(self):
        theme = self.theme_var.get()
        
        # Theme colors
        bg_color = "#F0F0F0" if theme == "light" else "#333333"
        text_bg_color = "#FFFFFF" if theme == "light" else "#555555"
        fg_color = "#000000" if theme == "light" else "#FFFFFF"
        
        # Colors for inverted elements (black boxes in light mode)
        inv_bg_color = "#222222" if theme == "light" else "#DDDDDD"
        inv_fg_color = "#FFFFFF" if theme == "light" else "#000000"
        
        # Colors for character coloring
        if theme == "light":
            self.correct_color = "#1E8449"  # Darker green on light background
            self.incorrect_color = "#C0392B" # Darker red on light background
            self.extra_color = "#888888" # Gray
        else:
            self.correct_color = "#34eb55"  # Brighter green on dark background
            self.incorrect_color = "#FF4500" # Orange/Red for contrast on dark background
            self.extra_color = "#AAAAAA" # Light Gray

        # Apply root background
        self.root.configure(bg=bg_color)
        
        # Style all frames (Login frame might exist)
        frames_to_style = [self.login_frame] if hasattr(self, 'login_frame') and self.login_frame.winfo_exists() else []
        if hasattr(self, 'top_bar'):
            frames_to_style.extend([self.top_bar, self.main_content, self.bottom_bar, self.theme_frame, self.wpm_frame])
        
        for frame in frames_to_style:
            frame.configure(bg=bg_color)

        # Style ttk widgets
        style = ttk.Style()
        style.theme_use('clam') # Use a theme that allows configuration

        # General Label
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Arial", 12))

        # Theme Radiobuttons (styled to look like buttons)
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

        # Comboboxes
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

        # WPM Labels (Only if test UI exists)
        if hasattr(self, 'wpm_frame') and self.wpm_frame.winfo_exists():
            style.configure("WPM.TLabel",
                            background=inv_bg_color,
                            foreground=inv_fg_color,
                            padding=(10, 5))
            self.wpm_frame.configure(bg=inv_bg_color) 

        # Buttons (Used for Login and Start Test)
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

        # Text Boxes (Only if test UI exists)
        if hasattr(self, 'input_box'):
            for canvas in [self.sentence_box.master, self.input_box.master]:
                canvas.config(bg=bg_color) 
                
                # Find the text widget
                text_widget = canvas.winfo_children()[0] 
                text_widget.config(bg=text_bg_color, fg=fg_color, 
                                   insertbackground=fg_color)
                
                # Redraw rounded rects with new text_bg_color
                items = canvas.find_all()
                for item in items:
                    if canvas.type(item) in ["arc", "rectangle"]:
                        canvas.itemconfig(item, fill=text_bg_color, outline=text_bg_color)
                        
            # Configure the text tags for coloring
            text_widget = self.input_box.master.winfo_children()[0]
            text_widget.tag_delete("correct")
            text_widget.tag_delete("incorrect")
            text_widget.tag_delete("extra")
            
            text_widget.tag_config("correct", foreground=self.correct_color)
            text_widget.tag_config("incorrect", foreground=self.incorrect_color)
            text_widget.tag_config("extra", foreground=self.extra_color)


    def start_test(self):
        # Difficulty is now a key in the filtered sentences dictionary
        difficulty = self.difficulty_var.get()
        
        # Check if the sentence list for the current difficulty is valid and not empty
        if difficulty not in self.sentences or not self.sentences[difficulty]:
            messagebox.showerror("Error", f"No sentences for {self.selected_subject} - {difficulty} difficulty!")
            return

        self.target_sentence = random.choice(self.sentences[difficulty])
        self.sentence_len = len(self.target_sentence)
        text_widget = self.input_box.master.winfo_children()[0]
        
        self.sentence_box.config(state="normal")
        self.sentence_box.delete("1.0", tk.END)
        self.sentence_box.insert(tk.END, self.target_sentence)
        self.sentence_box.config(state="disabled")

        self.input_box.config(state="normal")
        self.input_box.delete("1.0", tk.END)
        self.input_box.focus_set() # Automatically focus the input box
        self.start_time = None
        self.wpm_value_label.config(text="0") # Reset WPM counter
        self.start_button.config(text="Reset Test")
        
        # Clear tags at the start of a new test
        text_widget.tag_remove("correct", "1.0", tk.END)
        text_widget.tag_remove("incorrect", "1.0", tk.END)
        text_widget.tag_remove("extra", "1.0", tk.END)

        # Re-bind start_timer in case it was unbound
        # Note: Binds KeyPress and KeyRelease to the Text widget *inside* the canvas
        text_widget.bind("<KeyPress>", self.start_timer)
        text_widget.bind("<KeyRelease>", self.check_completion)
        self.start_timer_binding = text_widget.bind("<KeyPress>", self.start_timer)


    def start_timer(self, event):
        # Start timer only if it hasn't started and there's a target sentence
        if self.start_time is None and self.target_sentence:
            # Ignore modifier keys (heuristic check)
            if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Num_Lock", "Scroll_Lock", "Super_L", "Super_R", "Tab", "Up", "Down", "Left", "Right"):
                return
            
            # Check if it's a printable character or backspace/delete
            if len(event.char) > 0 or event.keysym in ("BackSpace", "Delete"):
                self.start_time = time.time()
                text_widget = self.input_box.master.winfo_children()[0]
                # Unbind this so it doesn't fire again
                text_widget.unbind("<KeyPress>", self.start_timer_binding)
                self.start_timer_binding = None # Clear the reference

    def check_completion(self, event):
        if not self.target_sentence or self.start_time is None:
            return

        text_widget = self.input_box.master.winfo_children()[0]
        # Get text without the trailing newline character
        user_text = text_widget.get("1.0", tk.END + "-1c")
        user_text_len = len(user_text)
        target_len = self.sentence_len
        target = self.target_sentence
        
        # 1. Clear previous tags
        text_widget.tag_remove("correct", "1.0", tk.END)
        text_widget.tag_remove("incorrect", "1.0", tk.END)
        text_widget.tag_remove("extra", "1.0", tk.END)

        # 2. Apply coloring and calculate errors live
        error_count = 0
        for i, char in enumerate(user_text):
            start_index = f"1.{i}"
            end_index = f"1.{i+1}"
            
            if i < target_len:
                if char == target[i]:
                    # Correct character
                    text_widget.tag_add("correct", start_index, end_index)
                else:
                    # Incorrect character
                    text_widget.tag_add("incorrect", start_index, end_index)
                    error_count += 1
            else:
                # Extra characters typed beyond the target sentence length
                text_widget.tag_add("extra", start_index, end_index)

        # --- Live WPM Update ---
        if user_text_len > 0:
            time_elapsed = time.time() - self.start_time
            if time_elapsed > 1: # Only update WPM after 1 second
                # WPM based on characters typed (CPM / 5)
                cpm = (user_text_len / time_elapsed) * 60
                live_wpm = max(0, (cpm / 5) - (error_count / 5)) # Gross WPM - penalty
                self.wpm_value_label.config(text=f"{live_wpm:.0f}")

        # --- Completion Check ---
        if user_text_len >= target_len and event.keysym not in ("BackSpace", "Delete"):
            self.input_box.config(state="disabled") # Stop typing
            # Truncate user text to match target length for calculation
            final_typed_text = user_text[:target_len]
            time_taken = time.time() - self.start_time
            self.calculate_results(final_typed_text, time_taken)

    def calculate_results(self, typed_text, time_taken):
        # 1. Calculate Errors
        error_count = 0
        target = self.target_sentence
        
        # Compare characters up to the length of the typed text
        for i, char in enumerate(typed_text):
            if i < len(target) and char != target[i]:
                error_count += 1
        
        # 2. Calculate Final WPM (Net WPM)
        words = len(self.target_sentence.split())
        
        # Gross WPM (Words / Time in minutes)
        gross_wpm = (words / time_taken) * 60
        
        # Net WPM (Gross WPM - (Errors / Time in minutes))
        # Assuming one word is 5 characters, one error is 1 word WPM penalty
        error_penalty_wpm = error_count / 5
        net_wpm = max(0, gross_wpm - error_penalty_wpm)

        if time_taken < 0.1: 
            net_wpm = 0.0 # Prevent division by near-zero

        # 3. Update UI and Show Popup
        self.wpm_value_label.config(text=f"{net_wpm:.0f}")
        
        messagebox.showinfo("Test Complete!", 
                            f"**User: {self.user_name}**\n"
                            f"**Subject: {self.selected_subject}**\n\n"
                            f"Time Taken: {time_taken:.2f} seconds\n"
                            f"Gross WPM: {gross_wpm:.0f}\n"
                            f"Net WPM: {net_wpm:.0f}\n"
                            f"Character Errors: {error_count}")
        
        self.start_button.config(text="Start Test")


if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTestApp(root)
    root.mainloop()