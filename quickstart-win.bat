cd /d %USERPROFILE%

if not exist venv (
    pip install virtualenv
    python -m venv venv
)

call ./venv/Scripts/Activate.bat
pip install -U xpuz
xpuz-ctk

pause
