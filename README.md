# SOULS MOD MANAGER (SMM) - UNIVERSAL LAUNCHER

[![Download Latest Release](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge&logo=windows)](https://github.com/JollyOscar/Souls-Mod-Manager-SMM-/releases/latest)

**Version:** 2.1  
**Target Games:** Dark Souls III, Elden Ring

## WHAT IS THIS?

A safe, "switchboard" style launcher for Dark Souls III and Elden Ring.
It allows you to swap between Vanilla (Online) and multiple Mods (Offline) without risking bans, by automatically managing and isolating your save files.

### FEATURES

* **Safe Save Swapping:** Mods get their own save "box". They never touch Vanilla.
* **Universal Support:** Works with DLL mods (Cinders) and External Launchers (Reforged).
* **"Vacuum" Backups:** Automatically captures every file in your save folder.
* **Multi-Account Support:** Safely handles multiple Steam IDs without overwriting saves.
* **Full Folder Mirroring:** Supports complex save structures (like Convergence's .cnv files).
* **Crash Recovery:** If the launcher crashes, your saves are automatically moved to a `_RESCUE` folder on next launch.

---

## UPDATING FROM OLDER VERSIONS

If you are updating from v1.x or v2.0:

1. **Backup:** It is always good practice to backup your `AppData/Roaming/EldenRing` or `DarkSoulsIII` folders manually first.
2. **Install:** Drag and drop the new files into your existing SMM folder.
3. **Run:** Run `RUNTHISFIRST.bat` to update your shortcuts.
4. **Launch:** Open the app. It will detect your existing `profiles.json` and keep all your mods.
   * **Note:** On the first run, SMM v2.1 will perform a "Smart Sort" of your save folder. It may move loose `.cnv` (Convergence) or `.err` (Reforged) files into their own backup folders to keep things clean. This is normal!

---

## INSTALLATION

1. Extract this folder anywhere (Desktop, Documents, etc.).
   * **DO NOT** run the app from inside the Zip file.
2. Run `RUNTHISFIRST.bat`.
   * This will check your files and create a Desktop Shortcut for you.
3. **FIRST TIME SETUP:**
   * **AUTO-DETECT:** The app will attempt to automatically find your games on Steam.
   * If not found, manually select the folders where `DarkSoulsIII.exe` and `eldenring.exe` live.
   * **AUTO-INSTALLER:** The app will automatically copy the required DS3 Executables (Legacy & Modern) into your game folder for you.

---

## FILE STRUCTURE GUIDE

For the manager to work best, ensure your folders look like this:

### 1. ELDEN RING

**Standard Steam Path:** `C:\Program Files (x86)\Steam\steamapps\common\ELDEN RING\Game`

* `eldenring.exe` (The Game)
* `_Mod_Switchboard\` (Created by SMM)

**Mod Setup (Example: Convergence):**

* Download the mod.
* Place it anywhere (e.g., `C:\Mods\ConvergenceER`).
* Inside, you should see `launch_mod.bat` or similar.
* **In SMM:** Select that `.bat` file.

### 2. DARK SOULS III

**Standard Steam Path:** `C:\Program Files (x86)\Steam\steamapps\common\DARK SOULS III\Game`

* `DarkSoulsIII.exe` (The Game)
* `DarkSoulsIII_Legacy.exe` (Installed by SMM)
* `DarkSoulsIII_Modern.exe` (Installed by SMM)

**Mod Setup (Example: Cinders):**

* Download the mod.
* Place it anywhere (e.g., `C:\Mods\Cinders`).
* Inside, you should see `dinput8.dll` and a `Cinders` folder.
* **In SMM:** Select this **Folder**.

---

## ADDING MODS

1. Click **ADD / REMOVE MODS**.

### [A] ELDEN RING MODS (e.g., Convergence, Reforged)

* **Select Game:** Elden Ring.
* **Name:** Give it a name (e.g., "Convergence").
* **Click "Select Mod File":** Browse to the `.bat` or `.exe` you usually click to launch that mod (e.g., `launch_convergence.bat`).
* **Click SAVE PROFILE.**

### [B] DARK SOULS III MODS (e.g., Cinders, Archipelago)

* **Select Game:** Dark Souls III.
* **Name:** Give it a name.
* **Click "Select Mod File":**
  * **For DLL Mods (Cinders):** Select the *Folder* containing `dinput8.dll`.
  * **For External Launchers (Archipelago):** Select the `.bat` file.
* **Click SAVE PROFILE.**

---

## DEVELOPER INFO

For technical details, architecture, and contribution guidelines, please refer to [DEVELOPER_CONTEXT.md](DEVELOPER_CONTEXT.md).
