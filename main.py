"""
main.py — ShizuMusic launcher.
Run with: python main.py
All logic lives inside the ShizuMusic package.
"""
import runpy

runpy.run_module("ShizuMusic", run_name="__main__", alter_sys=True)
