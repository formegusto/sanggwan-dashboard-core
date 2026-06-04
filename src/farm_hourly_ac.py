import argparse
import datetime as dt
import os

from db import get_local

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

    fhacm_col = db["FarmHourlyActivePowerMain"]
    fhacs_col = db["FarmHourlyActivePowerSub"]
    dhacs_col = db["DeviceHourlyActivePower"]

    for target_date in dates:
        for h in range(24):
            main_acs = []
            sub_acs = [] 
            start_time = target_date - dt.timedelta(hours=9) + dt.timedelta(hours=h)
            end_time = start_time + dt.timedelta(hours=1)
            for main_dev in main_devs:
                result = dhacs_col.find_one({
                    "$and": [
                        {
                            "devid": main_dev["devid"],
                        },
                        {
                            "model": main_dev["model"]
                        },
                        {
                            "createdAt": start_time
                        }
                    ]
                })
                if result is not None:
                    main_acs.append(result)
            main_total_kwh_list = [ac["kwh"] for ac in main_acs]
            main_total_kwh = sum(main_total_kwh_list)
                
            for sub_dev in sub_devs:
                result = dhacs_col.find_one({
                    "$and": [
                        {
                            "devid": sub_dev["devid"],
                        },
                        {
                            "model": sub_dev["model"]
                        },
                        {
                            "createdAt": start_time
                        }
                    ]
                })
                if result is not None:            
                    sub_acs.append(result)
            sub_total_kwh_list = [ac["kwh"] for ac in sub_acs]
            sub_total_kwh = sum(sub_total_kwh_list)
            
            rcvtime = (start_time + dt.timedelta(hours=9)).strftime("%Y%m%d%H%M%S")
            ex = fhacm_col.find_one({
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
                fhacm_col.insert_one({
                    "farmid": yj["farmid"],
                    "farmDocument": yj["_id"],
                    "kwh": main_total_kwh, ## 전체합
                    "reference": {
                        "value": {
                            "main": main_total_kwh,
                            "sub": sub_total_kwh,
                        },
                        "list": {
                            "main": main_total_kwh_list,
                            "sub": sub_total_kwh_list
                        }
                    },
                    "rcvtime": rcvtime,
                    "createdAt": start_time,
                    "updatedAt": start_time
                })
            else:
                fhacm_col.update_one(
                    {
                        "_id": ex["_id"]
                    },
                    {
                        "$set": {
                            "farmid": yj["farmid"],
                            "farmDocument": yj["_id"],
                            "kwh": main_total_kwh,
                            "reference": {
                                "value": {
                                    "main": main_total_kwh,
                                    "sub": sub_total_kwh,
                                },
                                "list": {
                                    "main": main_total_kwh_list,
                                    "sub": sub_total_kwh_list
                                }
                            }
                        }
                    })
        
        os.system("clear")