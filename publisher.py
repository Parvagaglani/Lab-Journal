import json
import shutil
from pathlib import Path

TRACKER_FILE = Path("tracker.json")
README_FILE = Path("README.md")

STORAGE_REPO = Path("college-experiments-storage")
EXPERIMENTS_DIR = Path("experiments")

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx"
}


def load_tracker():
    if not TRACKER_FILE.exists():
        return {"current_index": 0}

    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tracker(data):
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_all_files():
    files = []

    for file in STORAGE_REPO.rglob("*"):
        if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file)

    files.sort(key=lambda x: str(x).lower())

    return files


def publish_next_file():
    tracker = load_tracker()

    current_index = tracker.get("current_index", 0)

    files = get_all_files()

    if current_index >= len(files):
        print("No more experiments to publish.")
        generate_readme()
        return

    source_file = files[current_index]

    relative_path = source_file.relative_to(STORAGE_REPO)

    destination_file = EXPERIMENTS_DIR / relative_path

    destination_file.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_file, destination_file)

    tracker["current_index"] = current_index + 1

    save_tracker(tracker)

    print(f"Published: {relative_path}")

    generate_readme()


def generate_readme():
    lines = []

    lines.append("# Lab Journal 2026\n")
    lines.append("Automatically published college experiments.\n")

    total_files = 0

    if EXPERIMENTS_DIR.exists():

        subject_folders = sorted(
            [folder for folder in EXPERIMENTS_DIR.iterdir() if folder.is_dir()],
            key=lambda x: x.name.lower()
        )

        for subject in subject_folders:

            lines.append(f"\n## {subject.name}\n")

            subject_files = []

            for file in subject.rglob("*"):
                if file.is_file():
                    subject_files.append(file)

            subject_files.sort(key=lambda x: str(x).lower())

            for file in subject_files:

                relative_file = file.relative_to(Path("."))

                lines.append(
                    f"- [{file.name}]({relative_file.as_posix()})"
                )

                total_files += 1

    lines.append(f"\n\n---\n")
    lines.append(f"Total Experiments Published: {total_files}\n")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    publish_next_file()
