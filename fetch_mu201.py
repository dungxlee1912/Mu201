#!/usr/bin/env python3
"""Gọi Aviationstack lấy tình trạng MU6014 và MU201, cộng dồn vào data.json."""
import json, os, sys, urllib.request, urllib.parse, datetime

# tên hiển thị -> danh sách cách tra (thử lần lượt, cách nào có dữ liệu sẽ được nhớ lại)
FLIGHTS = {
    "MU6014": [("flight_iata", "MU6014"), ("flight_icao", "CES6014")],
    "MU201": [("flight_iata", "MU201")],
}
KEY = os.environ.get("AVIATIONSTACK_KEY")
if not KEY:
    sys.exit("Thiếu biến môi trường AVIATIONSTACK_KEY")

def call(param, code):
    q = urllib.parse.urlencode({"access_key": KEY, param: code})
    err = None
    for scheme in ("https", "http"):  # gói miễn phí có thể chỉ hỗ trợ HTTP
        try:
            with urllib.request.urlopen(f"{scheme}://api.aviationstack.com/v1/flights?{q}", timeout=30) as r:
                return json.load(r)
        except Exception as e:
            err = e
    raise err

def pick(side):
    return {k: side.get(k) for k in ("airport", "iata", "terminal", "gate", "scheduled", "estimated", "actual", "delay")}

try:
    with open("data.json", encoding="utf-8") as f:
        db = json.load(f)
except Exception:
    db = {}
fl = db.get("flights", {})
if fl and all(k[:2] == "20" for k in fl):  # dữ liệu cũ (chỉ MU201) -> chuyển sang cấu trúc mới
    fl = {"MU201": fl}

okc = 0
use = db.get("use", {})
for name, methods in FLIGHTS.items():
    order = sorted(methods, key=lambda m: m[0] != use.get(name))  # cách đã thành công đứng trước
    got = None
    for param, code in order:
        try:
            res = call(param, code)
        except Exception as e:
            print(name, param, code, "lỗi kết nối:", e)
            continue
        if "error" in res:
            print(name, "API báo lỗi:", json.dumps(res["error"]))
            break
        if res.get("data"):
            got = (param, res)
            break
        print(name, param, code, ": không có dữ liệu")
    if not got:
        continue
    okc += 1
    use[name] = got[0]
    d = fl.setdefault(name, {})
    for e in got[1]["data"]:
        fd = e.get("flight_date")
        if fd:
            d[fd] = {"status": e.get("flight_status"), "dep": pick(e.get("departure") or {}), "arr": pick(e.get("arrival") or {})}
    print(name, ":", len(got[1]["data"]), "bản ghi (cách tra:", got[0] + ")")

cutoff = (datetime.date.today() - datetime.timedelta(days=120)).isoformat()
db["flights"] = {n: {k: v for k, v in d.items() if k >= cutoff} for n, d in fl.items()}
db["use"] = use
db["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=1, sort_keys=True)
if okc == 0:
    sys.exit("Không lấy được dữ liệu của chuyến nào")
