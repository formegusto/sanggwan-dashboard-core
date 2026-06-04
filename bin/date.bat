@echo off

python ./src/remote_to_local.py --dev "Mpm310" %*
python ./src/remote_to_local.py --dev "Mpm330" %*

python ./src/device_hourly_ac.py %*
python ./src/device_daily_ac.py %*
python ./src/farm_hourly_ac.py %*
python ./src/farm_daily_ac.py %*
python ./src/week_report.py
