from distutils.core import setup
import py2exe

setup(
    windows = [
        {
            "script": "NHLghsb.py",
            "dest_base": "NHL Goal Horn Scoreboard",
            #"uac_info": "requireAdministrator",
            "icon_resources": [(1, "Assets/icon.ico")],           
            "name": "NHL Goal Horn Scoreboard",
            "version": "4.10.20",
            #"description": "Plays goal horns when NHL teams score.",
            "description": "NHL Goal Horn Scoreboard",
            "author": "Austin Chen",
            "company_name": "austin and emily",
            "copyright": "Copyright (C) 2018 Austin Chen"
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
