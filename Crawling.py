import os
import shutil
import re
from datetime import datetime

def main():
    print("="*70)
    print("🚗 사내 DB 자동차 PCM & SRI 추출기 (내부 텍스트 완벽 분석형) 🚗")
    print("="*70)

    # 1. 사용자 입력
    car_model = input("1. 검색할 자동차 일련번호? (예: AEKE10215) : ").strip()
    if not car_model:
        print("❌ 오류: 일련번호를 반드시 입력해야 합니다.")
        return

    start_str = input("2. 시작 날짜? (예: 20260101) : ").strip()
    end_str = input("3. 끝 날짜? (예: 20261231) : ").strip()
    save_path = input("4. 저장 경로? (예: /home/user/result) : ").strip()

    # ★★★ 사내 서버의 실제 DB 최상위 폴더 경로로 반드시 수정하세요! ★★★
    db_base_path = "/var/사내DB/pcm_data" 

    try:
        start_date = datetime.strptime(start_str, "%Y%m%d").date()
        end_date = datetime.strptime(end_str, "%Y%m%d").date()
    except ValueError:
        print("❌ 날짜 형식이 잘못되었습니다. YYYYMMDD 형태로 입력해주세요.")
        return

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    copied_count = 0
    # 검색 조건 요약 출력 UI
    print("\n" + "-"*70)
    print("🔍 검색을 시작합니다...")
    print(f"▶ 모델명: {car_model}")
    print(f"▶ 기  간: {start_str} ~ {end_str}")
    print(f"▶ 저장처: {save_path}")
    print("-" * 70 + "\n")

    for root, dirs, files in os.walk(db_base_path):
        for file in files:
            if file.endswith(".sri"):
                sri_path = os.path.join(root, file)
                
                # [1단계] 무조건 .sri 파일을 열어서 텍스트 읽기
                try:
                    with open(sri_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    try:
                        with open(sri_path, 'r', encoding='cp949') as f:
                            content = f.read()
                    except:
                        continue 
                
                # [2단계] CAR_NUM 확인 (내가 찾고자 하는 모델명인지)
                # 정규식: CAR_NUM: 바로 뒤에 오는 문자/숫자들을 찾음
                car_match = re.search(r'CAR_NUM:([A-Za-z0-9]+)', content, re.IGNORECASE)
                if not car_match:
                    continue # CAR_NUM 정보가 아예 없으면 패스
                
                found_car_num = car_match.group(1)
                
                # 파일 안의 CAR_NUM이 내가 입력한 모델명과 일치할 때만 진행
                if found_car_num == car_model:
                    
                    # [3단계] DATE 확인 (기간 체크)
                    # 정규식: DATE: 뒤에 오는 2026-03-01 형태를 찾음
                    date_match = re.search(r'DATE:\s*(\d{4}-\d{2}-\d{2})', content, re.IGNORECASE)
                    
                    if date_match:
                        date_str_raw = date_match.group(1) # '2026-03-01'
                        file_date = datetime.strptime(date_str_raw, "%Y-%m-%d").date()
                        
                        # 기간 안에 들어오는지 확인
                        if start_date <= file_date <= end_date:
                            
                            # [4단계] 필요한 나머지 정보(STORE, freq) 추출
                            store_match = re.search(r'STORE:([A-Za-z0-9\-]+)', content, re.IGNORECASE)
                            store_name = store_match.group(1) if store_match else "UNKNOWN"
                            
                            freq_match = re.search(r'freq:([\d\.]+)', content, re.IGNORECASE)
                            frequency = freq_match.group(1) if freq_match else "000.0"
                            
                            # 날짜를 파일명에 쓰기 좋게 20260301 형태로 변환 (하이픈 제거)
                            clean_date_str = file_date.strftime("%Y%m%d")
                            
                            # [5단계] 짝꿍 PCM 파일 찾기 및 새 이름으로 세트 복사
                            pcm_filename = file.replace(".sri", ".pcm")
                            pcm_path = os.path.join(root, pcm_filename)
                            
                            if os.path.exists(pcm_path):
                                
                                # 요구하신 파일명 형식: {매장명}_{연월일}_{일련번호}_{주파수}
                                # 예: A-10_20260301_AEKE10215_311.4
                                new_base_name = f"{store_name}_{clean_date_str}_{car_model}_{frequency}"
                                
                                target_sri = os.path.join(save_path, f"{new_base_name}.sri")
                                target_pcm = os.path.join(save_path, f"{new_base_name}.pcm")
                                
                                if not os.path.exists(target_pcm):
                                    shutil.copy2(sri_path, target_sri)
                                    shutil.copy2(pcm_path, target_pcm)
                                    copied_count += 1
                                    print(f"✔️ 복사 성공: {new_base_name}.(pcm/sri)")

    print("\n" + "="*70)
    if copied_count > 0:
        print(f"✅ 완료! 총 {copied_count}세트가 지정한 경로와 이름으로 저장되었습니다.")
    else:
        print("❌ 기간 내에 해당 일련번호의 파일을 찾지 못했습니다.")
    print("="*70)

if __name__ == "__main__":
    main()