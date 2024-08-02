pip install -r requirement.txt

pyinstaller --onefile --noconsole --add-data "src;src" --icon=icon.ico main.py # Windows