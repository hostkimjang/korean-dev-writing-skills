# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 문장과 문단을 다듬습니다.

v0.4.0에서는 긴 글의 흐름을 유지하면서 초기 상태·오류·거절 조건을 찾아보기 쉽게 구성하고, 시스템의 판정 조건과 사람이 확인하는 절차를 구분합니다. 짧은 글에서도 대상과 판단 한계의 이유를 남기도록 보강했습니다. [제안 검토와 변경 내용](docs/review-v0.4.0.md), [실제 생성 문서 비교](docs/evaluation.md)에서 적용 결과와 한계를 확인할 수 있습니다.

대상 문서는 README, PR 설명, 버그 리포트, 아키텍처 문서, 운영 절차, ADR, API 안내, 기술 글입니다. 표현 교정과 새 문서 작성을 구분하며, 제공되지 않은 기능·수치·일정으로 빈칸을 채우지 않습니다.

## 간편 설치

Node.js 22.20 이상과 Git이 필요합니다. 스킬을 사용할 **프로젝트 폴더**에서 실행하세요.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing
```

안내에 따라 사용할 도구로 Claude Code 또는 Codex를 선택합니다. 기본 설치 범위는 현재 프로젝트입니다. 두 도구에 함께 설치하거나 모든 프로젝트에서 사용하려면 [상세 설치 안내](docs/installation.md)를 확인하세요. 설치 확인, 업데이트·삭제, 수동 복사 방법도 같은 문서에 정리했습니다.

### 사용 예

설치한 도구에서 Claude Code는 `/korean-dev-writing`, Codex는 `$korean-dev-writing`을 명시하고 다음처럼 요청합니다.

```text
이 저장소의 실행 설정과 기존 문서를 확인한 뒤 한국어 README를 정리해 주세요.
처음 사용하는 개발자가 프로젝트의 목적을 이해하고 실행할 수 있게 작성해 주세요.
```

## 먼저 확인하기

- 스킬 본문: [SKILL.md](skills/korean-dev-writing/SKILL.md)
- 문장 교정과 유지 예시: [before-after-guide.md](skills/korean-dev-writing/references/before-after-guide.md)
- 문서 종류별 구성: [document-types.md](skills/korean-dev-writing/references/document-types.md)
- 긴 문서의 연결·재정리·정보 배치: [reading-flow.md](skills/korean-dev-writing/references/reading-flow.md)
- 현재 배포본으로 새로 쓴 8개 문서: [종합 비교](docs/evaluation.md) · [24개 전문을 나란히 읽는 HTML](docs/comparisons/index.html)
- 읽기 흐름 보강의 근거와 두 사례의 전문: [조사 기록](docs/reading-research.md) · [긴 온보딩·짧은 PR 비교](docs/comparisons/reading-flow.md)
- 긴 문서 세 사례의 전문과 개선점: [한눈에 보는 비교](docs/comparisons/long-documents.md)
- v0.4.0 리뷰 반영과 검증 방식: [제안 대조](docs/review-v0.4.0.md) · [필수 의미·탐색 질문 계약](docs/evaluation-contract.md)
- 새 설정배포 안내와 짧은 작업 보고: [두 버전의 전문 4개](docs/comparisons/transfer-checks.md)
- 참고한 글쓰기 원칙과 출처: [sources.md](docs/sources.md)

## 작성 원칙

문장을 짧게 만드는 것보다 원래 의미를 지키는 일을 우선합니다. `수 있다`가 가능성을, `기본적으로`가 기본값을 나타내면 유지합니다. 확인한 버전과 지원 범위, 가설과 확인된 원인, 테스트 계획과 실행 결과를 구분합니다.

문서는 독자의 목적에 맞춰 구성합니다. 설명과 인과관계는 문단으로 연결하고, 실행 순서는 번호로, 병렬 항목은 목록으로 정리합니다. 모든 프로젝트에 같은 목차나 설치 명령을 적용하지 않습니다.

## 현재 배포본으로 갱신한 비교

**[v0.4.0으로 기존 8개 사례의 적용 문서를 다시 작성했습니다.](docs/evaluation.md)** README·아키텍처·진단 PR·장애 대응 절차·ADR·문단 교정·긴 온보딩·짧은 관측 PR을 같은 기존 입력으로 한 번씩 생성했습니다. 새 설정배포 안내와 짧은 작업 보고에서는 v0.3.0·v0.4.0을 각각 새로 생성했습니다. 새 문서는 모두 12개이며, 생성 뒤 문장이나 구성을 고치지 않았습니다.

**[HTML 비교 파일](docs/comparisons/index.html)**을 다운로드해 브라우저에서 열면 8개 사례의 전문 24개를 읽을 수 있습니다. 기본은 **미적용 ↔ 현재 v0.4.0**이며, **v0.3.0 ↔ v0.4.0**으로 바꿀 수 있습니다. 입력과 각 생성 원문도 저장할 수 있습니다. 관찰 요약과 발췌 인용은 v0.3.0·v0.4.0 비교이며, 각 인용에 버전을 표시합니다.

| 읽고 싶은 내용 | 비교 자료 |
| --- | --- |
| 기존 8개 사례의 결과와 한계 | [종합 비교 보고서](docs/evaluation.md) |
| 아키텍처·ADR·장애 대응 절차의 전문 9개 | [긴 문서 비교](docs/comparisons/long-documents.md) |
| 긴 온보딩·짧은 관측 PR의 전문 6개 | [읽기 흐름 비교](docs/comparisons/reading-flow.md) |
| 새 설정배포 안내·작업 보고의 두 버전 전문 4개 | [새 사례 비교](docs/comparisons/transfer-checks.md) |
| 같은 입력·스킬 고정본·원문 해시·검토 기록 | [이번 실행 기록](evaluations/runs/2026-11-03-v0.4.0/manifest.json) |

온보딩에서는 첫 갱신 예외가 제목에 드러나고, 짧은 PR에는 대상 서비스와 로그만으로 판단할 수 없는 이유가 명시됐습니다. 다만 모든 문서가 짧아지거나 모든 문제가 해소된 것은 아닙니다. 아키텍처는 v0.3.0의 3,335자에서 2,553자로 줄었고, 장애 대응 절차는 2,337자에서 2,741자로 늘었습니다. 필요한 실행 조건의 반복과 줄일 수 있는 설명을 비교 보고서에 구분해 적었습니다.

이번 의미 재검토는 **v0.3.0·v0.4.0의 문서 20개**를 대상으로 합니다. 원자료·필수 의미 150개·탐색 질문 37개를 생성 전에 고정했고, 별도 컨텍스트의 검토자가 버전을 가린 문서에 근거 인용을 붙였습니다. 문자열 확인은 자동 신호로 기록하며 의미 보존·치명성 판단과 구분합니다. 이 숫자는 사례별 기준의 합계이며 품질 점수가 아닙니다.

기존 8개 사례의 미적용·v0.3.0 문서는 과거 원문을 그대로 사용했습니다. **생성 시점 차이와 단회 생성의 변동을 스킬 효과에서 분리할 수 없습니다.** 미적용은 이전 검토가 있는 참고 자료이며 이번 의미 재검토에는 포함하지 않았습니다. 새 두 사례도 요청 자체에 일부 구분이 명시돼 있습니다. 실제 독자의 이해·기억·읽는 시간·피로, Claude·Gemini에서의 효과는 측정하지 않았습니다. [실행 프로토콜](evaluations/runs/2026-11-03-v0.4.0/protocol.md)과 [새 사례의 전달 조건](docs/comparisons/transfer-checks.md)에 자세한 범위를 적었습니다.

[v0.3.0 보고서](docs/evaluation-v0.3.0.md)와 [v0.2.0 당시 20점 평가](docs/evaluation-v0.2.0.md)는 과거 기록으로 보존합니다. 새 품질 총점은 만들지 않았습니다.

## 검증과 패키징

저장소 루트에서 Python 3.12로 실행합니다. 별도 Python 패키지를 설치하지 않습니다.

```bash
python scripts/check.py
python scripts/check_claims.py
python scripts/package.py --version 0.4.0
```

패키징 스크립트는 `dist/`에 스킬 폴더만 포함한 ZIP을 만듭니다. 비교 입력과 결과, 저장소용 안내문은 설치 패키지에 포함하지 않습니다. 검사기의 확인 범위와 한계는 [개발 안내](docs/development.md)에 설명합니다.

CI에서는 고정한 `skills` CLI 버전으로 Claude Code·Codex용 기본 설치와 `--copy` 설치를 임시 프로젝트에서 검사합니다. 두 설치 위치의 파일 6개가 원본과 바이트 단위로 일치하는지 확인하고, `main`에 반영된 커밋을 GitHub에서 받아 설치하는 과정도 검사합니다. 실제 도구가 스킬을 호출하는지와 글쓰기 품질은 이 설치 검사의 범위에 포함되지 않습니다.

## 라이선스와 출처

새로 작성한 스킬·예시·도구는 [MIT License](LICENSE)로 배포합니다. 참고 문서의 저작권과 라이선스는 각 원문에 따릅니다. 위키독스의 편집 원칙을 참고해 지침과 예시를 새로 작성했으며, 채택한 원칙과 예외는 [출처 기록](docs/sources.md)에 연결했습니다.
