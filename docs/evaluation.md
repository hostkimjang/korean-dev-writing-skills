# v0.4.0 개발 문서 비교: 의미 보존과 찾아보기

갱신일: 2026-11-03 (Asia/Seoul) · 현재 적용본: **v0.4.0** · [사용한 스킬 고정본](../evaluations/runs/2026-11-03-v0.4.0/snapshots/v0.4.0)

**기존 사례는 같은 입력으로 v0.4.0 적용 문서를 새로 생성했다.** 미적용과 v0.3.0 문서는 과거 원문을 그대로 사용했다. 기존 사례의 모든 조건을 같은 시점에 다시 생성한 실험은 아니며, 생성 시점과 단회 생성의 변동을 스킬 효과에서 분리할 수 없다.

생성에 사용한 스킬의 여섯 파일은 공개한 v0.4.0 스냅샷 및 배포 파일과 바이트 단위로 일치한다. 작성 중 스킬을 바꾸거나 생성 결과를 후편집하지 않았다. 입력·버전·원문·검토 기록은 [실행 프로토콜](../evaluations/runs/2026-11-03-v0.4.0/protocol.md)과 [해시 기록](../evaluations/runs/2026-11-03-v0.4.0/manifest.json)에 연결했다.

기존 6개 사례와 읽기 흐름 점검 2개 사례의 **현재 적용본 8개**를 새로 작성했다. 미적용·v0.3.0·v0.4.0의 전문 24개는 [HTML 비교 화면](comparisons/index.html)에 들어 있습니다. 다운로드해 브라우저에서 열면 사례와 비교 조건을 선택할 수 있다. 새 두 사례의 조건별 전문 4개는 [새 사례 비교](comparisons/transfer-checks.md)에 별도로 실었다.

이번에는 [사용자 전달 리뷰를 대조한 뒤](review-v0.4.0.md) 지침을 보완하고, [필수 의미와 탐색 질문을 고정한 계약](evaluation-contract.md)으로 두 조건을 다시 검토했습니다. 문자열 신호와 의미 판정은 구분합니다.

## 한눈에 보는 결과

| 사례 | 미적용 원문 | 이전 v0.3.0 | 현재 v0.4.0 |
| --- | ---: | ---: | ---: |
| [CLI README](#cli_readme) | [1,981자](../evaluations/runs/2026-11-03/outputs/baseline/01_cli_readme.md) | [1,600자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/01_cli_readme.md) | [1,718자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/01_cli_readme.md) |
| [이벤트 수집 아키텍처](#event_architecture) | [4,233자](../evaluations/runs/2026-11-03/outputs/baseline/02_event_architecture.md) | [3,335자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/02_event_architecture.md) | [2,553자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/02_event_architecture.md) |
| [진단 PR](#investigation_pr) | [1,032자](../evaluations/runs/2026-11-03/outputs/baseline/03_investigation_pr.md) | [1,013자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/03_investigation_pr.md) | [973자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/03_investigation_pr.md) |
| [장애 대응 절차](#incident_runbook) | [3,187자](../evaluations/runs/2026-11-03/outputs/baseline/04_incident_runbook.md) | [2,337자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/04_incident_runbook.md) | [2,741자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/04_incident_runbook.md) |
| [중복 판정 저장소 ADR](#storage_adr) | [3,481자](../evaluations/runs/2026-11-03/outputs/baseline/05_storage_adr.md) | [2,199자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/05_storage_adr.md) | [2,240자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/05_storage_adr.md) |
| [문단 교정](#paragraph_edit) | [364자](../evaluations/runs/2026-11-03/outputs/baseline/06_paragraph_edit.md) | [361자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/06_paragraph_edit.md) | [379자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/06_paragraph_edit.md) |
| [색인 갱신 온보딩](#long_onboarding_index_refresh) | [7,687자](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/long-document.md) | [4,798자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/07_index_onboarding.md) | [4,620자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/07_index_onboarding.md) |
| [짧은 관측 PR](#short_investigation_wait_log) | [396자](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/short-pr.md) | [397자 · v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/08_short_log_pr.md) | [398자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/08_short_log_pr.md) |

글자 수는 공백·개행·Markdown 문법·마지막 개행을 포함한 Unicode 문자 수입니다. 길이 감소 자체를 개선 점수로 환산하지 않는다. 현재 출력에 이전의 20점 점수를 붙이지 않았다.

### 새 계약으로 다시 검토한 결과

| 조건 | 검토 문서 | 필수 의미: 보존 / 부분 / 누락 / 충돌 | 질문: 충분 / 부분 | 치명적 오류 문서 |
| --- | ---: | --- | --- | ---: |
| v0.3.0 | 10 | 147 / 1 / 2 / 0 | 34 / 3 | 0 |
| v0.4.0 | 10 | 150 / 0 / 0 / 0 | 36 / 1 | 0 |

조건마다 같은 필수 의미 150개와 질문 37개를 검토했다. 이 수치는 10개 사례를 세분화한 판정행의 합계이며 품질 총점이나 독자 효과가 아니다. 필수 의미의 판정 차이는 기존 짧은 관측 PR 한 사례에서 발생했다. 새 두 사례에서는 두 버전 모두 필수 의미를 보존했다.

현재 문서에서도 장애 대응 절차의 롤백 명령 절만 보면 5분 대기 한계를 앞 단계에서 더 찾아야 한다. 이 질문은 두 버전 모두 부분 충족으로 남겼다. 모든 필수 의미가 문서 전체에 있다는 판정이 모든 절의 탐색이나 문장 구성이 완전하다는 뜻은 아니다.

근거: [조건별 판정 집계](../evaluations/runs/2026-11-03-v0.4.0/review-summary.json) · [판정 기준과 인용 검사](evaluation-contract.md)

정확한 설명도 더 길어질 수 있고, 짧아져도 탐색이 불편해질 수 있다. 아래에서는 각 사례의 유지된 조건과 실제 배치·표현 차이를 함께 기록한다.

<a id="cli_readme"></a>

## CLI README

필수 기술 사실은 두 버전에서 같다. v0.4.0은 설치와 첫 실행을 나누고 오류 처리 절로 가는 내부 링크를 붙였으며, 원문은 1,600자에서 1,718자로 늘었다.

**확인한 구성과 표현**

- Python 요구 범위와 실제 확인 환경을 설치 절에서 구분한다. 첫 실행에는 입력 경로를 실제 파일 위치로 바꾸라는 안내가 있다.
- 입력 오류를 별도 제목과 표로 찾을 수 있으며, 파일 덮어쓰기와 기본 출력 위치는 같은 옵션 행에 있다.

**함께 볼 한계**

- 파일 저장의 덮어쓰기 조건을 찾으려면 두 버전 모두 첫 실행 예에서 옵션 절로 이동해야 한다. v0.4.0에도 별도 파일 저장 명령 예시는 없다.
- 심각도 목록과 기본값이 표와 아래 문단에 반복된다. 문장형 표와 구절형 표의 차이를 자연스러움의 자동 우열로 평가하지 않았다.

**사실·조건 대조:** 두 버전 모두 필수 의미 11개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-core.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/01_cli_readme.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/01_cli_readme.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/01_cli_readme.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/01_cli_readme.md)

<a id="event_architecture"></a>

## 이벤트 수집 아키텍처

v0.4.0은 저장 장애와 중복 처리를 한 절로 묶었고, 필수 조건을 유지하면서 3,335자에서 2,553자로 줄었다. 이전 문서의 역할·처리 순서 재진술 일부가 줄었다.

**확인한 구성과 표현**

- DB 기록 후 offset 커밋 전 종료와 event_id 유일성 제약을 같은 저장 장애 절에서 확인할 수 있다.
- 202 수락과 최종 저장을 구분하고 DB 성공 뒤 offset을 커밋하는 순서를 유지한다. API 응답과 writer 처리를 별개 단계로 연결한다.

**함께 볼 한계**

- v0.3.0의 표에는 202를 포함한 전체 응답이 있고, v0.4.0은 수락 설명과 오류 코드 표를 나눈다. 전체 응답을 표 하나로 훑는 구성은 이전 문서의 특징이다.
- 같은 event_id 조건과 202의 경계는 여러 진입점에서 반복된다. 필요한 재확인으로 검토했으며, 분량 감소를 실제 읽기 피로 개선으로 해석하지 않는다.

**사실·조건 대조:** 두 버전 모두 필수 의미 11개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-long.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/02_event_architecture.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/02_event_architecture.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/02_event_architecture.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/02_event_architecture.md)

<a id="investigation_pr"></a>

## 진단 PR

원인 가설·관측 변경·실행한 검증의 경계는 두 버전에서 유지된다. v0.4.0은 동작 유지와 해결 수정 제외를 변경 범위 문단에 모았고, 1,013자에서 973자가 됐다.

**확인한 구성과 표현**

- 기존 발송 순서·재시도 횟수·lock TTL·중복 방지 동작을 유지한다는 설명과 해결 수정이 아니라는 범위를 한곳에서 확인한다.
- 완료한 로컬 테스트와 미실시 스테이징·성능 검증을 같은 검증 절에서 구분한다.

**함께 볼 한계**

- v0.3.0은 가설을 읽는 문단에서 해결 수정 제외까지 확인할 수 있고, v0.4.0은 다음 변경 범위 절에서 확인한다. 정보가 모이는 위치가 달라졌다.
- 현재 리뷰 요청은 구체 필드 목록 대신 진단 필드라고 가리킨다. 반복은 줄지만 이 항목만 떼어 읽으면 앞의 필드 목록이 필요하다.

**사실·조건 대조:** 두 버전 모두 필수 의미 13개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-core.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/03_investigation_pr.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/03_investigation_pr.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/03_investigation_pr.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/03_investigation_pr.md)

<a id="incident_runbook"></a>

## 장애 대응 절차

v0.4.0은 초기 조회와 배포 판단을 나누고 마지막 이관 절에 중단 조건을 모았다. 필수 조건은 두 버전 모두 보존하지만 분량은 2,337자에서 2,741자로 늘었다.

**확인한 구성과 표현**

- 알람 발생 시각과 적체 시작 시각을 구분하고, 배포 관련 두 조건이 충족돼야 일시정지 단계로 넘어가게 한다.
- 명령 직전의 state=paused·inflight=0 복합 조건, 롤백 성공 뒤에만 재개하는 조건, 복구 확인과 이관 기준을 유지한다.

**함께 볼 한계**

- 두 버전 모두 롤백 명령 절에서 바로 시작하면 pause 반환의 의미와 요청 후 5분 한계를 앞 단계에서 더 읽어야 한다. 이 탐색 질문은 양쪽 모두 부분 충족이며 문서 전체의 사실 누락과 구분했다.
- 현재 마지막 이관 절은 여러 중단 조건을 긴 한 문장에 묶는다. 독립 조회에 필요한 요약이지만 조건을 분리해 읽어야 하는 부담이 남는다. 길이가 늘어난 사례를 그대로 공개했다.

**사실·조건 대조:** 두 버전 모두 필수 의미 14개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-long.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/04_incident_runbook.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/04_incident_runbook.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/04_incident_runbook.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/04_incident_runbook.md)

<a id="storage_adr"></a>

## 중복 판정 저장소 ADR

v0.4.0은 신규 키·기존 키·DB 실패의 처리를 조건별 표로 제시한다. 제안 상태와 보장 범위는 두 버전에서 같고, 길이도 2,199자와 2,240자로 비슷하다.

**확인한 구성과 표현**

- tenant_id와 event_id의 복합 키, 같은 트랜잭션, 503 뒤 같은 식별자로 재시도하는 조건을 유지한다.
- 미완료 검토와 승인 전 미결 사항을 분리하고, Redis 대안의 TTL·키 유실·저장소 간 원자성 제약을 원자료 범위 안에서 설명한다.

**함께 볼 한계**

- 두 버전 모두 대안 표 다음에 트랜잭션과 운영 이점을 다시 설명한다. 선택 이유를 연결하는 기능이 있으나 표와 겹치는 문장의 편집 여지도 남는다.
- 마지막 승인 조건 표에서 시작하면 실제 비용이 미측정이고 공식 성능 보장이 없다는 직접 설명은 앞 절을 더 읽어야 한다. 현재 문서만의 개선으로 보지 않았다.

**사실·조건 대조:** 두 버전 모두 필수 의미 13개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-long.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/05_storage_adr.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/05_storage_adr.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/05_storage_adr.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/05_storage_adr.md)

<a id="paragraph_edit"></a>

## 문단 교정

문단 교정은 두 버전의 차이가 작다. v0.4.0은 첫 문장에 API 맥락을 붙이고 확인·미확인 버전을 한 문장으로 연결했으며, 361자에서 379자가 됐다.

**확인한 구성과 표현**

- 상한과 실제 반환 수, 허용 범위와 0의 오류, 커서 종료 조건을 유지하며 표나 목록 없이 세 문단으로 작성했다.
- 확인한 버전과 미확인 버전을 구분한다. 다음 페이지 조건과 필터 유지가 담긴 둘째 문단은 두 버전이 같다.

**함께 볼 한계**

- 실질적인 차이는 첫 문장의 맥락 표시와 마지막 문장의 연결 방식이다. 의미 보존과 질문 답변에서 차이를 찾지 못했으며 큰 개선 사례로 소개하지 않는다.

**사실·조건 대조:** 두 버전 모두 필수 의미 9개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-core.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/06_paragraph_edit.md) · [미적용](../evaluations/runs/2026-11-03/outputs/baseline/06_paragraph_edit.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/06_paragraph_edit.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/06_paragraph_edit.md)

<a id="long_onboarding_index_refresh"></a>

## 색인 갱신 온보딩

v0.4.0은 첫 갱신 예외를 제목에 드러내고 시스템의 판 선택과 확인 절차의 목적을 구분해 설명한다. 4,798자에서 4,620자가 됐으며 두 버전 모두 필수 의미 29개를 보존했다.

**확인한 구성과 표현**

- 실패와 첫 갱신의 검색 동작이라는 제목에서 기존 활성 판이 있는 경우와 없는 경우를 함께 찾을 수 있다. 접수 조건과 거절 응답도 한 절에 있다.
- 재시도 절 첫 문장에 실패·중단 대상 조건과 진행 중 작업이 없어야 한다는 조건을 함께 둔다.
- 전환 확정과 검색 시작의 실제 규칙 뒤에 완료 조회의 목적을 설명한다. 이전 문서도 실제 규칙을 보존하므로 시스템 의미의 뒤집힘을 수정했다고 표현하지 않는다.

**함께 볼 한계**

- 식별자·원본 고정·상태 조회 번호는 두 버전 모두 여러 절을 연결해 읽는 부분이 있다. 탐색 시간 자체를 측정하지 않았다.
- 현재 재시도 절의 중단 작업에도 같은 조건이라는 문장은 새 조건을 추가하지 않는 재강조다. 전환점의 반복을 모두 없앤 결과는 아니다.

**사실·조건 대조:** 두 버전 모두 필수 의미 29개를 보존한 것으로 검토했다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-onboarding.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/07_index_onboarding.md) · [미적용](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/long-document.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/07_index_onboarding.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/07_index_onboarding.md)

<a id="short_investigation_wait_log"></a>

## 짧은 관측 PR

짧은 PR은 397자에서 398자로 분량을 거의 유지하면서 대상 서비스명과 로그 이름·순서만으로 판단할 수 없는 이유를 명시했다. 이번 계약의 필수 의미는 v0.3.0에서 보존 14·부분보존 1·누락 2, v0.4.0에서 보존 17로 검토됐다.

**확인한 구성과 표현**

- 관측한 로그 순서와 실제 응답 유실·중복 처리 여부를 첫 문단에서 구분하고, 어느 서비스의 기록인지 밝힌다.
- 환경 미준비, 테스트 미실시, 변경 후 로그 미수집, 가설·변경 동작 미검증은 그대로 남긴다. 두 버전 모두 해결이나 검증 완료를 주장하지 않는다.
- 다음 관측을 위해라는 목적과 생성·제거·만료 진입 기록의 연결을 의미가 같은 축약으로 허용했다. 특정 동사나 개별 처리 조건의 반복을 강제하지 않았다.

**함께 볼 한계**

- v0.3.0에 있던 상세 로그 필드 목록은 현재 본문에서 생략됐다. 이번 계약에서는 선택 정보이지만 필드 자체를 검토할 때는 이전 설명이 더 직접적이다.
- 현재 마지막 문장은 환경·테스트·로그·판단 한계를 길게 연결한다. 조건의 인과는 유지하지만 모든 문장이 짧아진 결과는 아니다. 한 쌍의 결과로 다른 짧은 글에서도 재현될 것이라고 보장하지 않는다.

**사실·조건 대조:** v0.3.0은 필수 의미 17개 중 보존 14·부분보존 1·누락 2; v0.4.0은 필수 의미 17개 중 보존 17로 검토했다. 작은 누락을 사용·운영·검증 판단을 뒤집는 치명적 오류로 확대하지 않았다. ([익명 검토](../evaluations/runs/2026-11-03-v0.4.0/reviews/review-core.md))

입력과 원문: [같은 입력](../evaluations/runs/2026-11-03-v0.4.0/inputs/08_short_log_pr.md) · [미적용](../evaluations/runs/2026-11-03-reading-flow/outputs/no-skill/short-pr.md) · [v0.3.0](../evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/08_short_log_pr.md) · [현재 v0.4.0](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/08_short_log_pr.md)

## 긴 본문을 한 페이지에서 비교하기

- [아키텍처·ADR·장애 대응 절차 전문](comparisons/long-documents.md)
- [색인 갱신 온보딩·짧은 관측 PR 전문](comparisons/reading-flow.md)
- [새 설정배포 안내·썸네일 작업 보고의 두 조건 전문](comparisons/transfer-checks.md)
- [8개 사례를 나란히 보는 HTML 파일](comparisons/index.html)

## 검토 방법과 한계

각 현재 문서는 별도의 새 컨텍스트에서 입력과 스킬만 읽고 한 번 작성했다. 생성자는 이전 출력·기대 답·평가 기준을 받지 않았다. 작성과 검토에는 같은 세션 계열 모델을 사용했으며 정확한 배포 식별자와 샘플링 설정은 노출되지 않았다.

검토자는 무작위 라벨과 순서의 v0.3.0·v0.4.0 두 문서를 원자료 및 사전에 고정한 보존 계약과 대조했습니다. 스킬이나 조건 대응표는 검토가 끝나기 전에 공개하지 않았다. 미적용 원문은 앞선 검토가 있는 참고 자료이며 이번 의미 재검토에는 포함하지 않았다. 필수 의미마다 보존·부분보존·누락·충돌과 근거를 적고, 탐색 질문에는 답의 위치와 국소 조건의 부족을 기록했습니다. 이전 점수를 재사용하거나 새 20점 합계를 만들지 않았다. 검토자가 원자료를 함께 보았으므로 실제 독자의 독해·기억 시험이 아닙니다.

새 설정배포·작업 보고 두 사례에서는 두 조건 모두 이번에 생성했다. 이 사례도 문제 유형을 고려해 설계했고 요청에 일부 구분을 명시했습니다. 실제 독자의 이해도·지연 회상·읽는 시간·피로, Claude·Gemini별 효과, 여러 번 생성했을 때의 변동은 측정하지 않았다. 모든 사례는 공개 가능한 가상 자료이며, 본문의 설치·운영 명령을 실제 서비스에서 실행한 결과가 아닙니다.

- [실행 프로토콜](../evaluations/runs/2026-11-03-v0.4.0/protocol.md)
- [파일 해시와 생성·검토 기록](../evaluations/runs/2026-11-03-v0.4.0/manifest.json)
- [익명 조건 대응표](../evaluations/runs/2026-11-03-v0.4.0/reviews/condition-mapping.json)
- [새 평가 계약 안내](evaluation-contract.md)
- [제안 대조와 v0.4.0 반영](review-v0.4.0.md)
- [v0.3.0 당시 비교 보고서](evaluation-v0.3.0.md)
- [v0.2.0 당시 점수와 보고서](evaluation-v0.2.0.md)
- [리서치와 채택한 원칙](reading-research.md)
