import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pyttsx3
import threading
import os
from datetime import datetime
import queue
import time

class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Text-to-Speech Converter")
        self.root.geometry("750x600")
        self.root.configure(bg="#2c3e50")
        
        # Initialize variables AFTER root window is created
        self.current_voice = tk.StringVar()
        self.speech_rate = tk.IntVar(value=180)
        self.volume = tk.DoubleVar(value=0.9)
        
        # Initialize TTS engine
        self.engine = None
        self.voices = []
        
        # Speech queue for continuous playback
        self.speech_queue = queue.Queue()
        self.is_playing = False
        self.stop_flag = False
        self.pause_flag = False
        
        # UI Theme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.setup_ui()
        self.initialize_engine()  # Initialize engine after UI is set up
        self.load_voices()
        
    def configure_styles(self):
        """Configure custom styles for the UI"""
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='#ecf0f1')
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        self.style.map('TButton',
            foreground=[('active', '#ffffff'), ('!active', '#ffffff')],
            background=[('active', '#3498db'), ('!active', '#2980b9')]
        )
        self.style.configure('TCombobox', fieldbackground='#34495e', background='#34495e')
        self.style.configure('TScale', background='#2c3e50')
        self.style.configure('TLabelframe', background='#2c3e50', foreground='#ecf0f1')
        self.style.configure('TLabelframe.Label', background='#2c3e50', foreground='#ecf0f1')
        
    def initialize_engine(self):
        """Initialize or reinitialize the TTS engine"""
        try:
            if self.engine:
                self.engine.stop()
                del self.engine
            self.engine = pyttsx3.init()
            # Set initial properties
            self.engine.setProperty('rate', self.speech_rate.get())
            self.engine.setProperty('volume', self.volume.get())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize TTS engine: {str(e)}")
            self.root.destroy()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = tk.Label(
            title_frame, 
            text="Advanced Text-to-Speech Converter", 
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        title_label.pack()
        
        # Text input frame
        text_frame = ttk.LabelFrame(main_frame, text="Text Input", padding=10)
        text_frame.pack(fill="both", expand=True, pady=5)
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="#34495e",
            fg="#ecf0f1",
            insertbackground="white",
            selectbackground="#3498db",
            width=60,
            height=12
        )
        self.text_area.pack(fill="both", expand=True)
        
        # Voice settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Voice Settings", padding=10)
        settings_frame.pack(fill="x", pady=5)
        
        # Voice selection
        voice_frame = ttk.Frame(settings_frame)
        voice_frame.pack(fill="x", pady=5)
        
        ttk.Label(voice_frame, text="Select Voice:").pack(side="left", padx=(0, 10))
        self.voice_combo = ttk.Combobox(
            voice_frame, 
            textvariable=self.current_voice,
            state="readonly",
            width=50
        )
        self.voice_combo.pack(side="left", fill="x", expand=True)
        self.voice_combo.bind("<<ComboboxSelected>>", self.change_voice)
        
        # Speech rate and volume
        controls_frame = ttk.Frame(settings_frame)
        controls_frame.pack(fill="x", pady=5)
        
        # Speech rate
        rate_frame = ttk.Frame(controls_frame)
        rate_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Label(rate_frame, text="Speech Rate:").pack(anchor="w")
        rate_scale = tk.Scale(
            rate_frame, 
            from_=50, 
            to=400, 
            orient="horizontal",
            variable=self.speech_rate,
            command=self.change_rate,
            bg="#2c3e50",
            fg="#ecf0f1",
            highlightthickness=0,
            troughcolor="#34495e",
            activebackground="#3498db"
        )
        rate_scale.pack(fill="x")
        
        # Volume
        volume_frame = ttk.Frame(controls_frame)
        volume_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        ttk.Label(volume_frame, text="Volume:").pack(anchor="w")
        volume_scale = tk.Scale(
            volume_frame, 
            from_=0.0, 
            to=1.0, 
            resolution=0.1,
            orient="horizontal",
            variable=self.volume,
            command=self.change_volume,
            bg="#2c3e50",
            fg="#ecf0f1",
            highlightthickness=0,
            troughcolor="#34495e",
            activebackground="#3498db"
        )
        volume_scale.pack(fill="x")
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Play button
        self.play_btn = ttk.Button(
            button_frame,
            text="▶️ Play Speech",
            command=self.play_speech,
            style="TButton"
        )
        self.play_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Pause button
        self.pause_btn = ttk.Button(
            button_frame,
            text="⏸️ Pause",
            command=self.pause_speech,
            state="disabled",
            style="TButton"
        )
        self.pause_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Stop button
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_speech,
            state="disabled",
            style="TButton"
        )
        self.stop_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Save button
        self.save_btn = ttk.Button(
            button_frame,
            text="💾 Save Audio",
            command=self.save_audio,
            style="TButton"
        )
        self.save_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Clear button
        self.clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Text",
            command=self.clear_text,
            style="TButton"
        )
        self.clear_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief="sunken", 
            anchor="w",
            bg="#34495e",
            fg="#ecf0f1",
            font=("Arial", 9)
        )
        status_bar.pack(side="bottom", fill="x")
        
    def load_voices(self):
        """Load available voices into the combobox"""
        try:
            self.voices = self.engine.getProperty('voices')
            voice_names = []
            
            for i, voice in enumerate(self.voices):
                # Extract voice name and language info
                name = voice.name.split('\\')[-1] if '\\' in voice.name else voice.name
                language = "Unknown"
                
                # Try to extract language info if available
                if hasattr(voice, 'languages') and voice.languages:
                    language = voice.languages[0]
                elif 'language' in voice.__dict__:
                    language = voice.__dict__['language']
                
                voice_names.append(f"{i}: {name} ({language})")
            
            self.voice_combo['values'] = voice_names
            if voice_names:
                self.voice_combo.current(0)
                self.change_voice()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load voices: {str(e)}")
    
    def change_voice(self, event=None):
        """Change the TTS voice"""
        if self.current_voice.get():
            try:
                voice_index = int(self.current_voice.get().split(':')[0])
                self.engine.setProperty('voice', self.voices[voice_index].id)
                voice_name = self.voices[voice_index].name.split('\\')[-1]
                self.status_var.set(f"Voice changed to: {voice_name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change voice: {str(e)}")
    
    def change_rate(self, value):
        """Change speech rate"""
        self.engine.setProperty('rate', int(value))
        
    def change_volume(self, value):
        """Change volume"""
        self.engine.setProperty('volume', float(value))
    
    def play_speech(self):
        """Play the text as speech"""
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert!")
            return
        
        # Clear any previous speech in the queue
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()
        
        # Add the text to the queue
        self.speech_queue.put(text)
        
        # Start the speech thread if not already running
        if not self.is_playing:
            self.is_playing = True
            self.stop_flag = False
            self.pause_flag = False
            threading.Thread(target=self._speak_from_queue, daemon=True).start()
        
        self.update_button_states()
    
    def _speak_from_queue(self):
        """Process speech from the queue"""
        while not self.speech_queue.empty() and not self.stop_flag:
            if self.pause_flag:
                time.sleep(0.1)
                continue
                
            text = self.speech_queue.get()
            
            try:
                # Reinitialize engine for each playback to ensure reliability
                self.initialize_engine()
                
                # Reapply settings
                if self.current_voice.get():
                    voice_index = int(self.current_voice.get().split(':')[0])
                    self.engine.setProperty('voice', self.voices[voice_index].id)
                self.engine.setProperty('rate', self.speech_rate.get())
                self.engine.setProperty('volume', self.volume.get())
                
                self.root.after(0, lambda: self.status_var.set("Playing speech..."))
                self.root.after(0, self.update_button_states)
                
                self.engine.say(text)
                self.engine.runAndWait()
                
                if self.stop_flag:
                    break
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error playing speech: {str(e)}"))
                break
        
        self.is_playing = False
        self.root.after(0, lambda: self.status_var.set("Ready" if not self.stop_flag else "Stopped"))
        self.root.after(0, self.update_button_states)
    
    def pause_speech(self):
        """Pause current speech"""
        if self.is_playing:
            self.pause_flag = not self.pause_flag
            if self.pause_flag:
                self.engine.stop()
                self.status_var.set("Speech paused")
                self.pause_btn.config(text="⏯️ Resume")
            else:
                self.status_var.set("Resuming speech...")
                self.pause_btn.config(text="⏸️ Pause")
            self.update_button_states()
    
    def stop_speech(self):
        """Stop current speech"""
        self.stop_flag = True
        self.pause_flag = False
        self.engine.stop()
        self.status_var.set("Speech stopped")
        self.update_button_states()
    
    def update_button_states(self):
        """Update button states based on current playback status"""
        if self.is_playing and not self.stop_flag:
            self.play_btn.config(state="disabled")
            self.pause_btn.config(state="normal")
            self.stop_btn.config(state="normal")
            self.save_btn.config(state="disabled")
            self.clear_btn.config(state="disabled")
        else:
            self.play_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            self.save_btn.config(state="normal")
            self.clear_btn.config(state="normal")
    
    def save_audio(self):
        """Save the speech as an audio file"""
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text to convert!")
            return
        
        # Get save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"speech_{timestamp}.wav"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if file_path:
            try:
                self.save_btn.config(state="disabled")
                self.status_var.set("Saving audio file...")
                self.root.update()
                
                # Create a temporary engine for saving
                temp_engine = pyttsx3.init()
                
                # Copy current settings to temp engine
                if self.current_voice.get():
                    voice_index = int(self.current_voice.get().split(':')[0])
                    temp_engine.setProperty('voice', self.voices[voice_index].id)
                temp_engine.setProperty('rate', self.speech_rate.get())
                temp_engine.setProperty('volume', self.volume.get())
                
                # Save to file
                temp_engine.save_to_file(text, file_path)
                temp_engine.runAndWait()
                
                self.save_btn.config(state="normal")
                self.status_var.set(f"Audio saved: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Audio file saved successfully!\n{file_path}")
                
            except Exception as e:
                self.save_btn.config(state="normal")
                self.status_var.set("Error saving file")
                messagebox.showerror("Error", f"Error saving audio file: {str(e)}")
            finally:
                if 'temp_engine' in locals():
                    del temp_engine
    
    def clear_text(self):
        """Clear the text area"""
        self.text_area.delete("1.0", tk.END)
        self.status_var.set("Text cleared")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    
    # Set window icon if available
    try:
        root.iconbitmap('tts_icon.ico')  # Replace with your icon file if available
    except:
        pass
    
    # Create app instance AFTER root window is created
    app = TextToSpeechApp(root)
    
    # Add some sample text
    sample_text = """Welcome to the Advanced Text-to-Speech Converter!

Features:
- Multiple voice selection
- Adjustable speech rate and volume
- Save audio to WAV or MP3 files
- Play, pause, and stop controls
- Modern dark theme interface
- Reliable continuous playback

Try typing or pasting your own text and click 'Play Speech' to hear it!"""
    
    app.text_area.insert("1.0", sample_text)
    
    root.mainloop()

if __name__ == "__main__":
    main()