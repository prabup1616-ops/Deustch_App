@echo off
title German B1 Daily Duel
cd /d "%~dp0\.."
echo ========================================================
echo        Starting German B1 Daily Duel (Server Mode)
echo ========================================================
echo Access on this PC:    http://localhost:8501
echo Access on same Wi-Fi: http://192.168.158.14:8501
echo ========================================================
python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501
pause
