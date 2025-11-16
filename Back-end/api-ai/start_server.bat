@echo off
echo ========================================
echo Starting AI API Server with TTS Support
echo ========================================
echo.
python app.py
pause

cd ..
python api.py