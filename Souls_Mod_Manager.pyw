import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import subprocess
import os
import sys
import json
import shutil
from PIL import Image, ImageTk
import winreg
import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================
APP_TITLE = "Souls Mod Manager"
BG_COLOR = "#1a1a1a"
TEXT_COLOR = "#D4C79F"
ACCENT_COLOR = "#BF5C00"
HOVER_COLOR = "#9E4D00"
FONT_MAIN = ("Georgia", 11)
FONT_BTN = ("Georgia", 12, "bold")
FONT_HEADER = ("Georgia", 22, "bold")
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800
PROFILE_FILE = "profiles.json"
ICON_PATH = "darksign.ico"

# =============================================================================
# CORE LOGIC
# =============================================================================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

CURRENT_DIR = get_base_path()

def load_config():
    config_path = os.path.join(CURRENT_DIR, PROFILE_FILE)
    if not os.path.exists(config_path): return None
    try:
        with open(config_path, "r") as f: return json.load(f)
    except: return None

def save_config(data):
    config_path = os.path.join(CURRENT_DIR, PROFILE_FILE)
    try:
        with open(config_path, "w") as f: json.dump(data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Config Error", f"Failed to save profiles.json: {e}")

# =============================================================================
# SETUP WIZARD & AUTO-INSTALLER
# =============================================================================
def run_first_time_setup(root_window):
    setup_win = tk.Toplevel(root_window)
    setup_win.title("First Time Setup")
    setup_win.geometry("550x450")
    setup_win.configure(bg=BG_COLOR)
    setup_win.transient(root_window)
    setup_win.grab_set()

    tk.Label(setup_win, text="SOULS MOD MANAGER", font=FONT_HEADER, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
    tk.Label(setup_win, text="Welcome. Please select your game directories.", font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)

    paths = {"ds3": "", "er": ""}

    def auto_detect_games():
        # Helper to find steam games via Registry or Common Paths
        def find_game(app_id, exe_name, folder_name):
            # 1. Registry Search
            try:
                key_path = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Steam App {app_id}"
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                    install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                    # Check /Game/ subdir first (Standard for Souls)
                    if os.path.exists(os.path.join(install_path, "Game", exe_name)):
                        return os.path.join(install_path, "Game")
                    if os.path.exists(os.path.join(install_path, exe_name)):
                        return install_path
            except: pass

            # 2. Common Paths Search
            drives = [f"{d}:\\" for d in "CDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
            common_libs = [
                r"Program Files (x86)\Steam\steamapps\common",
                r"Program Files\Steam\steamapps\common",
                r"SteamLibrary\steamapps\common",
                r"Steam\steamapps\common"
            ]
            
            for drive in drives:
                for lib in common_libs:
                    full_path = os.path.join(drive, lib, folder_name, "Game")
                    if os.path.exists(os.path.join(full_path, exe_name)): return full_path
                    
                    full_path_root = os.path.join(drive, lib, folder_name)
                    if os.path.exists(os.path.join(full_path_root, exe_name)): return full_path_root
            return ""

        # Attempt Detection
        ds3_found = find_game("374320", "DarkSoulsIII.exe", "DARK SOULS III")
        er_found = find_game("1245620", "eldenring.exe", "ELDEN RING")

        if ds3_found:
            paths["ds3"] = ds3_found
            btn_ds3.config(text=f"DS3 Detected: {ds3_found[:30]}...", fg="#00FF00")
        
        if er_found:
            paths["er"] = er_found
            btn_er.config(text=f"ER Detected: {er_found[:30]}...", fg="#00FF00")

        if ds3_found or er_found:
            messagebox.showinfo("Auto-Detect", "Games detected automatically! Click 'FINISH SETUP' if they look correct.")

    def browse_ds3():
        path = filedialog.askdirectory(title="Select Dark Souls III Game Folder")
        if path:
            if os.path.exists(os.path.join(path, "DarkSoulsIII.exe")):
                paths["ds3"] = path
                btn_ds3.config(text="DS3 Selected ✔", fg="#00FF00")
            else: messagebox.showerror("Error", "Could not find DarkSoulsIII.exe in that folder.")

    def browse_er():
        path = filedialog.askdirectory(title="Select Elden Ring Game Folder")
        if path:
            if os.path.exists(os.path.join(path, "eldenring.exe")):
                paths["er"] = path
                btn_er.config(text="Elden Ring Selected ✔", fg="#00FF00")
            else: messagebox.showerror("Error", "Could not find eldenring.exe in that folder.")

    btn_ds3 = tk.Button(setup_win, text="Browse Dark Souls III Folder...", command=browse_ds3, font=FONT_MAIN, width=35, bg="#333", fg="white", bd=0)
    btn_ds3.pack(pady=15)

    btn_er = tk.Button(setup_win, text="Browse Elden Ring Folder...", command=browse_er, font=FONT_MAIN, width=35, bg="#333", fg="white", bd=0)
    btn_er.pack(pady=15)

    # Run Auto-Detect on Launch
    setup_win.after(500, auto_detect_games)

    def finish_setup():
        if not paths["ds3"] and not paths["er"]:
            messagebox.showwarning("Incomplete", "Please select at least one game folder.")
            return

        # Check for Save Folders (Backend Verification)
        appdata = os.environ['APPDATA']
        missing_saves = []
        if paths["ds3"] and not os.path.exists(os.path.join(appdata, "DarkSoulsIII")):
            missing_saves.append("Dark Souls III")
        if paths["er"] and not os.path.exists(os.path.join(appdata, "EldenRing")):
            missing_saves.append("Elden Ring")
            
        if missing_saves:
            msg = f"Warning: Save folders not found for:\n{', '.join(missing_saves)}\n\nIf you have not played these games yet, please launch them once to create the save structure."
            messagebox.showwarning("Save Folder Missing", msg)

        # Check for Mod Files in Game Directory (Safety Warning)
        if paths["ds3"]:
            dirty_files = ["dinput8.dll", "modengine.ini", "HoodiePatcher.dll"]
            found_dirty = [f for f in dirty_files if os.path.exists(os.path.join(paths["ds3"], f))]
            if found_dirty:
                warn_msg = f"WARNING: Mod files detected in Dark Souls III folder:\n{', '.join(found_dirty)}\n\nSMM requires a CLEAN game folder to switch mods safely.\nIf you proceed, these files may be DELETED when you launch Vanilla.\n\nPlease move them to a separate folder before using SMM."
                messagebox.showwarning("Mod Files Detected", warn_msg)

        default_data = {
            "settings": { "ds3_path": paths["ds3"], "er_path": paths["er"] },
            "profiles": {
                "Dark Souls III": [{"name": "Vanilla", "type": "internal", "exe": "DarkSoulsIII_Modern.exe", "mod_folder": "NONE", "save_ext": ".sl2"}],
                "Elden Ring": [{"name": "Vanilla", "type": "internal", "launcher": "NONE", "save_ext": ".sl2"}]
            }
        }
        
        install_status = create_dirs_and_install(paths["ds3"], paths["er"])
        save_config(default_data)
        
        msg = "SMM Configured!"
        if install_status: msg += f"\n\nAuto-Install Report:\n{install_status}"
        
        messagebox.showinfo("Success", msg)
        setup_win.destroy()

    tk.Button(setup_win, text="FINISH SETUP", command=finish_setup, font=FONT_BTN, bg=ACCENT_COLOR, fg="white", bd=0).pack(pady=30)
    root_window.wait_window(setup_win)

def create_dirs_and_install(ds3_path, er_path):
    status_msg = ""
    appdata = os.environ['APPDATA']
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if er_path:
        save_root = os.path.join(appdata, "EldenRing")
        # Create a Timestamped Backup of whatever is currently in the folder
        # This ensures we capture "Leftover" saves or "Manual" progress without overwriting existing Vanilla backups
        backup_dest = os.path.join(save_root, "_Save_Backups", f"Imported_{timestamp}")
        if not os.path.exists(backup_dest): os.makedirs(backup_dest)
        
        # Perform Initial Backup
        if os.path.exists(save_root):
            count = 0
            for item in os.listdir(save_root):
                s = os.path.join(save_root, item)
                d = os.path.join(backup_dest, item)
                if os.path.isdir(s) and item != "_Save_Backups":
                    try:
                        shutil.copytree(s, d)
                        count += 1
                    except Exception as e: print(f"Backup Error: {e}")
            if count > 0: 
                status_msg += f"\n✔ Created Safety Backup of {count} Elden Ring profiles to 'Imported_{timestamp}'."
                
                # Also ensure a "Vanilla" folder exists for the UI to use
                vanilla_dest = os.path.join(save_root, "_Save_Backups", "Vanilla")
                if not os.path.exists(vanilla_dest):
                    try:
                        shutil.copytree(backup_dest, vanilla_dest)
                        status_msg += "\n✔ Established initial 'Vanilla' profile."
                    except: pass

        # SMART SORT: Detect specific mod extensions and create dedicated backups
        mod_map = {
            ".cnv": "Convergence",
            ".co2": "Seamless Coop",
            ".err": "Reforged"
        }
        detected_mods = []
        
        if os.path.exists(save_root):
            for root, dirs, files in os.walk(save_root):
                if "_Save_Backups" in root: continue
                
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in mod_map:
                        mod_name = mod_map[ext]
                        
                        # Calculate destination: _Save_Backups/ModName/SteamID/
                        rel_path = os.path.relpath(root, save_root)
                        target_dir = os.path.join(save_root, "_Save_Backups", mod_name, rel_path)
                        
                        if not os.path.exists(target_dir): os.makedirs(target_dir)
                        
                        try:
                            shutil.copy2(os.path.join(root, file), target_dir)
                            if mod_name not in detected_mods: detected_mods.append(mod_name)
                        except: pass
                        
        if detected_mods:
            status_msg += f"\n✔ Detected & Organized saves for: {', '.join(detected_mods)}"

    if ds3_path:
        save_root = os.path.join(appdata, "DarkSoulsIII")
        backup_dest = os.path.join(save_root, "_Save_Backups", f"Imported_{timestamp}")
        if not os.path.exists(backup_dest): os.makedirs(backup_dest)
        
        # Perform Initial Backup
        if os.path.exists(save_root):
            count = 0
            for item in os.listdir(save_root):
                s = os.path.join(save_root, item)
                d = os.path.join(backup_dest, item)
                if os.path.isdir(s) and item != "_Save_Backups":
                    try:
                        shutil.copytree(s, d)
                        count += 1
                    except Exception as e: print(f"Backup Error: {e}")
            if count > 0: 
                status_msg += f"\n✔ Created Safety Backup of {count} DS3 profiles to 'Imported_{timestamp}'."

                # Also ensure a "Vanilla" folder exists for the UI to use
                vanilla_dest = os.path.join(save_root, "_Save_Backups", "Vanilla")
                if not os.path.exists(vanilla_dest):
                    try:
                        shutil.copytree(backup_dest, vanilla_dest)
                        status_msg += "\n✔ Established initial 'Vanilla' profile."
                    except: pass

        sb_root = os.path.join(ds3_path, "_Mod_Switchboard", "Executables")
        if not os.path.exists(sb_root): os.makedirs(sb_root)

        # Auto-Install EXEs if bundled
        local_execs = os.path.join(CURRENT_DIR, "Executables")
        if os.path.exists(local_execs):
            try:
                copied = 0
                for file in os.listdir(local_execs):
                    src = os.path.join(local_execs, file)
                    dst = os.path.join(sb_root, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                        copied += 1
                if copied > 0: status_msg += f"\n✔ Installed {copied} DS3 Executables."
            except Exception as e: status_msg += f"\n❌ DS3 Install Error: {e}"

    return status_msg

# =============================================================================
# GUI APPLICATION
# =============================================================================
class ModManagerApp:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        icon_file = os.path.join(CURRENT_DIR, ICON_PATH)
        if os.path.exists(icon_file):
            try: self.root.iconbitmap(icon_file)
            except: pass

        if self.config is None:
            run_first_time_setup(self.root)
            self.config = load_config()
        if self.config is None:
            self.root.destroy()
            return
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children(): widget.destroy()
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TCombobox', fieldbackground=BG_COLOR, background=ACCENT_COLOR, foreground="white", selectbackground=HOVER_COLOR, arrowcolor="white", bordercolor=ACCENT_COLOR, darkcolor=ACCENT_COLOR, lightcolor=ACCENT_COLOR)
        self.style.map('TCombobox', fieldbackground=[('readonly', BG_COLOR)], selectbackground=[('readonly', BG_COLOR)], selectforeground=[('readonly', TEXT_COLOR)])
        self.style.configure('TEntry', fieldbackground="#333333", foreground="white", insertcolor="white", bordercolor="#333333", lightcolor="#333333", darkcolor="#333333")
        self.style.configure('TScrollbar', background=BG_COLOR, troughcolor='#222', arrowcolor=TEXT_COLOR, bordercolor=BG_COLOR)
        self.style.map('TScrollbar', background=[('active', HOVER_COLOR)])

        try:
            img_path = os.path.join(CURRENT_DIR, "darksign.png")
            if os.path.exists(img_path):
                pil_img = Image.open(img_path).resize((180, 180), Image.LANCZOS)
                self.icon_header = ImageTk.PhotoImage(pil_img)
                tk.Label(self.root, image=self.icon_header, bg=BG_COLOR).pack(pady=(20, 0))
        except: pass
        
        tk.Label(self.root, text="SOULS MOD MANAGER", font=FONT_HEADER, fg=ACCENT_COLOR, bg=BG_COLOR).pack(pady=(10, 20))

        tk.Label(self.root, text="SELECT GAME", font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        self.game_var = tk.StringVar(value="Elden Ring")
        self.game_combo = ttk.Combobox(self.root, textvariable=self.game_var, values=["Dark Souls III", "Elden Ring"], font=FONT_MAIN, state="readonly", width=25, justify='center')
        self.game_combo.pack(pady=5)
        self.game_combo.bind("<<ComboboxSelected>>", self.update_profiles)
        
        tk.Label(self.root, text="SELECT PROFILE", font=FONT_MAIN, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20, 0))
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(self.root, textvariable=self.profile_var, values=[], font=FONT_MAIN, state="readonly", width=25, justify='center')
        self.profile_combo.pack(pady=5)
        
        tk.Button(self.root, text="PLAY GAME", command=self.launch_game, font=FONT_BTN, bg="#008800", fg="white", width=20, bd=0, activebackground="#006600", activeforeground="white").pack(pady=(40, 10))
        tk.Button(self.root, text="BACKUP SAVE ONLY", command=self.backup_only, font=FONT_MAIN, bg="#444444", fg="white", width=20, bd=0, activebackground="#666666", activeforeground="white").pack(pady=5)
        tk.Button(self.root, text="OPEN SAVE FOLDER", command=self.open_save_folder, font=FONT_MAIN, bg="#444444", fg="white", width=20, bd=0, activebackground="#666666", activeforeground="white").pack(pady=5)
        tk.Button(self.root, text="ADD / REMOVE MODS", command=self.open_manager, font=FONT_MAIN, bg=ACCENT_COLOR, fg="white", width=20, bd=0, activebackground=HOVER_COLOR, activeforeground="white").pack(pady=30)

        self.update_profiles()

    def update_profiles(self, *args):
        game = self.game_var.get()
        if game not in self.config['profiles']: self.config['profiles'][game] = []
        profiles = [p['name'] for p in self.config['profiles'][game]]
        self.profile_combo['values'] = profiles
        if profiles: self.profile_var.set(profiles[0])
        else: self.profile_var.set("")

    def get_current_profile(self):
        game = self.game_var.get()
        name = self.profile_var.get()
        for p in self.config['profiles'][game]:
            if p['name'] == name: return p
        return None

    def open_save_folder(self):
        game = self.game_var.get()
        appdata = os.environ['APPDATA']
        save_root = os.path.join(appdata, "DarkSoulsIII") if game == "Dark Souls III" else os.path.join(appdata, "EldenRing")
        if os.path.exists(save_root):
            os.startfile(save_root)
        else:
            messagebox.showerror("Error", "Save folder not found.")

    def launch_game(self):
        profile = self.get_current_profile()
        if not profile: 
            messagebox.showwarning("No Profile", "Please select a mod profile.")
            return
        game = self.game_var.get()
        if game == "Dark Souls III":
            script = "Master_DS3.bat"
            exe_to_use = profile.get('exe', 'DarkSoulsIII_Modern.exe')
            args = [profile['name'], exe_to_use, profile['mod_folder'], self.config['settings']['ds3_path']]
        else:
            script = "Master_ER.bat"
            args = [profile['name'], profile['launcher'], profile['save_ext'], self.config['settings']['er_path']]
        self.run_batch(script, args)

    def backup_only(self):
        profile = self.get_current_profile()
        if not profile: return
        game = self.game_var.get()
        appdata = os.environ['APPDATA']
        save_root = os.path.join(appdata, "DarkSoulsIII") if game == "Dark Souls III" else os.path.join(appdata, "EldenRing")
        backup_dest = os.path.join(save_root, "_Save_Backups", profile['name'])
        if not os.path.exists(backup_dest): os.makedirs(backup_dest)
        count = 0
        for root_dir, dirs, files in os.walk(save_root):
            if "_Save_Backups" in root_dir: continue
            for file in files:
                if "GraphicsConfig" not in file:
                    try: shutil.copy2(os.path.join(root_dir, file), backup_dest); count += 1
                    except: pass
        messagebox.showinfo("Backup", f"Backed up {count} files for '{profile['name']}'.")

    def run_batch(self, script_name, args):
        script_path = os.path.join(CURRENT_DIR, "Start_Game", script_name)
        if not os.path.exists(script_path): messagebox.showerror("Error", f"Missing script: {script_path}"); return
        subprocess.Popen([script_path] + args, cwd=os.path.join(CURRENT_DIR, "Start_Game"), creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.root.quit()

    def open_manager(self):
        man_win = tk.Toplevel(self.root)
        man_win.title("Mod Profile Manager")
        man_win.geometry("600x800")
        man_win.configure(bg=BG_COLOR)
        man_win.transient(self.root)
        try: man_win.iconbitmap(os.path.join(CURRENT_DIR, ICON_PATH))
        except: pass

        tk.Label(man_win, text="ADD NEW MOD PROFILE", font=FONT_BTN, bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(15, 5))
        tk.Label(man_win, text="Select Game:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_MAIN).pack()
        man_game_var = tk.StringVar(value=self.game_var.get())
        game_combo = ttk.Combobox(man_win, textvariable=man_game_var, values=["Dark Souls III", "Elden Ring"], font=FONT_MAIN, state="readonly", width=25, justify='center')
        game_combo.pack(pady=5)
        tk.Label(man_win, text="Mod Name:", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT_MAIN).pack()
        name_entry = ttk.Entry(man_win, width=40, font=FONT_MAIN)
        name_entry.pack(pady=5)

        path_var = tk.StringVar()
        def pick_file():
            if man_game_var.get() == "Elden Ring":
                f = filedialog.askopenfilename(title="Select Launcher (.bat/.exe)", filetypes=[("Launcher", "*.bat *.exe")])
            else:
                choice = messagebox.askyesno("DS3 Mod Type", "Are you adding an External Launcher (like Archipelago)?\n\nYes = Select .bat/.exe file\nNo = Select Mod Folder (dinput8.dll)")
                if choice: f = filedialog.askopenfilename(title="Select Launcher (.bat/.exe)", filetypes=[("Launcher", "*.bat *.exe")])
                else: f = filedialog.askdirectory(title="Select Folder containing dinput8.dll")
            if f: path_var.set(f)

        tk.Button(man_win, text="Select Mod File/Folder", command=pick_file, bg="#444444", fg="white", bd=0, activebackground="#666", activeforeground="white", font=FONT_MAIN).pack(pady=5)
        tk.Label(man_win, textvariable=path_var, bg=BG_COLOR, fg="#888", wraplength=450).pack()

        # Save Ext is now handled automatically by the "Vacuum" system (mirrors all files)
        # Hidden from UI to simplify user experience

        def save_profile():
            name = name_entry.get().strip(); path = path_var.get().strip(); game = man_game_var.get()
            if not name or not path: messagebox.showerror("Error", "Name and Path required."); return
            if any(p['name'] == name for p in self.config['profiles'][game]): messagebox.showerror("Error", "Profile exists."); return

            path = path.replace("/", "\\")
            new_entry = {}
            if game == "Elden Ring":
                new_entry = { "name": name, "type": "external", "launcher": path, "save_ext": "AUTO" }
            else:
                # Logic: File = Modern Exe. Folder = Legacy Exe.
                is_file = os.path.isfile(path)
                new_entry = { "name": name, "type": "external" if is_file else "internal", "exe": "DarkSoulsIII_Modern.exe" if is_file else "DarkSoulsIII_Legacy.exe", "mod_folder": path, "save_ext": "AUTO" }

            self.config['profiles'][game].append(new_entry)
            save_config(self.config)
            refresh_list(); self.update_profiles(); name_entry.delete(0, 'end'); path_var.set("")
            messagebox.showinfo("Success", f"Added '{name}'.")

        tk.Button(man_win, text="SAVE PROFILE", command=save_profile, font=FONT_BTN, bg="#008800", fg="white", bd=0).pack(pady=15)
        tk.Frame(man_win, height=2, bg=ACCENT_COLOR).pack(fill="x", pady=20, padx=20)
        tk.Label(man_win, text="MANAGE EXISTING PROFILES", font=FONT_BTN, bg=BG_COLOR, fg="#FF5555").pack(pady=5)

        list_frame = tk.Frame(man_win, bg=BG_COLOR)
        list_frame.pack(pady=10, padx=20, fill="x", expand=True)
        profile_list = tk.Listbox(list_frame, height=8, bg="#222", fg=TEXT_COLOR, font=FONT_MAIN, bd=0, highlightthickness=0, selectbackground=ACCENT_COLOR)
        profile_list.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=profile_list.yview); scroll.pack(side="right", fill="y"); profile_list.config(yscrollcommand=scroll.set)

        def refresh_list(*args):
            profile_list.delete(0, 'end'); game = man_game_var.get()
            for p in self.config['profiles'].get(game, []): profile_list.insert('end', p['name'])
        game_combo.bind("<<ComboboxSelected>>", lambda e: refresh_list()); refresh_list()

        def delete_profile():
            sel = profile_list.curselection()
            if not sel: return
            name = profile_list.get(sel[0]); game = man_game_var.get()
            if name == "Vanilla": messagebox.showwarning("Error", "Cannot delete Vanilla."); return
            if messagebox.askyesno("Delete", f"Remove '{name}'?"):
                self.config['profiles'][game] = [p for p in self.config['profiles'][game] if p['name'] != name]
                save_config(self.config); refresh_list(); self.update_profiles()

        tk.Button(man_win, text="DELETE SELECTED", command=delete_profile, font=FONT_BTN, bg="#880000", fg="white", bd=0).pack(pady=10)

def main():
    global root; root = tk.Tk()
    root.title(APP_TITLE); root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"); root.configure(bg=BG_COLOR)
    app = ModManagerApp(root); root.mainloop()

if __name__ == "__main__": main()
