# TidyDesk ✨

## Overview
TidyDesk is a premium, zero-config workspace organizer for Windows. It provides a non-technical, safe way to declutter your Desktop, Downloads, or any other folder with a single click.

## Features
- **Zero Thinking:** No paths to type. No settings to configure.
- **Card-Based UI:** Select your folder using large, intuitive cards.
- **Preview First:** See exactly how many files will be moved before you hit "Clean".
- **Absolute Safety:** 
  - Never deletes files.
  - Skips folders and app shortcuts.
  - Skips hidden system files.
- **Restore:** Made a mistake? Use the "Restore last clean" button to put everything back instantly.

## How to Run
1. Open the latest release.
2. Double-click **`TidyDesk.exe`**.
3. Follow the simple on-screen cards.

## Destination
All files are moved into a new folder named **`TidyDesk`** created *inside* the folder you chose to clean.

---

### Technical Note (for developers)
Built with Python 3.13 and CustomTkinter. 
To rebuild:
```bash
python -m PyInstaller --onefile --noconsole --name "TidyDesk" tidydesk.py
```
