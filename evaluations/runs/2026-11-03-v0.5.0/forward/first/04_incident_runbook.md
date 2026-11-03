# river-worker 적체 장애 대응

`WorkerQueueAgeHigh` 알람이 울리면 이 절차로 `river-worker`와 작업 큐 `river-events`를 확인합니다. 알람만으로 배포가 원인이라고 확정할 수는 없습니다. 먼저 관찰 결과로 롤백 여부를 판단한 뒤 일시정지, 롤백, 소비 재개와 복구 확인을 진행합니다.

이 절차에서는 큐 삭제, offset 초기화, 처리 중 작업 강제 종료를 하지 않습니다. 작업 손실이나 중복을 일으킬 수 있어 별도 판단이 필요합니다.

## 1. 현재 상태와 롤백 조건 확인

큐, worker, 배포 상태를 조회합니다.

```sh
opsctl queue inspect river-events
opsctl worker status river-worker
opsctl deploy show river-worker
```

| 조회 대상 | 기록할 값 |
| --- | --- |
| 큐 | `pending`, `oldest_age_seconds`, `consumer_state` |
| worker | `state`, `inflight` |
| 배포 | `current`, `stable`, `changed_at` |

`stable`은 온콜이 복구 대상으로 사용할 수 있도록 미리 지정된 배포입니다. 알람 발생 시각과 적체 시작 시각을 기록하고, 적체 시작 시각을 `changed_at`과 비교합니다.

다음 조건을 **모두 확인한 경우에만** 롤백 절차를 진행합니다.

- 현재 배포 직후부터 적체가 시작됐습니다.
- `current`와 `stable`이 다릅니다.

조건을 충족하지 못하거나 확인할 수 없다면 롤백하지 말고 플랫폼 온콜에 관찰 결과를 전달합니다. `current`와 `stable`이 같을 때도 이관합니다.

## 2. 일시정지 완료 확인과 롤백

현재 배포 직후부터 적체가 시작됐고 `current`와 `stable`이 다름을 확인했다면, 먼저 worker에 일시정지를 요청합니다.

```sh
opsctl worker pause river-worker
```

명령 반환은 일시정지 요청이 접수됐다는 뜻입니다. 이미 처리 중인 작업은 계속 진행될 수 있으므로 반환만으로 롤백을 시작하지 않습니다. `pause` 요청 시각을 기준으로 아래 명령에서 완료 상태를 확인합니다.

```sh
opsctl worker status river-worker
```

`state=paused`와 `inflight=0`을 **모두 확인한 다음에만** 롤백합니다. `pause` 요청 후 5분이 지나도 두 조건을 모두 만족하지 못하면 롤백하지 말고 플랫폼 온콜에 이관합니다.

두 상태 조건을 모두 확인했다면 지정된 복구 대상인 `stable`로 롤백합니다.

```sh
opsctl deploy rollback river-worker --to stable
```

롤백 명령의 성공 여부를 확인합니다. 실패했다면 worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관합니다. 소비 재개는 롤백에 성공한 경우에만 진행합니다.

## 3. 소비 재개와 복구 확인

롤백 명령이 성공한 경우에만 소비를 재개합니다.

```sh
opsctl worker resume river-worker
```

재개 시각을 기록하고 큐 상태를 확인합니다.

```sh
opsctl queue inspect river-events
```

다음 두 조건을 모두 확인해야 복구로 판단합니다.

- `consumer_state=running`입니다.
- `oldest_age_seconds`가 감소합니다.

소비를 재개한 시각부터 10분 동안 개선되지 않으면 반복 롤백하지 말고 플랫폼 온콜에 이관합니다.

## 4. 플랫폼 온콜에 전달할 정보

중단·이관 기준에 해당하면 다음 정보를 전달합니다.

- 알람 발생 시각과 적체 시작 시각
- `current`와 `stable`
- 큐와 worker의 관찰 결과
- 실행한 명령과 각 명령의 결과
