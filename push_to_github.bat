@echo off
chcp 65001 >nul
echo ========================================
echo  Push code to GitHub and build APK
echo ========================================
echo.

cd /d "%~dp0"

echo Pushing to GitHub (force)...
git push --force -u origin main

echo.
if %errorlevel% equ 0 (
    echo SUCCESS!
    echo.
    echo GitHub Actions will build APK automatically
    echo Check build progress:
    echo   https://github.com/zsy990809/powerliftingapp-v1/actions
    echo.
    echo Download "lwup-apk" artifact when build completes
) else (
    echo FAILED. Check network and GitHub credentials.
    echo Make sure you are on a network that can reach GitHub.
)

pause
