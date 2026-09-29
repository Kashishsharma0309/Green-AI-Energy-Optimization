@echo off
title NEXUS - Green AI Energy Platform
echo ========================================================
echo   Starting NEXUS Smart Energy Optimization Platform
echo ========================================================
echo.
echo Launching Server on http://localhost:5000 ...
echo Opening your web browser...

start "" http://localhost:5000

python server.py

pause
