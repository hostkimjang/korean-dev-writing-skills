# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 문장과 문단을 다듬습니다.

대상 문서는 README, PR 설명, 버그 리포트, 아키텍처 문서, 운영 절차, ADR, API 안내, 기술 글입니다. 표현 교정과 새 문서 작성을 구분하며, 제공되지 않은 기능·수치·일정으로 빈칸을 채우지 않습니다.

## 먼저 확인하기

- 스킬 본문: [SKILL.md](skills/korean-dev-writing/SKILL.md)
- 문장 교정과 유지 예시: [before-after-guide.md](skills/korean-dev-writing/references/before-after-guide.md)
- 문서 종류별 구성: [document-types.md](skills/korean-dev-writing/references/document-types.md)
- 미적용·기존본·개선본 비교: [비교 보고서](docs/evaluation.md)
- 참고한 글쓰기 원칙과 출처: [sources.md](docs/sources.md)

## 작성 원칙

문장을 짧게 만드는 것보다 원래 의미를 지키는 일을 우선합니다. `수 있다`가 가능성을, `기본적으로`가 기본값을 나타내면 유지합니다. 확인한 버전과 지원 범위, 가설과 확인된 원인, 테스트 계획과 실행 결과를 구분합니다.

문서는 독자의 목적에 맞춰 구성합니다. 설명과 인과관계는 문단으로 연결하고, 실행 순서는 번호로, 병렬 항목은 목록으로 정리합니다. 모든 프로젝트에 같은 목차나 설치 명령을 적용하지 않습니다.

## 설치

먼저 저장소를 내려받습니다.

```bash
git clone https://github.com/hostkimjang/korean-dev-writing-skills.git
cd korean-dev-writing-skills
```

설치할 대상은 이 저장소의 `skills/korean-dev-writing/` 폴더 전체입니다. 폴더 안의 `SKILL.md`와 `references/`를 함께 복사하세요. 기존에 같은 이름의 스킬이 있다면 내용을 비교하고 백업한 뒤 교체하세요.

| 도구와 범위 | 복사할 위치 |
| --- | --- |
| Claude Code: 현재 프로젝트 | `.claude/skills/korean-dev-writing/` |
| Claude Code: 사용자 공통 | `~/.claude/skills/korean-dev-writing/` |
| Codex: 현재 프로젝트 | `.agents/skills/korean-dev-writing/` |
| Codex: 사용자 공통 | `~/.agents/skills/korean-dev-writing/` |

경로는 2026-11-03에 [Claude Code 공식 문서](https://code.claude.com/docs/en/skills)와 [OpenAI 공식 문서](https://learn.chatgpt.com/docs/build-skills)에서 확인했습니다. 로컬 설치와 웹·클라우드 제품의 스킬 등록 방식은 다를 수 있습니다. 이 저장소의 평가가 모든 제품에서의 설치나 자동 호출을 검증한 것은 아닙니다.

### 사용 예

Claude Code에서는 `/korean-dev-writing`, Codex에서는 `$korean-dev-writing`을 명시해 요청할 수 있습니다.

```text
이 저장소의 실행 설정과 기존 문서를 확인한 뒤 한국어 README를 정리해 주세요.
처음 사용하는 개발자가 프로젝트의 목적을 이해하고 실행할 수 있게 작성해 주세요.
```

```text
다음 PR 설명을 다듬어 주세요. 원인 조사 상태와 테스트 실행 여부는 그대로 유지해 주세요.
```

```text
제공한 메모로 현재 아키텍처 문서를 작성해 주세요.
현재 운영 중인 구성과 앞으로 검토할 변경을 구분해 주세요.
```

## 비교 자료

`evaluations/`에는 공개 가능한 가상 프로젝트 6개 사례, 동일한 입력, 사전 평가 기준, 생성 결과와 평가 기록을 보관합니다. 세 조건을 비교합니다.

1. 별도의 글쓰기 스킬 미적용
2. 사용자가 제공한 기존 스킬 적용
3. 이 저장소의 개선 스킬 적용

같은 세션 계열 모델을 조건별 독립 컨텍스트에서 사용합니다. 평가자는 조건을 가린 문서와 원자료로 평가합니다. 작은 표본의 탐색 실험이므로 모델 전체의 성능이나 모든 문서에서의 개선을 보장하지 않습니다. 자세한 실행 조건과 한계는 [평가 프로토콜](evaluations/protocol.md)과 [비교 보고서](docs/evaluation.md)를 확인하세요.

### 2026-11-03 비교 결과

| 조건 | 평균 총점 / 20 | 치명적 사실왜곡이 표시된 문서 |
| --- | ---: | ---: |
| 스킬 미적용 | 19.67 | 0/6 |
| 기존 스킬 | 19.58 | 0/6 |
| 개선 스킬 | 20.00 | 0/6 |

같은 계열 모델의 평가자 두 개가 각각 채점했습니다. 개선본은 미적용 대비 아키텍처·ADR에서 반복 설명이 줄어 각각 1점 높았고, 나머지 네 사례는 동점이었습니다. 기본 출력도 이미 상한에 가까워 차이는 작습니다. 사실 정확성은 세 조건 모두 같은 점수였으며, Claude·Gemini에서의 효과나 자동 설치·호출을 검증한 결과는 아닙니다.

## 검증과 패키징

저장소 루트에서 Python 3.12로 실행합니다. 별도 Python 패키지를 설치하지 않습니다.

```bash
python scripts/check.py
python scripts/package.py --version 0.2.0
```

패키징 스크립트는 `dist/`에 스킬 폴더만 포함한 ZIP을 만듭니다. 비교 입력과 결과, 저장소용 안내문은 설치 패키지에 포함하지 않습니다. 검사기의 확인 범위와 한계는 [개발 안내](docs/development.md)에 설명합니다.

## 라이선스와 출처

새로 작성한 스킬·예시·도구는 [MIT License](LICENSE)로 배포합니다. 참고 문서의 저작권과 라이선스는 각 원문에 따릅니다. 위키독스의 편집 원칙을 참고해 지침과 예시를 새로 작성했으며, 채택한 원칙과 예외는 [출처 기록](docs/sources.md)에 연결했습니다.
