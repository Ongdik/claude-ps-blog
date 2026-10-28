# claude-ps-blog

알고리즘 풀이(PS)를 티스토리용 한국어 기술 블로그 글로 정리하는 Claude 스킬이다.

[![test](https://github.com/Ongdik/claude-ps-blog/actions/workflows/test.yml/badge.svg)](https://github.com/Ongdik/claude-ps-blog/actions/workflows/test.yml)
![license](https://img.shields.io/badge/license-MIT-blue)

AI에게 풀이 글을 맡기면 비슷한 글이 나온다. "~에 대해 알아보겠습니다"로 시작하고, 정답 코드를 해설서처럼 설명하고, "자료구조 선택의 중요성을 깨달을 수 있었다" 같은 목록으로 끝난다. 정작 내가 어디서 막혔고 무엇을 알게 돼서 풀었는지는 빠진다.

이 스킬은 글을 **내 생각의 흐름**대로, 짧게 쓴다.

1. **흐름**: 처음 생각한 방법 → 막힌 지점 → 물어보고 알게 된 것 → 적용해 본 것 → 돌아보며. GPT나 Claude에 물어본 대화 기록을 주면, 질문 하나하나를 막힌 지점으로 읽고 그 순서대로 글을 쓴다.
2. **깊이**: 내가 이해한 만큼만 쓴다. AI 답변의 계산 과정이나 수식은 옮기지 않고, 아직 모르는 건 "추후 알아보려고 한다"로 남긴다. 번호 목록이나 `->` 같은 메모 형태도 그대로 살린다.
3. **내용**: 말하지 않은 경험, 막힘, 감정, 측정값을 지어내지 않는다.
4. **문체**: 한국어 AI 글에서 자주 보이는 표현을 목록으로 관리하고, 발행 전에 스크립트로 검사한다.

## 차이 예시

백준 1920 「수 찾기」. 리스트 `in`으로 풀었다가 시간 초과, 왜 느린지 물어보고 `set`으로 바꿔 통과한 경우.

**스킬 없이**

> ## 시간 초과의 원인 분석
> 리스트의 in 연산은 선형 탐색으로 동작하므로 O(N)의 시간이 소요됩니다. 따라서 해시 기반 자료구조인 set을 활용하여 개선할 필요가 있다고 판단했습니다.
>
> ## 정리
> - 자료구조 선택의 중요성을 깨달을 수 있었다.
> - 좋은 계기가 되었다.

**스킬 적용**

> ## in 한 줄이 왜 느린지 몰랐던 부분
> 코드에 반복문이 하나밖에 없어서 왜 느린지 감이 안 왔다. 그래서 `in`이 내부에서 어떻게 동작하는지 물어봤다. 리스트에서 `in`은 앞에서부터 하나씩 비교한다고 한다. 결국 눈에 보이는 반복문은 하나지만, `in` 안에 반복문이 하나 더 숨어 있었던 거다.
>
> ## 돌아보며
> 리스트 `in`이 느리다는 얘기는 어디서 들어본 것 같은데, 막상 코드를 쓸 때는 전혀 떠오르지 않았다. 다음부터는 같은 자료에서 여러 번 찾는 코드가 보이면 `in` 앞에 있는 게 리스트인지 먼저 확인해 볼 생각이다.

첫 번째는 AI 답변을 옮긴 해설이고, 어떤 문제에 붙여도 말이 되는 정리로 끝난다. 두 번째는 무엇을 몰랐는지에서 출발하고, 이 문제에서만 나올 수 있는 말로 끝난다.

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
| `SKILL.md` | 대화 기록에서 막힌 지점을 뽑는 방법, 처음 생각 → 막힘 → 알게 된 것 → 적용 → 돌아보며 글 구성, 사용자가 이해한 깊이만큼 쓰는 기준, 발행 전 검사 (기계 검사, 의미 검사 5항목, 채팅 보고) |
| `banned-phrases.md` | 도입·마무리 상투구, 과장, 반전·수사, 메타 서술·번역투("판단했다" 포함), 자기비하, 정리·회고 상투구, 과한 설명(계산 과정·연산량), 형식 8개 분류. 항목마다 `금지` / `주의` 수준과 대안 |
| `voice-exemplars.md` | 글 깊이(6중 for문 예시), 그리고 같은 질문 기록을 바탕으로 제목, 처음 생각, 막힌 지점, 적용, 돌아보며, "판단했다", 자기비하를 비교 |
| `scripts/check.py` | 표현 패턴 검사와 구조 검사 (코드 블록 언어 태그, 제목 개수·단계, 문체 혼용, 굵은 글씨 과다, 질문형 소제목, 목록으로만 된 정리, 수식 블록). 코드 블록 안은 검사하지 않음 |

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

문제와 코드, 그리고 막혔을 때 물어본 대화 기록을 같이 주면 가장 내 글처럼 나온다. 대화 기록이 없으면 어디서 막혔는지 몇 줄만 적어도 된다.

- "백준 1920 풀었어. 처음 코드랑 최종 코드, GPT한테 물어본 거 붙여줄게. 블로그 글 써줘."
- "처음엔 리스트 in으로 했다가 시간 초과 났고, 왜 느린지 물어보니까 하나씩 비교한대서 set으로 바꿨어."
- "이 글 발행 전에 검사해줘."

코드만 주면 어디서 막혔는지 한 번 물어본다.

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
