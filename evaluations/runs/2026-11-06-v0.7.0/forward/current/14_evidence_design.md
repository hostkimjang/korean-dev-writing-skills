# 구름 보관 서비스의 키 관리 설계 검토

관리 인력과 비용을 고려해 갈피 키 저장소를 첫 실증 후보로 권합니다. 실증 전에 대상 계정의 운영 값을 대조해야 하며, 실제 키 교체는 운영 값 대조와 복구 백업 검증이 모두 끝난 뒤에 진행해야 합니다. 현재 추천은 채택이나 설치 완료를 뜻하지 않습니다.

## 1. 운영 설정대로 배포하면 포털과 보관 API는 같은 Docker 호스트를 사용합니다

운영 Compose는 외부 bridge 네트워크 `archive-net`을 요구합니다. 이 설정대로 배포하면 포털과 보관 API는 같은 Docker 호스트를 사용합니다. 실제 운영 호스트 배치는 조회하지 않았으므로, 이는 설정을 읽어 도출한 배치 추론입니다.

근거:

- `cloud-archive/ops/deploy/production/compose.yaml:148-156`
- `cloud-archive/ops/.env.example:24-29`

## 2. 토큰을 전달하고 검증하는 설정이 나뉘어 있으며, 계정과 비밀값의 동일 여부는 미확인입니다

포털은 `PORTAL_TOKEN`을 읽어 API를 호출하고, API는 받은 토큰을 `SERVICE_TOKENS` 목록과 대조합니다.

| 역할 | 설정과 동작 | 근거 |
| --- | --- | --- |
| 포털 | `PORTAL_TOKEN`을 읽어 API 호출 | `cloud-archive/apps/portal/src/clients/archive/client.ts:42-58` |
| 보관 API | 받은 토큰을 `SERVICE_TOKENS` 목록과 대조 | `cloud-archive/services/api/src/http/auth/token_controller.py:90-113` |

`ARCHIVE_DB_USER`와 `PORTAL_DB_USER`는 설정상 같은 업무용 계정으로 보입니다. 다만 운영 값을 대조하지 않아 계정과 비밀값이 실제로 같은지는 확인하지 못했습니다.

근거:

- `cloud-archive/ops/.env.example:71-79`
- `cloud-archive/ops/.env.example:144-151`

동일 비밀값을 공유하는 서비스는 한쪽만 바꾸면 인증에 실패할 수 있습니다. 이러한 서비스가 키 저장소의 같은 항목을 참조하도록 구성하는 방안을 제안합니다. 실증 전에 대상 값을 대조해 공유 여부를 확인해야 합니다.

## 3. 점검 컨테이너에 비밀 파일을 읽을 수 있는 경로가 있으나, 실제 노출은 재현하지 않았습니다

점검 컨테이너는 `/srv/archive`를 `/host/archive`에 읽기 전용으로 마운트합니다. 이 경로의 비밀 파일은 컨테이너 읽기 권한에 따라 보일 수 있습니다. 실제 파일 열람과 노출 재현은 수행하지 않았으므로 노출이 확정된 것은 아닙니다.

근거: `cloud-archive/ops/deploy/production/compose.yaml:260-268`

## 4. 백업 스크립트는 .env를 그대로 복사하며, 현재 사본의 내용은 확인하지 않았습니다

백업 스크립트는 `.env`를 백업 디렉터리에 그대로 복사합니다. 로컬에서는 `.env-backups`라는 디렉터리 이름도 확인했지만 내용을 열지는 않았습니다. 따라서 디렉터리 이름만으로 현재 평문 비밀값이 남아 있다고 확정할 수는 없습니다.

근거: `cloud-archive/ops/scripts/archive-backup.sh:31-38`

## 5. 업로드 작업은 재시도하지만, 장기 장애와 재부팅 이후의 복구는 검증하지 않았습니다

업로드 작업자는 실패 결과를 `pending_uploads/results`에 저장합니다. 재시도 간격은 90초에서 시작해 최대 10,800초까지 늘어나며, 영구 실패는 재시도에서 제외합니다.

근거:

- `cloud-archive/agents/uploader/src/jobs/result_retry_worker.py:120-134`
- `cloud-archive/agents/uploader/src/jobs/result_retry_worker.py:310-329`

장기 장애 후 복구율과 재부팅 후 보존은 검증하지 않았습니다. 재시도 동작만으로 장기 장애의 복구 완료를 보장할 수는 없습니다.

## 실증용 변경 계획 확인

아래 명령은 `cloud-archive/ops`로 이동한 뒤 키 교체의 변경 계획을 확인하는 실증용 명령입니다. 변경 계획만 출력하고 키를 변경하지 않으며, 실제 운영에서는 실행하지 않았습니다.

```bash
cd cloud-archive/ops
archive-keys rotate --dry-run
```

## 키 교체의 중단 조건과 이전 키 폐기 검토 조건

실제 키 교체를 실행하려면 다음 두 조건을 모두 충족해야 합니다.

- 대상 계정의 운영 값 대조가 끝나야 합니다.
- 복구 백업 검증이 끝나야 합니다.

어느 하나라도 끝나지 않았으면 키 교체를 중단하고 기존 키를 유지합니다.

교체 요청의 `accepted`는 접수 상태입니다. `rotation_state=committed`를 확인한 뒤 연결 점검까지 성공해야 이전 키 폐기를 검토합니다. 요청 접수만으로 이전 키를 폐기하지 않습니다.

## 아직 정해지지 않은 사항

자동 교체 구현과 운영 적용 일정, 장기 장애의 복구 완료 보장은 아직 정해지지 않았습니다.
