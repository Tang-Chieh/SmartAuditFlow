"""Apply the approved detector timeout without changing pinned source snapshots."""
from pathlib import Path
import runpy
import sys

APP = Path(__file__).resolve().parent / "sources/saf/smart-contract-audit"


def main():
    sys.path.insert(0, str(APP))
    from src.workflow.models import ModelManager

    original = ModelManager.call_model_sync

    def call_with_timeout(self, prompt, preferred_model=None, timeout=180):
        return original(self, prompt, preferred_model=preferred_model, timeout=180)

    ModelManager.call_model_sync = call_with_timeout
    print("RUNTIME OVERRIDE: detector model-call timeout = 180 seconds", flush=True)
    runpy.run_path(str(APP / "scripts/run_dataset_smoke.py"), run_name="__main__")


if __name__ == "__main__":
    main()
