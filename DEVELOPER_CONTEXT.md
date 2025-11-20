# SOULS MOD MANAGER (SMM) - DEVELOPER CONTEXT

**Project:** Souls Mod Manager (SMM) v2.1
**Language:** Python 3 (Tkinter), Windows Batch
**Dependencies:** `pillow`, `pyinstaller`
**Target Games:** Dark Souls III, Elden Ring

## 1. CORE FUNCTIONALITY

SMM acts as a "Switchboard" launcher. It does not merge mods; it isolates them.

* **Safety Rule:** Only one save state exists in `%APPDATA%` at a time.
* **The Cycle:**
  1. **Backup:** Moves *current* save files from AppData to `_Save_Backups\<LastProfile>`.
  2. **Nuke:** Deletes `*.*` (everything) in the live AppData save folder.
  3. **Inject:** Copies `*.*` from `_Save_Backups\<NewProfile>` to AppData.
  4. **Launch:** Starts the game (Steam for Vanilla, ModEngine2/External for Mods).
  5. **Vacuum:** On exit, moves `*.*` back to storage and nukes the live folder again.

## 2. DIRECTORY STRUCTURE (RELEASE)

```text
Root/
├── Souls_Mod_Manager.exe    (Compiled Python App)
├── profiles.json            (User Config - Created on first run)
├── darksign.png             (UI Header)
├── darksign.ico             (App Icon)
├── Start_Game/              (Batch Scripts)
│   ├── Master_DS3.bat       (Universal DS3 Launcher)
│   └── Master_ER.bat        (Universal ER Launcher)
└── Executables/             (Auto-Install Assets for DS3)
    ├── DarkSoulsIII_Legacy.exe
    └── DarkSoulsIII_Modern.exe
```

## 3. SCRIPT LOGIC

**A. Python (`Souls_Mod_Manager.pyw`)**

* **Role:** UI, Config Manager, Setup Wizard.
* **Mod Logic:**
  * **Internal (DS3 only):** Point to a folder containing `dinput8.dll`. SMM forces `Legacy.exe`.
  * **External (DS3 & ER):** Point to a `.bat` or `.exe` launcher. SMM forces `Modern.exe` (DS3) or just runs the launcher (ER).
* **Execution:** Calls `Master_*.bat` with arguments: `[ModName] [ExeToUse] [ModPath] [GameDir]`.

**B. Batch (`Master_DS3.bat` / `Master_ER.bat`)**

* **Arguments:** `%1=Name`, `%2=Exe`, `%3=Path`, `%4=GameDir`.
* **Launch Logic:**
  * If `%3` is a **Folder**: Copies contents (DLLs) to Game Dir -> Launches Game.
  * If `%3` is a **File**: Runs file via `start "" /D "Folder" "File"` (Detached Process) -> Monitors Game Process.
* **Watchdog:** Loops checking for `DarkSoulsIII.exe` / `eldenring.exe`.
  * **Timeout Safety:** If game doesn't appear in 15s, it aborts and restores backup.
  * **Close Trigger:** When game process ends, it triggers the "Vacuum" backup.

## 4. KEY TECHNICAL DECISIONS

* **"Vacuum" Backup:** We use `copy *.*` instead of specific extensions (`.sl2`, `.co2`) to support any mod file type automatically.
* **DS3 Exe Swapping:** We maintain `Legacy` (1.15) and `Modern` executables in `_Mod_Switchboard` and swap them physically before launch.
* **Working Directory Fix:** External launchers (Archipelago, ModEngine2) are launched using `start /D` to ensure they find their relative config files.

## 5. KNOWN BEHAVIORS

* **First Run:** App detects missing `profiles.json` -> Runs Setup Wizard -> Auto-installs DS3 EXEs.
* **Archipelago:** Must be added as an **External Launcher** (`launchmod_darksouls3.bat`). This correctly forces `Modern.exe` and cleans up old DLLs.
* **Cinders/Convergence:** Must be added as **Internal Mods** (Select Folder). This correctly forces `Legacy.exe` and injects DLLs.
