import os
import shutil
import re
import sys
from datetime import datetime

# 파일명에 쓸 수 없는 특수문자를 제거/변경하는 안전 함수
def sanitize_filename(text):
    # 알파벳, 숫자, 가운뎃줄(-), 마침표(.)가 아닌 모든 문자를 언더바(_)로 교체
    return re.sub(r'[^\w\-\.]', '_', text)

def main():
    print("="*70)
    print("🚗 사내 DB 자동차 PCM & SRI 추출기 (초안정성 최적화 버전) 🚗")
    print("="*70)

    car_model = input("1. 검색할 자동차 일련번호? (예: AEKE10215) : ").strip()
    if not car_model:
        print("❌ 오류: 일련번호를 반드시 입력해야 합니다.")
        return

    start_str = input("2. 시작 날짜? (예: 20260101) : ").strip()
    end_str = input("3. 끝 날짜? (예: 20261231) : ").strip()
    save_path = input("4. 저장 경로? (예: /home/user/result) : ").strip()

    db_base_path = "/var/사내DB/pcm_data" 

    try:
        start_date = datetime.strptime(start_str, "%Y%m%d").date()
        end_date = datetime.strptime(end_str, "%Y%m%d").date()
    except ValueError:
        print("❌ 날짜 형식이 잘못되었습니다. YYYYMMDD 형태로 입력해주세요.")
        return

    # [개선 4] 검색할 연도 범위 미리 계산 (탐색 최적화용)
    target_years = [str(year) for year in range(start_date.year, end_date.year + 1)]

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    copied_count = 0
    skipped_count = 0
    scanned_count = 0
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    print("\n" + "-"*70)
    print("🔍 검색을 시작합니다...")
    print(f"▶ 모델명: {car_model}")
    print(f"▶ 기  간: {start_str} ~ {end_str}")
    print(f"▶ 저장처: {save_path}")
    print("-" * 70 + "\n")

    # os.walk 탐색
    for root, dirs, files in os.walk(db_base_path):
        
        # [개선 4-2] 연도 폴더 가지치기 (성능 최적화)
        # 만약 현재 폴더 이름이 4자리 연도(예: 2024)인데 검색 범위에 없으면 안쪽을 탐색하지 않고 건너뜀
        current_folder = os.path.basename(root)
        if re.match(r'^\d{4}$', current_folder) and current_folder not in target_years:
            dirs[:] = [] # 안쪽 폴더 탐색 취소
            continue

        for file in files:
            scanned_count += 1
            if scanned_count % 10 == 0:
                spin_char = spinner[(scanned_count // 10) % len(spinner)]
                sys.stdout.write(f"\r{spin_char} DB 탐색 중... (현재 {scanned_count}개의 파일 스캔 완료)")
                sys.stdout.flush()

            if file.endswith(".sri"):
                sri_path = os.path.join(root, file)
                
                try:
                    with open(sri_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(sri_path, 'r', encoding='cp949') as f:
                            content = f.read()
                    except:
                        continue 
                
                car_match = re.search(r'CAR_NUM:\s*([A-Za-z0-9]+)', content, re.IGNORECASE)
                if not car_match: continue 
                
                if car_match.group(1) == car_model:
                    
                    # [개선 2] 날짜 하이픈(-) 유무 동시 지원
                    date_match = re.search(r'DATE:\s*(\d{4}-?\d{2}-?\d{2})', content, re.IGNORECASE)
                    
                    if date_match:
                        # 하이픈이 있다면 제거하여 YYYYMMDD 통일
                        date_str_raw = date_match.group(1).replace("-", "") 
                        file_date = datetime.strptime(date_str_raw, "%Y%m%d").date()
                        
                        if start_date <= file_date <= end_date:
                            
                            store_match = re.search(r'STORE:\s*([A-Za-z0-9\-]+)', content, re.IGNORECASE)
                            store_raw = store_match.group(1) if store_match else "UNKNOWN"
                            
                            freq_match = re.search(r'freq:\s*([\d\.]+)', content, re.IGNORECASE)
                            freq_raw = freq_match.group(1) if freq_match else "000.0"
                            
                            # [개선 3] 특수문자 안전 필터링
                            store_name = sanitize_filename(store_raw)
                            frequency = sanitize_filename(freq_raw)
                            clean_date_str = file_date.strftime("%Y%m%d")
                            
                            pcm_filename = file.replace(".sri", ".pcm")
                            pcm_path = os.path.join(root, pcm_filename)
                            
                            if os.path.exists(pcm_path):
                                new_base_name = f"{store_name}_{clean_date_str}_{car_model}_{frequency}"
                                
                                target_sri = os.path.join(save_path, f"{new_base_name}.sri")
                                target_pcm = os.path.join(save_path, f"{new_base_name}.pcm")
                                
                                # [개선 1 & 5] 두 파일 모두 체크하고, 중복 시 로그 출력
                                if not os.path.exists(target_pcm) and not os.path.exists(target_sri):
                                    shutil.copy2(sri_path, target_sri)
                                    shutil.copy2(pcm_path, target_pcm)
                                    copied_count += 1
                                    sys.stdout.write("\r" + " "*60 + "\r") 
                                    print(f"✔️ 복사 성공: {new_base_name}.(pcm/sri)")
                                else:
                                    skipped_count += 1
                                    sys.stdout.write("\r" + " "*60 + "\r") 
                                    print(f"⏭️ 중복 스킵: {new_base_name}.(pcm/sri) - 이미 존재함")

    sys.stdout.write("\r" + " "*60 + "\r")

    print("\n" + "="*70)
    print(f"📊 스캔한 파일: 총 {scanned_count}개")
    if copied_count > 0 or skipped_count > 0:
        print(f"✅ 새롭게 저장됨: {copied_count}세트")
        print(f"⏭️ 이미 있어 넘김: {skipped_count}세트")
    else:
        print("❌ 기간 내에 해당 일련번호의 파일을 찾지 못했습니다.")
    print("="*70)

if __name__ == "__main__":
    main()