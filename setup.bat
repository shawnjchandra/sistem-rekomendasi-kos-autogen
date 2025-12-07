@echo off
echo ==========================================
echo  SEDANG MENYIAPKAN ENVIRONMENT UNTUK TUGAS BESAR
echo ==========================================

:: 1. Cek apakah venv sudah ada
if exist "autogen_env" (
    echo [INFO] Environment 'autogen_env' sudah ada. Melewati pembuatan ulang.
) else (
    echo [INFO] Membuat virtual environment baru...
    python -m venv autogen_env
)

:: 2. Aktivasi Environment
echo [INFO] Mengaktifkan environment...
call autogen_env\Scripts\activate

:: 3. Install Requirements
echo [INFO] Menginstall library dari requirements.txt...
pip install -r requirements.txt

echo ==========================================
echo  INSTALASI SELESAI!
echo  Silakan jalankan program dengan perintah:
echo  .\autogen_env\Scripts\python main.py
echo ==========================================
pause