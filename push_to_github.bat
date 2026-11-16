@echo off
echo ========================================================
echo     German B1 App - Push to GitHub Helper
echo ========================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/USERNAME/german-b1.git): "
if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty.
    pause
    exit /b
)

echo.
echo Adding remote origin and renaming branch to main...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Staging and committing any recent changes...
git add .
git commit -m "Update German B1 App" 2>nul

echo.
echo Pushing to GitHub (main branch)...
git push -u origin main

echo.
echo ========================================================
echo Done! Your code is now on GitHub!
echo Next: Deploy for free on https://share.streamlit.io
echo ========================================================
pause
