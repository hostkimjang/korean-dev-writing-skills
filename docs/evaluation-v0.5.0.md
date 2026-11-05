# v0.5.0 문서 교정 결과

갱신일: 2026-11-03 · 교정에 사용한 스킬: **v0.5.0** · [고정한 스킬 파일](../evaluations/runs/2026-11-03-v0.5.0/snapshots/v0.5.0)

기존 문서 10개를 검토·교정했습니다. 각 문서에서 무엇을 고쳤는지, 사실과 조건을 어떻게 보존했는지를 아래에서 확인할 수 있습니다.

[교정 완료본 10개 바로 읽기](examples/README.md) · [수정 결과 보고서](repairs-v0.5.0.md) · [교정 전후를 나란히 보기](comparisons/index.html)

## 사례별 수정 결과

| 문서 | 교정 전 | 교정 완료 | 수정 결과 |
| --- | ---: | ---: | --- |
| [CLI README](examples/01_cli_readme.md) | [1,718자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/01_cli_readme.md) | [1,855자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/01_cli_readme.md) | 파일 저장 명령과 덮어쓰기 조건을 붙이고 심각도 목록의 인접 중복을 정리했습니다. |
| [이벤트 수집 아키텍처](examples/02_event_architecture.md) | [2,553자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/02_event_architecture.md) | [2,553자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/02_event_architecture.md) | 원자료 대조 후 기존 본문을 유지했습니다. 수락·저장·재처리 경계를 보존합니다. |
| [진단 PR](examples/03_investigation_pr.md) | [973자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/03_investigation_pr.md) | [973자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/03_investigation_pr.md) | 원자료 대조 후 기존 본문을 유지했습니다. 관측 보강과 해결 여부를 구분합니다. |
| [장애 대응 절차](examples/04_incident_runbook.md) | [2,741자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/04_incident_runbook.md) | [2,939자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/04_incident_runbook.md) | 정지 확인과 롤백을 한 절로 묶고 5분 기준을 함께 배치했습니다. 이관 조건은 표로 나눴습니다. |
| [중복 판정 저장소 ADR](examples/05_storage_adr.md) | [2,240자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/05_storage_adr.md) | [2,116자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/05_storage_adr.md) | 비교 표의 재나열을 줄이고 미측정 비용·미설정 성능 보장을 승인 조건에 모았습니다. |
| [문단 교정](examples/06_paragraph_edit.md) | [379자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/06_paragraph_edit.md) | [379자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/06_paragraph_edit.md) | 원자료 대조 후 기존 본문을 유지했습니다. 기본값·상한·버전별 확인 범위를 보존합니다. |
| [색인 갱신 온보딩](examples/07_index_onboarding.md) | [4,620자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/07_index_onboarding.md) | [4,609자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/07_index_onboarding.md) | 식별자 설명에 상태 조회용 번호를 붙이고 재시도 조건의 빈 재강조를 삭제했습니다. |
| [짧은 관측 PR](examples/08_short_log_pr.md) | [398자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/08_short_log_pr.md) | [400자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/08_short_log_pr.md) | 399자 본문에 상세 로그 필드와 요청 본문 제외 범위를 복원하고 판단·검증의 한계를 유지했습니다. |
| [달무리 설정배포 서비스의 예약 적용 안내](examples/09_config_rollout.md) | [1,799자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/09_config_rollout.md) | [1,799자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/09_config_rollout.md) | 준비 단계에 입력 이름을 명시하고 예약 충돌 응답 옆에 재요청 가능 조건을 붙였습니다. |
| [단비함 썸네일 작업기의 기록 순서 변경 보고](examples/10_thumbnail_report.md) | [413자](../evaluations/runs/2026-11-03-v0.4.0/outputs/latest/10_thumbnail_report.md) | [413자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/10_thumbnail_report.md) | 원자료 대조 후 기존 본문을 유지했습니다. 완료 집계와 실제 파일 검증을 구분합니다. |

## 전문 비교

- [아키텍처·ADR·장애 대응 절차: 전문 9개](comparisons/long-documents.md)
- [온보딩·짧은 관측 PR: 전문 6개](comparisons/reading-flow.md)
- [설정배포 안내·썸네일 작업 보고: 전문 4개](comparisons/transfer-checks.md)

HTML에는 10개 사례의 본문 28개와 입력 10개를 포함했습니다. 교정 전 v0.4.0과 교정 완료 v0.5.0을 기본으로 비교하고, 처음 8개 사례에서는 미적용 원문도 선택할 수 있습니다.

## 작성과 확인 방법

v0.4.0 원문과 같은 원자료를 바탕으로 알려진 결함을 검토하고, v0.5.0 지침을 적용해 문서를 교정했습니다. 현재 본문은 검토와 수정을 거친 최종본입니다. 이전 원문과 수정 이력은 별도로 보존했고, 완성 예제는 최종본의 바이트를 그대로 복사했습니다.

이는 조건을 가린 단회 생성 비교가 아닙니다. 미적용 문서가 있는 8개 사례에서는 과거 원문을 참고용으로 함께 싣습니다. 검토 결과는 사실·조건의 보존과 문서 구성에 관한 판단이며, 실제 독자의 이해도·기억·읽는 시간·피로를 측정한 결과는 아닙니다. 사례는 공개용 가상 자료입니다. 문자 수는 공백·개행·Markdown 문법을 포함하며, 길이 자체를 품질 점수로 사용하지 않습니다.

- [교정 절차와 수정 이력](../evaluations/runs/2026-11-03-v0.5.0/protocol.md)
- [원문·버전·SHA-256 기록](../evaluations/runs/2026-11-03-v0.5.0/manifest.json)
- [사례별 수정 관찰](../evaluations/runs/2026-11-03-v0.5.0/observations.json)
- [수정 결과 보고서](repairs-v0.5.0.md)
- [v0.4.0 당시 평가 보존본](evaluation-v0.4.0.md)
