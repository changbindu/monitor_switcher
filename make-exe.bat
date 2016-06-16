#pip install pyinstaller

pyinstaller --clean --strip --onefile --windowed --icon=app.ico monitor_switcher.py
cp -r images dist/