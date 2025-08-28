from pathlib import Path
import sys

def resource_path(relative: str) -> Path:
    """
    Return an absolute path to a resource that works both:
      - in dev (running from source)
      - in a PyInstaller onedir/onefile build
    `relative` should be a POSIX-like path from the package root.
    """
    if getattr(sys, "frozen", False):
        # PyInstaller: onefile uses sys._MEIPASS, onedir puts files next to the exe.
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    else:
        # …/research_analytics_suite/utils/resources.py  -> go up to package root
        base = Path(__file__).resolve().parents[1]
    return (base / relative).resolve()
