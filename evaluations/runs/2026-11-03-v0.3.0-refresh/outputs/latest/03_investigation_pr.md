## 변경 이유

중복 발송 이슈 #184의 원인을 조사하기 위해 `src/workers/deliver.ts`에 진단 로그를 추가합니다. 운영 로그에서 같은 `job_id`가 두 번 발송된 사례를 확인했지만, 로컬에서는 아직 안정적인 재현 방법을 찾지 못했습니다.

발송 작업이 길어져 lock TTL이 먼저 만료되는 상황이 원인 후보 중 하나입니다. 다만 실제 원인인지는 확인하지 못했으며, 이번 PR에는 중복 발송을 해결하는 수정이 포함되지 않습니다.

## 변경 내용과 범위

진단 로그 `delivery_retry_probe`에 `job_id`, `attempt`, `lock_owner`를 기록합니다. 수신자 주소와 메시지 본문은 기록하지 않습니다.

진단 로그는 `DELIVERY_DIAG_ENABLED=true`일 때만 활성화됩니다. 이 설정의 기본값은 `false`입니다. 발송 순서, 재시도 횟수, lock TTL 값, 중복 방지 동작은 변경하지 않습니다.

## 검증 결과와 남은 확인 사항

`tests/workers/deliver-log.test.ts`에서 진단 로그의 조건부 출력과 기록 필드를 검증했습니다. 로컬에서 다음 명령을 실행했으며 통과했습니다.

```bash
pnpm exec vitest run tests/workers/deliver-log.test.ts
```

스테이징에서 실제 발송 경로는 검증하지 않았습니다. 진단 로그를 켰을 때의 처리량과 지연 변화도 아직 측정하지 않았습니다.

## 배포 후 확인 계획

배포 후 `DELIVERY_DIAG_ENABLED=true`로 진단 로그를 켜고, 중복 사례의 `job_id`, `attempt`, `lock_owner`를 대조할 예정입니다. 조사 결과를 이슈 #184에 정리한 뒤 수정 방향을 결정하려 합니다.

## 리뷰 요청

- `job_id`, `attempt`, `lock_owner`가 중복 사례를 구분하기에 충분한지 확인해 주세요.
- 수신자 주소나 메시지 본문이 로그에 섞일 여지가 없는지 확인해 주세요.
