import os
import shutil
import re
import sys
from datetime import datetime



# ─────────────────────────────────────────────
# 파일명에 쓸 수 없는 특수문자를 언더바(_)로 교체
# ─────────────────────────────────────────────
def sanitize_filename(text):
    return re.sub(r'[^\w\-\.]', '_', text)


# ─────────────────────────────────────────────
# 검색 대상 연도 / 연월 집합 미리 계산
# ─────────────────────────────────────────────
# 수정된 함수 (외부 라이브러리 설치 불필요 버전)
def build_target_sets(start_date, end_date):
    target_years = set()
    target_year_months = set()

    # datetime.date 객체에서 연도와 월을 숫자로 추출
    cur_year = start_date.year
    cur_month = start_date.month

    while (cur_year < end_date.year) or (cur_year == end_date.year and cur_month <= end_date.month):
        # 연도 저장 (문자열 'YYYY')
        target_years.add(f"{cur_year:04d}")
        # 연월 저장 (문자열 'YYYYMM')
        target_year_months.add(f"{cur_year:04d}{cur_month:02d}")
        
        # 1개월 더하기 로직
        cur_month += 1
        if cur_month > 12:
            cur_month = 1
            cur_year += 1

    return target_years, target_year_months


def main():
    print("=" * 70)
    print("🚗  사내 DB 자동차 PCM & SRI 추출기  (최종 안정화 버전)  🚗")
    print("=" * 70)

    # ── 사용자 입력 ──────────────────────────────────────────────────────
    car_model = input("1. 검색할 자동차 일련번호? (예: AEKE10215) : ").strip()
    if not car_model:
        print("❌ 오류: 일련번호를 반드시 입력해야 합니다.")
        return

    start_str = input("2. 시작 날짜? (예: 20260101) : ").strip()
    end_str   = input("3. 끝   날짜? (예: 20261231) : ").strip()
    save_path = input("4. 저장 경로? (예: /home/user/result) : ").strip()

    # ★★★ 사내 서버의 실제 DB 최상위 폴더 경로로 반드시 수정하세요! ★★★
    db_base_path = "/var/사내DB/pcm_data"

    # ── 날짜 파싱 ────────────────────────────────────────────────────────
    try:
        start_date = datetime.strptime(start_str, "%Y%m%d").date()
        end_date   = datetime.strptime(end_str,   "%Y%m%d").date()
    except ValueError:
        print("❌ 날짜 형식이 잘못되었습니다. YYYYMMDD 형태로 입력해주세요.")
        return

    if start_date > end_date:
        print("❌ 시작 날짜가 끝 날짜보다 늦습니다. 다시 확인해주세요.")
        return

    # ── 탐색 최적화용 연도·연월 집합 ─────────────────────────────────────
    target_years, target_year_months = build_target_sets(start_date, end_date)

    # ── 저장 폴더 생성 ───────────────────────────────────────────────────
    os.makedirs(save_path, exist_ok=True)

    # ── 카운터 & 스피너 ──────────────────────────────────────────────────
    copied_count  = 0
    skipped_count = 0
    failed_count  = 0
    scanned_count = 0
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    print("\n" + "-" * 70)
    print("🔍 검색을 시작합니다...")
    print(f"   ▶ 일련번호 : {car_model}")
    print(f"   ▶ 기    간 : {start_str} ~ {end_str}")
    print(f"   ▶ 저 장 처 : {save_path}")
    print("-" * 70 + "\n")

    # ── 메인 탐색 루프 ───────────────────────────────────────────────────
    for root, dirs, files in os.walk(db_base_path):
        current_folder = os.path.basename(root)

        # [개선 4-A] 연도 폴더 가지치기 (예: 2024, 2025, 2026)
        if re.match(r'^\d{4}$', current_folder):
            if current_folder not in target_years:
                dirs[:] = []   # 하위 폴더 탐색 취소
                continue

        # [개선 4-B] 연월 폴더 가지치기 (예: 202603, 202604 / 또는 2026-03)
        # ※ 폴더명이 YYYY-MM 형식이라면 아래 정규식을 r'^\d{4}-\d{2}$' 로 바꾸세요
        if re.match(r'^\d{6}$', current_folder):
            if current_folder not in target_year_months:
                dirs[:] = []
                continue

        for file in files:
            if not file.endswith(".sri"):
                continue

            scanned_count += 1
            if scanned_count % 10 == 0:
                spin_char = spinner[(scanned_count // 10) % len(spinner)]
                sys.stdout.write(
                    f"\r{spin_char} DB 탐색 중... ({scanned_count}개 스캔 완료)"
                )
                sys.stdout.flush()

            sri_path = os.path.join(root, file)

            # ── .sri 파일 읽기 (UTF-8 → CP949 fallback) ─────────────────
            content = None
            for enc in ("utf-8", "cp949"):
                try:
                    with open(sri_path, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, OSError):
                    continue

            if content is None:
                continue   # 읽기 실패 → 스킵

            # ── CAR_NUM 확인 ──────────────────────────────────────────────
            car_match = re.search(r'CAR_NUM:\s*([A-Za-z0-9]+)', content, re.IGNORECASE)
            if not car_match:
                continue
            if car_match.group(1) != car_model:
                continue

            # ── DATE 확인 (하이픈 유무 모두 지원) ────────────────────────
            date_match = re.search(
                r'DATE:\s*(\d{4}-?\d{2}-?\d{2})', content, re.IGNORECASE
            )
            if not date_match:
                # [개선 4] DATE 필드 없을 때 경고 로그
                sys.stdout.write("\r" + " " * 60 + "\r")
                print(f"⚠️  DATE 필드 없음, 스킵: {sri_path}")
                continue

            date_str_raw = date_match.group(1).replace("-", "")   # YYYYMMDD 통일
            try:
                file_date = datetime.strptime(date_str_raw, "%Y%m%d").date()
            except ValueError:
                sys.stdout.write("\r" + " " * 60 + "\r")
                print(f"⚠️  DATE 값 파싱 실패 ({date_str_raw}), 스킵: {sri_path}")
                continue

            if not (start_date <= file_date <= end_date):
                continue

            # ── STORE / freq 추출 ─────────────────────────────────────────
            store_match = re.search(r'STORE:\s*([A-Za-z0-9\-]+)', content, re.IGNORECASE)
            store_raw   = store_match.group(1) if store_match else "UNKNOWN"

            freq_match  = re.search(r'freq:\s*([\d\.]+)', content, re.IGNORECASE)
            freq_raw    = freq_match.group(1) if freq_match else "000.0"

            # [개선 3] 파일명 안전 필터링
            store_name      = sanitize_filename(store_raw)
            frequency       = sanitize_filename(freq_raw)
            clean_date_str  = file_date.strftime("%Y%m%d")

            # [개선 2] 확장자만 교체 (.sri → .pcm)
            pcm_filename = os.path.splitext(file)[0] + ".pcm"
            pcm_path     = os.path.join(root, pcm_filename)

            if not os.path.exists(pcm_path):
                sys.stdout.write("\r" + " " * 60 + "\r")
                print(f"⚠️  PCM 짝꿍 없음, 스킵: {pcm_path}")
                continue

            # ── 저장 경로 & 파일명 조립 ──────────────────────────────────
            new_base_name = (
                f"{store_name}_{clean_date_str}_{car_model}_{frequency}"
            )
            target_sri = os.path.join(save_path, f"{new_base_name}.sri")
            target_pcm = os.path.join(save_path, f"{new_base_name}.pcm")

            sys.stdout.write("\r" + " " * 60 + "\r")

            # [개선 1 & 5] sri·pcm 둘 다 중복 체크 + 중복 로그
            if os.path.exists(target_pcm) or os.path.exists(target_sri):
                skipped_count += 1
                print(f"⏭️  중복 스킵  : {new_base_name}.(pcm/sri)")
                continue

            # [개선 3] 복사 실패 예외처리
            try:
                shutil.copy2(sri_path, target_sri)
                shutil.copy2(pcm_path, target_pcm)
                copied_count += 1
                print(f"✔️  복사 성공  : {new_base_name}.(pcm/sri)")
            except (OSError, shutil.Error) as e:
                failed_count += 1
                print(f"❌ 복사 실패  : {new_base_name} → 원인: {e}")
                # 절반만 복사된 파일 정리 (롤백)
                for leftover in (target_sri, target_pcm):
                    if os.path.exists(leftover):
                        try:
                            os.remove(leftover)
                        except OSError:
                            pass

    # ── 최종 결과 출력 ───────────────────────────────────────────────────
    sys.stdout.write("\r" + " " * 60 + "\r")
    print("\n" + "=" * 70)
    print(f"📊 스캔한 .sri 파일 : 총 {scanned_count}개")

    if copied_count == 0 and skipped_count == 0 and failed_count == 0:
        print("❌ 기간 내에 해당 일련번호의 파일을 찾지 못했습니다.")
    else:
        print(f"✅ 새롭게 저장됨   : {copied_count} 세트")
        print(f"⏭️  이미 있어 넘김  : {skipped_count} 세트")
        if failed_count:
            print(f"❌ 복사 실패      : {failed_count} 세트  ← 권한·용량 확인 필요")

    print("=" * 70)


if __name__ == "__main__":
    main()