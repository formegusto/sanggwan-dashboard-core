import datetime as dt

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from db import get_local
from matplotlib.gridspec import GridSpec

sub_devs = [
    {
        "devid": 0,
        "model": "330"
    },
    
]

def report_get(start, end):
    db = get_local()
    dev_col = db["Device"]
    devices = list(dev_col.find({
        "farmid": "0005",
        "model": "310"
    }))
    total_device = dev_col.find_one({
        "farmid": "0005",
        "model": "330"
    })

    dates = []
    cur = start
    while cur < end:
        dates.append(cur)
        cur += dt.timedelta(days=1)

    dhac_col = db["DeviceHourlyActivePower"]
    daily_device_acs = []
    for target_date in dates:
        _daily_device_acs = []
        for target_device in devices:
            start_time = target_date - dt.timedelta(hours=9)
            end_time = start_time + dt.timedelta(days=1)
            results = list(dhac_col.find({
                "$and": [
                    {
                        "model": target_device["model"],
                    },
                    {
                        "devid": target_device["devid"],
                    },
                    {
                        "createdAt": {
                            "$gte": start_time
                        },
                    },
                    {
                        "createdAt": {
                            "$lt": end_time
                        }
                    }
                ]
            }, sort=[
                ("rcvtime", 1)
            ]))
            acs = np.full(24, .0)
            for r in results:
                h = dt.datetime.strptime(r["rcvtime"], "%Y%m%d%H%M%S").hour
                acs[h] = round(r["kwh"], 2)
            _daily_device_acs.append(acs)
        daily_device_acs.append(np.array(_daily_device_acs))
    daily_device_acs = np.array(daily_device_acs)
    daily_acs = np.round(daily_device_acs.sum(axis=1), 2)

    # df total
    # total_dev
    daily_total_acs = []
    total_dev_info = db["Device"].find_one({
        "model": sub_devs[0]["model"],
        "devid": sub_devs[0]["devid"]
    })
    for target_date in dates:
        start_time = target_date - dt.timedelta(hours=9)
        end_time = start_time + dt.timedelta(days=1)
        results = dhac_col.find({
            "$and": [
                {
                    "devDocument": total_dev_info["_id"]
                },
                {
                    "createdAt": {
                        "$gte": start_time
                    },
                },
                {
                    "createdAt": {
                        "$lt": end_time
                    }
                }
            ]
        })
        acs = np.full(24, 0)
        for r in results:
            h = dt.datetime.strptime(r["rcvtime"], "%Y%m%d%H%M%S").hour
            acs[h] = round(r["kwh"], 2)
        daily_total_acs.append(acs)
    daily_total_acs = np.array(daily_total_acs)
        

    df1 = pd.DataFrame(daily_acs)
    df1.index = [f'{d.strftime("%Y-%m-%d")}' for d in dates]
    df1.columns = [f"{str(c).zfill(2)}시" for c in df1.columns]
    df1["총합"] = np.round(df1.sum(axis=1), 2)
    df1.loc["평균"] = np.round(df1.mean(axis=0), 2)

    df_total = pd.DataFrame(daily_total_acs)
    df_total.index = [f'{d.strftime("%Y-%m-%d")}' for d in dates]
    df_total.columns = [f"{str(c).zfill(2)}시" for c in df_total.columns]
    df_total["총합"] = np.round(df_total.sum(axis=1), 2)
    df_total.loc["토탈 센서 평균"] = np.round(df_total.mean(axis=0), 2)

    df1 = pd.concat([df1, df_total])

    # ~{yesterday - 1}
    y1_max_acs = np.round(daily_acs[:-1].max(axis=0), 2)
    y1_mean_acs = np.round(daily_acs[:-1].mean(axis=0), 2)
    y1_min_acs = np.round(daily_acs[:-1].min(axis=0), 2)
    y1_median_acs = np.round(np.median(daily_acs[:-1], axis=0), 2)

    end_date_str = dates[-1].strftime("%Y-%m-%d")
    y1_date_str = dates[-2].strftime("%Y-%m-%d")

    y_acs = daily_acs[-1]
    df2 = pd.DataFrame([y1_mean_acs, y_acs, y1_mean_acs - y_acs,
                    y1_max_acs, y1_max_acs - y_acs, 
                    y1_median_acs, y1_median_acs - y_acs,
                    y1_min_acs, y1_min_acs - y_acs
                    ]).T


    df2.columns = [f"mean(~{y1_date_str})", f"{end_date_str}", "mean err", 
                f"max(~{y1_date_str})", "max err",
                f"med(~{y1_date_str})", "med err",
                f"min(~{y1_date_str})", "min err",
                ]


    df3 = pd.DataFrame(daily_device_acs[-1])
    last_day_total = daily_total_acs[-1]
    df3.index = [d["devname"] for d in devices]
    df3.columns = [f"{str(c).zfill(2)}시" for c in df3.columns]
    df3["총합"] = np.round(df3.sum(axis=1), 2)
    df3.loc["총합"] = np.round(df3.sum(axis=0), 2)
    df3.loc["토탈 센서"] = np.append(last_day_total, last_day_total.sum())


    start = dates[0].strftime("%Y%m%d")
    end = dates[-1].strftime("%Y%m%d")
    y1 = dates[-2].strftime("%Y%m%d")

    fig = plt.figure(figsize=(20, 14))  # 🔹더 크게 추천

    gs = GridSpec(4, 4, figure=fig)
    ax_main = fig.add_subplot(gs[0:2, 0:2])
    ax_main.plot(daily_acs[0], linewidth=3, color="lightblue", label=f"{start}~{y1}")
    ax_main.plot(daily_acs[1:-1].T, linewidth=2, color="lightblue")
    ax_main.plot(daily_acs.mean(axis=0), linewidth=3, color="blue",label="평균")

    ax_main.plot(daily_acs[-1], linewidth=3, color="red",label=f"{end}")

    ax_main.set_title(f'상관 ({start}~{end})', fontsize=20)
    ax_main.set_ylabel("Active Power", fontsize=18)
    ax_main.set_xticks(np.arange(24))
    ax_main.tick_params(axis='both', which='major', labelsize=14)
    ax_main.set_xlabel("Hours", fontsize=18)
    ax_main.legend(loc="upper right", ncol=3, fontsize=14)
    ax_main.grid(True)

    ax_sub = fig.add_subplot(gs[0:2, 2:4])
    ax_sub.plot(daily_total_acs[0], linewidth=3, color="lightblue", label="토탈 센서")
    ax_sub.plot(daily_total_acs[1: -1]. T, linewidth=2, color="lightblue")
    ax_sub.plot(daily_total_acs.mean(axis=0), linewidth=3, color="blue", label="토탈 센서 평균")
    ax_sub.plot(daily_total_acs[-1], linewidth=3, color="red", label=f"{end}")
    ax_sub.set_title(f'상관 토탈 센서 ({start}~{end})', fontsize=20)
    ax_sub.set_ylabel("Active Power", fontsize=18)
    ax_sub.set_xticks(np.arange(24))
    ax_sub.tick_params(axis='both', which='major', labelsize=14)
    ax_sub.set_xlabel("Hours", fontsize=18)
    ax_sub.legend(loc="upper right", ncol=3, fontsize=14)
    ax_sub.grid(True)



    for idx in range(8):
        if idx == 7:
            _acs = daily_total_acs
            devname = total_dev_info["devname"]
        else:
            _acs = daily_device_acs[:, idx, :]
            devname = devices[idx]["devname"]
        r = 2 + idx // 4
        c = idx % 4
        ax = fig.add_subplot(gs[r, c])
        ax.plot(_acs[:-1].T, linewidth=2, color="lightblue")
        ax.plot(_acs.mean(axis=0), linewidth=2, color="blue")
        ax.plot(_acs[-1], linewidth=2, color="red")
        ax.set_title(f'{devname}', fontsize=14)
        ax.set_xticks(np.arange(0, 24, 4))
        ax.tick_params(axis='both', which='major', labelsize=12)
        ax.grid(True)

    img_path = f'./notebook/report/report-sanggwan-{start}-{end}.png'
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # 🔥 제목과 영역 충돌 방지
    plt.savefig(img_path, dpi=150, bbox_inches="tight") # 🔥 잘림 방지
    plt.close()

    return df1, df2, df3, df_total, img_path