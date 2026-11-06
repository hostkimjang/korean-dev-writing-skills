# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 긴 글에서 조건을 다시 찾거나 같은 설명을 반복해서 읽는 부담을 줄이도록 안내합니다.

**v0.7.0에서는 실제 사용 피드백에 맞춰 조사·설계 보고서의 문단과 근거 배치를 보강했습니다.** 여러 발견을 소제목으로 나누고, 반복 면책과 긴 경로를 정리하면서 판단에 필요한 조건은 가까이 둡니다. 기존 12개 최종본과 새 보고서 2개를 함께 공개합니다.

**[완성 문서 읽기](docs/examples/README.md)** · **[이번에 고친 부분](docs/repairs-v0.7.0.md)** · **[교정 전후 비교 HTML](docs/comparisons/index.html)**

## 간편 설치

Node.js 22.20 이상과 Git이 필요합니다. 스킬을 사용할 **프로젝트 폴더**에서 실행하세요.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing
```

안내에 따라 Claude Code 또는 Codex를 선택합니다. 기본 설치 범위는 현재 프로젝트입니다. 두 도구에 함께 설치하거나 모든 프로젝트에서 사용하려면 [상세 설치 안내](docs/installation.md)를 확인하세요.

이미 현재 프로젝트에 설치했다면 같은 폴더에서 업데이트합니다.

```bash
npx skills@1.7.5 update korean-dev-writing -p
```

### 사용 예

Claude Code에서는 `/korean-dev-writing`, Codex에서는 `$korean-dev-writing`을 명시하고 다음처럼 요청합니다.

```text
이 저장소의 실행 설정과 기존 문서를 확인한 뒤 한국어 README를 정리해 주세요.
처음 사용하는 개발자가 목적과 실행 방법을 이해할 수 있게 작성해 주세요.
검토 중 발견한 누락·중복·조건 분산은 본문에서 고치고 원자료와 다시 대조해 주세요.
```

## 어떤 글에 쓰나요?

README, PR 설명, 버그 리포트, 아키텍처 문서, 운영 절차, ADR, API 안내, 조사·설계 검토 보고서, 기술 글에 사용할 수 있습니다. 표현 교정·구조 정리·새 문서 작성을 구분하고, 요청한 범위에서 작업합니다.

문장을 짧게 만드는 것보다 원래 의미를 지키는 일을 우선합니다. `수 있다`가 가능성을, `기본적으로`가 기본값을 나타내면 유지합니다. 확인한 기능과 계획, 가설과 확인된 원인, 테스트 계획과 실행 결과도 구분합니다.

설명과 인과관계는 문단으로 연결하고, 실행 순서는 번호로, 병렬 조건은 목록이나 표로 정리합니다. 긴 글의 흐름을 유지하면서도 초기 상태·거절·오류·중단 조건은 찾아볼 수 있게 합니다. 제공되지 않은 기능·수치·일정으로 빈칸을 채우지 않습니다.

## v0.7.0에서 달라진 점

| 읽기를 막던 부분 | 바뀐 지침과 예시 |
| --- | --- |
| 여러 실험·판단이 한 문단에 몰림 | 서로 다른 질문에 답하는 내용을 나누고, 관련 결과와 근거는 함께 설명합니다. 3~4문장·250~300자는 다시 살필 신호로 사용합니다. |
| 요약의 발견을 찾기 어려움 | 독립된 발견이 3개 이상 이어지는 조사·설계 검토에는 결론형 번호 소제목을 사용합니다. 짧은 항목은 번호 목록으로 충분합니다. |
| 반복 면책과 `(판단)` 꼬리표 | `확인했다`, `설정상 …로 보인다`, `권장한다`처럼 상태를 서술어로 드러냅니다. 결과의 신뢰도와 행동을 바꾸는 미검증·중단 조건은 판단 옆에 둡니다. |
| 문장 중간의 긴 경로·괄호 | 주장 아래 근거 줄·목록·표로 옮깁니다. 원래 경로와 불연속 행 범위, 주장과의 대응은 유지합니다. |
| 여러 스킬을 거치며 구조가 다시 뭉침 | 문체 교정이나 도식을 함께 적용해도 소제목·비교 표·근거·실행 조건의 배치를 유지하도록 명시했습니다. |
| 비교 자료에 긴 조사 보고서가 부족함 | 공개용 가상 보고서 2개를 추가해 같은 초안을 두 버전으로 교정하고 첫 제출·검토·최종본을 구분했습니다. |

기존 예제 12개는 바이트 그대로 보존했습니다. 새 회귀 사례의 이전 버전 출력은 이번 실행에서 v0.6.0 지침으로 작성한 비교용 문서입니다. [수정 결과와 근거](docs/repairs-v0.7.0.md)에서 실제 변화와 확인 범위를 볼 수 있습니다.

## 예시와 비교 자료

| 읽고 싶은 내용 | 자료 |
| --- | --- |
| 완성된 문서 본문 | [예시 문서 목록](docs/examples/README.md) |
| 이번에 해결한 문제와 검토 근거 | [v0.7.0 수정 결과](docs/repairs-v0.7.0.md) |
| 기존 예제의 변경·보존 여부 | [문서별 결과](docs/evaluation.md) |
| 전문을 좌우로 비교하고 원문 저장하기 | [HTML 비교 파일](docs/comparisons/index.html) |
| 아키텍처·ADR·런북의 전문 | [긴 문서 비교](docs/comparisons/long-documents.md) |
| 온보딩·짧은 PR의 전문 | [읽기 흐름 비교](docs/comparisons/reading-flow.md) |
| 설정배포 안내·작업 보고의 전문 | [추가 사례 비교](docs/comparisons/transfer-checks.md) |
| 같은 초안을 두 버전으로 교정한 보고서 | [조사·설계 검토의 최초 제출 비교](docs/comparisons/new-topics.md) |
| v0.6.0 당시 새 주제 비교 | [로그 보관·설정 우선순위 보존본](docs/comparisons/new-topics-v0.6.0.md) |

HTML 파일을 다운로드해 브라우저에서 열면 **이전 v0.6.0 ↔ 현재 v0.7.0**을 기본으로 비교합니다. 처음 8개 사례는 미적용 원문도 선택할 수 있습니다. 본문 36개와 입력 14개를 인터넷 없이 읽고 저장할 수 있으며, 긴 본문은 목차로 이동하거나 한 문서만 펼쳐 읽을 수 있습니다.

기존 최종본의 보존과 새 보고서의 교정을 구분해 기록합니다. 원자료, 이전 출력, 스킬 고정본, 검토 인용은 [실행 기록](evaluations/runs/2026-11-06-v0.7.0/manifest.json)에 남깁니다. 의미 보존과 구성·화면 동작을 확인한 결과이며, 사람의 읽기 속도·피로·기억을 측정한 실험은 아닙니다.

이전 결과는 [v0.6.0](docs/evaluation-v0.6.0.md), [v0.5.0](docs/evaluation-v0.5.0.md), [v0.4.0](docs/evaluation-v0.4.0.md), [v0.3.0](docs/evaluation-v0.3.0.md), [v0.2.0](docs/evaluation-v0.2.0.md) 보고서로 보존합니다.

## 스킬 구성과 근거

- [스킬 본문](skills/korean-dev-writing/SKILL.md): 작업 판단, 의미 보존, 구성과 교정 절차
- [문장 교정과 유지 예시](skills/korean-dev-writing/references/before-after-guide.md)
- [문서 종류별 구성](skills/korean-dev-writing/references/document-types.md)
- [긴 문서의 흐름과 정보 배치](skills/korean-dev-writing/references/reading-flow.md)
- [읽기 연구와 적용 범위](docs/reading-research.md) · [글쓰기 원칙의 출처](docs/sources.md)
- [필수 의미와 탐색 질문](docs/evaluation-contract.md)

## 검증과 패키징

저장소 루트에서 Python 3.12로 실행합니다. 별도 Python 패키지는 필요하지 않습니다.

```bash
python scripts/check.py
python scripts/check_claims.py
python scripts/check_repairs.py
python scripts/package.py --version 0.7.0
```

패키지는 `dist/korean-dev-writing-v0.7.0.zip`으로 생성되며 설치에 필요한 스킬 파일 6개만 포함합니다. 비교 자료는 별도로 배포합니다.

비교 자료를 다시 만들거나 최신 상태인지 확인할 때는 Node.js 20 이상도 사용합니다.

```bash
python scripts/build_docs.py
node scripts/build_viewer.mjs
python scripts/build_docs.py --check
node scripts/build_viewer.mjs --check
```

CI는 구조·검토 인용·생성 자료 최신성, Claude Code·Codex 설치, 패키지 재현성, 비교 화면의 기능을 검사합니다. 별도 Chromium 작업은 절 이동과 단독 읽기·모바일 배치를 확인합니다. 프로그램이 문장의 의미나 자연스러움을 자동 판정하는 것은 아닙니다. [개발 안내](docs/development.md)에 실행법과 검사 범위를 정리했습니다.

## 라이선스와 출처

새로 작성한 스킬·예시·도구는 [MIT License](LICENSE)로 배포합니다. 비교 자료 빌드에 포함한 Marked는 [별도 MIT 라이선스와 버전 기록](scripts/vendor/marked/README.md)을 따릅니다. 참고 문서의 저작권과 라이선스는 각 원문에 따릅니다. 위키독스 등의 편집 원칙을 참고해 지침과 예시를 새로 작성했으며, 채택한 원칙과 예외를 [출처 기록](docs/sources.md)에 연결했습니다.
