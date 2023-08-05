@echo off

if not "%1"=="Administrator" (
  powershell -Command "Start-Process cmd.exe -ArgumentList '/k cd /d %~dp0 & call "\"Activate Environment.bat"\" Administrator' -Verb RunAs"
  exit
)

cls
title "Activate Environment"

if not "%2"=="Launcher" (
  if not exist ".\Miniconda" (
    powershell -Command "Start-Process cmd.exe -ArgumentList '/k cd /d %~dp0 & call "\"Full Install & Reinstall.bat"\" Administrator Launcher' -Verb RunAs"
    exit
  )
)

CALL .\Miniconda\Scripts\activate.bat .\Miniconda\envs

cd "Project Infinite"