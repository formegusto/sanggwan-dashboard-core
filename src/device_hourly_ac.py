import argparse
import datetime as dt
import os

from db import get_local

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()

    if args.start is None:
        start = dt.datetime.strptime((dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    else:
        start = dt.datetime.strptime(args.start, "%Y-%m-%d")
    start_rcvtime = start.strftime("%Y%m%d%H%M%S")

    end = (start if args.end is None else dt.datetime.strptime(args.end, "%Y-%m-%d")) + dt.timedelta(days=1)
    end_rcvtime = end.strftime("%Y%m%d%H%M%S")

    dates = []
    cur = start
    while cur < end:
        dates.append(cur)
        cur += dt.timedelta(days=1)

    db = get_local()
    dev_col = db["Device"]
    devices = list(dev_col.find({
        "farmid": "0005"
    }))
    
    dhac_col = db["DeviceHourlyActivePower"]
    for target_date in dates:
        for target_device in devices:
            for h in range(24):
                start_time = target_date - dt.timedelta(hours=9) + dt.timedelta(hours=h)
                end_time = start_time + dt.timedelta(hours=1)
                results = list(db[f'Mpm{target_device["model"]}'].find({
                    "$and": [
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
                    ("createdAt", 1)
                ]))
                if len(results) != 0: 
                    print(target_device["devname"], start_time + dt.timedelta(hours=9), end_time + dt.timedelta(hours=9), len(results))
                    kw_key = "activepower" if target_device["model"] == "310" else "totalacpower"
                    kw_list = [r[kw_key] for r in results]
                    kwh_list = [kw / 60 for kw in kw_list]
                    total_kwh = sum(kwh_list)
                    rcvtime = (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S")

                    ex = dhac_col.find_one({
                        "$and": [
                            {
                                "devid": target_device["devid"],
                            },
                            {
                                "model": target_device["model"],
                            },
                            {
                                "rcvtime": rcvtime
                            }
                        ]
                    })
                    if ex is None:
                        dhac_col.insert_one({
                            "farmid": target_device["farmid"],
                            "devid": target_device["devid"],
                            "model": target_device["model"],
                            "devDocument": target_device["_id"],
                            "kwh": total_kwh,
                            "reference": {
                                "count": len(kw_list),
                                "kw": kw_list,
                                "kwh": kwh_list
                            },
                            "rcvtime": (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S"),
                            "createdAt": start_time,
                            "updatedAt": start_time
                        })
                    else:
                        dhac_col.update_one({
                            "_id": ex["_id"]
                        }, {
                            "$set": {
                                "farmid": target_device["farmid"],
                                "devid": target_device["devid"],
                                "model": target_device["model"],
                                "devDocument": target_device["_id"],
                                "kwh": total_kwh,
                                "reference": {
                                    "count": len(kw_list),
                                    "kw": kw_list,
                                    "kwh": kwh_list
                                },
                            }
                        })
                else:
                    print(target_device["devname"], start_time + dt.timedelta(hours=9), end_time + dt.timedelta(hours=9), "!!!! NO SAVE !!!!", len(results))
            os.system("clear")