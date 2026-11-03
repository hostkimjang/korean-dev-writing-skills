제공 자료로 요청한 한국어 문서를 작성하세요. 최종 문서 본문만 작성하세요.

{
  "user_prompt": "아래 작업 메모로 PR 본문을 작성해 주세요. 중복 발송 이슈를 함께 보고 있는 팀원이 변경 의도와 리뷰할 부분을 이해할 수 있으면 좋겠습니다. GitHub에 붙여 넣을 수 있는 한국어 Markdown으로 부탁합니다.",
  "audience": {
    "primary": "변경을 검토할 동료 백엔드 개발자와 운영 담당자",
    "prior_knowledge": "발송 worker의 역할은 알지만 이번 중복 발송 조사 과정은 아직 모른다.",
    "use_context": "PR을 읽고 실제 변경 범위, 검증한 내용, 배포 후 확인할 내용을 판단한다."
  },
  "document_purpose": "조사용 로깅 변경의 필요성과 범위를 설명하고 확인된 사실과 가설을 구분해 리뷰를 돕는다.",
  "source_facts": [
    {
      "id": "P1",
      "text": "관련 이슈는 #184다. 운영 로그에서 같은 job_id가 두 번 발송된 사례를 확인했다. 로컬 환경에서는 아직 안정적인 재현 방법을 찾지 못했다.",
      "certainty": "confirmed"
    },
    {
      "id": "P2",
      "text": "발송 작업이 길어져 lock TTL이 먼저 끝나는 것이 한 가지 원인 후보지만, 실제 원인인지는 확인하지 못했다.",
      "certainty": "hypothesis"
    },
    {
      "id": "P3",
      "text": "이번 PR은 src/workers/deliver.ts에 진단 로그를 추가한다. 발송 순서, 재시도 횟수, lock TTL 값, 중복 방지 동작은 바꾸지 않는다. 중복 발송을 해결하는 수정은 포함하지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "P4",
      "text": "진단 로그의 이름은 delivery_retry_probe다. 기록하는 필드는 job_id, attempt, lock_owner다. 수신자 주소와 메시지 본문은 기록하지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "P5",
      "text": "진단 로그는 DELIVERY_DIAG_ENABLED=true일 때만 활성화된다. 이 설정의 기본값은 false다.",
      "certainty": "confirmed"
    },
    {
      "id": "P6",
      "text": "tests/workers/deliver-log.test.ts에서 진단 로그의 조건부 출력과 필드를 검증했다. 로컬에서 실행한 명령은 pnpm exec vitest run tests/workers/deliver-log.test.ts이며 통과했다.",
      "certainty": "confirmed"
    },
    {
      "id": "P7",
      "text": "스테이징에서 실제 발송 경로를 검증하지 않았고, 진단 로그를 켰을 때의 처리량과 지연 변화도 측정하지 않았다.",
      "certainty": "unknown"
    },
    {
      "id": "P8",
      "text": "배포 후 진단 로그를 켜서 중복 사례의 job_id와 attempt, lock_owner를 대조하려 한다. 결과를 이슈 #184에 정리한 뒤 수정 방향을 결정할 예정이다.",
      "certainty": "confirmed"
    },
    {
      "id": "P9",
      "text": "리뷰 요청 사항은 진단 필드가 중복 사례의 구분에 충분한지, 그리고 수신자 주소나 메시지 본문이 로그에 섞일 여지가 없는지다.",
      "certainty": "confirmed"
    }
  ],
  "source_draft": null
}
