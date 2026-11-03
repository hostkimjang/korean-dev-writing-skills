# Korean Dev Writing

한국어 README와 개발 문서를 사실과 의미를 보존하면서 자연스럽게 작성하는 Agent Skill입니다. 독자가 이해하고 실행할 순서로 내용을 구성하고, 긴 글에서 조건을 다시 찾거나 같은 설명을 반복해서 읽는 부담을 줄이도록 안내합니다.

**v0.5.0은 검토에서 발견한 문제를 본문에서 고친 뒤, 바뀐 사실과 실행 조건을 다시 확인하도록 보강했습니다.** 기존 예시의 조건 분산·중복·긴 조건문도 직접 교정했습니다.

**[완성 예시 10개 읽기](docs/examples/README.md)** · **[어디를 고쳤는지 확인하기](docs/repairs-v0.5.0.md)** · **[교정 전후 나란히 보기](docs/comparisons/index.html)**

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

설명과 인과관계는 문단으로 연결하고, 실행 순서는 번호로, 병렬 조건은 목록이나 표로 정리합니다. 긴 글의 흐름을 유지하면서도 초기 상태·거절·오류·중단 조건은 제목과 표에서 찾을 수 있게 합니다. 제공되지 않은 기능·수치·일정으로 빈칸을 채우지 않습니다.

## v0.5.0에서 고친 내용

| 문서 | 직접 고친 부분 |
| --- | --- |
| CLI README | 파일 저장 예 바로 옆에 덮어쓰기 조건을 붙이고, 심각도 목록의 표·본문 중복을 정리했습니다. |
| 장애 런북 | 일시정지 확인과 롤백을 한 실행 절로 묶었습니다. 요청 후 5분 기준을 같은 자리에서 읽게 하고 이관 조건을 표로 나눴습니다. |
| ADR | 비교 표의 이점을 다시 나열하던 문장을 줄였습니다. 승인 조건 옆에 비용 미측정·성능 보장 미설정 상태를 모았습니다. |
| 긴 온보딩 | 식별자 표에 상태 조회용 번호를 명시하고, 실패·중단 재시도 조건의 빈 반복을 제거했습니다. |
| 짧은 관측 PR | 대상·판단 한계·미검증 이유와 함께 상세 로그 필드·요청 본문 제외 범위를 분량 안에 담았습니다. |
| 설정배포 안내 | 준비 단계에 두 설정 이름을 쓰고, 예약 충돌 응답과 재요청 가능 조건을 한곳에 붙였습니다. |

전체 10개 문서를 다시 검토했습니다. 기존 내용이 충분했던 아키텍처·일반 진단 PR·문단 교정·짧은 작업 보고는 불필요하게 다시 쓰지 않고 보존했습니다. [수정 결과 보고서](docs/repairs-v0.5.0.md)에서 완료 기준과 본문 근거를 확인할 수 있습니다.

## 예시와 비교 자료

| 읽고 싶은 내용 | 자료 |
| --- | --- |
| 완성된 문서만 읽거나 가져다 쓰기 | [예시 문서 10개](docs/examples/README.md) |
| 해결한 문제와 검토 근거 | [v0.5.0 수정 결과](docs/repairs-v0.5.0.md) |
| 문서별 변경 요약 | [교정 결과](docs/evaluation.md) |
| 전문을 좌우로 비교하고 원문 저장하기 | [HTML 비교 파일](docs/comparisons/index.html) |
| 아키텍처·ADR·런북의 전문 9개 | [긴 문서 비교](docs/comparisons/long-documents.md) |
| 온보딩·짧은 PR의 전문 6개 | [읽기 흐름 비교](docs/comparisons/reading-flow.md) |
| 설정배포 안내·작업 보고의 전문 4개 | [추가 사례 비교](docs/comparisons/transfer-checks.md) |

HTML 파일을 다운로드해 브라우저에서 열면 **교정 전 v0.4.0 ↔ 교정 완료 v0.5.0**이 기본으로 표시됩니다. 처음 8개 사례는 미적용 원문도 선택할 수 있습니다. 총 28개 본문과 입력 10개를 읽고 저장할 수 있습니다.

별도로 새 컨텍스트에서 원래 입력과 스킬만 보고 런북·짧은 PR·설정배포 안내를 작성했습니다. 세 문서도 다른 검토자가 원자료와 대조했으며, [첫 작성본과 검토 결과](evaluations/runs/2026-11-03-v0.5.0/forward)를 보존했습니다.

이번 결과는 기존 출력과 피드백을 보고 수정한 문서입니다. 첫 교정본과 이후 수정 이력, 원자료, 스킬 고정본, 검토 근거를 [실행 기록](evaluations/runs/2026-11-03-v0.5.0/manifest.json)에 남깁니다. 검토는 의미 보존과 문서 배치에 관한 확인이며, 사람의 읽기 속도·피로·이해도를 측정한 실험은 아닙니다. 자세한 범위는 [교정 절차](evaluations/runs/2026-11-03-v0.5.0/protocol.md)에 모았습니다.

이전 결과는 [v0.4.0](docs/evaluation-v0.4.0.md), [v0.3.0](docs/evaluation-v0.3.0.md), [v0.2.0](docs/evaluation-v0.2.0.md) 보고서로 보존합니다.

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
python scripts/package.py --version 0.5.0
```

`check_repairs.py`는 최종 검토 기록에 미해결 항목이 남지 않았는지, 인용과 해시가 실제 파일에 맞는지, 공개 예시가 검토한 최종본과 같은지 확인합니다. 프로그램이 문장의 의미나 자연스러움을 자동 판정하지는 않습니다.

패키징 결과는 `dist/korean-dev-writing-v0.5.0.zip`입니다. 설치에 필요한 스킬 파일 6개만 포함하며, 비교 자료는 포함하지 않습니다. CI에서는 Claude Code·Codex용 기본 설치와 `--copy` 설치, 공개된 커밋을 통한 설치, 패키지의 재현성을 검사합니다. [개발 안내](docs/development.md)에 검사 범위와 실행법을 정리했습니다.

## 라이선스와 출처

새로 작성한 스킬·예시·도구는 [MIT License](LICENSE)로 배포합니다. 참고 문서의 저작권과 라이선스는 각 원문에 따릅니다. 위키독스 등의 편집 원칙을 참고해 지침과 예시를 새로 작성했으며, 채택한 원칙과 예외를 [출처 기록](docs/sources.md)에 연결했습니다.
