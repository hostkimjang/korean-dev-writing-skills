# v0.6.0 문서 개선 결과

갱신일: 2026-11-05 · 적용한 스킬: **v0.6.0** · [고정한 스킬 파일](../evaluations/runs/2026-11-05-v0.6.0/snapshots/v0.6.0)

기존 문서 10개를 대조해 필요한 부분을 교정했습니다. 각 문서에서 무엇을 고쳤는지, 사실과 조건을 어떻게 보존했는지를 아래에서 확인할 수 있습니다.

[현재 문서 10개 바로 읽기](examples/README.md) · [수정 결과 보고서](repairs-v0.6.0.md) · [교정 전후를 나란히 보기](comparisons/index.html)

## 사례별 수정 결과

| 문서 | 교정 전 | 교정 완료 | 수정 결과 |
| --- | ---: | ---: | --- |
| [CLI README](examples/01_cli_readme.md) | [1,855자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/01_cli_readme.md) | [1,855자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/01_cli_readme.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [이벤트 수집 아키텍처](examples/02_event_architecture.md) | [2,553자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/02_event_architecture.md) | [2,553자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/02_event_architecture.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [진단 PR](examples/03_investigation_pr.md) | [973자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/03_investigation_pr.md) | [973자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/03_investigation_pr.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [장애 대응 절차](examples/04_incident_runbook.md) | [2,939자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/04_incident_runbook.md) | [2,939자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/04_incident_runbook.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [중복 판정 저장소 ADR](examples/05_storage_adr.md) | [2,116자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/05_storage_adr.md) | [2,116자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/05_storage_adr.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [문단 교정](examples/06_paragraph_edit.md) | [379자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/06_paragraph_edit.md) | [379자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/06_paragraph_edit.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [색인 갱신 온보딩](examples/07_index_onboarding.md) | [4,609자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/07_index_onboarding.md) | [4,609자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/07_index_onboarding.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [짧은 관측 PR](examples/08_short_log_pr.md) | [400자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/08_short_log_pr.md) | [399자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/08_short_log_pr.md) | 검증하지 못한 대상을 원인 가설과 추가 진단 로그 출력으로 명시했다. |
| [달무리 설정배포 서비스의 예약 적용 안내](examples/09_config_rollout.md) | [1,799자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/09_config_rollout.md) | [1,799자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/09_config_rollout.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |
| [단비함 썸네일 작업기의 기록 순서 변경 보고](examples/10_thumbnail_report.md) | [413자](../evaluations/runs/2026-11-03-v0.5.0/outputs/revised/10_thumbnail_report.md) | [413자](../evaluations/runs/2026-11-05-v0.6.0/outputs/revised/10_thumbnail_report.md) | v0.5.0 최종본을 바이트 단위로 보존했다. |

## 전문 비교

- [아키텍처·ADR·장애 대응 절차: 전문 9개](comparisons/long-documents.md)
- [온보딩·짧은 관측 PR: 전문 6개](comparisons/reading-flow.md)
- [설정배포 안내·썸네일 작업 보고: 전문 4개](comparisons/transfer-checks.md)

HTML에는 10개 사례의 본문 28개와 입력 10개를 포함했습니다. 이전 v0.5.0 문서와 현재 v0.6.0 문서를 기본으로 비교하고, 미적용 원문이 있는 8개 사례에서는 그 원문도 선택할 수 있습니다.

## 새 주제의 최초 작성본 비교

로그 보관 정책과 구성 값 우선순위를 이전 출력 없이 각각 작성했습니다. [두 버전의 본문·필수 의미 판정·읽기 관찰](comparisons/new-topics.md)을 별도로 공개합니다.

## 작성과 확인 방법

v0.5.0 문서와 같은 원자료를 대조해 필요한 부분을 고쳤습니다. v0.6.0 지침으로 교정한 문서와 수정할 필요가 없어 보존한 문서를 사례별로 구분합니다. 현재 본문은 검토와 수정을 거친 최종본입니다. 이전 원문과 수정 이력은 별도로 보존했고, 완성 예제는 최종본의 바이트를 그대로 복사했습니다.

이는 조건을 가린 단회 생성 비교가 아닙니다. 미적용 문서가 있는 8개 사례에서는 과거 원문을 참고용으로 함께 싣습니다. 검토 결과는 사실·조건의 보존과 문서 구성에 관한 판단이며, 실제 독자의 이해도·기억·읽는 시간·피로를 측정한 결과는 아닙니다. 사례는 공개용 가상 자료입니다. 문자 수는 공백·개행·Markdown 문법을 포함하며, 길이 자체를 품질 점수로 사용하지 않습니다.

- [교정 절차와 수정 이력](../evaluations/runs/2026-11-05-v0.6.0/protocol.md)
- [원문·버전·SHA-256 기록](../evaluations/runs/2026-11-05-v0.6.0/manifest.json)
- [사례별 수정 관찰](../evaluations/runs/2026-11-05-v0.6.0/observations.json)
- [수정 결과 보고서](repairs-v0.6.0.md)
- [v0.5.0 당시 평가 보존본](evaluation-v0.5.0.md)
