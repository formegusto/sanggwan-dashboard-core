##### python ./src/yj_device_hourly_ac.py --start "2025-07-23" --end "2025-08-31"

### 월요일 출근 시

- ./bin/yj_date.sh --start "2026-05-22" --end "2026-05-25"
  - 금요일 날짜 ~ 일요일 날짜 (3개 간격이 됨 금 토 일)
- ./bin/plc_date.sh --start "2026-05-22" --end "2026-05-25"
  - 금요일 날짜 ~ 일요일 날짜
- [예측] ./bin/date.sh --start "2026-05-22" --end "2026-05-25"
  - 금요일 날짜 ~ 일요일 날짜

### Yanjae Init

- python ./src/yangjae_init.py

### Remote To Local

- python ./src/remote_to_local.py --start "2025-01-01" --end "2025-11-20" --dev "Mpm310"
- python ./src/remote_to_local.py --start "2025-01-01" --end "2025-11-20" --dev "Mpm330"
- python ./src/remote_to_local.py --start "2025-11-16" --end "2025-11-16" --dev "Mpm310"
- python ./src/remote_to_local.py --start "2025-11-16" --end "2025-11-16" --dev "Mpm330"
  - 어제 데이터만 가지고 오고 싶을 때의 명령어. (이전 날의 날짜를 start, end에 동일하게 입력)

### Yangjae Device Hourly Active Power (시간대별 유효전력량)

- python ./src/yj_device_hourly_ac.py --start "2025-01-16" --end "2025-11-16"
  - 2025-01-16 이 시작점 데이터
- python ./src/yj_device_hourly_ac.py --start "2025-07-01" --end "2025-11-16"
  - (20) 이걸로 돌려놨음. 8월 데이터 쌓이면 한번 실 데이터랑 비교
- python ./src/yj_device_hourly_ac.py --start "2025-11-16" --end "2025-11-16"
- python ./src/yj_device_hourly_ac.py --start "2025-11-17" --end "2025-11-20"

### Yangjae Device Daily Active Power (일별 유효전력량 - Hourly Data 참고해서 생성됨)

- python ./src/yj_device_daily_ac.py --start "2025-01-01" --end "2025-11-16"
  - 이걸로 테이블 날리고 전체적으로 싹 진행해보기
- python ./src/yj_device_daily_ac.py --start "2025-11-10" --end "2025-11-16"
  - 우선은 박사님 보여드려야해서 이걸로 돌려놨음
- python ./src/yj_device_daily_ac.py --start "2025-11-17" --end "2025-11-20"

### Yangjae Hourly Active Power (시간대-기기별 유효전력량 참고해서 생성됨)

- MAIN - 현재 가장 중요하게 보고 있는 그러한,,
- SUB - 추가 설비까지 붙인 데이터
- python ./src/yj_hourly_ac.py --start "2025-01-01" --end "2025-11-16"
  - 이걸로 테이블 날리고 전체적으로 싹 진행해보기
- python ./src/yj_hourly_ac.py --start "2025-11-10" --end "2025-11-16"
  - 우선은 박사님 보여드려야해서 이걸로 돌려놨음
- python ./src/yj_hourly_ac.py --start "2025-11-17" --end "2025-11-20"

### Yangjae Daily Active Power (일-기기별 유효전력량 참고해서 생성됨)

- MAIN - 현재 가장 중요하게 보고 있는 그러한,,
- SUB - 추가 설비까지 붙인 데이터
- python ./src/yj_daily_ac.py --start "2025-01-01" --end "2025-11-16"
  - 이걸로 테이블 날리고 전체적으로 싹 진행해보기
- python ./src/yj_daily_ac.py --start "2025-11-10" --end "2025-11-16"
  - 우선은 박사님 보여드려야해서 이걸로 돌려놨음
- python ./src/yj_daily_ac.py --start "2025-11-17" --end "2025-11-20"

### Yangjae Report Export

- python ./src/yj_week_report.py
- 어제부터 일주일 전까지의 DeviceDailyActivePower를 탐색하여 8월 데이터와 비교.
