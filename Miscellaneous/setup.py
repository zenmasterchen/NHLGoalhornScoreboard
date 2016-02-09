from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "NHLghsb.py",
            "icon_resources": [(1, "Assets/icon.ico")],           
            "name": "NHL Goal Horn Scoreboard",
            "version": "2.0.0",
            "description": "Plays goal horns when NHL teams score.",
            "author": "Austin Chen",
            "company_name": "austin and emily",
            "copyright": "(c) Austin Chen 2016"
        }
    ],
    zipfile = "Python Resources/NHLghsb.zip",
    options = {
        "py2exe": {
            "skip_archive": True,
            "optimize": 1,
            "bundle_files": 3,
            "dll_excludes": ["w9xpopen.exe"]
            }
    }
)
