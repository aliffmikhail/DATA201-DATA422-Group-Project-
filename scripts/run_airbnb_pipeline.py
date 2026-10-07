from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    "Deliverable3_DataPrep.py",
    "Deliverable3_Concatenate.py",
    "Deliverable4_DataCleaning.py",
    "area_code.py",
    "Deliverable3_SummaryStats.py",
    "Deliverable3_Visualisations.py",
]


def run_stage(script):
    path = ROOT / "scripts" / script

    print(f"\n{'=' * 60}")
    print(f"Running {script}")
    print("=" * 60)

    subprocess.run(
        [sys.executable, str(path)],
        check=True,
        cwd=ROOT,
    )


def main():
    for script in STAGES:
        run_stage(script)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()