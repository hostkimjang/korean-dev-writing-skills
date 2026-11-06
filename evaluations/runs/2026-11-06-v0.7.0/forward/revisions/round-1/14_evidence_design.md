# 구름 보관 서비스의 키 관리 설계 검토

관리 인력과 비용을 고려해 갈피 키 저장소를 첫 실증 후보로 권합니다. 아래에는 설정에서 확인한 내용과 실증·키 교체 전에 확인할 조건을 정리했습니다.

## 1. 같은 Docker 호스트를 전제로 한 배치입니다

운영 Compose는 외부 bridge 네트워크 `archive-net`을 요구합니다. 이 설정대로 배포하면 포털과 보관 API는 같은 Docker 호스트를 사용합니다. 실제 운영 호스트 배치는 조회하지 않았으므로, 설정으로 추론한 배치입니다.

근거:

- `cloud-archive/ops/deploy/production/compose.yaml:148-156`
- `cloud-archive/ops/.env.example:24-29`

## 2. 토큰 설정은 나뉘어 있고, DB 계정 값은 아직 대조하지 않았습니다

포털에서 API로 전달하는 토큰은 다음 두 설정에서 다룹니다.

| 역할 | 설정과 동작 | 근거 |
| --- | --- | --- |
| 포털 | `PORTAL_TOKEN`을 읽어 API 호출 | `cloud-archive/apps/portal/src/clients/archive/client.ts:42-58` |
| 보관 API | 받은 토큰을 `SERVICE_TOKENS` 목록과 대조 | `cloud-archive/services/api/src/http/auth/token_controller.py:90-113` |

`ARCHIVE_DB_USER`와 `PORTAL_DB_USER`는 설정상 같은 업무용 계정으로 보입니다. 다만 운영 값을 대조하지 않아 계정과 비밀값이 실제로 같은지는 확인하지 못했습니다.

근거:

- `cloud-archive/ops/.env.example:71-79`
- `cloud-archive/ops/.env.example:144-151`

동일 비밀값을 공유하는 서비스에는 키 저장소의 같은 항목을 참조하는 방식을 제안합니다. 한쪽만 바꾸면 인증에 실패할 수 있으므로 실증 전에 대상 값을 대조해야 합니다.

## 3. 읽기 전용 마운트로 비밀 파일이 보일 수 있습니다

점검 컨테이너는 `/srv/archive`를 `/host/archive`에 읽기 전용으로 마운트합니다. 이 경로의 비밀 파일은 컨테이너 읽기 권한에 따라 보일 수 있습니다. 실제 파일 열람과 노출 재현은 수행하지 않았습니다.

근거: `cloud-archive/ops/deploy/production/compose.yaml:260-268`

## 4. 백업 스크립트는 .env를 그대로 복사합니다

백업 스크립트는 `.env`를 백업 디렉터리에 그대로 복사합니다. 로컬에서는 `.env-backups`라는 디렉터리 이름도 확인했지만 내용을 열지는 않았습니다. 현재 평문 비밀값이 남아 있는지는 확인할 대상입니다.

근거: `cloud-archive/ops/scripts/archive-backup.sh:31-38`

## 5. 업로드 실패는 재시도하지만 장기 장애의 복구율은 미검증입니다

업로드 작업자는 실패 결과를 `pending_uploads/results`에 저장합니다. 재시도 간격은 90초에서 시작해 최대 10,800초까지 늘어나며, 영구 실패는 재시도에서 제외합니다.

근거:

- `cloud-archive/agents/uploader/src/jobs/result_retry_worker.py:120-134`
- `cloud-archive/agents/uploader/src/jobs/result_retry_worker.py:310-329`

장기 장애 후 복구율과 재부팅 후 보존은 검증하지 않았습니다.

## 6. dry-run으로 변경 계획을 확인합니다

실증 전에는 대상 계정의 운영 값을 대조합니다. 아래 명령은 변경 계획만 출력하고 키를 변경하지 않으며, 실제 운영에서는 실행하지 않았습니다.

```bash
cd cloud-archive/ops
archive-keys rotate --dry-run
```

## 7. 두 필수 조건이 충족돼야 키를 교체합니다

실제 키 교체를 실행하려면 다음 두 조건을 모두 충족해야 합니다.

- 대상 계정의 운영 값 대조가 끝나야 합니다.
- 복구 백업 검증이 끝나야 합니다.

어느 하나라도 끝나지 않았으면 키 교체를 중단하고 기존 키를 유지합니다.

교체 요청의 `accepted`는 접수 상태입니다. `rotation_state=committed`를 확인한 뒤 연결 점검까지 성공해야 이전 키 폐기를 검토합니다. 접수만으로는 폐기를 진행하지 않습니다.

## 8. 자동 교체의 구현·운영 일정은 미정입니다

자동 교체 구현과 운영 적용 일정은 아직 정해지지 않았습니다. 장기 장애 뒤 복구를 완료한다는 보장도 정해지지 않았습니다.
