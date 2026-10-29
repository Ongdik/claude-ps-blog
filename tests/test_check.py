"""check.py 테스트. 실행: python3 -m unittest discover tests"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "ps-solution-blog"
sys.path.insert(0, str(SKILL / "scripts"))

import check  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def ids(findings, level=None):
    return {f.id for f in findings if level is None or f.level == level}


class RulesTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def test_ids_are_unique(self):
        all_ids = [r.id for r in self.rules]
        self.assertEqual(len(all_ids), len(set(all_ids)))

    def test_each_example_triggers_its_rule(self):
        """규칙 표의 예시 칸은 그 규칙에 반드시 걸려야 한다."""
        for r in self.rules:
            with self.subTest(rule=r.id):
                self.assertIsNotNone(r.pattern.search(r.example),
                                     f"{r.id} 예시가 패턴에 걸리지 않음: {r.example}")

    def test_escaped_pipe_is_alternation(self):
        row = r"| X01 | `(가\|나)` | 금지 | 가 | - |"
        self.assertEqual(check.split_row(row)[1], "`(가|나)`")


class FixtureTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def run_fixture(self, name):
        text = (FIXTURES / name).read_text(encoding="utf-8")
        return check.run(text, self.rules)

    def test_good_post_passes_strict(self):
        self.assertEqual(self.run_fixture("good.md"), [])

    def test_bad_post_hits_expected_rules(self):
        found = ids(self.run_fixture("bad.md"))
        expected = {"A01", "A03", "A07", "B01", "B03", "B04", "B07", "C01",
                    "D07", "E01", "F01", "G01", "G02", "G03", "G06", "G07",
                    "D08", "H01", "H02",
                    "S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09"}
        self.assertTrue(expected <= found, f"빠진 항목: {expected - found}")


class MaskTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def test_code_block_is_ignored(self):
        text = "# 제목\n\n```python\n# 핵심은 바로 여기!!\n```\n"
        self.assertEqual(check.run(text, self.rules), [])

    def test_inline_code_is_ignored(self):
        text = "# 제목\n\n`print('극적으로')`를 호출한다.\n"
        self.assertEqual(check.run(text, self.rules), [])

    def test_html_comment_is_ignored(self):
        text = "# 제목\n\n<!-- 이미지 삽입 위치: 🚀 -->\n"
        self.assertEqual(check.run(text, self.rules), [])

    def test_blockquote_is_ignored(self):
        text = "# 제목\n\n> 모든 정수는 2^31보다 작습니다. 매우 큰 수가 주어질 수 있다.\n"
        self.assertEqual(check.run(text, self.rules), [])

    def test_line_numbers_survive_masking(self):
        text = "# 제목\n\n```python\nx = 1\n```\n\n결론적으로 끝났다.\n"
        found = check.run(text, self.rules)
        self.assertEqual([(f.id, f.line) for f in found], [("A05", 7)])


class ReflectionTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def test_list_only_reflection_warns(self):
        text = "# 제목\n\n## 정리\n\n- 첫째다.\n- 둘째다.\n"
        self.assertIn("S07", ids(check.run(text, self.rules)))

    def test_prose_reflection_passes(self):
        text = "# 제목\n\n## 돌아보며\n\n처음엔 몰랐다.\n\n- 다음엔 set부터 본다.\n"
        self.assertNotIn("S07", ids(check.run(text, self.rules)))

    def test_other_section_list_is_fine(self):
        text = "# 제목\n\n## 문제\n\n- 조건 하나다.\n- 조건 둘이다.\n"
        self.assertNotIn("S07", ids(check.run(text, self.rules)))


class MathBlockTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def count_s08(self, text):
        return sum(1 for f in check.run(text, self.rules) if f.id == "S08")

    def test_latex_fence_warns(self):
        self.assertEqual(self.count_s08("# 제목\n\n```latex\nx = 1\n```\n"), 1)

    def test_dollar_block_warns_once(self):
        self.assertEqual(self.count_s08("# 제목\n\n$$\nx = 1\n$$\n"), 1)

    def test_inline_dollar_block_warns_once(self):
        text = "# 제목\n\n$$x = 1$$\n\n$$y = 2$$\n"
        self.assertEqual(self.count_s08(text), 2)

    def test_python_fence_is_fine(self):
        self.assertEqual(self.count_s08("# 제목\n\n```python\nx = 1\n```\n"), 0)


class TitleTest(unittest.TestCase):
    def setUp(self):
        self.rules = check.load_rules(SKILL / "banned-phrases.md")

    def test_subtitle_warns(self):
        text = "# [백준 1920] 수 찾기 - 시계 방향 회전에서 꼬인 부분\n"
        self.assertIn("S09", ids(check.run(text, self.rules)))

    def test_plain_title_passes(self):
        for title in ("# [백준 1920] 수 찾기", "# 2차원 바람", "# [SWEA 1234] A-B 게임"):
            with self.subTest(title=title):
                self.assertNotIn("S09", ids(check.run(title + "\n", self.rules)))


class ExitCodeTest(unittest.TestCase):
    def test_exit_codes(self):
        self.assertEqual(check.main([str(FIXTURES / "good.md"), "--strict"]), 0)
        self.assertEqual(check.main([str(FIXTURES / "bad.md")]), 1)
        self.assertEqual(check.main([str(FIXTURES / "없는파일.md")]), 2)


if __name__ == "__main__":
    unittest.main()
