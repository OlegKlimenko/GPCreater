import sys
from cx_Freeze import setup, Executable
import os

build_exe_options = {"packages": ["sys", "os", "random"],
                     "include_msvcr": True}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup( name = "GPcreater",
       version = "1.00",
       description = "App for creating Graphs",
       options = {"build_exe": build_exe_options},
       author = "Oleg Klimenko",
       executables = [Executable(script = "GPcreater.py",
                                 base = base,
                                 icon = "GPcreater.ICO")])
