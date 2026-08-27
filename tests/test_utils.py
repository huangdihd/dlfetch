import unittest

from utils import CYAN, RESET, get_info_lines


class GetInfoLinesTests(unittest.TestCase):
    def test_next_class_includes_start_and_end_times(self):
        next_lesson = {
            "beginTime": "/Date(1787796000000+0800)/",
            "endTime": "/Date(1787799600000+0800)/",
            "classInfo": {"className": "Physics"},
            "playgroundName": "A403",
        }

        lines = get_info_lines(
            {"name": "2026 Fall"}, [], next_lesson, 4.0, 123
        )

        self.assertEqual(
            lines[-1],
            f"Next Class: {CYAN}Physics (10:00-11:00) in A403{RESET}",
        )

    def test_next_class_without_location_still_includes_times(self):
        next_lesson = {
            "beginTime": "2026-08-27T08:00:00",
            "endTime": "2026-08-27T08:45:00",
            "classInfo": {"className": "Math"},
        }

        lines = get_info_lines(
            {"name": "2026 Fall"}, [], next_lesson, 4.0, 123
        )

        self.assertEqual(lines[-1], f"Next Class: {CYAN}Math (08:00-08:45){RESET}")


if __name__ == "__main__":
    unittest.main()
