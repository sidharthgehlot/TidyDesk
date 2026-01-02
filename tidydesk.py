import os
import shutil
import json
import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import sys

# --- CONFIGURATION ---
APP_NAME = "TidyDesk"
DEST_FOLDER_NAME = "TidyDesk"
RESTORE_LOG = "_restore.json"
STATE_FILE = Path(os.path.expanduser("~/.tidydesk_state.json"))

FILE_CATEGORIES = {
    "PDFs": [".pdf"],
    "Documents": [".doc", ".docx", ".txt", ".rtf"],
    "Excel": [".xls", ".xlsx", ".csv"],
    "Presentations": [".ppt", ".pptx"],
    "Images": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"],
    "Videos": [".mp4", ".mov", ".mkv", ".avi"],
    "Installers": [".zip", ".rar", ".7z", ".exe", ".msi"],
}

class TidyDeskApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("600x550")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_source = None
        self.scan_results = {}
        self.last_clean_folder = self.load_state()

        # UI Container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self.show_home()

    # --- STATE MANAGEMENT ---
    def load_state(self):
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get("last_clean_folder")
            except: pass
        return None

    def save_state(self, path):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({"last_clean_folder": str(path)}, f)
        except: pass

    # --- NAVIGATION ---
    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_container()
        
        # Title
        title_label = ctk.CTkLabel(self.container, text=APP_NAME, font=ctk.CTkFont(size=36, weight="bold"))
        title_label.pack(pady=(40, 5))
        
        subtitle_label = ctk.CTkLabel(self.container, text="One click. Nothing deleted.", font=ctk.CTkFont(size=16), text_color="gray")
        subtitle_label.pack(pady=(0, 30))

        # Cards Frame
        cards_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        cards_frame.pack(fill="x", padx=40)

        self.create_card(cards_frame, "🖥", "Desktop", lambda: self.handle_selection("desktop"))
        self.create_card(cards_frame, "📥", "Downloads", lambda: self.handle_selection("downloads"))
        self.create_card(cards_frame, "📁", "Choose folder", lambda: self.handle_selection("custom"))

        # Restore Button
        if self.last_clean_folder and Path(self.last_clean_folder).exists():
            restore_btn = ctk.CTkButton(
                self.container, 
                text="Restore last clean", 
                fg_color="transparent", 
                text_color="gray",
                hover_color="#2B2B2B",
                font=ctk.CTkFont(size=12, underline=True),
                command=self.confirm_restore
            )
            restore_btn.pack(side="bottom", pady=20)

    def create_card(self, parent, icon, label, command):
        card = ctk.CTkFrame(parent, corner_radius=20, fg_color="#2B2B2B", cursor="hand2")
        card.pack(fill="x", pady=10)
        
        # Make card clickable
        card.bind("<Button-1>", lambda e: command())
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", padx=20, pady=15)
        content.bind("<Button-1>", lambda e: command())

        icon_lbl = ctk.CTkLabel(content, text=icon, font=ctk.CTkFont(size=32))
        icon_lbl.pack(side="left", padx=(0, 15))
        icon_lbl.bind("<Button-1>", lambda e: command())

        label_lbl = ctk.CTkLabel(content, text=label, font=ctk.CTkFont(size=18, weight="bold"))
        label_lbl.pack(side="left")
        label_lbl.bind("<Button-1>", lambda e: command())

    def show_preview(self):
        self.clear_container()
        
        ctk.CTkLabel(self.container, text="Here’s what we’ll organize", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(40, 20))
        
        # Summary
        summary_frame = ctk.CTkFrame(self.container, fg_color="#2B2B2B", corner_radius=15)
        summary_frame.pack(fill="x", padx=60, pady=10)
        
        total_files = 0
        for cat, count in self.scan_results.items():
            if count > 0:
                row = ctk.CTkFrame(summary_frame, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=5)
                ctk.CTkLabel(row, text=f"{count} {cat}", font=ctk.CTkFont(size=16)).pack(side="left")
                ctk.CTkLabel(row, text="→", font=ctk.CTkFont(size=16), text_color="gray").pack(side="left", padx=10)
                ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
                total_files += count

        if total_files == 0:
            self.show_success(is_already_clean=True)
            return

        # Buttons
        btn_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=60, pady=40)
        
        ctk.CTkButton(
            btn_frame, 
            text="Clean Now", 
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            corner_radius=25,
            command=self.start_cleanup
        ).pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="Go Back", 
            fg_color="transparent",
            hover_color="#2B2B2B",
            command=self.show_home
        ).pack(fill="x")

    def show_success(self, is_already_clean=False):
        self.clear_container()
        
        icon_text = "👍" if is_already_clean else "✨"
        msg_header = "This folder was already clean" if is_already_clean else "All set"
        msg_sub = "" if is_already_clean else f"Your files are now inside ‘{DEST_FOLDER_NAME}’."

        ctk.CTkLabel(self.container, text=icon_text, font=ctk.CTkFont(size=64)).pack(pady=(100, 10))
        ctk.CTkLabel(self.container, text=msg_header, font=ctk.CTkFont(size=28, weight="bold")).pack()
        if msg_sub:
            ctk.CTkLabel(self.container, text=msg_sub, font=ctk.CTkFont(size=16), text_color="gray").pack(pady=10)
            
        ctk.CTkButton(
            self.container, 
            text="Done", 
            width=200, 
            height=40,
            corner_radius=20,
            command=self.show_home
        ).pack(pady=40)

    # --- LOGIC ---
    def handle_selection(self, choice):
        if choice == "desktop":
            path = Path(os.path.expanduser("~/Desktop"))
        elif choice == "downloads":
            path = Path(os.path.expanduser("~/Downloads"))
        else:
            path_str = filedialog.askdirectory()
            if not path_str: return
            path = Path(path_str)
        
        self.current_source = path
        self.scan_files()
        self.show_preview()

    def scan_files(self):
        self.scan_results = {cat: 0 for cat in FILE_CATEGORIES}
        self.scan_results["Others"] = 0
        
        for item in self.current_source.iterdir():
            if self.is_safe_to_move(item):
                ext = item.suffix.lower()
                found = False
                for cat, exts in FILE_CATEGORIES.items():
                    if ext in exts:
                        self.scan_results[cat] += 1
                        found = True
                        break
                if not found:
                    self.scan_results["Others"] += 1

    def is_safe_to_move(self, item):
        if item.is_dir() or item.suffix.lower() == ".lnk" or item.name.startswith("."):
            return False
        # Avoid moving the TidyDesk folder itself if it already exists
        if item.name == DEST_FOLDER_NAME:
            return False
        # Avoid moving self
        try:
            if item.resolve() == Path(sys.argv[0]).resolve():
                return False
        except: pass
        return True

    def start_cleanup(self):
        source = self.current_source
        dest = source / DEST_FOLDER_NAME
        
        dest.mkdir(exist_ok=True)
        move_log = []
        
        for item in source.iterdir():
            if not self.is_safe_to_move(item):
                continue
            
            # Determine Category
            ext = item.suffix.lower()
            category = "Others"
            for cat, exts in FILE_CATEGORIES.items():
                if ext in exts:
                    category = cat
                    break
            
            cat_folder = dest / category
            cat_folder.mkdir(exist_ok=True)
            
            target_path = cat_folder / item.name
            
            # Conflict handling: Skip if exists
            if target_path.exists():
                continue
            
            try:
                shutil.move(str(item), str(target_path))
                move_log.append({
                    "from": str(item),
                    "to": str(target_path)
                })
            except: continue

        # Save restore log
        if move_log:
            log_path = dest / RESTORE_LOG
            with open(log_path, 'w') as f:
                json.dump(move_log, f)
            
            self.save_state(dest)
            self.last_clean_folder = str(dest)
            
        self.show_success()

    def confirm_restore(self):
        if messagebox.askyesno("Restore", "Put everything back where it was?"):
            self.perform_restore()

    def perform_restore(self):
        if not self.last_clean_folder: return
        
        dest_path = Path(self.last_clean_folder)
        log_path = dest_path / RESTORE_LOG
        
        if not log_path.exists():
            messagebox.showinfo("Wait", "Restore information not found.")
            return

        try:
            with open(log_path, 'r') as f:
                move_log = json.load(f)
            
            for entry in move_log:
                orig = Path(entry["from"])
                new = Path(entry["to"])
                if new.exists() and not orig.exists():
                    shutil.move(str(new), str(orig))
            
            # Clean up the TidyDesk folder if empty
            # We don't delete everything, just the categories we created
            for cat in list(FILE_CATEGORIES.keys()) + ["Others"]:
                cat_dir = dest_path / cat
                if cat_dir.exists() and not any(cat_dir.iterdir()):
                    cat_dir.rmdir()
            
            log_path.unlink()
            if not any(dest_path.iterdir()):
                dest_path.rmdir()
            
            self.last_clean_folder = None
            self.save_state("")
            
            messagebox.showinfo("Restored", "Everything is back to normal! ✨")
            self.show_home()
        except Exception as e:
            messagebox.showerror("Error", f"Could not restore: {e}")

if __name__ == "__main__":
    app = TidyDeskApp()
    app.mainloop()
