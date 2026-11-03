# river-worker 적체 알람 대응 절차

`WorkerQueueAgeHigh` 알람이 발생하면 이 절차에 따라 `river-worker`와 작업 큐 `river-events`의 상태를 확인하고 롤백 여부를 판단합니다. 알람만으로 배포가 원인이라고 확정할 수는 없습니다.

이 절차에서는 **큐 삭제, offset 초기화, 처리 중인 작업 강제 종료를 하지 않습니다.** 작업 손실이나 중복을 일으킬 수 있어 별도 판단이 필요합니다.

## 1. 큐와 worker 상태 확인

다음 명령으로 현재 상태를 확인합니다.

```sh
opsctl queue inspect river-events
opsctl worker status river-worker
```

| 명령 | 확인할 항목 |
| --- | --- |
| `queue inspect` | `pending`, `oldest_age_seconds`, `consumer_state` |
| `worker status` | `state`, `inflight` |

명령 실행 결과와 알람 발생 시각을 기록하고, 적체가 시작된 시각을 확인합니다. `oldest_age_seconds`는 소비 재개 후 적체가 개선되는지 판단할 때도 확인합니다.

## 2. 롤백 조건 확인

배포 정보를 조회합니다.

```sh
opsctl deploy show river-worker
```

출력의 `current`, `stable`, `changed_at`을 확인합니다. `stable`은 온콜이 복구 대상으로 사용할 수 있도록 미리 지정된 배포입니다.

`changed_at`과 적체 시작 시각을 비교하고, **다음 두 조건을 모두 확인한 경우에만** 3단계로 진행합니다.

- 적체가 현재 배포 직후부터 시작됐습니다.
- `current`와 `stable`이 다릅니다.

조건을 확인할 수 없거나 `current`와 `stable`이 같으면 이 절차에서 롤백하지 않습니다. 관찰 결과를 정리해 플랫폼 온콜에 이관합니다.

## 3. 일시정지 요청 후 처리 중인 작업 확인

롤백 조건을 충족하면 worker에 일시정지를 요청하고 요청 시각을 기록합니다.

```sh
opsctl worker pause river-worker
```

명령이 반환됐다는 것은 **일시정지 요청을 접수했다는 뜻**입니다. 이미 처리 중인 작업은 계속 진행될 수 있으므로, 반환만으로 롤백을 시작하지 않습니다.

다음 명령으로 상태를 다시 확인합니다.

```sh
opsctl worker status river-worker
```

**`state=paused`와 `inflight=0`을 모두 확인한 다음에만** 4단계로 진행합니다. 일시정지 요청 후 5분이 지나도 두 조건을 만족하지 못하면 롤백하지 않고 플랫폼 온콜에 이관합니다.

## 4. 롤백 성공 후 소비 재개

일시정지 상태와 처리 중인 작업이 없음을 모두 확인했다면 `stable`로 롤백합니다.

```sh
opsctl deploy rollback river-worker --to stable
```

롤백 명령의 결과를 확인합니다. **롤백에 실패하면 worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관합니다.**

롤백 명령이 성공한 경우에만 소비를 재개하고 재개 시각을 기록합니다.

```sh
opsctl worker resume river-worker
```

## 5. 소비 재개 후 복구 여부 확인

소비를 재개한 뒤 큐 상태를 다시 조회합니다.

```sh
opsctl queue inspect river-events
```

큐 상태를 관찰하며 다음 두 조건을 모두 확인해야 복구로 판단합니다.

- `consumer_state=running`입니다.
- `oldest_age_seconds`가 감소합니다.

소비가 재개됐다는 사실만으로 복구로 판단하지 않습니다. **재개 후 10분 동안 개선되지 않으면 반복 롤백하지 말고 플랫폼 온콜에 이관합니다.**

## 플랫폼 온콜 이관 시 전달할 내용

이관할 때는 다음 내용을 함께 전달합니다.

- 알람 발생 시각
- 적체 시작 시각과 확인 여부
- 배포 정보의 `current`와 `stable`
- 실행한 명령과 각 명령의 결과

롤백 조건을 확인하지 못했는지, 일시정지 요청 후 5분이 지나도 조건을 충족하지 못했는지, 롤백에 실패했는지, 소비 재개 후 10분 동안 개선되지 않았는지 등 이관하게 된 관찰 결과를 함께 설명합니다.
