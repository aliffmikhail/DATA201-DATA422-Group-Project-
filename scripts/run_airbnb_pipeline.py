from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]

STAGES = [
    ("Preparing monthly Airbnb data", "Deliverable3_DataPrep.py"),
    ("Combining Christchurch monthly data", "Deliverable3_Concatenate.py"),
    ("Cleaning combined Airbnb data", "Deliverable4_DataCleaning.py"),
    ("Updating Stats NZ area codes", "area_code.py"),
    ("Running Airbnb vs rental bond analysis", "Deliverable5_areaoperations.py"),
    ("Generating summary statistics", "Deliverable3_SummaryStats.py"),
    ("Generating visualisations", "Deliverable3_Visualisations.py"),
]


def run_stage(label, script):
    path = ROOT / "scripts" / script

    print(f"\n{'=' * 60}")
    print(label)
    print("=" * 60)

    subprocess.run(
        [sys.executable, str(path)],
        check=True,
        cwd=ROOT,
    )


def main():
    for label, script in STAGES:
        run_stage(label, script)

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()