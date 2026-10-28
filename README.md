# claude-ps-blog

알고리즘 풀이(PS)를 티스토리용 한국어 기술 블로그 글로 정리하는 Claude 스킬이다.

[![test](https://github.com/Ongdik/claude-ps-blog/actions/workflows/test.yml/badge.svg)](https://github.com/Ongdik/claude-ps-blog/actions/workflows/test.yml)
![license](https://img.shields.io/badge/license-MIT-blue)

AI에게 풀이 글을 맡기면 비슷한 말투가 나온다. "~에 대해 알아보겠습니다"로 시작하고, "핵심은 바로"로 강조하고, "도움이 되었으면 좋겠습니다"로 끝난다. 하지 않은 시행착오를 지어내거나, 정렬 비용을 빼먹은 복잡도를 쓰기도 한다.

이 스킬은 두 가지를 막는다.

1. **내용**: 사용자가 말하지 않은 경험, 확인되지 않은 측정값, 근거 없는 복잡도를 쓰지 않는다.
2. **문체**: 한국어 AI 글에서 자주 보이는 표현을 목록으로 관리하고, 발행 전에 스크립트로 검사한다.

## 차이 예시

백준 1920 「수 찾기」 도입부.

**스킬 없이**

> 안녕하세요! 오늘은 백준 1920번 '수 찾기' 문제에 대해 알아보겠습니다. 이 문제는 단순한 탐색 문제가 아니라 효율적인 알고리즘의 중요성을 보여주는 문제라고 할 수 있습니다. 과연 어떻게 풀 수 있을까요? 핵심은 바로 이분 탐색입니다!

**스킬 적용**

> N개의 정수가 주어지고, 다음으로 주어지는 M개의 수가 각각 그 안에 있는지 확인하는 문제다. N과 M이 모두 최대 100,000이라서, 수 하나를 찾을 때마다 배열 전체를 훑으면 최악의 경우 10^10번 비교한다. 탐색 한 번의 비용을 O(N)보다 줄여야 한다.

첫 번째는 네 문장을 쓰고도 문제가 무엇인지 말하지 않는다. 두 번째는 첫 문장에서 문제를 설명하고, 입력 제한에서 풀이 방향을 끌어낸다.

## 구성

```text
skills/ps-solution-blog/
├── SKILL.md            글 구성, 원칙, 문체 규칙, 발행 전 검사 절차
├── banned-phrases.md   금지·주의 표현 목록 (검사 스크립트가 이 표를 읽음)
├── voice-exemplars.md  나쁜 예 / 좋은 예 비교
└── scripts/check.py    발행 전 기계 검사
```

| 파일 | 내용 |
|---|---|
| `SKILL.md` | 경험을 지어내지 않는 원칙, 문제 소개부터 정리까지의 글 구성, 문체 규칙, 4단계 발행 전 검사 (기계 검사, 의미 검사 9항목, 새로 읽기, 채팅 보고) |
| `banned-phrases.md` | 도입·마무리 상투구, 과장, 반전·수사, 메타 서술·번역투, 자기비하, 형식 6개 분류. 항목마다 `금지` / `주의` 수준과 대안 |
| `voice-exemplars.md` | 제목, 도입, 접근 과정, 복잡도, 최적화, 정리, 자기비하를 같은 문제로 비교 |
| `scripts/check.py` | 표현 패턴 검사와 구조 검사 (코드 블록 언어 태그, 제목 개수·단계, 문체 혼용, 굵은 글씨 과다, 질문형 소제목). 코드 블록 안은 검사하지 않음 |

## 설치

### claude.ai (채팅, Claude 문서)

1. [Releases](https://github.com/Ongdik/claude-ps-blog/releases)에서 `ps-solution-blog.zip`을 받는다.
2. claude.ai의 스킬 설정에서 zip을 업로드한다. 같은 이름의 스킬이 있으면 교체한다.

Release가 아직 없으면 직접 묶는다.

```bash
cd skills && zip -r ../ps-solution-blog.zip ps-solution-blog -x '*/__pycache__/*'
```

### Claude Code (플러그인)

```text
/plugin marketplace add Ongdik/claude-ps-blog
/plugin install ps-solution-blog@claude-ps-blog
```

### Claude Code (심볼릭 링크)

```bash
git clone https://github.com/Ongdik/claude-ps-blog.git
ln -s "$(pwd)/claude-ps-blog/skills/ps-solution-blog" ~/.claude/skills/ps-solution-blog
```

## 사용

문제와 코드를 주고 평소 말로 요청한다.

- "백준 1920 풀었어. 이 코드로 블로그 글 써줘."
- "처음엔 이중 반복문으로 했다가 시간 초과 났고, 정렬하고 이분 탐색으로 바꿨어. 두 코드 다 줄게."
- "이 글 발행 전에 검사해줘."

claude.ai에서는 Claude 문서로, Claude Code에서는 Markdown 파일로 결과가 나온다. 검사 결과는 본문이 아니라 채팅에 보고된다. 티스토리에는 문서를 Markdown으로 내보내 붙여 넣는다.

### 검사 스크립트만 쓰기

Python 3.10 이상, 외부 패키지 없음.

```bash
python3 skills/ps-solution-blog/scripts/check.py 글.md
python3 skills/ps-solution-blog/scripts/check.py 글.md --strict   # 주의 항목도 실패 처리
python3 skills/ps-solution-blog/scripts/check.py 글.md --json
```

```text
검사 대상: 글.md
결과: 금지 2건, 주의 1건

[금지]
  A01 3행: 알아보겠습니다
      예: 이분 탐색에 대해 알아보겠습니다 → 바로 본론을 쓴다
  S01 11행: ```
      코드 블록에 언어 태그를 붙인다 (예: ```python)

[주의]
  D03 5행: 라고 할 수 있습니다
      예: 핵심 아이디어라고 할 수 있습니다 → 핵심 아이디어다
```

종료 코드는 0(통과), 1(금지 발견), 2(실행 오류)다.

## 기여

오탐·미탐, 새 금지 표현, 스킬 동작 개선은 [이슈 템플릿](https://github.com/Ongdik/claude-ps-blog/issues/new/choose)으로 남긴다. 커밋 규칙과 규칙 추가 방법은 [CONTRIBUTING.md](CONTRIBUTING.md)에 있다.

## 참고

규칙 파일과 예시 파일을 나누고, 금지 표현을 기계적으로 검사하는 구조는 [sjmoran/claude-blog-prose](https://github.com/sjmoran/claude-blog-prose)를 참고했다. 규칙 내용은 한국어 PS 글에 맞춰 새로 작성했다.

## 라이선스

[MIT](LICENSE)
