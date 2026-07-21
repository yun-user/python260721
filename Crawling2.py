#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automobile model file downloader.

- Search DB_SYS by date range and model name.
- Expected folder layout: DB_ROOT / <YYYY> / <MM> / *.sri, *.pcm
- Match DATE and GP-Ⅲ / GP-III / GP-3 inside each .sri file.
- Copy matched files with this name:
  {model}_{YYYYMMDD}_{factory}_{machine_count}.sri
  {model}_{YYYYMMDD}_{factory}_{machine_count}.pcm

Save this file as UTF-8.
"""

import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple


SAVE_PATH = "/data/user/y66sj/signal"
DEFAULT_DB_ROOT = "/DB_SYS"

# 회사 폴더 구조가 /DB_SYS/2023/03 처럼 월 폴더가 숫자만 있으므로 빈 문자열 사용
MONTH_SUFFIX = ""

# .sri 안에서 공장명/기계개수 키워드가 실제로 다르면 여기만 바꾸면 됩니다.
# 예: 공장명이 PlantName으로 적혀 있으면 FACTORY_KEYS에 "PlantName" 추가
FACTORY_KEYS = ["Contain", "Factory", "Plant", "FactoryName"]
MACHINE_COUNT_KEYS = ["number", "MachineCount", "MachineNumber", "Count"]


DATE_REGEX = re.compile(r"\b(\d{4})[-/\.]?(\d{2})[-/\.]?(\d{2})\b")
GP3_REGEX = re.compile(
    r"GP\s*[-_]\s*(?:III|3)\s*[:=]?\s*([A-Za-z0-9._-]+)",
    re.IGNORECASE,
)


@dataclass
class SriInfo:
    file_date: Optional[date]
    model: Optional[str]
    factory: Optional[str]
    machine_count: Optional[str]


def get_date_input(prompt: str) -> date:
    """Read YYYYMMDD input and return a date object."""
    while True:
        raw = input(prompt).strip()
        try:
            return datetime.strptime(raw, "%Y%m%d").date()
        except ValueError:
            print("  ※ 날짜 형식이 올바르지 않습니다. YYYYMMDD 형식으로 입력해주세요.\n")


def get_path_input(prompt: str, default: Optional[str] = None) -> str:
    """Read a path. Use default when input is empty. Expand ~."""
    raw = input(prompt).strip()
    if not raw and default is not None:
        raw = default
    return os.path.abspath(os.path.expanduser(raw))


def get_inputs():
    print("\n" + "=" * 50)
    print("  자동차 모델 파일 다운로더")
    print("=" * 50 + "\n")

    start_date = get_date_input("1. 시작 날짜는 (YYYYMMDD)? : ")
    end_date = get_date_input("2. 끝 날짜는   (YYYYMMDD)? : ")

    if start_date > end_date:
        print("  ※ 시작 날짜가 끝 날짜보다 늦습니다. 프로그램을 다시 실행해주세요.")
        raise SystemExit(1)

    model_name = input("3. 자동차 모델명은? : ").strip()
    if not model_name:
        print("  ※ 모델명이 비어있습니다. 프로그램을 다시 실행해주세요.")
        raise SystemExit(1)

    db_root = get_path_input(
        "DB_ROOT 경로는? (기본: /DB_SYS) : ",
        default=DEFAULT_DB_ROOT,
    )

    return start_date, end_date, model_name, SAVE_PATH, db_root


def read_text_best_effort(path: str) -> Optional[str]:
    """Read text using common Korean/UTF encodings. Return None on failure."""
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except OSError:
            return None

    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def parse_date_match(match: re.Match) -> Optional[date]:
    """Convert a DATE_REGEX match to date."""
    y, mo, d = match.group(1), match.group(2), match.group(3)
    try:
        return datetime.strptime(f"{y}{mo}{d}", "%Y%m%d").date()
    except ValueError:
        return None


def find_value_by_keys(text: str, keys: List[str]) -> Optional[str]:
    """
    Find value written like 'Key: value' or 'Key = value' in .sri text.

    Example:
        Contain: 18t -> 18t
        number: 40000 -> 40000
    """
    normalized_keys = [unicodedata.normalize("NFKC", key).casefold() for key in keys]

    for line in text.splitlines():
        if ":" in line:
            key_part, value_part = line.split(":", 1)
        elif "=" in line:
            key_part, value_part = line.split("=", 1)
        else:
            continue

        key_part = unicodedata.normalize("NFKC", key_part).strip().casefold()
        if key_part in normalized_keys:
            value = value_part.strip()
            if value:
                return value

    return None


def parse_sri(sri_path: str) -> SriInfo:
    """Read DATE, model, factory, and machine count from a .sri file."""
    text = read_text_best_effort(sri_path)
    if text is None:
        return SriInfo(None, None, None, None)

    # GP-Ⅲ becomes GP-III after NFKC normalization.
    text = unicodedata.normalize("NFKC", text)

    file_date = None

    # Prefer dates on lines containing DATE.
    for line in text.splitlines():
        line_s = line.strip()
        if "DATE" in line_s.upper():
            match = DATE_REGEX.search(line_s)
            if match:
                file_date = parse_date_match(match)
                if file_date is not None:
                    break

    # Fallback: first date-looking value in the whole file.
    if file_date is None:
        match = DATE_REGEX.search(text)
        if match:
            file_date = parse_date_match(match)

    model_val = None
    for line in text.splitlines():
        match = GP3_REGEX.search(line)
        if match:
            model_val = match.group(1).strip()
            break

    factory = find_value_by_keys(text, FACTORY_KEYS)
    machine_count = find_value_by_keys(text, MACHINE_COUNT_KEYS)

    return SriInfo(file_date, model_val, factory, machine_count)


def sri_matches(info: SriInfo, start: date, end: date, model: str) -> bool:
    """Return True when .sri date and model match the requested condition."""
    if info.file_date is None or info.model is None:
        return False

    date_ok = start <= info.file_date <= end
    model_ok = info.model.strip().upper() == model.strip().upper()
    return date_ok and model_ok


def year_month_folders(start: date, end: date) -> List[Tuple[int, str]]:
    """Return included (year, month) pairs, e.g. [(2023, '01'), ...]."""
    result = []
    y, m = start.year, start.month

    while (y, m) <= (end.year, end.month):
        result.append((y, f"{m:02d}"))
        m += 1
        if m > 12:
            m = 1
            y += 1

    return result


def find_file_case_insensitive(directory: str, target_name: str) -> Optional[str]:
    """Find a file in directory while ignoring filename case."""
    target_lower = target_name.lower()

    try:
        for fname in os.listdir(directory):
            if fname.lower() == target_lower:
                full_path = os.path.join(directory, fname)
                if os.path.isfile(full_path):
                    return full_path
    except OSError:
        return None

    return None


def find_pcm_for_sri(month_dir: str, sri_name: str) -> Optional[str]:
    """Find same-basename .pcm file while ignoring extension case."""
    base = os.path.splitext(sri_name)[0]
    return find_file_case_insensitive(month_dir, base + ".pcm")


def find_matching_files(start: date, end: date, model: str, db_root: str):
    """
    Return matching file items.

    Returns:
        [(pcm_path_or_none, sri_path, sri_info), ...]
    """
    matched = []

    for year, month in year_month_folders(start, end):
        month_dir = os.path.join(db_root, str(year), f"{month}{MONTH_SUFFIX}")

        if not os.path.isdir(month_dir):
            continue

        try:
            file_names = os.listdir(month_dir)
        except OSError as exc:
            print(f"  [WARN] Cannot read folder: {month_dir} ({exc})")
            continue

        for fname in file_names:
            if not fname.lower().endswith(".sri"):
                continue

            sri_path = os.path.join(month_dir, fname)
            if not os.path.isfile(sri_path):
                continue

            info = parse_sri(sri_path)
            if not sri_matches(info, start, end, model):
                continue

            pcm_path = find_pcm_for_sri(month_dir, fname)
            matched.append((pcm_path, sri_path, info))

    return matched


def sanitize_filename_part(value: Optional[str], fallback: str) -> str:
    """Make a value safe to use as one part of a filename."""
    if value is None or not value.strip():
        value = fallback

    value = value.strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = value.strip("._ ")

    return value or fallback


def make_output_base_name(info: SriInfo) -> str:
    """Build '{model}_{YYYYMMDD}_{factory}_{machine_count}'."""
    model = sanitize_filename_part(info.model, "UNKNOWN_MODEL")
    date_text = info.file_date.strftime("%Y%m%d") if info.file_date else "UNKNOWN_DATE"
    factory = sanitize_filename_part(info.factory, "UNKNOWN_FACTORY")
    machine_count = sanitize_filename_part(info.machine_count, "UNKNOWN_NUMBER")

    return f"{model}_{date_text}_{factory}_{machine_count}"


def make_unique_path(dest_path: str) -> str:
    """Avoid overwrite by appending _1, _2, ... when needed."""
    if not os.path.exists(dest_path):
        return dest_path

    directory = os.path.dirname(dest_path)
    filename = os.path.basename(dest_path)
    stem, ext = os.path.splitext(filename)

    index = 1
    while True:
        candidate = os.path.join(directory, f"{stem}_{index}{ext}")
        if not os.path.exists(candidate):
            return candidate
        index += 1


def copy_with_new_name(src: str, save_path: str, output_base_name: str) -> str:
    """Copy src into save_path using output_base_name and src extension."""
    _, ext = os.path.splitext(src)
    dest_name = output_base_name + ext.lower()
    dest_path = os.path.join(save_path, dest_name)
    dest_path = make_unique_path(dest_path)
    shutil.copy2(src, dest_path)
    return dest_path


def download_files(file_items: list, save_path: str) -> None:
    """Copy matched .sri and .pcm files into save_path."""
    os.makedirs(save_path, exist_ok=True)

    total = len(file_items)
    success = 0
    failed = 0

    print(f"\n  총 {total}개의 매칭을 발견했습니다.")
    print(f"  저장 경로: {save_path}\n")

    for idx, (pcm_path, sri_path, info) in enumerate(file_items, 1):
        try:
            output_base_name = make_output_base_name(info)

            sri_dest = copy_with_new_name(sri_path, save_path, output_base_name)
            print(f"  [{idx}/{total}] SRI 복사: {os.path.basename(sri_dest)}")

            if pcm_path:
                pcm_dest = copy_with_new_name(pcm_path, save_path, output_base_name)
                print(f"  [{idx}/{total}] PCM 복사: {os.path.basename(pcm_dest)}")
            else:
                print(f"  [{idx}/{total}] PCM 없음: SRI만 복사")

            if info.factory is None or info.machine_count is None:
                print("      [WARN] 공장명 또는 기계개수를 찾지 못해 UNKNOWN 값으로 저장했습니다.")

            success += 1
        except Exception as exc:
            print(f"  [{idx}/{total}] 복사 실패: {exc}")
            failed += 1

    print("\n" + "-" * 50)
    print(f"  완료: 성공 {success} / 실패 {failed}")
    print("-" * 50 + "\n")


def main() -> None:
    start_date, end_date, model_name, save_path, db_root = get_inputs()

    print("\n  검색 조건")
    print(f"    - 기간      : {start_date} ~ {end_date}")
    print(f"    - 모델명    : {model_name}")
    print(f"    - 저장 경로 : {save_path}")
    print(f"    - DB 루트   : {db_root}\n")

    print("  파일을 검색 중입니다...\n")
    file_items = find_matching_files(start_date, end_date, model_name, db_root)

    if not file_items:
        print("  ※ 조건에 맞는 파일을 찾지 못했습니다.")
        print("    - 날짜/모델명/DB_ROOT/월폴더명(01~12)을 확인해주세요.\n")
        return

    download_files(file_items, save_path)


if __name__ == "__main__":
    main()
