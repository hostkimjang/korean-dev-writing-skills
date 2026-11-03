# 현재 v0.3.0으로 갱신한 개발 문서 비교

갱신일: 2026-11-03 · 현재 적용본: **v0.3.0 배포본** · [사용한 스킬 고정본](https://github.com/hostkimjang/korean-dev-writing-skills/tree/372622959b7561427b111b4d1f528ec80239b3df/skills/korean-dev-writing)

**같은 기존 입력으로 현재 스킬 적용 문서를 새로 생성했습니다.** 미적용과 이전 적용 문서는 과거 원문을 그대로 사용했습니다. 모든 조건을 같은 시점에 다시 생성한 실험이 아니며, 생성 시점과 단회 생성의 변동을 스킬 효과에서 분리할 수 없습니다.

생성에 사용한 스킬의 여섯 파일은 마지막 문구 보완까지 완료된 배포본과 바이트 단위로 일치합니다. 작성 중 스킬을 바꾸거나 생성 결과를 후편집하지 않았습니다. 입력·버전·원문·검토 기록은 [실행 프로토콜](../evaluations/runs/2026-11-03-v0.3.0-refresh/protocol.md)과 [해시 기록](../evaluations/runs/2026-11-03-v0.3.0-refresh/manifest.json)에 연결했습니다.

기존 6개 사례와 읽기 흐름 점검 2개 사례의 **현재 적용본 8개**를 새로 작성했습니다. 미적용·이전 적용·현재 적용의 전문은 [HTML 비교 화면](comparisons/index.html)에 들어 있습니다. 다운로드해 브라우저에서 열면 사례와 비교할 이전 조건을 선택할 수 있습니다.

## 한눈에 보는 결과

| 사례 | 미적용 원문 | 이전 적용 원문 | 현재 v0.3.0 |
| --- | ---: | ---: | ---: |
| [CLI README](#cli_readme) | [1,981자](../evaluations/runs/2026-11-03/outputs/baseline/01_cli_readme.md) | [1,389자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/01_cli_readme.md) | [1,600자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/01_cli_readme.md) |
| [이벤트 수집 아키텍처](#event_architecture) | [4,233자](../evaluations/runs/2026-11-03/outputs/baseline/02_event_architecture.md) | [2,190자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/02_event_architecture.md) | [3,335자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/02_event_architecture.md) |
| [진단 PR](#investigation_pr) | [1,032자](../evaluations/runs/2026-11-03/outputs/baseline/03_investigation_pr.md) | [981자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/03_investigation_pr.md) | [1,013자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/03_investigation_pr.md) |
| [장애 대응 절차](#incident_runbook) | [3,187자](../evaluations/runs/2026-11-03/outputs/baseline/04_incident_runbook.md) | [2,186자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/04_incident_runbook.md) | [2,337자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/04_incident_runbook.md) |
| [중복 판정 저장소 ADR](#storage_adr) | [3,481자](../evaluations/runs/2026-11-03/outputs/baseline/05_storage_adr.md) | [1,948자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/05_storage_adr.md) | [2,199자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/05_storage_adr.md) |
| [문단 교정](#paragraph_edit) | [364자](../evaluations/runs/2026-11-03/outputs/baseline/06_paragraph_edit.md) | [363자 · v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/06_paragraph_edit.md) | [361자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/06_paragraph_edit.md) |
| [색인 갱신 온보딩](#long_onboarding_index_refresh) | [7,687자](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/long-document.md) | [4,994자 · v0.2.1](../evaluations/runs/2026-11-03-reading-flow/outputs/v0.2.1/long-document.md) | [4,798자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/07_index_onboarding.md) |
| [짧은 관측 PR](#short_investigation_wait_log) | [396자](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/short-pr.md) | [398자 · v0.2.1](../evaluations/runs/2026-11-03-reading-flow/outputs/v0.2.1/short-pr.md) | [397자](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/08_short_log_pr.md) |

글자 수는 공백·개행·Markdown 문법·마지막 개행을 포함한 Unicode 문자 수입니다. 길이 감소 자체를 개선 점수로 환산하지 않습니다. 현재 출력에 이전의 20점 점수를 붙이지 않았습니다.

정확한 설명도 더 길어질 수 있고, 짧아져도 탐색이 불편해질 수 있습니다. 아래에서는 각 사례의 유지된 조건과 실제 배치·표현 차이를 함께 기록합니다.

<a id="cli_readme"></a>

## CLI README

현재본은 설치·도움말·첫 실행을 한 흐름으로 묶고, 입력 오류와 버전 제약을 별도 제목으로 나눴습니다. v0.2.0보다 설명이 늘었으며, 미적용본에 있던 완성된 파일 저장 명령 예시는 줄었습니다.

**확인한 구성과 표현**

- 현재본의 「설치와 첫 실행」은 세 단계로 이어집니다. 입력 파일의 전제와 첫 명령의 결과를 해당 단계에서 확인할 수 있습니다.
- 미적용·이전·현재본 모두 요구 Python 버전과 실제 검증 환경을 구분합니다. 현재본은 오류 처리와 0.4.2의 기능 제약을 다른 제목에서 찾게 합니다.

**함께 볼 한계**

- 미적용본에는 --output을 포함한 완성된 저장 명령이 있습니다. 현재본은 사용 형식과 설명으로 저장 방법을 전달하므로, 그대로 복사할 예제를 찾는 독자에게는 미적용본의 장점도 있습니다.
- 현재본은 INPUT의 필수 여부와 덮어쓰기 동작을 표와 본문에서 반복합니다. v0.2.0의 1,389자에서 1,600자로 늘어난 만큼 모두 새로운 정보를 제공하는 것은 아닙니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 설치 버전, 필수 입력 경로, 기본 심각도, 출력 파일 덮어쓰기, 잘못된 JSON 행과 파일 읽기 실패의 구분에 치명적 오류가 없습니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-core.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/01_cli_readme.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/01_cli_readme.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/01_cli_readme.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/01_cli_readme.md)

<a id="event_architecture"></a>

## 이벤트 수집 아키텍처

현재본은 역할·정상 흐름·응답·장애·중복 처리 순으로 설명합니다. 장애 표 바로 뒤에서 재소비와 저장 상태의 관계를 다시 풀어 주지만, 202의 의미와 중복 처리 설명에는 반복과 떨어진 참조가 남아 있습니다.

**확인한 구성과 표현**

- 현재본의 장애 표 뒤에는 「offset이 커밋되지 않았다는 사실만으로 데이터베이스에도 이벤트가 없다고 판단할 수는 없습니다」라는 해석이 붙습니다. 표의 마지막 장애와 운영상 판단을 연결합니다.
- 데이터베이스 기록 뒤 offset을 커밋하는 순서를 한 단계 안에서 명시하고, API 수락과 최종 저장 완료를 구분합니다. 미적용·v0.2.0에도 있던 기술적 경계는 유지됩니다.

**함께 볼 한계**

- 현재본은 v0.2.0의 2,190자에서 3,335자로 늘었습니다. 설명 연결이 추가됐지만 202의 의미는 도입·처리 흐름·응답 표에서 겹칩니다.
- 클라이언트 재시도 절의 「뒤에서 설명하는」 중복 처리까지 읽으려면 장애 설명을 지나야 합니다. 필요한 정보가 모두 한곳에 모인 결과는 아닙니다.
- 미적용본도 기록과 offset 사이의 중단 구간, 추가 저장 행 방지의 범위, 운영 판단을 설명합니다. 이 원리가 현재본에서 처음 생긴 것처럼 평가하지 않습니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 202를 저장 완료로 바꾸지 않았고, API의 중복 제거·exactly-once·미확정 복구 시간을 보장하지 않습니다. 동일 논리 이벤트의 event_id 유지와 DB 쓰기 후 offset 커밋 순서도 유지합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-long.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/02_event_architecture.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/02_event_architecture.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/02_event_architecture.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/02_event_architecture.md)

<a id="investigation_pr"></a>

## 진단 PR

현재본은 변경 목적을 먼저 제시하고, 검증 완료 항목과 미실시 항목을 한 제목 아래 구분합니다. 원인 미확정과 진단 전용 범위는 세 조건에 모두 있어, 큰 품질 차이를 주장할 근거는 작습니다.

**확인한 구성과 표현**

- 현재본은 첫 문장에서 원인 조사를 위한 진단 로그 추가라는 목적과 대상 경로를 제시합니다.
- 「검증 결과와 남은 확인 사항」에서 로컬 테스트 통과와 스테이징·성능 미검증을 구분합니다. 배포 후 조사 계획과 리뷰 요청도 별도 제목으로 찾을 수 있습니다.

**함께 볼 한계**

- 관측과 TTL 가설의 구분, 진단 필드와 설정, 테스트의 한계는 미적용·v0.2.0에도 있습니다. 현재본이 처음 확보한 사실 정확성으로 보지 않습니다.
- 해결 수정이 없다는 설명은 배경에, 네 가지 불변 동작은 다음 절에 있습니다. 변경 범위를 확인하려면 두 위치를 함께 읽습니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 운영 관측을 안정적 재현으로, TTL 가설을 확정 원인으로, 진단 로그를 문제 해결로 바꾸지 않았습니다. 테스트 결과와 계획, 민감 내용 미기록 조건도 유지합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-core.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/03_investigation_pr.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/03_investigation_pr.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/03_investigation_pr.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/03_investigation_pr.md)

<a id="incident_runbook"></a>

## 장애 대응 절차

현재본은 금지 조치를 시작 부분에 두고, 각 명령 앞에서 진행 조건을 확인하게 합니다. v0.2.0에서도 주요 조건은 가까이 배치돼 있었으며, 이번에는 복구 판단을 위한 반복 조회를 더 직접 설명합니다.

**확인한 구성과 표현**

- 미적용본 마지막에 있던 큐 삭제·offset 초기화·강제 종료 금지를 현재본은 첫 점검 전에 알립니다. 이 배치는 이전 v0.2.0에도 있던 장점입니다.
- 현재본은 롤백 실패 시 이관을 설명한 다음, 성공한 경우에만 재개한다는 조건과 resume 명령을 바로 이어 둡니다.
- 복구 확인 절은 queue inspect를 다시 실행해 oldest_age_seconds의 변화를 비교하라고 명시합니다. 단일 관측과 감소 추세를 혼동하지 않게 하는 설명입니다.

**함께 볼 한계**

- 미적용본에는 모든 이관 사유와 중단 행동을 모은 표가 있습니다. 현재본은 각 단계에 조건을 배치하므로 절차를 따라가기와 이관 사유만 재탐색하기 사이에 차이가 있습니다.
- v0.2.0보다 151자 늘었습니다. state=paused와 inflight=0을 다음 단계 입구에서 반복하는 것은 실행 전 확인 기능이 있으므로 일괄 삭제 대상으로 보지 않습니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 배포 시점·current/stable 조건, 두 일시정지 조건, 5분 이관, 롤백 성공 후에만 재개, 두 복구 조건, 10분 이관과 반복 롤백 금지를 유지합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-long.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/04_incident_runbook.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/04_incident_runbook.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/04_incident_runbook.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/04_incident_runbook.md)

<a id="storage_adr"></a>

## 중복 판정 저장소 ADR

현재본은 제안과 근거를 도입에 제시하고 새 키·중복 키·DB 실패를 병렬 규칙으로 나눕니다. 보존 정책과 성능 미검증은 유지했지만, 보존 조건을 여러 절에서 다시 설명하는 부담도 남습니다.

**확인한 구성과 표현**

- 미적용본의 번호 목록은 기록 생성 뒤 새 키·중복 키를 차례로 처리하는 것처럼 잠깐 읽힐 수 있습니다. 현재본은 세 경우를 병렬 항목으로 제시해 분기를 구별합니다.
- 현재본의 비교 표 바로 뒤에는 과거 이벤트 재수집과 원자적 처리를 근거로 PostgreSQL을 제안한 이유가 이어집니다. 표와 선택 이유를 연결합니다.

**함께 볼 한계**

- 보존 정책은 배경·대안 표·제안 이유·감수할 점·승인 항목에 등장합니다. 일부는 의사결정에 필요한 재확인이지만 반복이 모두 제거된 것은 아닙니다.
- v0.2.0은 비용과 보장 범위를 같은 절에서 찾을 수 있습니다. 현재본에서는 보존 조건이 여러 위치에 흩어져 있고 분량도 1,948자에서 2,199자로 늘었습니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 아직 제안 상태이며 복합 키, 같은 DB 트랜잭션, 중복 키의 미생성, 503과 동일 키 재시도, Redis TTL·키 유실의 한계, 미정 보존 정책과 성능 미검증을 유지합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-long.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/05_storage_adr.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/05_storage_adr.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/05_storage_adr.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/05_storage_adr.md)

<a id="paragraph_edit"></a>

## 문단 교정

세 조건의 의미와 문단 구성이 거의 같습니다. 현재본의 작은 표현 차이를 독해 품질의 뚜렷한 향상으로 확대하지 않습니다.

**확인한 구성과 표현**

- 현재본은 상한의 정의 바로 뒤에 실제 반환 수가 더 적을 수 있다는 한계를 둡니다. 이전 v0.2.0도 같은 배치를 사용합니다.
- 세 조건 모두 설정 범위·커서와 종료·검증 버전을 세 본문 문단으로 정리하고, 요청하지 않은 제목이나 편집 해설을 덧붙이지 않습니다.

**함께 볼 한계**

- 「한 요청」과 「한 번의 요청」, 지시어의 차이 정도로 v0.2.0 대비 개선을 판정할 근거는 작습니다.
- 현재본의 「이 값을 설정하면」보다 v0.2.0의 「이 값으로 요청하면」이 요청과 오류 응답의 관계를 더 직접 드러냅니다. 현재본의 표현을 치명적인 기술 오류로 보지는 않습니다.

**사실·조건 대조:** 세 조건 모두 필수 명제를 보존합니다. 상한과 실제 반환 수, 기본값과 허용 범위, 0의 오류 처리, 커서 조건과 기존 필터 유지, 확인·미확인 버전을 유지합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-core.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/06_paragraph_edit.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/06_paragraph_edit.md) · [v0.2.0](../evaluations/runs/2026-11-03/outputs/revised/06_paragraph_edit.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/06_paragraph_edit.md)

<a id="long_onboarding_index_refresh"></a>

## 색인 갱신 온보딩

현재본은 접수·검증·활성 판 전환을 먼저 구분하고, 단계별 설명 뒤에 검색 결과·중단·재시도 판단을 연결합니다. 이전 v0.2.1보다 짧아졌지만, 특정 예외와 접수 거절 응답을 찾는 위치에는 아쉬움이 남습니다.

**확인한 구성과 표현**

- 현재본은 대기/구축, 검증, 반영/완료를 소제목으로 나누고 각 단계에서 무엇이 확인되는지 설명합니다. 상태 이름만 나열하지 않고 후보와 활성 판의 관계를 이어 줍니다.
- 현재본은 기존 판을 계속 사용한다는 설명의 전제가 이미 활성 판이 있는 자료집임을 다시 밝힙니다. 첫 갱신에는 「색인 준비 안 됨」이 반환되며 빈 목록과 다르다는 조건을 유지합니다.
- 「다음 작업은 종료 상태를 확인한 뒤 요청한다」에서 중단 요청 수락, 실제 중단, 새 접수 가능 시점을 연결합니다. 미적용·v0.2.1에도 이 관계가 있었으며 현재본에서는 실패·중단 절 안의 독립 소제목으로 찾습니다.

**함께 볼 한계**

- 첫 갱신 예외는 「완료 상태와 실제 검색 결과를 함께 읽기」 안에 있습니다. v0.2.1의 「실패하거나 첫 갱신이 끝나지 않았을 때」처럼 제목에서 해당 예외가 바로 보이지는 않습니다.
- 접수 절에는 진행 중 작업이 있으면 새 작업을 받지 않는다고 적지만, 「진행 중 작업 있음」·현재 접수 번호·새 번호 미생성이라는 응답 세부는 중단 절에 있습니다. 일반 접수의 거절 응답을 찾으려면 뒤를 읽어야 합니다.
- 현재본의 반영 대기 설명에도 기존 활성 판을 사용하는 문장이 있고, 기존 판이 있는 자료집이라는 일반 전제는 다음 절에서 다시 밝힙니다. 모든 조건을 각 문장에 붙인 결과는 아닙니다.
- 「완료를 확인한 뒤 검색 요청을 시작」하라는 안내는 새 판을 확인하는 절차입니다. 사람이 완료를 조회하는 행위가 판 선택의 필수조건인 것은 아니며, 실제 기준은 전환 확정과 검색 시작의 선후입니다.

**사실·조건 대조:** 익명 검토에서 세 조건 모두 문서 전체 기준으로 원자료 L01~L20을 보존했습니다. 고정된 원본, 전환 확정과 요청 시작 시점, 첫 갱신의 예외, 중단 표시 후 활성화 금지, 같은 원본으로 처음부터 재시도, 미확정 운영 정책을 유지합니다. 부분 조회의 전제 위치와 작은 모호함은 별도로 기록했습니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-onboarding.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/07_index_onboarding.md) · [미적용](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/long-document.md) · [v0.2.1](../evaluations/runs/2026-11-03-reading-flow/outputs/v0.2.1/long-document.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/07_index_onboarding.md)

<a id="short_investigation_wait_log"></a>

## 짧은 관측 PR

현재본은 관측과 실제 영향의 미확정을 첫 문단에 모으고 세 문단 안에서 변경과 미검증 상태를 설명합니다. 분량은 거의 같으며, 짧게 쓰는 과정에서 서비스명과 추론 한계의 이유가 압축됐습니다.

**확인한 구성과 표현**

- 현재본은 기존 로그의 순서 관측과 원인·실제 영향·빈도의 미확정을 같은 첫 문단에 둡니다. 추가 로그는 두 번째, 수행하지 못한 검증은 세 번째 문단입니다.
- 진단 설정이 켜졌을 때만 기록한다는 조건과 기록 필드의 범위를 명시합니다. 250~400자 정도라는 요청 안에서 불필요한 목차를 만들지 않습니다.

**함께 볼 한계**

- 현재본은 서비스명을 생략했습니다. 실제 영향이 불명확하다는 결론은 유지하지만, 「로그 이름과 순서만으로 판단할 수 없다」는 구체적인 근거의 한계는 직접 적지 않습니다.
- 세 조건 모두 항목이 언제 남고 사라졌는지 비교하려는 세부 목적을 압축합니다. 처리 동작 불변의 포괄 요약은 유지되지만, 모든 맥락을 완전하게 옮겼다는 평가는 피합니다.
- 마지막 개행을 포함하면 397자, 제외하면 396자입니다. 미적용 396자·이전 398자와 거의 같아 분량으로 개선을 설명할 수 없습니다.

**사실·조건 대조:** 원인 확정·해결 완료·수행하지 않은 검증의 성공 보고는 없습니다. 익명 검토는 현재본의 서비스명, 세부 비교 목적, 로그 이름·순서라는 추론 한계 설명을 부분보존으로 구분했습니다. 이를 치명적 왜곡 없음과 별도로 기록합니다. ([익명 검토](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/review-core.md))

원자료: [같은 입력](../evaluations/runs/2026-11-03-v0.3.0-refresh/inputs/08_short_log_pr.md) · [미적용](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/short-pr.md) · [v0.2.1](../evaluations/runs/2026-11-03-reading-flow/outputs/v0.2.1/short-pr.md) · [현재 v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/08_short_log_pr.md)

## 긴 본문을 한 페이지에서 비교하기

- [아키텍처·ADR·장애 대응 절차 전문](comparisons/long-documents.md)
- [색인 갱신 온보딩·짧은 관측 PR 전문](comparisons/reading-flow.md)
- [8개 사례를 나란히 보는 HTML 파일](comparisons/index.html)

## 검토 방법과 한계

각 현재 문서는 별도의 새 컨텍스트에서 입력과 스킬만 읽고 한 번 작성했습니다. 생성자는 이전 출력·기대 답·평가 기준을 받지 않았습니다. 작성과 검토에는 같은 세션 계열 모델을 사용했으며 정확한 배포 식별자와 샘플링 설정은 노출되지 않았습니다.

검토자는 무작위 라벨과 순서의 세 문서를 원자료와 대조했습니다. 스킬이나 조건 대응표는 검토가 끝나기 전에 공개하지 않았습니다. 문서별 필수 사실과 구체적인 장단점을 기록했으며, 이전 점수를 재사용하거나 새 20점 합계를 만들지 않았습니다. 검토자가 원자료를 함께 보았으므로 실제 독자의 독해·기억 시험이 아닙니다.

실제 독자의 이해도·지연 회상·읽는 시간·피로, Claude·Gemini별 효과, 여러 번 생성했을 때의 변동은 측정하지 않았습니다. 모든 사례는 공개 가능한 가상 자료이며, 본문의 설치·운영 명령을 실제 서비스에서 실행한 결과가 아닙니다.

- [실행 프로토콜](../evaluations/runs/2026-11-03-v0.3.0-refresh/protocol.md)
- [파일 해시와 생성·검토 기록](../evaluations/runs/2026-11-03-v0.3.0-refresh/manifest.json)
- [익명 조건 대응표](../evaluations/runs/2026-11-03-v0.3.0-refresh/reviews/condition-mapping.json)
- [v0.2.0 당시 점수와 보고서](evaluation-v0.2.0.md)
- [리서치와 채택한 원칙](reading-research.md)
