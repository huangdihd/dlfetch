import datetime
import re

from constants import BLUE, RESET, GREEN, YELLOW, CYAN


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

def get_info_lines(current_semester, unfinished, next_lesson, realtime_GPA, current_semester_id):
    if next_lesson:
        begin = parse_date_string(next_lesson["beginTime"])
        end = parse_date_string(next_lesson["endTime"])
        time_range = (
            f"{begin.strftime('%H:%M')}-{end.strftime('%H:%M')}"
            if begin and end else "time unavailable"
        )
        class_name = next_lesson.get("classInfo", {}).get("className", "Unknown")
        location = next_lesson.get("playgroundName", "")
        next_class_line = f"Next Class: {CYAN}{class_name} ({time_range})"
        if location:
            next_class_line += f" in {location}"
        next_class_line += RESET
    else:
        next_class_line = f"Next Class: {CYAN}None today{RESET}"

    # 📋 右侧信息内容
    info_lines = [
        f"🏫  {BLUE}THISDL Student Info{RESET}",
        f"{'-' * 28}",
        f"Semester  : {current_semester['name']} ({current_semester_id})",
        f"GPA       : {GREEN}{realtime_GPA}{RESET}",
        f"Tasks     : {YELLOW}{len(unfinished)} not handed in(in last 12 tasks){RESET}",
        next_class_line
    ]
    return info_lines
