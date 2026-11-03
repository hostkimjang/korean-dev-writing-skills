# river-worker 적체 알람 대응 절차

`WorkerQueueAgeHigh` 알람이 발생하면 이 절차를 시작합니다. 대상은 `river-worker`와 작업 큐 `river-events`입니다. 알람만으로 배포가 원인이라고 확정할 수는 없으므로, 현재 상태와 배포 시점을 확인한 뒤 롤백 여부를 판단합니다.

이 절차에서는 **큐 삭제, offset 초기화, 처리 중인 작업 강제 종료를 하지 않습니다.** 이 조치는 작업 손실이나 중복을 일으킬 수 있어 별도 판단이 필요합니다.

## 1. 알람 발생 시각과 현재 상태 확인

알람 발생 시각을 기록하고 큐와 worker의 상태를 조회합니다.

```bash
opsctl queue inspect river-events
opsctl worker status river-worker
```

다음 값을 기록합니다. 이후 상태 변화와 복구 여부를 판단하고, 필요하면 플랫폼 온콜에 전달할 정보입니다.

| 조회 대상 | 확인할 값 |
| --- | --- |
| `river-events` | `pending`, `oldest_age_seconds`, `consumer_state` |
| `river-worker` | `state`, `inflight` |

## 2. 배포 정보로 롤백 여부 판단

현재 배포와 복구 대상 배포를 확인합니다.

```bash
opsctl deploy show river-worker
```

출력의 `current`, `stable`, `changed_at`을 기록합니다. `stable`은 온콜이 복구 대상으로 사용할 수 있도록 미리 지정된 배포입니다. 적체 시작 시각을 확인하고 `changed_at`과 비교해 현재 배포 직후부터 적체가 시작됐는지 판단합니다. 알람 발생 시각과 적체 시작 시각은 구분해서 기록합니다.

**다음 두 조건을 모두 확인한 경우에만 3단계로 진행합니다.**

- 현재 배포 직후부터 적체가 시작됐습니다.
- `current`와 `stable`이 다릅니다.

조건을 충족하지 않거나 확인할 수 없으면 롤백하지 않습니다. `current`와 `stable`이 같은 경우에도 롤백하지 않고, 관찰 결과를 플랫폼 온콜에 전달합니다. 전달할 항목은 아래의 「중단 및 플랫폼 온콜 이관」을 따릅니다.

## 3. 일시정지 완료를 확인한 뒤 롤백하고 소비 재개

현재 배포 직후부터 적체가 시작됐고 `current`와 `stable`이 다르다면 worker에 일시정지를 요청하고, 요청 시각을 기록합니다.

```bash
opsctl worker pause river-worker
```

이 명령의 반환은 **일시정지 요청을 접수했다는 뜻**입니다. 이미 처리 중인 작업은 계속 진행될 수 있으므로, 명령이 반환됐다는 이유만으로 롤백하지 않습니다.

다음 명령으로 worker 상태를 확인합니다.

```bash
opsctl worker status river-worker
```

**롤백은 `state=paused`와 `inflight=0`을 모두 확인한 다음에만 진행합니다.** 두 조건을 아직 만족하지 않으면 상태를 다시 조회합니다.

일시정지 요청 후 **5분이 지나도 두 조건을 모두 만족하지 못하면 롤백하지 않고 플랫폼 온콜에 이관합니다.** 처리 중인 작업을 강제로 종료하지 않습니다.

`state=paused`와 `inflight=0`을 모두 확인했다면 다음 명령으로 롤백합니다.

```bash
opsctl deploy rollback river-worker --to stable
```

명령 결과를 확인하고 기록합니다. **롤백에 실패하면 worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관합니다.** 이 경우 소비를 재개하지 않습니다.

롤백 명령이 성공한 경우에만 다음 명령으로 소비를 재개합니다. 재개 시각도 기록합니다.

```bash
opsctl worker resume river-worker
```

## 4. 소비 상태와 큐 대기 시간으로 복구 확인

재개 후 큐 상태를 조회합니다.

```bash
opsctl queue inspect river-events
```

시간을 두고 같은 명령을 다시 실행해 `oldest_age_seconds`의 변화를 비교합니다. **다음 두 조건을 모두 확인해야 복구로 판단합니다.**

- `consumer_state=running`입니다.
- `oldest_age_seconds`가 감소합니다.

소비가 재개됐다는 사실만으로 복구로 판단하지 않습니다. 재개 후 **10분 동안 개선되지 않으면 반복 롤백하지 말고 플랫폼 온콜에 이관합니다.**

## 중단 및 플랫폼 온콜 이관

다음 중 하나라도 해당하면 해당 단계에서 조치를 중단하고 플랫폼 온콜에 이관합니다.

| 이관 조건 | 중단 시 조치 |
| --- | --- |
| 현재 배포 직후부터 적체가 시작됐다는 조건을 충족하지 않거나 확인할 수 없음 | 롤백하지 않습니다. |
| `current`와 `stable`이 같거나 서로 다른지 확인할 수 없음 | 롤백하지 않습니다. |
| 일시정지 요청 후 5분이 지나도 `state=paused`와 `inflight=0`을 모두 만족하지 못함 | 롤백하지 않습니다. |
| 롤백 명령 실패 | worker를 일시정지한 상태로 두고 소비를 재개하지 않습니다. |
| 소비 재개 후 10분 동안 개선되지 않음 | 반복 롤백하지 않습니다. |

이관할 때는 다음 정보를 전달합니다. 확인하지 못한 항목은 확인하지 못했다고 표시합니다.

- 알람 발생 시각과 적체 시작 시각
- `current`, `stable`, `changed_at`
- 큐의 `pending`, `oldest_age_seconds`, `consumer_state`와 worker의 `state`, `inflight` 등 관찰 결과
- 실행한 명령과 각 명령의 결과
- 일시정지 요청 시각과 소비 재개 시각 등 해당 단계에서 기록한 시각
- 조치를 중단한 단계와 충족하지 못한 조건
