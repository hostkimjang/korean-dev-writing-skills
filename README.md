# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 긴 글에서 조건을 다시 찾거나 같은 설명을 반복해서 읽는 부담을 줄이도록 안내합니다.

**v0.8.0에서는 한국어 윤문과 아키텍처 도식 스킬을 함께 설치하는 선택형 설치기를 추가했습니다.** 현재 향상 설치는 이 저장소에서 개발 문서 규칙을 보강한 `humanize-korean`과 원본 커밋을 고정한 `stack-diagram`을 함께 설치합니다. 기본 스킬만 사용할 수도 있으며, 윤문·도식 스킬의 다른 배포본을 지정하는 옵션도 제공합니다.

**[향상 설치와 출처](docs/enhancements.md)** · **[완성 문서 읽기](docs/examples/README.md)** · **[v0.7.0 교정 비교](docs/comparisons/index.html)**

개발 문서의 용어·문장 구조·문서 역할·종결어미·띄어쓰기 규칙을 보강하고 안내 문서를 전수 교정했습니다. [전체 검증 기록](docs/evidence/language-audit.md)에서 수정 범위, 원문 보존 확인, 검사 결과와 보존 기록의 참조 예외를 확인할 수 있습니다.

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

### 향상 스킬 함께 설치

스킬을 사용할 프로젝트 폴더에서 실행합니다. 아래 명령은 Codex에 기본 스킬과 두 향상 스킬을 함께 설치합니다.

```bash
npx --yes --package=github:hostkimjang/korean-dev-writing-skills korean-dev-writing-install --with-enhancements -a codex
```

설치할 스킬·출처·대상 도구·설치 범위를 확인한 뒤 한 번 승인합니다. Claude Code에는 `-a claude-code`를 사용하고, 두 도구에 설치하려면 두 옵션을 함께 지정합니다. 모든 프로젝트에서 쓰려면 `-g`를 추가합니다. 이미 같은 이름의 스킬이 있으면 교체 여부를 명시하기 전까지 설치를 중단합니다.

| 구성 | 역할 | 향상 설치의 기본 설치본 |
| --- | --- | --- |
| `korean-dev-writing` | 사실 보존, 문서 구조와 읽기 흐름 | 이 저장소 |
| `humanize-korean` | 한국어 문장 교정·윤문, 개발 문서 표현 점검 | 이 저장소의 보강본. [nathankim0/humanize-korean](https://github.com/nathankim0/humanize-korean)에 참고 규칙을 추가했습니다. |
| `stack-diagram` | 기술 스택·아키텍처 도식 | [caru-ini/stack-diagram](https://github.com/caru-ini/stack-diagram) |

윤문 스킬은 참고 문서와 실행 스크립트를 함께 담은 배포본입니다. 기존에 쓰던 동명 스킬과 같다고 가정하지 않으며, `--humanize-source`로 외부의 다른 독립 배포본을 지정할 수 있습니다. 각 스킬은 필요한 작업에서만 적용합니다. [상세 설치 옵션](docs/installation.md)과 [실행 환경·원본 라이선스·검증 범위](docs/enhancements.md)를 확인하세요.

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

## 한국어 개발 문서 점검

개발 용어의 어색한 직역, 번역투 문장 구조, 과거 작업 기록과 세션 표현, 문서 세트의 종결어미, 공백을 생략한 압축 표기를 함께 점검합니다. 윤문 스킬의 규칙·예시·점검표에서 동일한 탐지 ID를 사용하고, 기본 스킬의 지침과 예시에도 같은 교정 기준을 반영했습니다.

코드 식별자와 명령, 수치와 검증 상태는 원문대로 보존합니다. 현행 명세에는 현재 동작을 설명하고, 일회성 검증 기록은 별도 이력 문서에 남깁니다. [교정 규칙과 예시](skills/korean-dev-writing/references/before-after-guide.md)와 [개발 문서 탐지 사전](skills/humanize-korean/references/quick-rules.md)에서 구체적인 표현과 예외를 확인할 수 있습니다.

## 문서 교정 비교: v0.7.0

아래 문서 교정 결과와 비교 화면은 v0.7.0의 기록입니다. v0.8.0은 설치와 선택 스킬의 적용 기준을 보강한 버전이며, 이 14개 문서를 세 스킬 조합으로 다시 생성하거나 문장 품질 향상을 새로 측정한 결과가 아닙니다.

| 읽기를 막던 부분 | 바뀐 지침과 예시 |
| --- | --- |
| 여러 실험·판단이 한 문단에 몰림 | 서로 다른 질문에 답하는 내용을 나누고, 관련 결과와 근거는 함께 설명합니다. 3~4문장·250~300자는 다시 살필 신호로 사용합니다. |
| 요약의 발견을 찾기 어려움 | 독립된 발견이 3개 이상 이어지는 조사·설계 검토에는 결론형 번호 소제목을 사용합니다. 짧은 항목은 번호 목록으로 충분합니다. |
| 반복 면책과 `(판단)` 꼬리표 | `확인했다`, `설정상 …로 보인다`, `권장한다`처럼 상태를 서술어로 드러냅니다. 결과의 신뢰도와 행동을 바꾸는 미검증·중단 조건은 판단 옆에 둡니다. |
| 문장 중간의 긴 경로·괄호 | 주장 아래 근거 줄·목록·표로 옮깁니다. 원래 경로와 불연속 행 범위, 주장과의 대응은 유지합니다. |
| 여러 스킬을 거치며 구조가 다시 뭉침 | 문체 교정이나 도식을 함께 적용해도 소제목·비교 표·근거·실행 조건의 배치를 유지하도록 명시했습니다. |
| 비교 자료에 긴 조사 보고서가 부족함 | 공개용 가상 보고서 2개를 추가해 같은 초안을 두 버전으로 교정하고 첫 제출·검토·최종본을 구분했습니다. |

v0.7.0 평가에서는 기존 예제 12개를 바이트 그대로 보존했습니다. 새 회귀 사례의 이전 버전 출력은 해당 평가 당시 v0.6.0 지침으로 작성한 비교용 문서입니다. [수정 결과와 근거](docs/repairs-v0.7.0.md)에서 실제 변화와 확인 범위를 볼 수 있습니다.

## 예시와 비교 자료

| 읽고 싶은 내용 | 자료 |
| --- | --- |
| 완성된 문서 본문 | [예시 문서 목록](docs/examples/README.md) |
| v0.7.0에서 해결한 문제와 검토 근거 | [v0.7.0 수정 결과](docs/repairs-v0.7.0.md) |
| 기존 예제의 변경·보존 여부 | [문서별 결과](docs/evaluation.md) |
| 전문을 좌우로 비교하고 원문 저장하기 | [HTML 비교 파일](docs/comparisons/index.html) |
| 아키텍처·ADR·런북의 전문 | [긴 문서 비교](docs/comparisons/long-documents.md) |
| 온보딩·짧은 PR의 전문 | [읽기 흐름 비교](docs/comparisons/reading-flow.md) |
| 설정배포 안내·작업 보고의 전문 | [추가 사례 비교](docs/comparisons/transfer-checks.md) |
| 같은 초안을 두 버전으로 교정한 보고서 | [조사·설계 검토의 최초 제출 비교](docs/comparisons/new-topics.md) |
| v0.6.0 당시 새 주제 비교 | [로그 보관·설정 우선순위 보존본](docs/comparisons/new-topics-v0.6.0.md) |

HTML 파일을 다운로드해 브라우저에서 열면 **v0.6.0 ↔ v0.7.0**을 기본으로 비교합니다. 처음 8개 사례는 미적용 원문도 선택할 수 있습니다. 본문 36개와 입력 14개를 인터넷 없이 읽고 저장할 수 있으며, 긴 본문은 목차로 이동하거나 한 문서만 펼쳐 읽을 수 있습니다.

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

저장소 루트에서 Python 3.12로 실행합니다. 아래의 기존 구조·배포 검사에는 별도 Python 패키지가 필요하지 않습니다. 문서 전수 검사와 pytest 실행 환경은 [개발 안내](docs/development.md#문서-전수-검사)에 정리했습니다.

```bash
python scripts/check.py
python scripts/check_claims.py
python scripts/check_repairs.py
node --test scripts/test_install.mjs
node scripts/check_enhanced_install.mjs
python scripts/package.py --version 0.8.0
```

ZIP은 `dist/korean-dev-writing-v0.8.0.zip`으로 생성되며 기본 스킬 파일 6개만 포함합니다. 향상 설치기의 npm 패키지에는 보강한 윤문 스킬을 함께 담고, 도식 스킬은 고정한 원본에서 내려받습니다. 기본 스킬 ZIP에는 향상 스킬을 포함하지 않습니다. 설치기 통합 검증에는 Node.js 22.20 이상과 Git, npm·GitHub에 대한 네트워크 접근이 필요합니다. 비교 자료는 별도로 배포합니다.

비교 자료를 다시 만들거나 최신 상태인지 확인할 때는 Node.js 20 이상도 사용합니다.

```bash
python scripts/build_docs.py
node scripts/build_viewer.mjs
python scripts/build_docs.py --check
node scripts/build_viewer.mjs --check
```

CI는 구조·검토 인용·생성 자료 최신성, Claude Code·Codex 설치, 패키지 재현성, 비교 화면의 기능을 검사합니다. 향상 설치기는 Linux·Windows에서 별도로 검증합니다. Chromium 작업은 절 이동과 단독 읽기·모바일 배치를 확인합니다. 프로그램이 문장의 의미나 자연스러움을 자동 판정하는 것은 아닙니다. [개발 안내](docs/development.md)에 기존 검사 범위를, [향상 설치 안내](docs/enhancements.md)에 이번 변경의 검증 범위를 정리했습니다.

## 라이선스와 출처

새로 작성한 스킬·예시·도구는 [MIT License](LICENSE)로 배포합니다. 동봉한 윤문 스킬에는 [해당 라이선스](skills/humanize-korean/LICENSE)와 [기반 프로젝트 고지](skills/humanize-korean/THIRD_PARTY_NOTICES.md)를 함께 포함합니다. 비교 자료 빌드에 포함한 Marked는 [별도 MIT 라이선스와 버전 기록](scripts/vendor/marked/README.md)을 따릅니다. 참고 문서의 저작권과 라이선스는 각 원문에 따릅니다. 위키독스 등의 편집 원칙을 참고해 지침과 예시를 새로 작성했으며, 채택한 원칙과 예외를 [출처 기록](docs/sources.md)에 연결했습니다.
