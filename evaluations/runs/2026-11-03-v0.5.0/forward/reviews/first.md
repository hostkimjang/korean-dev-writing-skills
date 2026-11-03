# v0.5.0 새 작성본 원자료 대조 검토

## 판정

필수 요구사항 **52개 모두 preserved**, 선택 요구사항 **1개 preserved**, 독자 질문 **15개 모두 sufficient**다. 문서 세 개의 `hard_fail`은 모두 `false`이며, 실제 본문 수정을 요구할 `open_issues`는 없다. 지정된 보완 확인 **5개 모두 resolved**다.

이 검토는 제공된 review-packet의 원자료·사용자 요청·새 본문 세 개를 직접 대조했다. 스킬과 다른 리뷰 파일은 읽지 않았고, 본문은 수정하지 않았다. 과거 문서와 같은 절·표를 요구하지 않고 현재 구성에서 필요한 조건과 행동을 찾을 수 있는지 판단했다.

| 문서 | 필수 요구사항 | 선택 요구사항 | 질문 | 보완 확인 | 본문 문자 수 |
| --- | --- | --- | --- | --- | --- |
| incident_runbook | 14/14 preserved | 없음 | 2/2 sufficient | 2/2 resolved | 1,952 |
| short_investigation_wait_log | 17/17 preserved | 1/1 preserved | 6/6 sufficient | 1/1 resolved | 400 |
| v04_new_a_config_rollout | 21/21 preserved | 없음 | 7/7 sufficient | 2/2 resolved | 1,799 |

문자 수는 공백·줄바꿈·Markdown 및 마지막 줄바꿈을 포함한 Unicode 문자 수다. 짧은 PR과 설정배포 안내는 각각 250~400자, 1,200~1,800자 정도라는 요청 범위 안이다. 장애 절차의 600~1,000자는 원자료에서 `scoring: false`인 제안 범위이며, 그 초과를 필수 의미 결함으로 판정하지 않았다.

## 핵심 근거

### 장애 운영 절차

일시정지 요청의 반환이 접수라는 설명, `state=paused`와 `inflight=0`의 동시 확인, pause 요청 후 5분 경과 시 롤백 없이 이관하는 조건이 롤백 명령과 같은 절에 있다. 재개 절도 롤백 성공을 첫 문장에서 다시 밝히고 두 복구 조건 및 재개 후 10분 기준을 유지한다.

이관 기준은 마지막 OR 문장에 모으지 않고 해당 단계마다 조건과 행동을 분리해 제시한다. 롤백 실패의 일시정지 유지와 개선 부재 시 반복 롤백 금지를 찾을 수 있으며 이관 정보 목록도 남아 있다. 마지막 통합 표가 없어도 `FIX-RUNBOOK-ESCALATION`의 탐색 문제는 해결된다.

### 짧은 PR 설명

400자 안에서 서비스명, 기존 개발용 합성 로그라는 출처, 변경 경로, 세 로그 시점, 비교 목적과 미확정 원인·재현 부재를 유지한다. `diag_waits` 조건, `ticket_ref`, `elapsed_ms`, 남은 대기 항목 수와 요청 본문 제외도 모두 복원했다.

응답 유실·중복 처리 판단 불가를 로그 이름·순서라는 증거 한계와 연결하며 빈도 미집계를 남겼다. 로컬 합성 요청 환경 미준비 때문에 테스트·변경 후 로그 수집을 못 했다는 이유와 미검증 상태가 마지막 문단에서 이어진다. 해결이 확인된 수정이나 변경 후 검증 결과로 확대하지 않는다.

### 설정배포 안내

예약 충돌의 원인, HTTP 409와 정확한 `PENDING_RELEASE_EXISTS` 본문, 활성화 또는 예약 취소 후 재요청 가능 조건이 같은 표 행에 있다. 초안 준비 절은 두 입력을 이름으로 명시하고 수정 뒤 재검사를 연결한다.

첫 적용 예외의 입력과 세 공통 접수 조건, 일반 적용의 서버 접수 시각 기준 5분 경계·UTC, 접수와 실제 전환의 구분, 조회의 비작동성, ACTIVE 이후 복구와 평가 재개 조건을 보존한다. 일반 시각 경계는 정상 절차 문단에서, 정확한 오류값은 바로 다음 거절 표에서 찾는 구성이다. 두 위치에 동일한 기준점과 거절 조건이 유지되어 이를 실행 조건 누락으로 판정하지 않았다.

## 필요한 수정

현재 본문에서 원자료 대조에 근거해 요구할 수정은 없다. 모든 보완 확인의 근거와 각 요구사항·질문의 정확한 연속 인용은 `first.json`에 기록했다. 이 판정은 원자료 보존과 문서 탐색의 독립 검토이며 사람 대상 사용성 실험의 결과를 주장하지 않는다.

## 무결성 검사

다음 명령을 실행했고 종료 코드는 0이다.

```sh
python scripts/check_claims.py --output-index evaluations/runs/2026-11-03-v0.5.0/forward/output-index.json --reviews evaluations/runs/2026-11-03-v0.5.0/forward/reviews/first.json
```

```text
PASS: 10 contract cases, 3 frozen outputs, 3 review records.
Structure, references, hashes, and exact quotations only. Literal presence/absence is not a semantic verdict or hard_fail.
```

이 검사는 구조·참조·해시·정확한 인용을 확인한다. 의미 보존·독자 질문·보완 여부의 판정은 위 대조 검토에서 별도로 수행했다. `repair_checks`의 인용도 작성 시 본문 연속 부분문자열 여부를 직접 검사했다.
