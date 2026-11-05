# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 긴 글에서 조건을 다시 찾거나 같은 설명을 반복해서 읽는 부담을 줄이도록 안내합니다.

**v0.6.0에서는 겹치던 작성 지침을 정리하고, 비교 화면에 문서별 목차와 단독 읽기를 추가했습니다.** 짧은 PR의 모호한 검증 대상도 고쳤습니다. 기존 예제 10개와 새 주제로 작성한 문서를 함께 공개합니다.

**[완성 문서 읽기](docs/examples/README.md)** · **[이번에 고친 부분](docs/repairs-v0.6.0.md)** · **[교정 전후 비교 HTML](docs/comparisons/index.html)**

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

README, PR 설명, 버그 리포트, 아키텍처 문서, 운영 절차, ADR, API 안내, 기술 글에 사용할 수 있습니다. 표현 교정·구조 정리·새 문서 작성을 구분하고, 요청한 범위에서 작업합니다.

문장을 짧게 만드는 것보다 원래 의미를 지키는 일을 우선합니다. `수 있다`가 가능성을, `기본적으로`가 기본값을 나타내면 유지합니다. 확인한 기능과 계획, 가설과 확인된 원인, 테스트 계획과 실행 결과도 구분합니다.

설명과 인과관계는 문단으로 연결하고, 실행 순서는 번호로, 병렬 조건은 목록이나 표로 정리합니다. 긴 글의 흐름을 유지하면서도 초기 상태·거절·오류·중단 조건은 찾아볼 수 있게 합니다. 제공되지 않은 기능·수치·일정으로 빈칸을 채우지 않습니다.

## v0.6.0에서 달라진 점

| 영역 | 바뀐 내용 |
| --- | --- |
| 스킬 지침 | 재정리 원칙 8개를 5개로 합치고, 독자의 익숙함을 ‘해당 문서의 개념·동작’ 기준으로 명시했습니다. |
| 짧은 PR | ‘변경 동작 미검증’을 ‘가설과 추가 로그 출력 미검증’으로 구체화했습니다. 기능 동작은 유지했고 검증은 끝나지 않았다는 뜻을 분명히 했습니다. |
| 긴 문서 탐색 | 비교 화면에서 원문의 제목으로 이동할 수 있습니다. 절 링크를 열면 해당 사례와 버전이 함께 표시됩니다. |
| 단독 읽기·표 | 한 문서를 읽을 때 문서 상자 안의 별도 스크롤을 없앴습니다. 넓은 표는 좁은 화면에서 표 영역을 가로로 이동하며 읽습니다. |
| 자료 재생성 | 저장소 안의 Python·Node 도구만으로 Markdown 비교와 HTML을 다시 만듭니다. 공개 파일이 예전 내용이면 최신성 검사에서 실패합니다. |
| 새 주제 확인 | 로그 보관 정책과 구성 값 우선순위를 원자료부터 작성하고, 두 버전의 최초 작성본을 별도로 대조했습니다. |

기존 10개 예제 중 짧은 PR 한 개를 고쳤고 나머지 9개는 보존했습니다. 바꾸지 않은 문서를 새로 작성하거나 새로 검토한 결과로 세지 않습니다. [수정 결과와 근거](docs/repairs-v0.6.0.md)에서 확인할 수 있습니다.

## 예시와 비교 자료

| 읽고 싶은 내용 | 자료 |
| --- | --- |
| 완성된 문서 본문 | [예시 문서 목록](docs/examples/README.md) |
| 이번에 해결한 문제와 검토 근거 | [v0.6.0 수정 결과](docs/repairs-v0.6.0.md) |
| 기존 예제의 변경·보존 여부 | [문서별 결과](docs/evaluation.md) |
| 전문을 좌우로 비교하고 원문 저장하기 | [HTML 비교 파일](docs/comparisons/index.html) |
| 아키텍처·ADR·런북의 전문 | [긴 문서 비교](docs/comparisons/long-documents.md) |
| 온보딩·짧은 PR의 전문 | [읽기 흐름 비교](docs/comparisons/reading-flow.md) |
| 설정배포 안내·작업 보고의 전문 | [추가 사례 비교](docs/comparisons/transfer-checks.md) |
| 이전 출력 없이 쓴 두 새 주제 | [로그 보관·설정 우선순위 비교](docs/comparisons/new-topics.md) |

HTML 파일을 다운로드해 브라우저에서 열면 **이전 v0.5.0 ↔ 현재 v0.6.0**을 기본으로 비교합니다. 처음 8개 사례는 미적용 원문도 선택할 수 있습니다. 본문 28개와 입력 10개를 인터넷 없이 읽고 저장할 수 있으며, 긴 본문은 목차로 이동하거나 한 문서만 펼쳐 읽을 수 있습니다.

기존 문서의 교정과 새 주제의 최초 작성을 구분해 기록합니다. 원자료, 이전 출력, 스킬 고정본, 검토 인용은 [실행 기록](evaluations/runs/2026-11-05-v0.6.0/manifest.json)에 남깁니다. 의미 보존과 구성·화면 동작을 확인한 결과이며, 사람의 읽기 속도·피로·기억을 측정한 실험은 아닙니다.

이전 결과는 [v0.5.0](docs/evaluation-v0.5.0.md), [v0.4.0](docs/evaluation-v0.4.0.md), [v0.3.0](docs/evaluation-v0.3.0.md), [v0.2.0](docs/evaluation-v0.2.0.md) 보고서로 보존합니다.

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
python scripts/package.py --version 0.6.0
```

패키지는 `dist/korean-dev-writing-v0.6.0.zip`으로 생성되며 설치에 필요한 스킬 파일 6개만 포함합니다. 비교 자료는 별도로 배포합니다.

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
