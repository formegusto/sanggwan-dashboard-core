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
    ddac_col = db["DeviceDailyActivePower"]
    for target_date in dates:
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
                ("createdAt", 1)
            ]))
            if len(results) != 0: 
                print(target_device["devname"], start_time + dt.timedelta(hours=9), end_time + dt.timedelta(hours=9), len(results))
                kwh_list = [r["kwh"] for r in results]
                total_kwh = sum(kwh_list)
                rcvtime = (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S")

                ex = ddac_col.find_one({
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
                    ddac_col.insert_one({
                        "farmid": target_device["farmid"],
                        "devid": target_device["devid"],
                        "model": target_device["model"],
                        "devDocument": target_device["_id"],
                        "kwh": total_kwh,
                        "reference": {
                            "kwh": kwh_list
                        },
                        "rcvtime": (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S"),
                        "createdAt": start_time,
                        "updatedAt": start_time
                    })
                else:
                    ddac_col.update_one({
                        "_id": ex["_id"]
                    }, {
                        "$set": {
                            "farmid": target_device["farmid"],
                            "devid": target_device["devid"],
                            "model": target_device["model"],
                            "devDocument": target_device["_id"],
                            "kwh": total_kwh,
                            "reference": {
                                "kwh": kwh_list
                            },
                        }
                    })
            else:
                print(target_device["devname"], start_time + dt.timedelta(hours=9), end_time + dt.timedelta(hours=9), "!!!! NO SAVE !!!!", len(results))
        os.system("clear")