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
    yj = db["Farm"].find_one({
        "farmid": "0005"
    })

    # fhacs_col = db["FarmHourlyActivePowerSub"]
    fhacm_col = db["FarmHourlyActivePowerMain"]
    fdacm_col = db["FarmDailyActivePowerMain"]
    # fdacs_col = db["FarmDailyActivePowerSub"]

    for target_date in dates:
        start_time = target_date - dt.timedelta(hours=9)
        end_time = start_time + dt.timedelta(days=1)
        
        results = list(fhacm_col.find({
            "$and": [
                {
                    "createdAt": {
                        "$gte": start_time
                    }
                },
                {
                    "createdAt": {
                        "$lt": end_time
                    }
                }
            ]
        }))
        
        main_acs = [r["reference"]["value"]["main"] for r in results]
        sub_acs = [r["reference"]["value"]["sub"] for r in results] 
        
        main_total = sum(main_acs)
        sub_total = sum(sub_acs)
        
        rcvtime = (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S")
        ex = fdacm_col.find_one({
                "$and": [
                    {
                        "farmid": yj["farmid"],
                    },
                    {
                        "rcvtime": rcvtime
                    }
                ]
            })
        if ex is None:
            fdacm_col.insert_one({
                "farmid": yj["farmid"],
                "farmDocument": yj["_id"],
                "kwh": main_total,
                "reference": {
                    "value": {
                        "main": main_total,
                        "sub": sub_total,
                    },
                    "list": {
                        "main": main_acs,
                        "sub": sub_acs
                    }
                },
                "rcvtime": rcvtime,
                "createdAt": start_time,
                "updatedAt": start_time
            })
        else:
            fdacm_col.update_one(
                {
                    "_id": ex["_id"]
                },
                {
                    "$set": {
                        "farmid": yj["farmid"],
                        "farmDocument": yj["_id"],
                        "kwh": main_total,
                        "reference": {
                            "value": {
                                "main": main_total,
                                "sub": sub_total,
                            },
                            "list": {
                                "main": main_acs,
                                "sub": sub_acs
                            }
                        }    
                    }
                })