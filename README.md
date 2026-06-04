### Sanggwan Init Setting

- python ./src/init_dev_info.py
- python ./src/remote_to_local.py --start "2026-05-22" --end "2026-06-03" --dev "Mpm310"

  ```
  SELECT *
  FROM mpm330_sang
  ORDER BY rcvtime ASC
  LIMIT 1; => 20260522131237

  작업날짜 => 2026-06-03
  ```

- python ./src/remote_to_local.py --start "2026-05-22" --end "2026-06-03" --dev "Mpm330"

  ```
  SELECT *
  FROM mpm330_sang
  ORDER BY rcvtime ASC
  LIMIT 1; => 20260522125936

  작업날짜 => 2026-06-03
  ```

- python ./src/device_hourly_ac.py --start "2026-05-22" --end "2026-06-03"
- python ./src/device_daily_ac.py --start "2026-05-22" --end "2026-06-03"
