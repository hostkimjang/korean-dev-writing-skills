제공 자료로 요청한 한국어 문서를 작성하세요. 최종 문서 본문만 작성하세요.

{
  "user_prompt": "새로 합류한 개발자에게 전달할 이벤트 수집 서비스 아키텍처 문서를 작성해 주세요. 아래 구현 메모를 바탕으로 각 구성요소의 역할과 이벤트가 저장될 때까지의 흐름을 설명하고, 연동하거나 운영할 때 헷갈릴 만한 지점도 짚어 주세요. Markdown으로 작성해 주세요.",
  "audience": {
    "primary": "이벤트 수집 API와 연동하거나 서비스 운영을 인계받는 백엔드 개발자",
    "prior_knowledge": "HTTP, Kafka, 관계형 데이터베이스의 기본 개념을 안다.",
    "use_context": "이벤트를 제출한 뒤 응답이 무엇을 뜻하는지, 장애 시 어디에서 재처리가 일어나는지 확인한다."
  },
  "document_purpose": "구성요소, 데이터 흐름, 수락과 저장의 경계, 중복 처리 및 장애 복구 동작을 설명한다.",
  "source_facts": [
    {
      "id": "A1",
      "text": "가상 내부 서비스 이름은 Harbor Intake다. 구성요소는 collector-api, Kafka 토픽 telemetry.raw.v1, event-writer, PostgreSQL 데이터베이스 event_store다.",
      "certainty": "confirmed"
    },
    {
      "id": "A2",
      "text": "클라이언트는 POST /v1/events에 이벤트를 제출한다. collector-api는 토큰과 스키마를 확인한 후 telemetry.raw.v1에 발행한다. 유효하지 않은 토큰에는 401, 스키마 오류에는 400을 반환한다.",
      "certainty": "confirmed"
    },
    {
      "id": "A3",
      "text": "collector-api는 Kafka 발행이 확인된 뒤 202와 event_id를 반환한다. 이 응답은 큐에 수락되었다는 뜻이며, event_store 저장 완료를 뜻하지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "A4",
      "text": "Kafka 발행에 실패하면 collector-api는 503을 반환한다. 클라이언트는 같은 논리적 이벤트를 재시도할 때 같은 event_id를 사용해야 한다. collector-api 자체에서는 중복 요청을 제거하지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "A5",
      "text": "event-writer는 토픽에서 이벤트를 읽고 event_store에 기록한다. 데이터베이스 트랜잭션이 성공한 뒤 Kafka offset을 커밋한다.",
      "certainty": "confirmed"
    },
    {
      "id": "A6",
      "text": "데이터베이스 기록 후 offset 커밋 전에 worker가 종료되면 같은 이벤트를 다시 읽을 수 있다. 전송 및 소비 과정은 중복 전달 가능성을 가진다.",
      "certainty": "confirmed"
    },
    {
      "id": "A7",
      "text": "event_store에는 event_id의 유일성 제약이 있다. event-writer는 이 제약으로 확인된 중복 이벤트를 이미 기록된 이벤트로 취급해 추가 행을 만들지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "A8",
      "text": "데이터베이스 쓰기에 실패하면 해당 이벤트의 offset을 커밋하지 않는다. 데이터베이스가 회복되면 event-writer가 미커밋 이벤트를 다시 처리한다.",
      "certainty": "confirmed"
    },
    {
      "id": "A9",
      "text": "Kafka 보존 기간, 공식 처리량 목표, 장애 복구 시간 목표는 이 문서용 자료에서 확정되지 않았다.",
      "certainty": "unknown"
    },
    {
      "id": "A10",
      "text": "현재 구현에는 클라이언트가 event_id로 최종 저장 상태를 조회하는 API가 없다.",
      "certainty": "confirmed"
    }
  ],
  "source_draft": null
}
