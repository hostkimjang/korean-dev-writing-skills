# river-worker 적체 알람 대응 절차

`WorkerQueueAgeHigh` 알람이 울리면 `river-events` 큐와 `river-worker` 상태를 확인하고, 배포 직후 적체가 시작됐는지 판단합니다. 알람만으로 배포를 원인으로 확정하지 마세요. **현재 배포 직후부터 적체가 시작됐고 `current`와 `stable`이 다를 때만 롤백합니다.**

## 1. 큐, worker, 배포 상태 확인

알람 발생 시각을 기록한 뒤 다음 명령을 실행합니다.

큐 상태와 가장 오래된 작업의 대기 시간을 확인합니다.

```bash
opsctl queue inspect river-events
```

- `pending`: 대기 중인 작업 수
- `oldest_age_seconds`: 가장 오래된 작업의 대기 시간
- `consumer_state`: 큐 소비 상태

worker 상태와 처리 중인 작업 수를 확인합니다.

```bash
opsctl worker status river-worker
```

- `state`: worker 상태
- `inflight`: 처리 중인 작업 수

현재 배포와 복구 대상 배포를 확인합니다.

```bash
opsctl deploy show river-worker
```

- `current`: 현재 배포
- `stable`: 온콜이 복구 대상으로 사용하도록 미리 지정한 배포
- `changed_at`: 배포 변경 시각

명령 결과를 기록하고, 적체 시작 시각을 확인해 `changed_at`과 비교합니다. 알람 발생 시각을 적체 시작 시각으로 대신하지 마세요. 현재 배포 직후부터 적체가 시작됐는지 확인하지 못했다면 다음 단계에서 롤백 대상에서 제외합니다.

## 2. 롤백 여부 판단

| 확인 결과 | 다음 행동 |
| --- | --- |
| 현재 배포 직후부터 적체가 시작됐고, `current`와 `stable`이 다름 | 3단계에서 worker를 일시정지합니다. |
| 배포 직후부터 적체가 시작됐다는 조건을 확인하지 못함 | 롤백하지 않고 플랫폼 온콜에 관찰 결과를 전달합니다. |
| `current`와 `stable`이 같거나 두 값을 확인하지 못함 | 롤백하지 않고 플랫폼 온콜에 관찰 결과를 전달합니다. |

롤백 조건을 충족해도 worker가 작업을 처리 중이면 바로 롤백하지 마세요. 먼저 아래 절차로 일시정지 완료와 처리 중 작업 종료를 확인해야 합니다.

## 3. worker 일시정지 및 처리 중 작업 종료 확인

롤백 조건을 모두 확인한 경우에만 일시정지를 요청하고, 요청 시각을 기록합니다.

```bash
opsctl worker pause river-worker
```

이 명령의 반환은 **일시정지 요청을 접수했다는 뜻**입니다. 이미 처리 중인 작업은 계속 진행될 수 있으므로, 명령이 반환됐다고 바로 롤백하지 마세요.

다음 명령을 반복 실행해 상태를 확인합니다.

```bash
opsctl worker status river-worker
```

**`state=paused`와 `inflight=0`을 모두 확인한 다음에만** 4단계로 이동합니다. 어느 한 조건만 충족한 상태에서는 롤백하지 않습니다.

pause 요청 후 **5분이 지나도 두 조건을 모두 충족하지 못하면** 롤백하지 않고 플랫폼 온콜에 이관합니다. 처리 중인 작업을 강제로 종료하지 마세요.

## 4. stable로 롤백하고 소비 재개

worker 상태가 `state=paused`, `inflight=0`인지 확인한 뒤, 미리 지정된 `stable` 배포로 롤백합니다.

```bash
opsctl deploy rollback river-worker --to stable
```

롤백 명령 결과를 확인하고 기록합니다.

- **성공:** 아래 명령으로 소비를 재개합니다.
- **실패:** 소비를 재개하지 않습니다. worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관합니다.

롤백 명령이 성공한 경우에만 다음 명령을 실행합니다.

```bash
opsctl worker resume river-worker
```

재개 시각과 명령 결과를 기록하고 5단계에서 큐 상태를 확인합니다. 롤백이나 재개 명령이 성공했다는 이유만으로 복구를 선언하지 마세요.

## 5. 복구 여부 확인

재개 후 다음 명령을 반복 실행합니다. 각 확인 시각과 `oldest_age_seconds`를 기록해 이전 값과 비교합니다.

```bash
opsctl queue inspect river-events
```

다음 두 조건을 **모두 확인해야 복구로 판단**합니다.

1. `consumer_state=running`이다.
2. `oldest_age_seconds`가 감소한다.

`consumer_state=running`이어도 대기 시간이 줄지 않으면 복구로 판단하지 않습니다. 한 번 조회한 값만으로 감소 여부를 판단하지 마세요.

재개 후 **10분 동안 개선되지 않으면** 반복 롤백하지 말고 플랫폼 온콜에 이관합니다. 이관 시 마지막 큐 상태와 대기 시간 변화도 함께 전달합니다.

## 6. 플랫폼 온콜 이관

앞 단계에서 이관 조건에 해당하면, 어느 단계에서 멈췄는지와 아래 정보를 전달합니다. 확인하지 못한 항목은 추정해서 채우지 말고 미확인으로 표시합니다.

| 전달 항목 | 기록할 내용 |
| --- | --- |
| 알람 발생 시각 | `WorkerQueueAgeHigh` 발생 시각 |
| 적체 시작 시각 | 확인한 시작 시각 또는 미확인 여부 |
| 배포 정보 | `current`, `stable`, `changed_at` |
| 큐 관찰 결과 | 확인 시각별 `pending`, `oldest_age_seconds`, `consumer_state` |
| worker 상태 | 마지막으로 확인한 `state`, `inflight` |
| 실행 기록 | 실행한 명령과 결과, pause 요청 시각, 재개한 경우 재개 시각 |
| 이관 사유 | 롤백 조건 미충족, pause 요청 후 5분 내 정지 조건 미충족, 롤백 실패, 재개 후 10분간 개선 없음 등 |

## 이 절차에서 실행하지 않는 조치

큐 삭제, offset 초기화, 처리 중 작업 강제 종료는 하지 않습니다. 이 조치는 작업 손실이나 중복을 일으킬 수 있으므로 별도 판단이 필요합니다.
