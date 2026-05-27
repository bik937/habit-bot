@echo off
cd /d "G:\Projects\habit-bot"
:loop
python bot.py >> bot_output.log 2>&1
echo [%date% %time%] Bot crashed, restarting in 10 seconds... >> bot_output.log
timeout /t 10 /nobreak > nul
goto loop
