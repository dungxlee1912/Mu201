#!/usr/bin/env python3
"""Gọi Aviationstack lấy tình trạng MU6014 và MU201, cộng dồn vào data.json."""
import json, os, sys, urllib.request, urllib.parse, datetime

# tên hiển thị -> mã dùng để tra trên API (đổi mã bên phải nếu API trả dữ liệu dưới số hiệu khác)
FLIGHTS = {"MU6014": "MU6014", "MU201": "MU201"}
KEY = os.environ.get("AVIATIONSTACK_KEY")
if not KEY:
    sys.exit("Thiếu biến môi trường AVIATIONSTACK_KEY")

def call(code):
    q = urllib.parse.urlencode({"access_key": KEY, "flight_iata": code})
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
for name, code in FLIGHTS.items():
    try:
        res = call(code)
    except Exception as e:
        print(name, "lỗi kết nối:", e)
        continue
    if "error" in res:
        print(name, "API báo lỗi:", json.dumps(res["error"]))
        continue
    okc += 1
    d = fl.setdefault(name, {})
    for e in res.get("data", []):
        fd = e.get("flight_date")
        if fd:
            d[fd] = {"status": e.get("flight_status"), "dep": pick(e.get("departure") or {}), "arr": pick(e.get("arrival") or {})}
    print(name, ":", len(res.get("data", [])), "bản ghi")

cutoff = (datetime.date.today() - datetime.timedelta(days=120)).isoformat()
db["flights"] = {n: {k: v for k, v in d.items() if k >= cutoff} for n, d in fl.items()}
db["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=1, sort_keys=True)
if okc == 0:
    sys.exit("Không lấy được dữ liệu của chuyến nào")
