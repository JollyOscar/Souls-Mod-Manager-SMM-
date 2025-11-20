@echo off
setlocal
:: ARGS: [1:ModName] [2:ExeName] [3:ModPath] [4:GameDir]

set "MOD_NAME=%~1"
set "EXE_NAME=%~2"
set "MOD_PATH=%~3"
set "GAME_DIR=%~4"
set "SAVE_ROOT=%APPDATA%\DarkSoulsIII"
set "BACKUP_DIR=%SAVE_ROOT%\_Save_Backups\%MOD_NAME%"

echo [SMM] Launching Dark Souls III: %MOD_NAME%

:: 1. Safety Nuke
echo [SMM] Clearing live save state...
taskkill /F /IM "DarkSoulsIII.exe" >nul 2>&1
for /d %%D in ("%SAVE_ROOT%\0*") do (
    del /Q "%%D\*.*" >nul 2>&1
)

:: 2. Inject State
if exist "%BACKUP_DIR%" (
    echo [SMM] Importing save state...
    for /d %%D in ("%SAVE_ROOT%\0*") do (
        copy /Y "%BACKUP_DIR%\*.*" "%%D\" >nul
    )
) else (
    echo [SMM] No backup found. Starting fresh state.
)

:: 3. Swap Executable
echo [SMM] Swapping to %EXE_NAME%...
copy /Y "%GAME_DIR%\_Mod_Switchboard\Executables\%EXE_NAME%" "%GAME_DIR%\DarkSoulsIII.exe" >nul

:: 4. Inject OR Launch
if "%MOD_PATH%"=="NONE" (
    echo [SMM] Cleaning Vanilla directory...
    call :CLEANUP
    echo [SMM] Launching Vanilla...
    cd /d "%GAME_DIR%"
    start "" "DarkSoulsIII.exe"

) else if exist "%MOD_PATH%\*" (
    :: DIRECTORY -> DLL INJECTION MODE
    echo [SMM] Injecting Mod DLLs...
    copy /Y "%MOD_PATH%\*" "%GAME_DIR%\" >nul
    echo [SMM] Launching Game...
    cd /d "%GAME_DIR%"
    start "" "DarkSoulsIII.exe"

) else (
    :: FILE -> EXTERNAL LAUNCHER MODE
    echo [SMM] Launching External Script...
    call :CLEANUP
    
    for %%I in ("%MOD_PATH%") do (
        echo [SMM] Running: %%~nxI
        start "" /D "%%~dpI" "%%~nxI"
    )
)

:: 5. Watchdog
echo [SMM] Waiting for game to start...
set /a TIMEOUT_COUNT=0

:WAIT_START
timeout /t 2 /nobreak >nul
tasklist /FI "IMAGENAME eq DarkSoulsIII.exe" 2>NUL | find /I /N "DarkSoulsIII.exe">NUL
if "%ERRORLEVEL%"=="0" goto GAME_RUNNING

set /a TIMEOUT_COUNT+=1
if %TIMEOUT_COUNT% GEQ 8 (
    echo [SMM] ERROR: Game did not start after 15 seconds.
    goto BACKUP_AND_EXIT
)
goto WAIT_START

:GAME_RUNNING
echo [SMM] Game detected! Monitoring session...

:WAIT_CLOSE
timeout /t 5 /nobreak >nul
tasklist /FI "IMAGENAME eq DarkSoulsIII.exe" 2>NUL | find /I /N "DarkSoulsIII.exe">NUL
if "%ERRORLEVEL%"=="0" goto WAIT_CLOSE

:: 6. Backup & Cleanup
:BACKUP_AND_EXIT
echo [SMM] Game closed. Capturing save state...
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
for /d %%D in ("%SAVE_ROOT%\0*") do (
    copy /Y "%%D\*.*" "%BACKUP_DIR%\" >nul
    del /Q "%%D\*.*" >nul
)
echo [SMM] State saved. Safe to close.
timeout /t 3
exit

:: ---------------------------------------------------------
:CLEANUP
del /Q "%GAME_DIR%\dinput8.dll" >nul 2>&1
del /Q "%GAME_DIR%\modengine.ini" >nul 2>&1
del /Q "%GAME_DIR%\HoodiePatcher.dll" >nul 2>&1
del /Q "%GAME_DIR%\HoodiePatcher.ini" >nul 2>&1
del /Q "%GAME_DIR%\blue sentinel.dll" >nul 2>&1
del /Q "%GAME_DIR%\blue sentinel.ini" >nul 2>&1
goto :EOF