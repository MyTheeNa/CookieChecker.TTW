@echo off
title Roblox Cookie Checker TTW.CODE
echo Installing requirements...
pip install -r requirements.txt >nul 2>&1
cls
echo Starting Roblox Cookie Checker...
start /b pythonw main.py
exit
