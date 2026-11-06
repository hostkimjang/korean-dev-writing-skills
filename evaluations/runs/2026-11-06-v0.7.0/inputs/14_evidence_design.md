아래 초안을 개발 인계용 한국어 문서로 다듬어 주세요. 관계를 설명하는 자연스러운 문장을 쓰고, 사실·조건·수치·기술 식별자와 근거를 유지해 주세요. 문서 전문만 작성해 주세요. 자료는 공개용 가상 사례입니다.

독자: 설정을 인계받아 키 관리 도구의 실증 범위를 결정할 개발자

## 편집할 초안

# 구름 보관 서비스의 키 관리 설계 검토

**두 서비스가 같은 호스트에서 동작한다(판단).** 운영 Compose는 외부 bridge 네트워크 archive-net을 요구하며(cloud-archive/ops/deploy/production/compose.yaml:148-156, cloud-archive/ops/.env.example:24-29), 이 설정대로 배포하면 포털과 보관 API는 같은 Docker 호스트를 사용합니다. 실제 운영 호스트 배치는 조회하지 않았습니다. 이 설명은 설정을 읽은 추론이지 실제 배치 확인이 아닙니다.

**토큰과 계정 전달이 두 곳에 나뉜다.** 포털은 PORTAL_TOKEN을 읽어 API를 호출하고(cloud-archive/apps/portal/src/clients/archive/client.ts:42-58), API는 받은 토큰을 SERVICE_TOKENS 목록과 대조합니다(cloud-archive/services/api/src/http/auth/token_controller.py:90-113). ARCHIVE_DB_USER와 PORTAL_DB_USER는 설정상 같은 업무용 계정으로 보이지만(cloud-archive/ops/.env.example:71-79, 144-151) 운영 값은 대조하지 않아 계정·비밀값의 동일 여부는 미확인입니다. 동일 비밀값을 공유하는 서비스는 한쪽만 바꾸면 인증에 실패할 수 있으므로 저장소의 같은 항목을 참조하는 방안을 제안하며 실증 전에 대상 값을 대조해야 합니다. 이는 현재 구현 완료를 뜻하지 않습니다.

**마운트가 읽기 경로를 만든다(판단).** 점검 컨테이너는 /srv/archive를 /host/archive에 읽기 전용으로 마운트합니다(cloud-archive/ops/deploy/production/compose.yaml:260-268). 그 경로의 비밀 파일은 컨테이너 읽기 권한에 따라 보일 수 있지만 실제 열람과 노출 재현은 수행하지 않았습니다. 따라서 이 결과는 노출 확정이 아닙니다.

**백업 사본도 확인해야 한다.** 백업 스크립트는 .env를 백업 디렉터리에 그대로 복사하며(cloud-archive/ops/scripts/archive-backup.sh:31-38), 로컬에서 .env-backups 디렉터리 이름도 확인했습니다(내용은 열지 않았다). 디렉터리 이름만으로 현재 평문 비밀값이 남았다고 확정할 수 없습니다.

**갈피 키 저장소를 첫 실증 후보로 권한다(판단).** 관리 인력과 비용을 고려한 추천입니다. 실제 채택이나 설치 완료를 뜻하지 않습니다. 실증용 명령은 아래와 같으며 변경 계획만 출력하고 키를 변경하지 않습니다. 실제 운영에서는 실행하지 않았습니다.

```bash
cd cloud-archive/ops
archive-keys rotate --dry-run
```

키 교체 실행 전에는 대상 계정의 운영 값 대조와 복구 백업 검증이 모두 필요합니다. 어느 하나라도 끝나지 않았으면 키 교체를 중단하고 기존 키를 유지합니다. 교체 요청의 accepted는 접수 상태일 뿐이며 rotation_state=committed를 확인한 뒤 연결 점검이 성공해야 이전 키 폐기를 검토합니다. 접수만으로 이전 키를 폐기하지 않습니다.

**업로드 작업의 재시도는 복구 보장과 구분한다.** 업로드 작업자는 실패 결과를 pending_uploads/results에 저장하고 90초마다 재시도하며 최대 간격을 10,800초로 늘립니다(cloud-archive/agents/uploader/src/jobs/result_retry_worker.py:120-134, 310-329). 영구 실패는 재시도에서 제외하고, 장기 장애 후 복구율과 재부팅 후 보존은 검증하지 않았습니다. 자동 교체 구현, 운영 적용 일정, 장기 장애의 복구 완료 보장은 아직 정해지지 않았습니다.
