#! python3
# -*- coding: utf-8 -*-
import ast
import os
import re
import datetime
import requests
from SignIn import sign_in
from sys import exit


def parse_date_string(date_str):
    match = re.search(r'/Date\((\d+)([+-]\d{4})?\)/', date_str)
    if not match:
        match = re.match(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', date_str)
        if not match:
            return None
        year, month, day, hour, minute, second = map(int, match.groups())
        return datetime.datetime(year, month, day, hour, minute, second)
    timestamp_ms = int(match.group(1))
    tz_str = match.group(2) or '+0000'
    sign = 1 if tz_str[0] == '+' else -1
    hours = int(tz_str[1:3])
    minutes = int(tz_str[3:5])
    tz_offset = datetime.timedelta(hours=sign * hours, minutes=sign * minutes)
    tzinfo = datetime.timezone(tz_offset)
    dt_utc = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.timezone.utc)
    return dt_utc.astimezone(tzinfo)


# 🎟️ Cookie 加载
cookie_path = os.path.expanduser("~/.dlfetch_cookies")
cookies = []
print("Loading cookies...")

if os.path.exists(cookie_path):
    try:
        with open(cookie_path) as cookie_file:
            cookies = ast.literal_eval(cookie_file.read())
    except SyntaxError:
        cookies = []
    if type(cookies) != list:
        open(cookie_path, "w").close()
        cookies = []

if not cookies:
    print("Cookies are empty! Trying to sign in...")
    cookies = sign_in(cookie_path)

cookies_dict = {cookie["name"]: cookie["value"] for cookie in cookies}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://thisdlstu.schoolis.cn/",
}

# 🏫 获取学期
semesters = requests.get(
    "https://thisdlstu.schoolis.cn/api/School/GetSchoolSemesters",
    headers=headers,
    cookies=cookies_dict
).json().get("data")

if not semesters:
    print("Identification information is expired!")
    open(cookie_path, "w").close()
    print("Please run the script again.")
    exit(1)

current_semester = next(s for s in semesters if s["isNow"])
current_semester_id = current_semester["id"]

# 📚 获取任务
def fetch_task(page):
    return requests.get(
        f"https://thisdlstu.schoolis.cn/api/LearningTask/GetList?semesterId={current_semester_id}&pageIndex={page}&pageSize=1",
        headers=headers,
        cookies=cookies_dict
    ).json()["data"]

first_task = fetch_task(1)
total_task_count = first_task["totalCount"]
tasks = [fetch_task(i)["list"][0] for i in range(1, total_task_count + 1)]
unfinished = [t for t in tasks if not t["finishState"]]

# 🎓 获取 GPA
realtime_GPA = requests.get(
    f"https://thisdlstu.schoolis.cn/api/DynamicScore/GetGpa?semesterId={current_semester_id}",
    headers=headers,
    cookies=cookies_dict
).json()["data"]

# 📅 获取课程表
schedule = requests.post(
    "https://thisdlstu.schoolis.cn/api/Schedule/ListScheduleByParent",
    headers=headers,
    cookies=cookies_dict,
    json={
        "beginTime": str(datetime.date.today()),
        "endTime": str(datetime.date.today()),
    }
).json()["data"]


future_lessons = sorted(
    [l for l in schedule if parse_date_string(l["beginTime"]) >= datetime.datetime.now(tz=parse_date_string(l["beginTime"]).tzinfo)],
    key=lambda l: parse_date_string(l["beginTime"])
)
next_lesson = future_lessons[0] if future_lessons else None

# 🎨 ANSI 颜色定义
BLUE = "\033[1;34m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
RESET = "\033[0m"

# 🐱 左侧 logo（可改）
logo = [
    "   /\\_/\\  ",
    "  ( o.o ) ",
    "   > ^ <  "
]

# 📋 右侧信息内容
info_lines = [
    f"🏫  {BLUE}THISDL Student Info{RESET}",
    f"{'-'*28}",
    f"Semester  : {current_semester['name']} ({current_semester_id})",
    f"GPA       : {GREEN}{realtime_GPA}{RESET}",
    f"Tasks     : {YELLOW}{len(unfinished)} not handed in{RESET}",
    f"Next Class: {CYAN}{next_lesson['classInfo']['className']} in {next_lesson['playgroundName']}{RESET}" if next_lesson else f"Next Class: {CYAN}None today{RESET}"
]

# 🧩 Neofetch 风格输出
max_lines = max(len(logo), len(info_lines))
for i in range(max_lines):
    left = logo[i] if i < len(logo) else " " * 9
    right = info_lines[i] if i < len(info_lines) else ""
    print(f"{left:<10}  {right}")
