from pathlib import Path
import shutil


DOWNLOADS_DIR = Path(r"C:\Users\student\Downloads")

GROUPS = {
    "images": {".jpg", ".jpeg", ".png"},
    "data": {".csv", ".xlsx"},
    "docs": {".txt", ".doc", ".pdf"},
    "archive": {".zip", ".exe"},
}


def unique_destination(target_dir: Path, source_name: str) -> Path:
    destination = target_dir / source_name
    if not destination.exists():
        return destination

    stem = Path(source_name).stem
    suffix = Path(source_name).suffix
    counter = 1
    while True:
        candidate = target_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def organize_downloads() -> None:
    if not DOWNLOADS_DIR.exists():
        raise FileNotFoundError(f"다운로드 폴더를 찾을 수 없습니다: {DOWNLOADS_DIR}")

    for folder_name in GROUPS:
        (DOWNLOADS_DIR / folder_name).mkdir(exist_ok=True)

    for item in DOWNLOADS_DIR.iterdir():
        if item.is_dir():
            continue

        extension = item.suffix.lower()
        target_folder = next(
            (folder_name for folder_name, extensions in GROUPS.items() if extension in extensions),
            None,
        )

        if target_folder is None:
            continue

        destination_dir = DOWNLOADS_DIR / target_folder
        destination = unique_destination(destination_dir, item.name)
        shutil.move(str(item), str(destination))
        print(f"{item.name} -> {destination}")


if __name__ == "__main__":
    organize_downloads()