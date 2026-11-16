@echo off
title German B1 Daily Duel - Server & Real-Time Sharing
echo ===================================================================
echo             GERMAN B1 DAILY DUEL - REAL-TIME SERVER
echo ===================================================================
echo.
echo [!] This PC acts as the server. Keep this window open while playing.
echo.
echo [1] On this PC:           http://localhost:8501
echo [2] On same Wi-Fi:        http://192.168.158.14:8501
echo [3] On Tailscale:         http://100.101.253.123:8501
echo.
echo Starting Streamlit and Cloudflare Tunnel for Internet Sharing...
echo (Copy the https://...trycloudflare.com link below and send to friends!)
echo ===================================================================
echo.

start "Streamlit Server (German App)" cmd /c "python -m streamlit run app.py --server.address=0.0.0.0 --server.port=8501"

timeout /t 3 /nobreak >nul
cloudflared tunnel --url http://localhost:8501
pause
