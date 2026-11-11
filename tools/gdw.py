from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parents[1] / 'skills/gamedev-workbench/scripts/workbench.py'), run_name='__main__')
