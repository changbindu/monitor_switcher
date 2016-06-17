#pip install pyinstaller

pyinstaller --clean --strip --onefile --windowed --icon=app.ico monitor_switcher.pyw
cp -r images app.ico dist/
