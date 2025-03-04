@echo off
echo Setting up Azure Cost Optimizer...

:: Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.8 or higher.
    exit /b 1
)

:: Check if pip is installed
pip --version > nul 2>&1
if errorlevel 1 (
    echo pip is not installed! Please install pip.
    exit /b 1
)

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

:: Upgrade pip and install wheel
echo Upgrading pip and installing wheel...
python -m pip install --upgrade pip
pip install wheel

:: Install dependencies
echo Installing dependencies...
pip install -e .

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo Please edit the .env file with your Azure credentials.
)

echo Setup complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your Azure credentials
echo 2. Run 'python main.py' to start the application
echo.
pause
