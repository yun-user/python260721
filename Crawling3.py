import os
import shutil
import re
from datetime import datetime

# ─────────────────────────────────────────────
# 파일명 특수문자 안전 필터링
# ─────────────────────────────────────────────
def sanitize_filename(text):
    return re.sub(r'[^\w\-\.]', '_', text)

# ─────────────────────────────────────────────
# 검색 대상 연도/연월 가지치기,우리가 들어가서 뒤져볼 폴더 이름들의 목록'**을 미리 만들어 두는 함수
# ─────────────────────────────────────────────
def build_target_sets(start_date, end_date):
    target_years = set()
    target_year_months = set()

    cur_year = start_date.year
    cur_month = start_date.month
    #연도와 월단위까지만 계산
    while (cur_year < end_date.year) or (cur_year == end_date.year and cur_month <= end_date.month):
        target_years.add(f"{cur_year:04d}")
        target_year_months.add(f"{cur_year:04d}{cur_month:02d}")
        
        cur_month += 1
        if cur_month > 12:
            cur_month = 1
            cur_year += 1

    return target_years, target_year_months

def main():
    print("=" * 70)
    print("🚗  신호 다운로드 프로그램램 (원인 분석 엑스레이 버전)  🚗")
    print("=" * 70)

    # ── 사용자 입력 ──
    signal = input("1. 신호명? (예: M0785) : ").strip()
    if not signal:
        print("❌ 오류: 신호명을 반드시 입력해야 합니다.")
        return

    start_str    = input("2. 시작 날짜? (예: 20260101) : ").strip()
    end_str      = input("3. 끝   날짜? (예: 20261231) : ").strip()
    save_path    = input("4. 저장 경로? (예: /home/user/result) : ").strip()
    db_base_path = input("5. DB   경로? (예: /var/사내DB/DB_SYS) : ").strip()

    if not db_base_path or not os.path.isdir(db_base_path):
        print("❌ 오류: DB 경로가 존재하지 않거나 접근할 수 없습니다.")
        return

    # ── 날짜 파싱 ──
    try:
        start_date = datetime.strptime(start_str, "%Y%m%d").date()
        end_date   = datetime.strptime(end_str,   "%Y%m%d").date()
    except ValueError:
        print("❌ 날짜 형식이 잘못되었습니다.")
        return

    target_years, target_year_months = build_target_sets(start_date, end_date)
    os.makedirs(save_path, exist_ok=True)

    # ── 카운터 및 탈락 원인 분석기 ──
    copied_count  = 0
    scanned_count = 0
    
    # 왜 탈락했는지 기록하는 변수들
    err_read      = 0 # 파일이 안 읽힘
    err_no_date   = 0 # DATE 텍스트가 없음
    err_out_date  = 0 # 기간이 안 맞음
    err_wrong_car = 0 # 차 번호가 안 맞음
    err_no_pcm    = 0 # .pcm 파일이 없음

    print("\n" + "-" * 70)
    print("🔍 검색을 시작합니다...")
    print("-" * 70 + "\n")

    for root, dirs, files in os.walk(db_base_path):
        current_folder = os.path.basename(root)

        if re.match(r'^\d{4}$', current_folder) and current_folder not in target_years:
            dirs[:] = []
            continue
        if re.match(r'^\d{6}$', current_folder) and current_folder not in target_year_months:
            dirs[:] = []
            continue

        # 승재님이 직접 고치셨던 완벽한 위치!
        for file in files:
            if not file.endswith(".sri"):
                continue

            sri_path = os.path.join(root, file)

            scanned_count += 1
            if scanned_count % 500 == 0:
                print(f"   ▶ DB 탐색 중... ({scanned_count}개 스캔 완료)")

            # 파일 열기
            content = None
            for enc in ("utf-8", "cp949"):
                try:
                    with open(sri_path, "r", encoding=enc) as f:
                        content = f.read()
                    break
                except (UnicodeDecodeError, OSError):
                    continue
            
            if content is None:
                err_read += 1
                continue

            # ─────────────────────────────────────────────────────────
            # [관문 1] 파일 안에 DATE 라는 글자와 날짜가 있는가?
            # ─────────────────────────────────────────────────────────
            # (수정) 날짜가 2026/03/01 처럼 빗금(/)이나 점(.)으로 되어있을 경우도 대비함
            date_match = re.search(r'DATE\s*:\s*(\d{4}[-/\.]?\d{2}[-/\.]?\d{2})', content, re.IGNORECASE)
            if not date_match:
                err_no_date += 1
                continue 

            date_str_raw = re.sub(r'[-/\.]', '', date_match.group(1)) # 특수문자 다 지우고 숫자만
            try:
                file_date = datetime.strptime(date_str_raw, "%Y%m%d").date()
            except ValueError:
                err_no_date += 1
                continue

            # ─────────────────────────────────────────────────────────
            # [관문 2] 내가 입력한 기간 안에 있는가?
            # ─────────────────────────────────────────────────────────
            if not (start_date <= file_date <= end_date):
                err_out_date += 1
                continue

            # ─────────────────────────────────────────────────────────
            # [관문 3] 차 번호가 일치하는가?
            # ─────────────────────────────────────────────────────────
            signal_match = re.search(r'GP-3\s*:\s*([A-Za-z0-9]+)', content, re.IGNORECASE)
            if not signal_match or signal_match.group(1).upper() != signal.upper():
                err_wrong_car += 1
                continue 

            # ─────────────────────────────────────────────────────────
            # [관문 4] 나머지 정보 추출 및 짝꿍 PCM 확인
            # ─────────────────────────────────────────────────────────
            location = re.search(r'SITE\s*:\s*([A-Za-z0-9\-]+)', content, re.IGNORECASE)
            location_raw  = location.group(1) if location else "UNKNOWN_LOC"

            freq_match  = re.search(r'FREQ\s*:\s*([\d\.]+)', content, re.IGNORECASE)
            freq_raw    = freq_match.group(1) if freq_match else "000.0"

            location_name   = sanitize_filename(location_raw)
            frequency       = sanitize_filename(freq_raw)
            clean_date_str  = file_date.strftime("%Y%m%d")

            pcm_filename = os.path.splitext(file)[0] + ".pcm"
            pcm_path     = os.path.join(root, pcm_filename)

            if not os.path.exists(pcm_path):
                err_no_pcm += 1
                continue

            # 새 파일명 및 복사
            new_base_name = f"{location_name}_{clean_date_str}_{signal.upper()}_{frequency}"
            target_sri = os.path.join(save_path, f"{new_base_name}.sri")
            target_pcm = os.path.join(save_path, f"{new_base_name}.pcm")

            if os.path.exists(target_pcm) or os.path.exists(target_sri):
                continue

            try:
                shutil.copy(sri_path, target_sri)
                shutil.copy(pcm_path, target_pcm)
                copied_count += 1
                print(f"   ✔️ 복사 성공 : {new_base_name}.(pcm/sri)")
            except:
                pass

    # ── 엑스레이 결과 출력 ──
    print("\n" + "=" * 70)
    print(f"📊 최종 분석 리포트 (총 스캔한 파일: {scanned_count}개)")
    print("-" * 70)
    print(f"✅ 성공적으로 복사된 세트 : {copied_count}개")
    print("\n[💀 파일들이 탈락한 진짜 이유]")
    print(f" 1. 파일 안에 'DATE: 날짜' 형식이 없어서 탈락 : {err_no_date}개")
    print(f" 2. 날짜는 있지만 입력한 기간이 아니라서 탈락 : {err_out_date}개")
    print(f" 3. 기간은 맞는데 자동차 번호가 달라서 탈락 : {err_wrong_car}개")
    print(f" 4. 차 번호까지 다 맞는데 짝꿍 .pcm이 없어서 : {err_no_pcm}개")
    print(f" 5. 파일이 깨져서 읽지 못함                 : {err_read}개")
    print("=" * 70)

if __name__ == "__main__":
    main()