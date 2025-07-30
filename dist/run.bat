@echo off
echo Starting Help Desk... please wait a moment for the browser to open.

REM Start the application in the background
start "" "run.exe"

REM Give the server a few seconds to start up before opening the browser
timeout /t 5 /nobreak > nul

REM Open the web browser to the correct page
start http://127.0.0.1:5001

exit