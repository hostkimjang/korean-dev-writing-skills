제공 자료로 요청한 한국어 문서를 작성하세요. 최종 문서 본문만 작성하세요.

{
  "user_prompt": "아래 설계 메모를 바탕으로 리뷰에 올릴 ADR 초안을 써 주세요. 왜 이 선택을 제안하는지, 다른 선택지는 무엇이었는지, 도입하면 감수할 점과 더 결정해야 할 점이 드러났으면 합니다. 한국어 Markdown으로 작성해 주세요.",
  "audience": {
    "primary": "이벤트 API의 설계를 검토하는 백엔드, 데이터, 운영 담당자",
    "prior_knowledge": "기존 API가 PostgreSQL에 이벤트를 기록한다는 점과 Redis의 일반적인 역할을 안다.",
    "use_context": "설계 리뷰에서 저장소 선택의 근거, 비용, 남은 결정 사항을 검토한다."
  },
  "document_purpose": "중복 판정 저장소에 관한 제안과 대안을 비교하고 보장 범위, 비용, 미결 사항을 기록한다.",
  "source_facts": [
    {
      "id": "D1",
      "text": "문서 번호는 ADR-007이고 제목은 이벤트 중복 판정 저장소다. 작성일은 2026-10-15, 상태는 제안이다. 데이터와 운영 담당자의 검토는 아직 끝나지 않았다.",
      "certainty": "confirmed"
    },
    {
      "id": "D2",
      "text": "기존 이벤트 API는 PostgreSQL에 업무 이벤트를 저장한다. 같은 tenant_id에서 같은 event_id가 다시 제출되면 업무 이벤트가 중복 생성되지 않아야 한다. 서로 다른 tenant_id에서는 같은 event_id를 사용할 수 있다.",
      "certainty": "confirmed"
    },
    {
      "id": "D3",
      "text": "과거 이벤트를 다시 가져오는 작업도 중복 판정 대상이다. 중복 판정 기록을 얼마나 오래 보관할지는 아직 정하지 않았다.",
      "certainty": "unknown"
    },
    {
      "id": "D4",
      "text": "제안은 PostgreSQL에 event_receipts 테이블을 두고 (tenant_id, event_id)에 유일성 제약을 설정하는 것이다. 중복 판정 기록과 업무 이벤트 생성을 같은 데이터베이스 트랜잭션에서 처리한다.",
      "certainty": "confirmed"
    },
    {
      "id": "D5",
      "text": "중복 키가 이미 있으면 업무 이벤트를 새로 만들지 않는다. 데이터베이스 작업이 실패하면 요청에 503을 반환하고, 클라이언트가 같은 tenant_id와 event_id로 재시도하게 한다.",
      "certainty": "confirmed"
    },
    {
      "id": "D6",
      "text": "비교한 대안은 Redis에 중복 판정 키를 저장하고 TTL을 두는 방식이다. 이 방식은 TTL 만료 또는 키 유실 뒤 과거 이벤트가 다시 들어오면 중복을 놓칠 수 있고, PostgreSQL의 업무 이벤트 생성과 원자적으로 처리하려면 추가 설계가 필요하다.",
      "certainty": "confirmed"
    },
    {
      "id": "D7",
      "text": "PostgreSQL 제안은 기존 데이터베이스의 트랜잭션을 쓸 수 있고 별도 Redis 운영을 추가하지 않는다는 이점이 있다. 대신 쓰기와 인덱스 부하가 늘고, 중복 판정 기록을 정리하는 정책을 마련해야 한다.",
      "certainty": "confirmed"
    },
    {
      "id": "D8",
      "text": "현재 부하에서 event_receipts 추가 비용을 측정한 결과는 없다. 공식 지연 목표나 처리량 보장은 이번 ADR에서 정하지 않았다.",
      "certainty": "unknown"
    },
    {
      "id": "D9",
      "text": "리뷰에서 보존 정책, 성능 검증 계획, 운영 시 책임 주체를 정한 뒤 제안의 승인 여부를 결정한다.",
      "certainty": "confirmed"
    }
  ],
  "source_draft": null
}
