# 글쓰기 원칙과 출처

확인일: 2026-11-03. 이 문서는 스킬에 반영한 편집 원칙을 원문과 연결합니다. 원문 전체나 장별 본문을 복제하는 자료가 아닙니다.

## 한국어 개발 글쓰기

출발점은 초코글쟁_개발의 [「910. (초안) 글 잘 쓰고 싶은 개발자」](https://wikidocs.net/book/20224)입니다. 글쓰기 원칙을 문맥에 따라 적용하며, 특정 단어 삭제나 문장 길이를 절대 규칙으로 삼지 않습니다.

| 원문 | 채택한 원칙 | 함께 보존한 조건 |
| --- | --- | --- |
| [13. 한 문장에는 하나의 뜻만 담기](https://wikidocs.net/367575) | 문장마다 중심 역할을 분명히 한다. | 서술어가 두 개라는 이유만으로 문장을 나누지 않는다. |
| [15. “의”, “것”, “수 있다” 줄이기](https://wikidocs.net/367577) | 불필요한 명사화와 반복을 줄인다. | 관계·가능성·능력 등 실제 의미는 유지한다. |
| [20. 추측을 사실처럼 쓰지 않기](https://wikidocs.net/367582) | 확인한 사실과 가설을 구분한다. | 미확인 항목을 남기며 원인을 확정하지 않는다. |
| [51. README는 프로젝트의 첫인상이다](https://wikidocs.net/367613) | 프로젝트의 목적과 첫 실행을 이해하게 한다. | 프로젝트 성격과 현재 상태에 맞춰 정보를 고른다. |
| [54. 사용법 문서는 독자의 행동 순서로 작성한다](https://wikidocs.net/367616) | 독자의 행동과 확인 결과를 순서대로 연결한다. | 원자료에 없는 경로나 성공 메시지를 만들지 않는다. |
| [68. 짧은 문장과 긴 문장을 섞는 법](https://wikidocs.net/367630) | 핵심과 설명의 역할에 맞춰 문장 길이를 조절한다. | 너무 짧게 끊긴 문장도 다시 연결한다. |
| [76. AI에게 글 피드백을 받는 방법](https://wikidocs.net/367638) | 목적과 독자를 정하고 기술 사실을 확인한다. | 매끄러운 표현이 사실 검증을 대신하지 않는다. |

## 스킬 구성과 평가

- [Agent Skills specification](https://agentskills.io/specification): `SKILL.md`와 선택적으로 읽는 참고 자료의 구조.
- [Anthropic: Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): 간결한 지침, 구체적 예시, 스킬 미적용 결과와 비교하는 평가 방식.
- [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills): Codex의 로컬 스킬 경로와 메타데이터.
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills): 프로젝트·사용자 스킬 경로와 명시적 호출.
- [CommonMark 0.31.2: Fenced code blocks](https://spec.commonmark.org/0.31.2/#fenced-code-blocks): Markdown 예시에 코드 블록이 들어갈 때 바깥 펜스를 더 길게 작성하는 근거.

## 긴 문서의 이해와 읽기 부담

v0.3.0에서는 독해·기억 연구, 한국어 독해와 공공언어 연구, 화면 사용성 연구, W3C·Google·Microsoft의 공식 지침과 Diátaxis를 추가로 검토했습니다. 원저 전문·공개 초록·실무 지침을 구분하고, 근거와 적용 한계를 [읽기 흐름 조사](reading-research.md)에 기록했습니다.

핵심은 구조를 알아볼 단서, 문장 간 관계, 관련 정보의 근접 배치, 필요한 재정리입니다. 제목 길이·집중시간·문장 수를 고정하는 규칙이나 길이 감소를 품질 향상으로 환산하는 기준은 채택하지 않았습니다. 스킬에 적용하는 상세 내용은 [긴 문서의 읽기 흐름](../skills/korean-dev-writing/references/reading-flow.md)에 있습니다.

## 예시의 출처

스킬의 전후 교정 예시와 평가용 프로젝트는 이 저장소를 위해 새로 작성한 가상 자료입니다. 실제 사용자 서비스의 운영 현황, 개인정보, 내부 문서를 포함하지 않습니다. 비교에 사용한 기존 스킬은 사용자가 제공한 첨부 파일이며, 출처와 바이트 해시는 평가 실행 기록에 별도로 남깁니다.
