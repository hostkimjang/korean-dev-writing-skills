제공 자료로 요청한 한국어 문서를 작성하세요. 최종 문서 본문만 작성하세요.

{
  "user_prompt": "아래 운영 메모를 온콜이 바로 사용할 수 있는 장애 대응 절차로 정리해 주세요. 상황을 확인하는 방법부터 복구 여부를 판단하는 과정까지 이어지게 작성해 주세요. 명령은 코드 블록으로 제시하고, 한국어 Markdown으로 부탁합니다.",
  "audience": {
    "primary": "배포 후 발생한 적체 알람에 대응하는 서비스 온콜 개발자",
    "prior_knowledge": "터미널과 사내 opsctl을 사용할 수 있지만 river-worker 운영은 익숙하지 않다.",
    "use_context": "알람을 받은 뒤 롤백 여부를 판단하고, 안전하게 작업을 중단·롤백·재개하거나 담당자에게 넘긴다."
  },
  "document_purpose": "관찰 결과에 따른 판단, 명령 실행의 선행조건, 성공 확인, 중단 및 이관 기준을 안내한다.",
  "source_facts": [
    {
      "id": "O1",
      "text": "대상은 river-worker와 작업 큐 river-events다. WorkerQueueAgeHigh 알람이 울리면 이 절차를 시작한다. 알람만으로 배포가 원인이라고 확정할 수는 없다.",
      "certainty": "confirmed"
    },
    {
      "id": "O2",
      "text": "opsctl queue inspect river-events는 pending, oldest_age_seconds, consumer_state를 보여 준다. opsctl worker status river-worker는 state와 inflight를 보여 준다.",
      "certainty": "confirmed"
    },
    {
      "id": "O3",
      "text": "opsctl deploy show river-worker는 current, stable, changed_at을 보여 준다. stable은 온콜이 복구 대상으로 사용할 수 있도록 미리 지정된 배포다.",
      "certainty": "confirmed"
    },
    {
      "id": "O4",
      "text": "현재 배포 직후부터 적체가 시작됐고 current와 stable이 다를 때만 이 절차에서 롤백을 진행한다. 이 조건을 확인할 수 없거나 current와 stable이 같으면 플랫폼 온콜에 관찰 결과를 전달한다.",
      "certainty": "confirmed"
    },
    {
      "id": "O5",
      "text": "롤백 전 opsctl worker pause river-worker를 실행한다. 이 명령의 반환은 일시정지 요청을 접수했다는 뜻이다. 이미 처리 중인 작업은 계속 진행될 수 있다.",
      "certainty": "confirmed"
    },
    {
      "id": "O6",
      "text": "opsctl worker status river-worker에서 state=paused와 inflight=0을 모두 확인한 다음에만 롤백한다. pause 요청 후 5분이 지나도 두 조건을 만족하지 못하면 롤백하지 않고 플랫폼 온콜에 이관한다.",
      "certainty": "confirmed"
    },
    {
      "id": "O7",
      "text": "롤백 명령은 opsctl deploy rollback river-worker --to stable이다. 명령이 성공한 경우에만 opsctl worker resume river-worker로 소비를 재개한다. 롤백 실패 시 worker를 일시정지한 상태로 두고 플랫폼 온콜에 이관한다.",
      "certainty": "confirmed"
    },
    {
      "id": "O8",
      "text": "재개 후 opsctl queue inspect river-events에서 consumer_state=running인지 확인하고 oldest_age_seconds가 감소하는지 살핀다. 두 조건을 확인해야 복구로 판단한다. 재개 후 10분 동안 개선되지 않으면 반복 롤백하지 말고 플랫폼 온콜에 이관한다.",
      "certainty": "confirmed"
    },
    {
      "id": "O9",
      "text": "이관할 때는 알람 발생 시각, 적체 시작 시각, current와 stable, 실행한 명령과 결과를 전달한다.",
      "certainty": "confirmed"
    },
    {
      "id": "O10",
      "text": "이 절차에서는 큐 삭제, offset 초기화, 처리 중 작업 강제 종료를 하지 않는다. 이 조치는 작업 손실이나 중복을 일으킬 수 있어 별도 판단이 필요하다.",
      "certainty": "confirmed"
    }
  ],
  "source_draft": null
}
