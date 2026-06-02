import argparse
import datetime as dt

from decimal import Decimal
from db import get_local, get_remote

def result_to_document(row):
    r = {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}
    now = dt.datetime.strptime(r["rcvtime"], "%Y%m%d%H%M%S") - dt.timedelta(hours=9)
    r["createdAt"] = now
    r["updatedAt"] = now
    
    return r

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--dev")
    args = parser.parse_args()

    if args.start is None:
        start = dt.datetime.strptime((dt.datetime.now() - dt.timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    else:
        start = dt.datetime.strptime(args.start, "%Y-%m-%d")
    start_rcvtime = start.strftime("%Y%m%d%H%M%S")

    end = (start if args.end is None else dt.datetime.strptime(args.end, "%Y-%m-%d")) + dt.timedelta(days=1)
    end_rcvtime = end.strftime("%Y%m%d%H%M%S")

    dev = args.dev
    if not (dev == "Mpm310" or dev == "Mpm330"):
        exit(0)

    remote_conn = get_remote()
    sql = f'SELECT * FROM {dev} WHERE farmid = "0003" AND rcvtime >= "{start_rcvtime}" AND rcvtime < "{end_rcvtime}" ORDER BY rcvtime ASC;'
    print(sql)
    with remote_conn.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()

    inserted = [
        result_to_document(r)
        for r in results
    ]
    local_conn = get_local()
    dev_col = local_conn[dev]
    dev_col.insert_many(inserted)