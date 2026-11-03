# river-worker 적체 장애 대응 절차

`WorkerQueueAgeHigh` 알람이 울리면 이 절차로 `river-worker`와 작업 큐 `river-events`를 점검합니다. 알람만으로 배포가 원인이라고 확정할 수는 없습니다. 먼저 적체와 배포 시점을 확인한 뒤, 롤백 조건을 충족할 때만 일시정지·롤백·재개를 진행합니다.

이 절차에서는 **큐 삭제, offset 초기화, 처리 중인 작업 강제 종료를 하지 않습니다.** 작업 손실이나 중복을 일으킬 수 있으므로 별도 판단이 필요합니다.

## 1. 현재 상태를 확인하고 롤백 여부를 판단합니다

알람 발생 시각과 적체 시작 시각을 기록하고, 다음 명령으로 큐·worker·배포 상태를 확인합니다.

```bash
opsctl queue inspect river-events
opsctl worker status river-worker
opsctl deploy show river-worker
```

| 점검 대상 | 확인할 출력 |
| --- | --- |
| 큐 `river-events` | `pending`, `oldest_age_seconds`, `consumer_state` |
| worker `river-worker` | `state`, `inflight` |
| 배포 | `current`, `stable`, `changed_at` |

`stable`은 온콜이 복구 대상으로 사용할 수 있도록 미리 지정된 배포입니다. `changed_at`과 적체 시작 시각을 비교하고, `current`와 `stable`이 다른지 확인합니다.

**다음 두 조건을 모두 확인한 경우에만 2단계로 진행합니다.**

- 현재 배포 직후부터 적체가 시작됐습니다.
- `current`와 `stable`이 다릅니다.

조건을 확인할 수 없거나 `current`와 `stable`이 같으면 이 절차에서 롤백하지 않습니다. 관찰 결과를 플랫폼 온콜에 전달합니다. 이관할 정보는 5단계를 참고합니다.

## 2. 일시정지를 요청하고 처리 중인 작업이 끝났는지 확인합니다

1단계의 롤백 조건을 충족했다면 일시정지를 요청하고 요청 시각을 기록합니다.

```bash
opsctl worker pause river-worker
```

이 명령의 반환은 **일시정지 요청을 접수했다는 뜻**입니다. 이미 처리 중인 작업은 계속 진행될 수 있으므로, 명령이 반환됐다는 이유만으로 롤백하지 않습니다.

다음 명령으로 상태를 확인합니다.

```bash
opsctl worker status river-worker
```

**`state=paused`와 `inflight=0`을 모두 확인한 다음에만** 3단계로 진행합니다. 아직 두 조건을 충족하지 않았다면 상태를 다시 확인합니다.

일시정지 요청 후 **5분이 지나도 두 조건을 충족하지 못하면 롤백하지 않고 플랫폼 온콜에 이관합니다.** 처리 중인 작업을 강제로 종료하지 않습니다.

## 3. stable로 롤백하고 성공한 경우에만 소비를 재개합니다

`state=paused`와 `inflight=0`을 모두 확인했다면 롤백합니다.

```bash
opsctl deploy rollback river-worker --to stable
```

롤백 명령의 결과를 확인합니다. **롤백에 실패하면 worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관합니다.** 소비를 재개하지 않습니다.

**롤백 명령이 성공한 경우에만** 다음 명령으로 소비를 재개하고, 재개 시각을 기록합니다.

```bash
opsctl worker resume river-worker
```

## 4. 소비 상태와 적체 변화를 확인해 복구 여부를 판단합니다

소비를 재개한 뒤 다음 명령으로 큐 상태를 확인합니다. 이후에도 명령을 다시 실행해 `oldest_age_seconds`의 변화를 비교합니다.

```bash
opsctl queue inspect river-events
```

다음 두 조건을 **모두 확인해야 복구로 판단합니다.**

- `consumer_state=running`입니다.
- `oldest_age_seconds`가 감소합니다.

소비가 재개됐다는 사실만으로 복구로 판단하지 않습니다. **재개 후 10분 동안 개선되지 않으면 반복 롤백하지 말고 플랫폼 온콜에 이관합니다.**

## 5. 플랫폼 온콜에 관찰 결과와 실행 내역을 전달합니다

앞 단계에서 이관 조건에 해당하면 다음 정보를 전달합니다.

- 알람 발생 시각
- 적체 시작 시각. 확인하지 못했다면 미확인임을 표시합니다.
- 확인한 `current`와 `stable`
- 실행한 명령과 결과. 큐·worker·배포 상태, 일시정지·롤백·재개 중 어디까지 진행했는지 알 수 있도록 전달합니다.
