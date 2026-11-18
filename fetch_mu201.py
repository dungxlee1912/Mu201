#!/usr/bin/env python3
"""Gọi Aviationstack lấy tình trạng MU201 và cộng dồn vào data.json."""
import json, os, sys, urllib.request, urllib.parse, datetime

FLIGHT = "MU201"
KEY = os.environ.get("AVIATIONSTACK_KEY")
if not KEY:
    sys.exit("Thiếu biến môi trường AVIATIONSTACK_KEY")

def call(scheme):
    q = urllib.parse.urlencode({"access_key": KEY, "flight_iata": FLIGHT})
    with urllib.request.urlopen(f"{scheme}://api.aviationstack.com/v1/flights?{q}", timeout=30) as r:
        return json.load(r)

# Gói miễn phí có thể chỉ hỗ trợ HTTP, nên thử HTTPS trước rồi mới tới HTTP
try:
    res = call("https")
except Exception:
    res = call("http")

if "error" in res:
    sys.exit("API báo lỗi: " + json.dumps(res["error"]))

try:
    with open("data.json", encoding="utf-8") as f:
        db = json.load(f)
except Exception:
    db = {"flights": {}}

def pick(side):
    return {k: side.get(k) for k in ("airport", "iata", "terminal", "gate", "scheduled", "estimated", "actual", "delay")}

for e in res.get("data", []):
    d = e.get("flight_date")
    if not d:
        continue
    db["flights"][d] = {
        "status": e.get("flight_status"),
        "dep": pick(e.get("departure") or {}),
        "arr": pick(e.get("arrival") or {}),
    }

# Chỉ giữ 120 ngày gần nhất
cutoff = (datetime.date.today() - datetime.timedelta(days=120)).isoformat()
db["flights"] = {k: v for k, v in db["flights"].items() if k >= cutoff}
db["updated"] = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=1, sort_keys=True)
print("Đã lưu", len(res.get("data", [])), "bản ghi")
