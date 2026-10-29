#!/usr/bin/env python3
"""PS 블로그 글 발행 전 검사.

banned-phrases.md의 표에 적힌 패턴과 Markdown 구조를 검사한다.
외부 패키지 없이 Python 3.10 이상에서 동작한다 (CI에서 3.10, 3.13으로 테스트).

사용법:
    python3 check.py post.md
    python3 check.py post.md --strict      # 주의 항목도 실패로 처리
    python3 check.py post.md --json        # JSON으로 출력
    cat post.md | python3 check.py -       # 표준 입력

종료 코드:
    0  금지 항목 없음 (--strict면 주의 항목도 없음)
    1  금지 항목 발견
    2  실행 오류 (파일 없음, 규칙 파싱 실패 등)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_RULES = Path(__file__).resolve().parent.parent / "banned-phrases.md"

LEVEL_BAN = "금지"
LEVEL_WARN = "주의"


@dataclass
class Rule:
    id: str
    pattern: re.Pattern
    level: str
    example: str
    alternative: str


@dataclass
class Finding:
    id: str
    level: str
    line: int
    text: str
    message: str


# ---------------------------------------------------------------- 규칙 파싱

ROW_RE = re.compile(r"^\|\s*([A-Z]\d{2})\s*\|")


def split_row(row: str) -> list[str]:
    """표 한 줄을 칸으로 나눈다. `\\|`는 칸 구분자가 아니라 문자 `|`로 본다."""
    cells, buf, i = [], [], 0
    body = row.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def load_rules(path: Path) -> list[Rule]:
    rules = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not ROW_RE.match(line):
            continue
        cells = split_row(line)
        if len(cells) < 5:
            raise ValueError(f"{path}:{lineno}: 칸이 5개보다 적습니다")
        rid, raw, level, example, alternative = cells[:5]
        if not (raw.startswith("`") and raw.endswith("`")):
            raise ValueError(f"{path}:{lineno}: 정규식은 백틱으로 감싸야 합니다")
        if level not in (LEVEL_BAN, LEVEL_WARN):
            raise ValueError(f"{path}:{lineno}: 수준은 금지 또는 주의여야 합니다")
        try:
            pattern = re.compile(raw[1:-1])
        except re.error as e:
            raise ValueError(f"{path}:{lineno}: 정규식 오류 ({e})") from e
        rules.append(Rule(rid, pattern, level, example, alternative))
    if not rules:
        raise ValueError(f"{path}: 규칙을 하나도 찾지 못했습니다")
    return rules


# ---------------------------------------------------------- 본문 전처리

FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def blank(s: str) -> str:
    return re.sub(r"[^\n]", " ", s)


def mask(text: str) -> tuple[list[str], list[tuple[int, str]]]:
    """코드 블록, 인라인 코드, HTML 주석, 인용(>) 줄을 공백으로 바꾼다.

    인용은 다른 사람의 글처럼 사용자가 쓰지 않은 글을 넣는 자리라 검사하지 않는다.

    줄 번호를 유지하기 위해 줄 수는 그대로 둔다.
    반환값: (가린 줄 목록, [(코드 블록 시작 줄, 언어 태그)])
    """
    text = HTML_COMMENT_RE.sub(lambda m: blank(m.group(0)), text)
    lines = text.splitlines()
    out, fences = [], []
    fence = None
    for i, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if fence is None and m:
            fence = m.group(2)[0] * len(m.group(2))
            fences.append((i, m.group(3).strip()))
            out.append("")
            continue
        if fence is not None:
            if m and m.group(2).startswith(fence) and not m.group(3).strip():
                fence = None
            out.append("")
            continue
        if line.lstrip().startswith(">"):
            out.append("")
            continue
        out.append(INLINE_CODE_RE.sub(lambda mm: blank(mm.group(0)), line))
    return out, fences


# ---------------------------------------------------------------- 검사

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BOLD_RE = re.compile(r"\*\*[^*\n]+?\*\*")
LIST_RE = re.compile(r"^([-*+]|\d+[.)])\s")
REFLECTION_RE = re.compile(r"정리|돌아보|회고|느낀 ?점")
MATH_LANGS = {"latex", "math", "tex", "katex"}
SUBTITLE_RE = re.compile(r"\s[-–—:|]\s")
FORMAL_END_RE = re.compile(r"니다[.!?](\s|$)")
PLAIN_END_RE = re.compile(r"(?<!니)다[.!?](\s|$)")
POLITE_END_RE = re.compile(r"(?<!까)(?<=[가-힣])요[.!?](\s|$)")  # "~까요?"는 합니다체 글에서도 쓰여 제외


def is_prose(line: str) -> bool:
    s = line.strip()
    return bool(s) and not s.startswith(("#", "|", ">"))


def check_patterns(lines: list[str], rules: list[Rule]) -> list[Finding]:
    found = []
    for i, line in enumerate(lines, 1):
        for r in rules:
            for m in r.pattern.finditer(line):
                found.append(Finding(r.id, r.level, i, m.group(0),
                                     f"예: {r.example} → {r.alternative}"))
    return found


def check_structure(lines: list[str], fences: list[tuple[int, str]]) -> list[Finding]:
    found = []

    for lineno, lang in fences:
        if not lang:
            found.append(Finding("S01", LEVEL_BAN, lineno, "```",
                                 "코드 블록에 언어 태그를 붙인다 (예: ```python)"))
        elif lang.lower() in MATH_LANGS:
            found.append(Finding("S08", LEVEL_WARN, lineno, "```" + lang,
                                 "수식 유도는 빼고, 필요하면 결론만 문장으로 쓴다"))
    in_math = False
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s.startswith("$$"):
            continue
        if not in_math:
            found.append(Finding("S08", LEVEL_WARN, i, "$$",
                                 "수식 유도는 빼고, 필요하면 결론만 문장으로 쓴다"))
        # 한 줄짜리 $$...$$는 열고 닫음이 같은 줄에 있다
        if not (len(s) > 2 and s.endswith("$$") and s != "$$"):
            in_math = not in_math

    headings = [(i, len(m.group(1)), m.group(2))
                for i, l in enumerate(lines, 1) if (m := HEADING_RE.match(l))]
    h1 = [h for h in headings if h[1] == 1]
    if len(h1) != 1:
        line = h1[1][0] if len(h1) > 1 else 1
        found.append(Finding("S02", LEVEL_BAN, line, f"# 제목 {len(h1)}개",
                             "# 제목은 글 맨 위에 하나만 둔다"))
    if h1 and SUBTITLE_RE.search(h1[0][2]):
        found.append(Finding("S09", LEVEL_WARN, h1[0][0], h1[0][2],
                             "제목에는 [플랫폼 번호] 문제 이름만 쓴다. 막힌 내용은 돌아보며에 쓴다"))

    prev = 0
    for i, level, title in headings:
        if prev and level > prev + 1:
            found.append(Finding("S03", LEVEL_WARN, i, "#" * level + " " + title,
                                 f"제목 단계가 {prev}단계에서 {level}단계로 건너뛰었다"))
        prev = level
        if title.rstrip().endswith("?"):
            found.append(Finding("S06", LEVEL_WARN, i, title,
                                 "소제목을 질문이 아니라 내용을 나타내는 말로 쓴다"))

    for idx, (i, level, title) in enumerate(headings):
        if level != 2 or not REFLECTION_RE.search(title):
            continue
        end = next((h[0] for h in headings[idx + 1:] if h[1] <= 2), len(lines) + 1)
        body = [l.strip() for l in lines[i:end - 1] if l.strip()]
        items = [l for l in body if LIST_RE.match(l)]
        if len(items) >= 2 and len(items) == len(body):
            found.append(Finding("S07", LEVEL_WARN, i, title,
                                 "정리를 목록 대신 사용자 목소리의 짧은 문단으로 쓴다"))

    para, start = [], 0
    for i, line in enumerate(lines + [""], 1):
        if line.strip():
            if not para:
                start = i
            para.append(line)
            continue
        if para:
            n = len(BOLD_RE.findall("\n".join(para)))
            if n >= 3:
                found.append(Finding("S05", LEVEL_WARN, start, f"굵은 글씨 {n}개",
                                     "한 문단의 굵은 글씨는 2개 이하로 줄인다"))
        para = []

    prose = "\n".join(l for l in lines if is_prose(l))
    counts = {
        "합니다체": len(FORMAL_END_RE.findall(prose)),
        "한다체": len(PLAIN_END_RE.findall(prose)),
        "해요체": len(POLITE_END_RE.findall(prose)),
    }
    total = sum(counts.values())
    used = {k: v for k, v in counts.items() if v}
    if len(used) > 1 and total >= 5:
        others = total - max(used.values())
        if others >= 2 and others / total >= 0.15:
            desc = ", ".join(f"{k} {v}문장" for k, v in used.items())
            found.append(Finding("S04", LEVEL_WARN, 0, desc,
                                 "한 글 안에서는 문체를 하나로 통일한다"))
    return found


def run(text: str, rules: list[Rule]) -> list[Finding]:
    lines, fences = mask(text)
    found = check_patterns(lines, rules) + check_structure(lines, fences)
    return sorted(found, key=lambda f: (f.level != LEVEL_BAN, f.line, f.id))


# ---------------------------------------------------------------- 출력

def report(findings: list[Finding], name: str) -> str:
    bans = [f for f in findings if f.level == LEVEL_BAN]
    warns = [f for f in findings if f.level == LEVEL_WARN]
    out = [f"검사 대상: {name}",
           f"결과: 금지 {len(bans)}건, 주의 {len(warns)}건", ""]
    for title, group in (("[금지]", bans), ("[주의]", warns)):
        if not group:
            continue
        out.append(title)
        for f in group:
            where = f"{f.line}행" if f.line else "전체"
            out.append(f"  {f.id} {where}: {f.text}")
            out.append(f"      {f.message}")
        out.append("")
    if not findings:
        out.append("걸린 항목이 없습니다.")
    return "\n".join(out).rstrip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PS 블로그 글 발행 전 검사")
    ap.add_argument("file", help="검사할 Markdown 파일, 표준 입력은 -")
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES,
                    help="규칙 파일 경로 (기본: banned-phrases.md)")
    ap.add_argument("--strict", action="store_true", help="주의 항목도 실패로 처리")
    ap.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = ap.parse_args(argv)

    try:
        rules = load_rules(args.rules)
        if args.file == "-":
            text, name = sys.stdin.read(), "표준 입력"
        else:
            text, name = Path(args.file).read_text(encoding="utf-8"), args.file
    except (OSError, ValueError) as e:
        print(f"오류: {e}", file=sys.stderr)
        return 2

    findings = run(text, rules)
    if args.json:
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        print(report(findings, name))

    failed = any(f.level == LEVEL_BAN for f in findings)
    if args.strict:
        failed = failed or bool(findings)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
