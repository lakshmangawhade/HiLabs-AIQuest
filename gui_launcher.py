#!/usr/bin/env python3
"""
HiLabs AIQuest - GUI Launcher
Graphical interface for launching the HiLabs application
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
import time
import webbrowser
from pathlib import Path
import queue

class HiLabsLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("HiLabs AIQuest - Contract Analysis System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Set icon if available
        try:
            icon_path = Path("hilabs-dash/public/favicon.ico")
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except:
            pass
        
        # Process references
        self.backend_process = None
        self.frontend_process = None
        self.output_queue = queue.Queue()
        
        # Create UI
        self.create_widgets()
        
        # Start output reader thread
        self.root.after(100, self.process_output_queue)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="HiLabs AIQuest",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Professional Contract Intelligence Platform",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()
        
        # Control Frame
        control_frame = tk.Frame(self.root, bg="#ecf0f1", height=120)
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Buttons
        button_style = {
            "font": ("Arial", 11),
            "width": 15,
            "height": 2,
            "cursor": "hand2"
        }
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ Start System",
            command=self.start_system,
            bg="#27ae60",
            fg="white",
            **button_style
        )
        self.start_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="■ Stop System",
            command=self.stop_system,
            bg="#e74c3c",
            fg="white",
            state=tk.DISABLED,
            **button_style
        )
        self.stop_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.restart_btn = tk.Button(
            control_frame,
            text="↻ Restart",
            command=self.restart_system,
            bg="#f39c12",
            fg="white",
            state=tk.DISABLED,
            **button_style
        )
        self.restart_btn.grid(row=0, column=2, padx=10, pady=10)
        
        self.browser_btn = tk.Button(
            control_frame,
            text="🌐 Open Browser",
            command=self.open_browser,
            bg="#3498db",
            fg="white",
            state=tk.DISABLED,
            **button_style
        )
        self.browser_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Options Frame
        options_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=10)
        options_frame.pack(fill=tk.X, padx=20)
        
        self.skip_install_var = tk.BooleanVar()
        skip_install_cb = tk.Checkbutton(
            options_frame,
            text="Skip dependency installation (faster startup)",
            variable=self.skip_install_var
        )
        skip_install_cb.pack(anchor=tk.W)
        
        self.auto_browser_var = tk.BooleanVar(value=True)
        auto_browser_cb = tk.Checkbutton(
            options_frame,
            text="Automatically open browser when ready",
            variable=self.auto_browser_var
        )
        auto_browser_cb.pack(anchor=tk.W)
        
        # Status Frame
        status_frame = tk.LabelFrame(self.root, text="Status", padx=10, pady=10)
        status_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        self.backend_status = tk.Label(
            status_frame,
            text="⚫ Backend: Stopped",
            font=("Arial", 10),
            anchor=tk.W
        )
        self.backend_status.pack(fill=tk.X)
        
        self.frontend_status = tk.Label(
            status_frame,
            text="⚫ Frontend: Stopped",
            font=("Arial", 10),
            anchor=tk.W
        )
        self.frontend_status.pack(fill=tk.X)
        
        # Output Frame
        output_frame = tk.LabelFrame(self.root, text="Output Log", padx=10, pady=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#00ff00"
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear button
        clear_btn = tk.Button(
            output_frame,
            text="Clear Log",
            command=self.clear_output,
            font=("Arial", 9)
        )
        clear_btn.pack(pady=(5, 0))
    
    def log_output(self, message, color="#00ff00"):
        """Add message to output queue"""
        self.output_queue.put((message, color))
    
    def process_output_queue(self):
        """Process messages from output queue"""
        try:
            while True:
                message, color = self.output_queue.get_nowait()
                self.output_text.config(state=tk.NORMAL)
                self.output_text.insert(tk.END, message + "\n", color)
                self.output_text.see(tk.END)
                self.output_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_output_queue)
    
    def clear_output(self):
        """Clear output text"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def update_status(self, component, status, color):
        """Update status labels"""
        if component == "backend":
            self.backend_status.config(text=f"{color} Backend: {status}")
        elif component == "frontend":
            self.frontend_status.config(text=f"{color} Frontend: {status}")
    
    def start_system(self):
        """Start the system in a separate thread"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.restart_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self._start_system_thread)
        thread.daemon = True
        thread.start()
    
    def _start_system_thread(self):
        """Thread function to start the system"""
        try:
            # Change to project directory
            os.chdir(Path(__file__).parent)
            
            self.log_output("Starting HiLabs AIQuest System...", "#3498db")
            self.log_output("-" * 50)
            
            # Start Backend
            self.log_output("Starting Backend Server...")
            self.update_status("backend", "Starting", "🟡")
            
            backend_path = Path("Backend")
            if not backend_path.exists():
                self.log_output("ERROR: Backend folder not found", "#e74c3c")
                return
            
            # Check for virtual environment
            venv_python = backend_path / "venv" / "Scripts" / "python.exe"
            if not venv_python.exists():
                self.log_output("Creating virtual environment...")
                subprocess.run([sys.executable, "-m", "venv", str(backend_path / "venv")])
            
            # Install dependencies if needed
            if not self.skip_install_var.get():
                self.log_output("Installing backend dependencies...")
                pip_exe = backend_path / "venv" / "Scripts" / "pip.exe"
                subprocess.run([str(pip_exe), "install", "-r", str(backend_path / "requirements.txt")], 
                             capture_output=True)
            
            # Start backend
            self.backend_process = subprocess.Popen(
                [str(venv_python), "main.py"],
                cwd=str(backend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            time.sleep(3)
            self.update_status("backend", "Running", "🟢")
            self.log_output("Backend started successfully on http://localhost:5000", "#27ae60")
            
            # Start Frontend
            self.log_output("\nStarting Frontend Dashboard...")
            self.update_status("frontend", "Starting", "🟡")
            
            frontend_path = Path("hilabs-dash")
            if not frontend_path.exists():
                self.log_output("ERROR: Frontend folder not found", "#e74c3c")
                return
            
            # Install dependencies if needed
            if not self.skip_install_var.get():
                if not (frontend_path / "node_modules").exists():
                    self.log_output("Installing frontend dependencies (this may take a while)...")
                    subprocess.run(["npm", "install"], cwd=str(frontend_path), capture_output=True)
            
            # Copy results
            if (frontend_path / "copy-results.js").exists():
                self.log_output("Syncing results...")
                subprocess.run(["node", "copy-results.js"], cwd=str(frontend_path), capture_output=True)
            
            # Start frontend
            self.frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=str(frontend_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env={**os.environ, "BROWSER": "none"}  # Prevent auto-opening browser
            )
            
            time.sleep(5)
            self.update_status("frontend", "Running", "🟢")
            self.log_output("Frontend started successfully on http://localhost:3000", "#27ae60")
            
            self.browser_btn.config(state=tk.NORMAL)
            
            # Auto-open browser if enabled
            if self.auto_browser_var.get():
                time.sleep(2)
                self.open_browser()
            
            self.log_output("\n" + "=" * 50)
            self.log_output("System is running! Press 'Stop System' to shut down.", "#3498db")
            
        except Exception as e:
            self.log_output(f"ERROR: {str(e)}", "#e74c3c")
            self.stop_system()
    
    def stop_system(self):
        """Stop the system"""
        self.log_output("\nStopping system...", "#f39c12")
        
        # Stop frontend
        if self.frontend_process:
            self.frontend_process.terminate()
            self.frontend_process = None
            self.update_status("frontend", "Stopped", "⚫")
        
        # Stop backend
        if self.backend_process:
            self.backend_process.terminate()
            self.backend_process = None
            self.update_status("backend", "Stopped", "⚫")
        
        # Kill processes on ports
        self._kill_port(5000)
        self._kill_port(3000)
        
        self.log_output("System stopped.", "#27ae60")
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.restart_btn.config(state=tk.DISABLED)
        self.browser_btn.config(state=tk.DISABLED)
    
    def restart_system(self):
        """Restart the system"""
        self.log_output("\nRestarting system...", "#f39c12")
        self.stop_system()
        time.sleep(2)
        self.start_system()
    
    def open_browser(self):
        """Open browser to frontend"""
        webbrowser.open("http://localhost:3000")
        self.log_output("Opened browser to http://localhost:3000", "#3498db")
    
    def _kill_port(self, port):
        """Kill process on port (Windows)"""
        try:
            result = subprocess.run(
                f'netstat -aon | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
        except:
            pass
    
    def on_closing(self):
        """Handle window close"""
        if self.backend_process or self.frontend_process:
            if messagebox.askokcancel("Quit", "Stop all services and quit?"):
                self.stop_system()
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    root = tk.Tk()
    app = HiLabsLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
