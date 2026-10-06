# Desktop (PyInstaller) — General Development System (GDS)

ملف تشغيل مكتبي مستقل (Windows) بدون الحاجة لـ PostgreSQL — البيانات تُحفظ محليًا
في ملف `db.sqlite3` بجوار التطبيق.

## Files

| File | Purpose |
|------|---------|
| `desktop_launcher.py` | Entry point. Starts a local Waitress server, opens the browser, adds a system tray icon, and auto-creates the `admin`/`admin123` user on first run. Uses `config.settings.desktop`. |
| `build.py` | One-click PyInstaller build tool. Run: `python desktop/build.py` (add `--clean` to purge artifacts first). |
| `GDS.spec` | PyInstaller spec for a manual build. Run from project root: `pyinstaller desktop/GDS.spec`. |

## Build

```powershell
python desktop/build.py --clean
```

Produces `dist\GDS Management\` containing `GDS Management.exe`.
Copy that folder to any Windows PC and run the exe.

## Requirements

```powershell
pip install -r requirements-desktop.txt
```

## Notes

- Data is stored in `db.sqlite3` next to the executable (`db.sqlite3` in the
  project root when running from source).
- The build tool only adds an icon if `build\icon.ico` exists; otherwise it is
  skipped.
- Ports 8000–8019 are probed; the first free port is used.
