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
"""

import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Tuple, Union


SAVE_PATH = "/data/user/y66sj/signal"
DEFAULT_DB_ROOT = "/DB_SYS"

# 월 폴더가 /DB_SYS/2023/03처럼 숫자로 되어 있음
MONTH_SUFFIX = ""

# 실제 .sri 키워드가 다르면 여기에 추가하거나 변경
FACTORY_KEYS = ["Contain", "Factory", "Plant", "FactoryName"]
MACHINE_COUNT_KEYS = ["number", "MachineCount", "MachineNumber", "Count"]


DATE_REGEX = re.compile(
    r"\b(\d{4})[-/\.]?(\d{2})[-/\.]?(\d{2})\b"
)

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
    """YYYYMMDD 형식의 날짜를 입력받음."""
    while True:
        raw = input(prompt).strip()

        try:
            return datetime.strptime(raw, "%Y%m%d").date()
        except ValueError:
            print(
                "  ※ 날짜 형식이 올바르지 않습니다. "
                "YYYYMMDD 형식으로 입력해주세요.\n"
            )


def get_path_input(
    prompt: str,
    default: Optional[str] = None,
) -> str:
    """경로를 입력받고 빈 값이면 기본 경로를 사용함."""
    raw = input(prompt).strip()

    if not raw and default is not None:
        raw = default

    return os.path.abspath(os.path.expanduser(raw))


def get_inputs():
    """프로그램 실행에 필요한 조건을 입력받음."""
    print("\n" + "=" * 50)
    print("  자동차 모델 파일 다운로더")
    print("=" * 50 + "\n")

    start_date = get_date_input(
        "1. 시작 날짜는 (YYYYMMDD)? : "
    )
    end_date = get_date_input(
        "2. 끝 날짜는   (YYYYMMDD)? : "
    )

    if start_date > end_date:
        print(
            "  ※ 시작 날짜가 끝 날짜보다 늦습니다. "
            "프로그램을 다시 실행해주세요."
        )
        raise SystemExit(1)

    model_name = input(
        "3. 자동차 모델명은? : "
    ).strip()

    if not model_name:
        print(
            "  ※ 모델명이 비어있습니다. "
            "프로그램을 다시 실행해주세요."
        )
        raise SystemExit(1)

    db_root = get_path_input(
        "DB_ROOT 경로는? (기본: /DB_SYS) : ",
        default=DEFAULT_DB_ROOT,
    )

    return (
        start_date,
        end_date,
        model_name,
        SAVE_PATH,
        db_root,
    )


def read_text_best_effort(path: str) -> Optional[str]:
    """여러 인코딩을 사용하여 .sri 파일을 읽음."""
    encodings = (
        "utf-8-sig",
        "utf-8",
        "cp949",
        "euc-kr",
    )

    for encoding in encodings:
        try:
            with open(
                path,
                "r",
                encoding=encoding,
            ) as file:
                return file.read()

        except UnicodeDecodeError:
            continue
        except OSError:
            return None

    try:
        with open(
            path,
            "r",
            encoding="utf-8",
            errors="replace",
        ) as file:
            return file.read()
    except OSError:
        return None


def parse_date_match(
    match: re.Match,
) -> Optional[date]:
    """정규표현식으로 찾은 날짜를 date 객체로 변환함."""
    year = match.group(1)
    month = match.group(2)
    day = match.group(3)

    try:
        return datetime.strptime(
            f"{year}{month}{day}",
            "%Y%m%d",
        ).date()
    except ValueError:
        return None


def find_value_by_keys(
    text: str,
    keys: List[str],
) -> Optional[str]:
    """
    '키: 값' 또는 '키 = 값' 형태의 값을 찾음.

    예:
        Contain: 18t
        number: 40000
    """
    normalized_keys = [
        unicodedata.normalize(
            "NFKC",
            key,
        ).casefold()
        for key in keys
    ]

    for line in text.splitlines():
        if ":" in line:
            key_part, value_part = line.split(":", 1)
        elif "=" in line:
            key_part, value_part = line.split("=", 1)
        else:
            continue

        key_part = unicodedata.normalize(
            "NFKC",
            key_part,
        ).strip().casefold()

        if key_part in normalized_keys:
            value = value_part.strip()

            if value:
                return value

    return None


def parse_sri(sri_path: str) -> SriInfo:
    """SRI 파일에서 날짜, 모델명, 공장명, 기계개수를 찾음."""
    text = read_text_best_effort(sri_path)

    if text is None:
        return SriInfo(
            None,
            None,
            None,
            None,
        )

    # GP-Ⅲ를 GP-III 형태로 정규화
    text = unicodedata.normalize("NFKC", text)

    file_date = None

    # DATE가 적힌 줄에서 날짜를 먼저 찾음
    for line in text.splitlines():
        line_s = line.strip()

        if "DATE" in line_s.upper():
            match = DATE_REGEX.search(line_s)

            if match:
                file_date = parse_date_match(match)

                if file_date is not None:
                    break

    # DATE 줄에서 못 찾으면 전체 내용에서 날짜를 찾음
    if file_date is None:
        match = DATE_REGEX.search(text)

        if match:
            file_date = parse_date_match(match)

    # 자동차 모델명 찾기
    model_val = None

    for line in text.splitlines():
        match = GP3_REGEX.search(line)

        if match:
            model_val = match.group(1).strip()
            break

    # 공장명과 기계개수 찾기
    factory = find_value_by_keys(
        text,
        FACTORY_KEYS,
    )
    machine_count = find_value_by_keys(
        text,
        MACHINE_COUNT_KEYS,
    )

    return SriInfo(
        file_date=file_date,
        model=model_val,
        factory=factory,
        machine_count=machine_count,
    )


def sri_matches(
    info_or_path: Union[SriInfo, str],
    start: date,
    end: date,
    model: str,
) -> bool:
    """
    날짜와 모델명이 검색 조건에 맞는지 확인함.

    SriInfo 객체와 .sri 파일 경로 문자열을 모두 받을 수 있음.
    """
    if isinstance(info_or_path, SriInfo):
        info = info_or_path

    elif isinstance(info_or_path, str):
        info = parse_sri(info_or_path)

    else:
        return False

    if info.file_date is None:
        return False

    if info.model is None:
        return False

    date_ok = start <= info.file_date <= end

    model_ok = (
        info.model.strip().upper()
        == model.strip().upper()
    )

    return date_ok and model_ok


def year_month_folders(
    start: date,
    end: date,
) -> List[Tuple[int, str]]:
    """검색 기간에 포함되는 연도와 월 목록을 만듦."""
    result = []

    year = start.year
    month = start.month

    while (year, month) <= (
        end.year,
        end.month,
    ):
        result.append(
            (year, f"{month:02d}")
        )

        month += 1

        if month > 12:
            month = 1
            year += 1

    return result


def find_file_case_insensitive(
    directory: str,
    target_name: str,
) -> Optional[str]:
    """대소문자를 구분하지 않고 파일을 찾음."""
    target_lower = target_name.lower()

    try:
        file_names = os.listdir(directory)
    except OSError:
        return None

    for file_name in file_names:
        if file_name.lower() != target_lower:
            continue

        full_path = os.path.join(
            directory,
            file_name,
        )

        if os.path.isfile(full_path):
            return full_path

    return None


def find_pcm_for_sri(
    month_dir: str,
    sri_name: str,
) -> Optional[str]:
    """SRI 파일과 같은 이름의 PCM 파일을 찾음."""
    base_name = os.path.splitext(sri_name)[0]

    return find_file_case_insensitive(
        month_dir,
        base_name + ".pcm",
    )


def find_matching_files(
    start: date,
    end: date,
    model: str,
    db_root: str,
):
    """검색 조건에 맞는 SRI와 PCM 파일 목록을 반환함."""
    matched = []

    for year, month in year_month_folders(
        start,
        end,
    ):
        month_dir = os.path.join(
            db_root,
            str(year),
            f"{month}{MONTH_SUFFIX}",
        )

        if not os.path.isdir(month_dir):
            continue

        try:
            file_names = os.listdir(month_dir)
        except OSError as error:
            print(
                f"  [경고] 폴더를 읽을 수 없습니다: "
                f"{month_dir} ({error})"
            )
            continue

        for file_name in file_names:
            if not file_name.lower().endswith(".sri"):
                continue

            sri_path = os.path.join(
                month_dir,
                file_name,
            )

            if not os.path.isfile(sri_path):
                continue

            info = parse_sri(sri_path)

            if not sri_matches(
                info,
                start,
                end,
                model,
            ):
                continue

            pcm_path = find_pcm_for_sri(
                month_dir,
                file_name,
            )

            matched.append(
                (
                    pcm_path,
                    sri_path,
                    info,
                )
            )

    return matched


def sanitize_filename_part(
    value: Optional[str],
    fallback: str,
) -> str:
    """파일명에 사용할 수 없는 문자를 안전하게 바꿈."""
    if value is None or not value.strip():
        value = fallback

    value = value.strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(
        r'[\\/:*?"<>|]+',
        "_",
        value,
    )
    value = value.strip("._ ")

    return value or fallback


def make_output_base_name(
    info: SriInfo,
) -> str:
    """
    새 파일명을 만듦.

    모델명_연월일_공장명_기계개수
    """
    model = sanitize_filename_part(
        info.model,
        "UNKNOWN_MODEL",
    )

    if info.file_date:
        date_text = info.file_date.strftime(
            "%Y%m%d"
        )
    else:
        date_text = "UNKNOWN_DATE"

    factory = sanitize_filename_part(
        info.factory,
        "UNKNOWN_FACTORY",
    )

    machine_count = sanitize_filename_part(
        info.machine_count,
        "UNKNOWN_NUMBER",
    )

    return (
        f"{model}_"
        f"{date_text}_"
        f"{factory}_"
        f"{machine_count}"
    )


def make_unique_path(
    dest_path: str,
) -> str:
    """같은 파일이 있으면 _1, _2 등을 붙임."""
    if not os.path.exists(dest_path):
        return dest_path

    directory = os.path.dirname(dest_path)
    file_name = os.path.basename(dest_path)
    stem, extension = os.path.splitext(file_name)

    index = 1

    while True:
        candidate = os.path.join(
            directory,
            f"{stem}_{index}{extension}",
        )

        if not os.path.exists(candidate):
            return candidate

        index += 1


def copy_with_new_name(
    source: str,
    save_path: str,
    output_base_name: str,
) -> str:
    """새 파일명을 사용하여 파일을 복사함."""
    _, extension = os.path.splitext(source)

    destination_name = (
        output_base_name
        + extension.lower()
    )

    destination_path = os.path.join(
        save_path,
        destination_name,
    )

    destination_path = make_unique_path(
        destination_path
    )

    shutil.copy2(
        source,
        destination_path,
    )

    return destination_path


def download_files(
    file_items: list,
    save_path: str,
) -> None:
    """조건에 맞는 SRI와 PCM 파일을 복사함."""
    os.makedirs(
        save_path,
        exist_ok=True,
    )

    total = len(file_items)
    success = 0
    failed = 0

    print(
        f"\n  총 {total}개의 매칭을 발견했습니다."
    )
    print(
        f"  저장 경로: {save_path}\n"
    )

    for index, item in enumerate(
        file_items,
        start=1,
    ):
        pcm_path, sri_path, info = item

        try:
            output_base_name = make_output_base_name(
                info
            )

            sri_destination = copy_with_new_name(
                sri_path,
                save_path,
                output_base_name,
            )

            print(
                f"  [{index}/{total}] SRI 복사: "
                f"{os.path.basename(sri_destination)}"
            )

            if pcm_path:
                pcm_destination = copy_with_new_name(
                    pcm_path,
                    save_path,
                    output_base_name,
                )

                print(
                    f"  [{index}/{total}] PCM 복사: "
                    f"{os.path.basename(pcm_destination)}"
                )
            else:
                print(
                    f"  [{index}/{total}] "
                    "PCM 없음: SRI만 복사"
                )

            if (
                info.factory is None
                or info.machine_count is None
            ):
                print(
                    "      [경고] 공장명 또는 기계개수를 "
                    "찾지 못해 UNKNOWN 값으로 저장했습니다."
                )

            success += 1

        except Exception as error:
            print(
                f"  [{index}/{total}] "
                f"복사 실패: {error}"
            )
            failed += 1

    print("\n" + "-" * 50)
    print(
        f"  완료: 성공 {success} / 실패 {failed}"
    )
    print("-" * 50 + "\n")


def main() -> None:
    (
        start_date,
        end_date,
        model_name,
        save_path,
        db_root,
    ) = get_inputs()

    print("\n  검색 조건")
    print(
        f"    - 기간      : "
        f"{start_date} ~ {end_date}"
    )
    print(
        f"    - 모델명    : {model_name}"
    )
    print(
        f"    - 저장 경로 : {save_path}"
    )
    print(
        f"    - DB 루트   : {db_root}\n"
    )

    print("  파일을 검색 중입니다...\n")

    file_items = find_matching_files(
        start=start_date,
        end=end_date,
        model=model_name,
        db_root=db_root,
    )

    if not file_items:
        print(
            "  ※ 조건에 맞는 파일을 "
            "찾지 못했습니다."
        )
        print(
            "    - 날짜/모델명/DB_ROOT/"
            "월폴더명(01~12)을 확인해주세요.\n"
        )
        return

    download_files(
        file_items,
        save_path,
    )


if __name__ == "__main__":
    main()