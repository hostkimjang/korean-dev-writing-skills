# 향상 스킬 설치와 적용

v0.8.0은 한국어 개발 문서 스킬에 선택형 향상 설치기를 추가합니다. 새 사용자도 기본 문서 작성, 추가 윤문, 아키텍처 도식을 같은 설치 절차로 준비할 수 있습니다. 기본 스킬은 단독으로 사용할 수 있습니다.

## 설치할 구성

| 스킬 | 역할 | 기본 원본 | 고정 커밋 |
| --- | --- | --- | --- |
| `korean-dev-writing` | 사실·의미 보존, 문서 구성, 읽기 흐름, 실행 안내 | 이 배포 패키지의 `skills/korean-dev-writing` | 실행한 배포 패키지의 파일 |
| `humanize-korean` | 문장 교정·교열·윤문 | [nathankim0/humanize-korean](https://github.com/nathankim0/humanize-korean) | `b51aa5985be0a94a645788f1395b29a118bc9c33` |
| `stack-diagram` | 기술 스택과 아키텍처 도식 | [caru-ini/stack-diagram](https://github.com/caru-ini/stack-diagram) | `1ed53e3e9525364ae5d82e0430f2bb3f7ef4c838` |

확인일은 2026-11-08입니다. 원본·리비전·역할은 [enhancements.json](../enhancements.json)에서 관리합니다. 외부 스킬을 이 저장소에 복제하지 않고 설치할 때 각각의 원본에서 가져옵니다.

`humanize-korean`은 동명 배포본이 여러 개입니다. 여기서는 필요한 참고 자료와 Python 스크립트를 스킬 폴더 안에 포함한 Nathan 배포본을 새 사용자용 기본값으로 선택했습니다. 기존 사용자가 설치한 스킬의 출처를 탐지하거나 동일성을 확인한 결과는 아닙니다. 다른 독립 배포본은 `--humanize-source`와 필요한 경우 `--humanize-ref`로 지정할 수 있습니다. 원본을 변경하면 기존 기본값의 커밋과 하위 경로를 새 원본에 잘못 붙이지 않습니다.

## 함께 설치하기

Node.js 22.20 이상과 Git이 필요합니다. 스킬을 사용할 프로젝트 폴더에서 실행합니다.

```bash
npx --yes --package=github:hostkimjang/korean-dev-writing-skills korean-dev-writing-install --with-enhancements -a codex
```

설치할 출처·커밋·도구·범위를 확인하고 승인하면 설치합니다. Claude Code에는 `-a claude-code`, 두 도구에는 두 옵션을 함께 지정합니다. 전역 설치, 기존 스킬 교체, 미리보기와 원본 변경은 [설치 안내](installation.md)에 정리했습니다.

같은 이름의 기존 스킬이 있으면 먼저 중단하며, `--yes`만으로 덮어쓰지 않습니다. `--replace-existing`로 교체 의도를 명시해야 합니다. 설치 오류가 발생하면 완료한 항목과 실패 항목을 구분하고, 성공한 설치를 임의로 되돌리지 않습니다.

## 작업에 맞춰 적용하기

1. `korean-dev-writing`으로 사실·조건·문서 구조를 먼저 정리합니다.
2. 문장 교정이 필요하면 `humanize-korean`의 해당 모드를 적용하고, 원자료와 의미·식별자·구조를 다시 대조합니다.
3. 관계를 그림으로 설명해야 하면 `stack-diagram`을 적용하고, 본문과 요소·방향·조건을 맞춥니다.

설치된 스킬을 매번 모두 실행하는 절차가 아닙니다. 짧은 문장 교정에 아키텍처 그림을 추가하거나, 이미 충분히 다듬은 문서를 반복 교정하지 않습니다. 실제 적용은 에이전트가 현재 환경에서 읽을 수 있는 스킬과 사용자의 요청에 따라 결정합니다. 외부 스킬이 없거나 실행 환경이 부족하면 기본 문서 작업을 마치고, 수행하지 않은 단계를 완료했다고 표시하지 않습니다.

문서 작성에 필요한 조건·예외·수치·코드 식별자·소제목·표를 보존합니다. 자연스러운 문체를 위해 사실을 추가하거나 기술적 의미를 약화하지 않습니다. 갤러리 게시나 외부 공유는 별도의 사용자 요청 범위에서 수행합니다.

## 실행 환경과 라이선스

| 원본 | 실행 환경 | 라이선스·출처 |
| --- | --- | --- |
| Nathan `humanize-korean` | 텍스트 지침은 에이전트가 읽어 적용합니다. 장문 작업표·재조립·검사 스크립트는 Python 표준 라이브러리를 사용합니다. | [MIT LICENSE](https://github.com/nathankim0/humanize-korean/blob/b51aa5985be0a94a645788f1395b29a118bc9c33/LICENSE), [기반 프로젝트 고지](https://github.com/nathankim0/humanize-korean/blob/b51aa5985be0a94a645788f1395b29a118bc9c33/THIRD_PARTY_NOTICES.md) |
| `stack-diagram` | Python 3.9 이상, 로고 다운로드용 네트워크, PNG 생성·시각 검수용 Playwright와 Chromium이 필요합니다. | [코드·문서 MIT](https://github.com/caru-ini/stack-diagram/blob/1ed53e3e9525364ae5d82e0430f2bb3f7ef4c838/LICENSE), [글꼴 SIL OFL 1.1](https://github.com/caru-ini/stack-diagram/tree/1ed53e3e9525364ae5d82e0430f2bb3f7ef4c838/skills/stack-diagram/assets/fonts) |

설치기는 스킬 파일을 설치합니다. Python·Playwright·Chromium을 시스템에 자동 설치하거나 외부 스킬의 프로그램을 실행하지 않습니다. `stack-diagram`은 최종 산출물이 HTML이어도 PNG를 렌더링해 확인하는 과정을 지시하므로, 해당 검수까지 수행할 때 렌더링 환경이 필요합니다. 각 원본의 실행 지침과 라이선스가 적용됩니다.

이 프로젝트의 MIT 라이선스가 외부 스킬과 그 자산의 라이선스를 대체하지 않습니다. 향후 외부 파일을 복사해 재배포하는 방식을 추가한다면 원본의 저작권·라이선스·기반 프로젝트 고지를 함께 포함해야 합니다.

## 검증 범위

- `scripts/test_install.mjs`: 옵션과 설치 범위, 원본 변경 시 리비전 처리, 기존 스킬 보호, 설치 실패·일부 성공·잘못된 응답을 검사합니다.
- `scripts/check_enhanced_install.mjs`: 임시 프로젝트에서 실제 설치 도구로 기본·향상 구성을 설치하고, Codex·Claude Code 경로의 기본 파일과 외부 스킬 자원을 확인합니다. 배포 패키지에 설치기와 설정이 포함되는지도 검사합니다.
- CI는 Linux와 Windows에서 설치 통합 검증을 실행합니다. 플랫폼별 결과는 해당 실행 로그로 확인합니다.
- 기본 스킬 6개 파일은 [v0.8.0 배포 기록](../evaluations/runs/2026-11-08-v0.8.0/manifest.json)에 고정합니다. 기존 14개 문서와 교정 리뷰는 v0.7.0 기록을 보존하며, 새 조합의 품질 측정 결과로 표시하지 않습니다.

설치 검증은 에이전트의 실제 스킬 호출, 전체 윤문 작업, 그림 생성, 사람의 읽기 속도나 선호도 평가와 구분합니다. 설치된 파일과 명령의 동작을 확인했다고 해서 모든 작업의 결과가 향상된다고 보증하지 않습니다.

## 설치 도구 근거

설치기는 `skills@1.7.5`의 `add`를 원본별로 한 번씩 실행합니다. `--skill`, `--agent`, `--global`, `--copy`는 [공식 명령 안내](https://github.com/vercel-labs/skills/blob/v1.7.5/docs/commands.md)를 따릅니다. 기계 판독 결과는 [설치 구현의 JSON 출력](https://github.com/vercel-labs/skills/blob/v1.7.5/src/add.ts)으로 확인합니다. `experimental_sync`의 실험적 스킬팩 기능에는 의존하지 않습니다.
