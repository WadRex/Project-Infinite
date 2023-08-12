@echo off

if not "%1"=="Administrator" (
  powershell -Command "Start-Process cmd.exe -ArgumentList '/k cd /d %~dp0 & call "\"Full Install & Reinstall.bat"\" Administrator' -Verb RunAs"
  exit
)

cls
title "Full Install & Reinstall - Warning"
mode con:cols=71 lines=12
color 4
echo  =====================================================================
echo                                [WARNING]
echo.
echo    This operation will remove ALL files and folders in the current 
echo    directory where this script is located. 
echo.
echo    PLEASE ENSURE this script is not placed in a directory containing
echo    important files and folders as they will be PERMANENTLY DELETED.
echo.
echo  =====================================================================
echo.

set /p "choice=To continue type in the phrase: 'Yes, do as I say!': "
if /i not "%choice%"=="Yes, do as I say!" goto terminate

cls
title "Full Install & Reinstall - In Progress"
mode con:cols=120 lines=30
color 7
echo Starting Installation / Reinstallation

for %%F in ("%~dp0*.*") do (
    if not "%%~nxF"=="README.md" if not "%%~nxF"=="Full Install & Reinstall.bat" if not "%%~nxF"=="Activate Environment.bat" del "%%F"
)
for /d %%D in ("%~dp0*") do (
    if /i not "%%~nxD"==".git" if /i not "%%~nxD"=="Project Infinite" rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\*.*") do (
    if not "%%~nxF"=="file_to_keep.txt" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\*") do (
    if /i not "%%~nxD"=="1. Prepare Dataset" if /i not "%%~nxD"=="2. Train Model" rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\1. Prepare Dataset\*.*") do (
    if not "%%~nxF"=="1. Extract & Decompile (.rpa & .rpyc) Files.py" if not "%%~nxF"=="2. Extract Text from (.rpy) Files.py" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\1. Prepare Dataset\*") do (
    if /i not "%%~nxD"=="Files (.rpa & .rpyc)" if /i not "%%~nxD"=="Files (.rpy)" if /i not "%%~nxD"=="Files (.txt)" rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.rpa & .rpyc)\*.*") do (
    if not "%%~nxF"==".gitkeep" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.rpa & .rpyc)\*") do (
    rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.rpy)\*.*") do (
    if not "%%~nxF"==".gitkeep" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.rpy)\*") do (
    rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.txt)\*.*") do (
    if not "%%~nxF"==".gitkeep" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\1. Prepare Dataset\Files (.txt)\*") do (
    rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\2. Train Model\*.*") do (
    if not "%%~nxF"=="1. Download Model.py" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\2. Train Model\*") do (
    if /i not "%%~nxD"=="Model" rd /s /q "%%D"
)

for %%F in ("%~dp0Project Infinite\2. Train Model\Model\*.*") do (
    if not "%%~nxF"==".gitkeep" del "%%F"
)
for /d %%D in ("%~dp0Project Infinite\2. Train Model\Model\*") do (
    rd /s /q "%%D"
)

mkdir "Temporary Files"
bitsadmin /transfer "Download Microsoft Visual C++ Redistributable" /download /priority normal "https://aka.ms/vs/17/release/vc_redist.x64.exe" "%~dp0\Temporary Files\vc_redist.x64.exe"
start /wait "" ".\Temporary Files\vc_redist.x64.exe" /install /quiet /norestart
rd /s /q ".\Temporary Files"

mkdir "Temporary Files"
bitsadmin /transfer "Download Miniconda" /download /priority normal "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" "%~dp0\Temporary Files\Miniconda3-latest-Windows-x86_64.exe"
start /wait "" ".\Temporary Files\Miniconda3-latest-Windows-x86_64.exe" /InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /S /D=%cd%\Miniconda
rd /s /q ".\Temporary Files"

echo y | .\Miniconda\Scripts\conda.exe create --prefix .\Miniconda\envs python=3.10
CALL .\Miniconda\Scripts\activate.bat .\Miniconda\envs

echo y | .\Miniconda\Scripts\conda.exe install cudatoolkit==11.8.0 -c conda-forge

echo y | python -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --extra-index-url https://download.pytorch.org/whl/cu118
echo y | python -m pip install transformers==4.31.0 sentencepiece==0.1.99 protobuf==4.24.0
echo y | python -m pip install bitsandbytes==0.41.1 --prefer-binary --extra-index-url https://jllllll.github.io/bitsandbytes-windows-webui
echo y | python -m pip install unrpa==2.3.0

mkdir "Temporary Files"
bitsadmin /transfer "Download unrpyc Pre-Built Wheel" /download /priority normal "https://github.com/WadRex/Project-Infinite/releases/download/unrpyc-0.1-py3-none-any.whl/unrpyc-0.1-py3-none-any.whl" "%~dp0\Temporary Files\unrpyc-0.1-py3-none-any.whl"
echo y | pip install ".\Temporary Files\unrpyc-0.1-py3-none-any.whl"
rd /s /q ".\Temporary Files"

CALL conda.bat deactivate

cls
title "Full Install & Reinstall - Completed"
mode con:cols=71 lines=9
color 2
echo  =====================================================================
echo                               [COMPLETED]
echo.
echo               The installation has successfully completed.
echo.
echo          This window will close automatically after 10 seconds.
echo.
echo  =====================================================================
timeout /t 10 /nobreak > nul
if "%2"=="Launcher" (
  powershell -Command "Start-Process cmd.exe -ArgumentList '/k cd /d %~dp0 & call "\"Activate Environment.bat"\" Administrator Launcher' -Verb RunAs"
)
exit

:terminate
cls
title "Full Install & Reinstall - Terminated"
mode con:cols=71 lines=11
color 6
echo  =====================================================================
echo                              [TERMINATED]
echo.
echo            You have chosen not to proceed with the operation.
echo.
echo                Your files and folders were NOT affected.
echo.
echo          This window will close automatically after 10 seconds.
echo.
echo  =====================================================================
timeout /t 10 /nobreak > nul
exit