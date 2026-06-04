import datetime as dt
import pandas as pd

from db import get_local
from week_report_util import report_get

import matplotlib.pyplot as plt

import platform

system = platform.system()

if system == 'Darwin':  # Mac
    plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
elif system == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:  # Linux
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

main_devs = [
    {
        "devid": 2,
        "model": "310"
    },
    {
        "devid": 3,
        "model": "310"
    },
    {
        "devid": 4,
        "model": "310"
    },
    {
        "devid": 5,
        "model": "310"
    },
    {
        "devid": 6,
        "model": "310"
    },
    {
        "devid": 7,
        "model": "310"
    },
    {
        "devid": 8,
        "model": "310"
    },
]

sub_devs = [
    {
        "devid": 0,
        "model": "330"
    },
    
]

all_devs = main_devs

if __name__ == "__main__":
    start = dt.datetime.strptime("2026-05-29", "%Y-%m-%d")
    end = dt.datetime.strptime(dt.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
    
    dates = []
    cur = start
    while cur < end:
        dates.append(cur)
        cur += dt.timedelta(days=1)

    db = get_local()
    totals = []
    ddac_col = db["DeviceDailyActivePower"]
    df = pd.DataFrame()
    for dev_info in all_devs:
        dev = db["Device"].find_one({
            "$and": [
                {
                    "model": dev_info["model"]
                },
                {
                    "devid": dev_info["devid"]
                }
            ]
        })

        for target_date in dates:
            result = ddac_col.find_one({
                "$and": [
                    {
                        "devDocument": dev["_id"]
                    },
                    {
                        "createdAt": target_date - dt.timedelta(hours=9)
                    }
                ]
            })
            if result is not None:
                df = pd.concat([df, pd.DataFrame([
                    {
                        "devid": result["devid"],
                        "date": target_date.strftime("%Y-%m-%d"),
                        "model": result["model"],
                        "devname": dev["devname"],
                        "kwh": round(result["kwh"], 2)
                    }
                ])])

            
    total_kg = 1558.512 # 260206 -> 1558.512kg
    total_days = 36
    week_kg = round(total_kg / total_days * 7, 2)
    kg_day = round(week_kg / 7, 2)

    df = pd.concat([df, pd.DataFrame([
                {
                    "devid": "yield",
                    "date": "constant",
                    "model": "kg/40day",
                    "devname": "-",
                    "kwh": total_kg,
                }
            ])])
    df = pd.concat([df, pd.DataFrame([
                {
                    "devid": "yield",
                    "date": "constant",
                    "model": "kg/day",
                    "devname": "-",
                    "kwh": kg_day,
                }
            ])])
    

    # total_dev
    total_dev_info = db["Device"].find_one({
        "model": sub_devs[0]["model"],
        "devid": sub_devs[0]["devid"]
    })
    total_df = pd.DataFrame()
    for target_date in dates:
        result = ddac_col.find_one({
            "$and": [
                {
                    "devDocument": total_dev_info["_id"]
                },
                {
                    "createdAt": target_date - dt.timedelta(hours=9)
                }
            ]
        })
        if result is not None:
            total_df = pd.concat([total_df, pd.DataFrame([
                {
                    "devid": result["devid"],
                    "date": target_date.strftime("%Y-%m-%d"),
                    "model": result["model"],
                    "devname": total_dev_info["devname"],
                    "kwh": round(result["kwh"], 2)
                }
            ])])
    
    evals = []
    evals_total = []
    for target_date in dates:
        date_str = target_date.strftime("%Y-%m-%d")
        kwh = round(df[df["date"] == date_str]["kwh"].values.sum(), 2)
        kwh_total = round(total_df[total_df["date"] == date_str]["kwh"].values.sum(), 2)
        df = pd.concat([df, pd.DataFrame([
                {
                    "devid": "total",
                    "date": date_str,
                    "model": "-",
                    "devname": "-",
                    "kwh": round(kwh, 2),
                    "kwh_total": kwh_total,
                }
            ])])
        kwh_kg = round(kwh / kg_day, 2)
        kwh_total_kg = round(kwh_total / kg_day, 2)
        evals.append(kwh_kg)
        evals_total.append(kwh_total_kg)
        df = pd.concat([df, pd.DataFrame([
                {
                    "devid": "kwh/kg",
                    "date": "",
                    "model": "-",
                    "devname": "-",
                    "kwh": kwh_kg,
                    "kwh_total": kwh_total_kg,
                }
            ])])
        
    total_kwh = round(df[df["devid"] == "total"]["kwh"].values.sum(), 2)
    total_kwh_total = round(df[df["devid"] == "total"]["kwh_total"].values.sum(), 2)
    df = pd.concat([df, pd.DataFrame([
            {
                "devid": "total",
                "date": "all",
                "model": "-",
                "devname": "-",
                "kwh": total_kwh,
                "kwh_total": total_kwh_total
            }
        ])])
    days = len(dates)
    kg_n_day = round(kg_day * days, 2)
    df = pd.concat([df, pd.DataFrame([
            {
                "devid": "yield",
                "date": "constant",
                "model": f"kg/{days}day",
                "devname": "-",
                "kwh": kg_n_day,
                "kwh_total": kg_n_day
            }
        ])])
    avg_kwh_kg_n_day = round(total_kwh / kg_n_day, 2)
    avg_kwh_total_kg_n_day = round(total_kwh_total / kg_n_day, 2)
    df = pd.concat([df, pd.DataFrame([
            {
                "devid": "kwh/kg",
                "date": "average",
                "model": f"kwh/kg/{days}day",
                "devname": "-",
                "kwh": avg_kwh_kg_n_day,
                "kwh_total": avg_kwh_total_kg_n_day
            }
        ])])

    evals_img_path = f'./notebook/report/evals-report-sanggwan-{start.strftime("%Y%m%d")}-{end.strftime("%Y%m%d")}.png'

    goal_mean = 14
    fig = plt.figure(figsize=(16, 6))
    plt.plot(dates, evals, linewidth=3, label="kWh/kg", color="blue")
    plt.plot(dates, evals, linewidth=3, label="kwh_total/kg", color="skyblue")
    plt.hlines(avg_kwh_kg_n_day, linewidth=3, xmin=dates[0], xmax=dates[-1], label="평균", color="orange")
    plt.hlines(avg_kwh_total_kg_n_day, linewidth=3, xmin=dates[0], xmax=dates[-1], label="토탈 센서 평균", color="coral")
    plt.hlines(goal_mean, linewidth=3, xmin=dates[0], xmax=dates[-1], label="목표", color="red")
    plt.xticks(fontsize=16, rotation=45, ha="right")
    plt.yticks(fontsize=16)
    plt.title(f'상관 일일 평가 결과 {dates[0].strftime("%Y%m%d")}~{dates[-1].strftime("%Y%m%d")}', fontsize=16)
    plt.xlabel("날짜", fontsize=16)
    plt.ylabel("kWh/kg", fontsize=16)
    plt.grid(True)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.legend(fontsize=16)
    plt.savefig(evals_img_path, dpi=150, bbox_inches="tight") # 🔥 잘림 방지
    plt.close()
    
    evals = df
    time, stat, hourly, total_hourly, img_path = report_get(start, end)
    if system == 'Windows':
        sys_root_path = "C:/Users/keti-eco-server/Desktop/KETI-CASTER/ktc-download/files"
    else: # mac and linux
        sys_root_path = "./notebook/report"
    excel_path = f'{sys_root_path}/report-sanggwan-{dates[0].strftime("%Y%m%d")}-{dates[-1].strftime("%Y%m%d")}.xlsx'

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_format = workbook.add_format({
            "bg_color": "#DDDDDD",
            "bold": True,
            "border": 1
        })
        worksheet = workbook.add_worksheet("평가")
        writer.sheets["평가"] = worksheet
        worksheet.insert_image("A1", evals_img_path, {'x_scale':0.55, 'y_scale':0.55})
        start_row = 16  # 이미지 높이에 따라 조절 (필요하면 올려/내려 조정)
        evals.to_excel(writer, index=False, sheet_name="평가", startrow=start_row, startcol=0)
        for col_idx in range(evals.shape[1]):  
            worksheet.set_column(col_idx, col_idx, 16)
        for col_num, value in enumerate(evals.columns.values):
            worksheet.write(start_row, col_num, value, header_format)
        
        # Sheet1: 일별값
        _df1 = time.reset_index()
        worksheet = workbook.add_worksheet("일별")
        writer.sheets["일별"] = worksheet
        
        _df1.rename({
            "index": "날짜"
        }, axis=1, inplace=True)
        _df1.to_excel(writer, sheet_name="일별", index=False)
        for i, col in enumerate(_df1.columns):
            width = max(_df1[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, width)
        for col_num, value in enumerate(_df1.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Sheet2: 통계
        _df2 = stat.reset_index()
        worksheet = workbook.add_worksheet("통계")
        writer.sheets["통계"] = worksheet
        _df2.rename({
            "index": "시간",
        }, axis=1, inplace=True)
        _df2.to_excel(writer, sheet_name="통계", index=False)
        for i, col in enumerate(_df2.columns):
            width = max(_df2[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, width)
        for col_num, value in enumerate(_df2.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Sheet3: 시각화
        worksheet = workbook.add_worksheet("시간대별")
        writer.sheets["시간대별"] = worksheet

        # PNG 이미지 삽입
        worksheet.insert_image("A1", img_path, {'x_scale':0.95, 'y_scale':0.95})
        
        start_row = 63  # 이미지 높이에 따라 조절 (필요하면 올려/내려 조정)
        _df3 = hourly.reset_index()
        _df3.rename({
            "index": "장치명",
        }, axis=1, inplace=True)
        _df3.to_excel(writer, sheet_name="시간대별",
                    startrow=start_row, startcol=0, index=False)
        for col_num, value in enumerate(_df3.columns.values):
            worksheet.write(start_row, col_num, value, header_format)
        worksheet.set_column(0, 0, 30)

        print("📌 Excel 생성 완료:", excel_path)

    