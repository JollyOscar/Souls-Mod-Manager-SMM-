@echo off
setlocal
:: ARGS: [1:ModName] [2:LauncherPath] [3:Ignored] [4:GameDir]

set "MOD_NAME=%~1"
set "LAUNCHER=%~2"
set "GAME_DIR=%~4"
set "SAVE_ROOT=%APPDATA%\EldenRing"
set "BACKUP_DIR=%SAVE_ROOT%\_Save_Backups\%MOD_NAME%"
set "LOG_FILE=%~dp0..\SMM_Debug.log"

echo [%DATE% %TIME%] [ER] Launching %MOD_NAME% >> "%LOG_FILE%"

:: 1. Safety Nuke & Rescue
taskkill /F /IM "eldenring.exe" >nul 2>&1
echo [SMM] Clearing live save state...
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        :: Check for stranded files (Crash Recovery)
        dir /A-D /B "%%D" >nul 2>&1
        if not errorlevel 1 (
            echo [SMM] WARNING: Stranded save files detected!
            echo [SMM] Moving to _RESCUE folder... >> "%LOG_FILE%"
            if not exist "%SAVE_ROOT%\_Save_Backups\_RESCUE" mkdir "%SAVE_ROOT%\_Save_Backups\_RESCUE"
            robocopy "%%D" "%SAVE_ROOT%\_Save_Backups\_RESCUE\%%~nxD" /MIR /R:3 /W:1 >> "%LOG_FILE%"
        )
        del /Q "%%D\*.*" >nul 2>&1
    )
)

:: 2. Inject State
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
echo [SMM] Importing save state...
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        if exist "%BACKUP_DIR%\%%~nxD" (
            echo [%DATE% %TIME%] Restoring Nested Backup to %%D >> "%LOG_FILE%"
            robocopy "%BACKUP_DIR%\%%~nxD" "%%D" /MIR /R:2 /W:1 >> "%LOG_FILE%"
        ) else (
            echo [%DATE% %TIME%] Restoring Flat Backup to %%D >> "%LOG_FILE%"
            robocopy "%BACKUP_DIR%" "%%D" /E /IS /IT /R:2 /W:1 /XD * >> "%LOG_FILE%"
        )
    )
)

:: 3. Launch
if "%LAUNCHER%"=="NONE" (
    echo [SMM] Launching Vanilla via Steam...
    start steam://rungameid/1245620
) else (
    echo [SMM] Launching Mod Script...
    for %%I in ("%LAUNCHER%") do (
        echo [SMM] Running: %%~nxI
        start "" /D "%%~dpI" "%%~nxI"
    )
)

:: 4. Watchdog
echo [SMM] Monitoring session...
set /a TIMEOUT_COUNT=0

:WAIT_START
timeout /t 2 >nul
tasklist /FI "IMAGENAME eq eldenring.exe" 2>NUL | find /I /N "eldenring.exe">NUL
if "%ERRORLEVEL%"=="0" goto WAIT_CLOSE

set /a TIMEOUT_COUNT+=1
if %TIMEOUT_COUNT% GEQ 15 (
    echo [SMM] ERROR: Game did not start after 30 seconds.
    goto BACKUP_AND_EXIT
)
goto WAIT_START

:WAIT_CLOSE
timeout /t 5 >nul
tasklist /FI "IMAGENAME eq eldenring.exe" 2>NUL | find /I /N "eldenring.exe">NUL
if "%ERRORLEVEL%"=="0" goto WAIT_CLOSE

:: 5. Backup & Cleanup
:BACKUP_AND_EXIT
echo [SMM] Game closed. Waiting for file release...
timeout /t 3 >nul
echo [SMM] Capturing save state...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
for /d %%D in ("%SAVE_ROOT%\*") do (
    if /I not "%%~nxD"=="_Save_Backups" (
        :: Check for files before backing up to prevent wiping backups with empty folders (Multi-User Safety)
        dir /A-D /B "%%D" >nul 2>&1
        if not errorlevel 1 (
            echo [%DATE% %TIME%] Backing up %%D >> "%LOG_FILE%"
            if not exist "%BACKUP_DIR%\%%~nxD" mkdir "%BACKUP_DIR%\%%~nxD"
            robocopy "%%D" "%BACKUP_DIR%\%%~nxD" /MIR /R:3 /W:1 >> "%LOG_FILE%"
            
            echo [%DATE% %TIME%] Nuking %%D >> "%LOG_FILE%"
            del /Q "%%D\*.*" >nul
        )
    )
)

echo [SMM] State saved. Safe to close.
timeout /t 3
exit