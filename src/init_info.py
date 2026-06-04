import datetime as dt
from db import get_local

dev_infos = [
    {
        "farmid": "0005",
        "model": "330",
        "devid": 0,
        "devname": "메인차단기 3상 전력감시컨트롤",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 2,
        "devname": "육묘 LED 1",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 3,
        "devname": "육묘 LED 2",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 4,
        "devname": "육묘 LED 3",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 5,
        "devname": "육묘 LED 4",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 6,
        "devname": "써큘레이터 1",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 7,
        "devname": "써큘레이터 2",
        "settime": None,
    },
    {
        "farmid": "0005",
        "model": "310",
        "devid": 8,
        "devname": "회수펌프 1",
        "settime": None,
    },
]

if __name__ == "__main__":
    local = get_local()

    farm_col = local["Farm"]
    now = dt.datetime.now() - dt.timedelta(hours=9)
    farm_info = {
        "farmid": "0005",
        "name": "상관 식물공장",
        "location": "전북특별자치도 완주군 상관면",
        "createdAt": now,
        "updatedAt": now
    }
    ex = farm_col.find_one({
        "farmid": farm_info["farmid"]
    })
    if ex is None:
        farm_col.insert_one(farm_info)
    else:
        farm_col.update_one({
            "_id": ex["_id"]
        }, {
            "$set": farm_info
        })
    

    dev_col = local["Device"]
    for dev_info in dev_infos:
        ex = dev_col.find_one({
            "model": dev_info["model"],
            "devid": dev_info["devid"]
        })
        if ex is None:
            dev_col.insert_one(dev_info)
        else:
            dev_col.update_one({
                "_id": ex["_id"]
            }, {
                "$set": dev_info
            })