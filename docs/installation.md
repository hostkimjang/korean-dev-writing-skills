# 설치와 관리

이 안내는 Claude Code와 Codex의 로컬 스킬 설치를 다룹니다. 간편 설치에는 Node.js 22.20 이상(npm·npx 포함)과 Git이 필요합니다. 명령의 `skills@1.7.5`는 설치 도구의 버전이며, 설치할 스킬 이름은 `korean-dev-writing`입니다.

## 간편 설치

스킬을 사용할 **프로젝트 폴더**에서 실행합니다.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing
```

안내에 따라 Claude Code 또는 Codex를 선택합니다. 기본 설치 범위는 현재 프로젝트입니다.

### 사용할 도구 지정

Claude Code에 설치합니다.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing -a claude-code
```

Codex에 설치합니다.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing -a codex
```

두 도구에 함께 설치합니다.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing -a claude-code -a codex
```

### 모든 프로젝트에서 사용

사용자 공통 경로에 설치하려면 `-g`를 붙입니다. 다음 명령은 Claude Code와 Codex에 공통으로 설치합니다. 한 도구만 사용한다면 해당 `-a` 옵션만 남기세요.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing -a claude-code -a codex -g
```

| 도구 | 프로젝트 설치 | 사용자 공통 설치 (`-g`) |
| --- | --- | --- |
| Claude Code | `.claude/skills/korean-dev-writing/` | `~/.claude/skills/korean-dev-writing/` |
| Codex | `.agents/skills/korean-dev-writing/` | `~/.agents/skills/korean-dev-writing/` |

기본 설치에서는 여러 도구가 하나의 스킬 원본을 공유하도록 심볼릭 링크를 사용할 수 있습니다. 이때 Claude Code의 스킬 경로가 공통 원본을 가리키는 것은 정상입니다.

### 복사 방식 선택

각 도구의 경로에 독립된 복사본을 두려면 `--copy`를 붙입니다.

```bash
npx skills@1.7.5 add hostkimjang/korean-dev-writing-skills --skill korean-dev-writing -a claude-code -a codex --copy
```

사용자 공통 설치에도 `-g --copy`를 함께 사용할 수 있습니다. 설치 선택과 확인을 생략하려면 도구를 지정한 명령 끝에 `-y`(`--yes`)를 붙입니다. 처음 실행할 때 npx의 다운로드 확인도 생략하려면 명령의 시작을 `npx --yes skills@1.7.5`로 바꾸세요.

## 향상 스킬 함께 설치

v0.8.0에서 추가한 선택형 설치기는 기본 스킬과 `humanize-korean`, `stack-diagram`을 같은 도구·설치 범위에 설치합니다. 현재 기본 구성에는 이 저장소에서 보강한 윤문 스킬을 동봉하며, 도식 스킬은 [선정한 원본과 커밋](enhancements.md)에서 가져옵니다. 기본 설치 명령도 그대로 사용할 수 있습니다.

스킬을 사용할 프로젝트 폴더에서 실행합니다.

```bash
npx --yes --package=github:hostkimjang/korean-dev-writing-skills korean-dev-writing-install --with-enhancements -a codex
```

Claude Code에는 `-a claude-code`를 지정합니다. 두 도구의 사용자 공통 경로에 설치하려면 다음 명령을 사용합니다.

```bash
npx --yes --package=github:hostkimjang/korean-dev-writing-skills korean-dev-writing-install --with-enhancements -a codex -a claude-code -g
```

설치기는 실행 전에 대상 스킬·원본·커밋·도구·범위를 보여 줍니다. 여기서 승인하면 각 스킬을 순서대로 설치하고 실제 결과를 확인합니다. 명령 앞의 `npx --yes`는 npm 다운로드 확인만 생략합니다. 설치기의 최종 확인도 생략하려면 명령 끝에 `--yes`를 붙입니다.

| 옵션 | 동작 |
| --- | --- |
| `--with-enhancements` | 기본 스킬과 두 향상 스킬을 설치합니다. 생략하면 기본 스킬만 설치합니다. |
| `-a codex`, `-a claude-code` | 대상 도구를 지정합니다. 두 옵션을 함께 쓸 수 있습니다. 터미널에서는 생략 시 선택하고, 비대화형 실행에서는 명시해야 합니다. |
| `-g`, `--global` | 사용자 공통 경로에 설치합니다. 기본값은 현재 프로젝트입니다. |
| `--project-dir PATH` | 프로젝트 설치의 기준 폴더를 지정합니다. |
| `--copy` | 도구별 경로에 파일을 복사합니다. 기본은 설치 도구의 공유 경로·링크 방식입니다. |
| `--dry-run` | 설치 계획만 출력합니다. 스킬 파일을 설치하거나 교체하지 않습니다. |
| `--humanize-source SOURCE` | 동봉한 윤문 보강본 대신 외부 원본을 설치합니다. 기본 원본의 커밋과 하위 경로는 새 원본에 적용하지 않습니다. |
| `--humanize-ref REF` | 외부 윤문 원본의 40자리 커밋 SHA를 선택합니다. 윤문 원본 옵션과 함께 사용해야 하며, 동봉본에 이 옵션만 지정하면 설치 전에 중단합니다. |
| `--stack-source SOURCE`, `--stack-ref REF` | 도식 스킬의 원본과 리비전을 변경합니다. |
| `--replace-existing` | 같은 이름으로 설치된 스킬의 교체를 명시적으로 허용합니다. |
| `--yes` | 표시된 설치 계획의 확인을 생략합니다. 기존 스킬 교체까지 허용하지는 않습니다. |

`SOURCE`에는 GitHub의 `소유자/저장소` 또는 저장소 루트의 HTTPS 주소를 사용합니다. 커밋은 `--humanize-ref`·`--stack-ref` 또는 주소 뒤의 `#40자리SHA`로 지정합니다. 이동하는 태그·브랜치 이름이나 `/tree/` 하위 경로 URL은 받지 않습니다. 다른 원본에도 해당 스킬 이름과 필요한 자원이 포함된 독립 스킬 디렉터리가 있어야 합니다. 별도 설치 스크립트나 저장소 바깥 자원이 필요한 모든 동명 프로젝트를 지원하는 옵션은 아닙니다.

전역 설치에서 `CLAUDE_CONFIG_DIR` 또는 `CODEX_HOME`을 직접 설정했다면 앞뒤 공백 없는 절대 경로를 사용합니다. 선택한 도구의 설정이 상대 경로이거나 앞뒤 공백을 포함해 실제 설치 위치와 사전 검사 위치가 어긋날 수 있으면 설치 전에 중단합니다.

### 기존 스킬 교체와 설치 실패

선택한 설치 범위에 같은 이름의 디렉터리나 링크가 있으면 첫 설치 전에 중단합니다. 직접 수정한 파일이나 다른 제작자의 동명 스킬을 보존하기 위한 동작입니다. 교체할 원본과 대상을 확인한 뒤 필요한 파일을 보관하고 `--replace-existing`를 추가하세요.

설치 도중 한 스킬이 실패하면 나머지 설치를 중단하고 성공한 항목과 실패한 항목을 구분합니다. 이미 설치된 파일을 자동으로 삭제하지 않습니다. 원인을 해결한 뒤 같은 대상을 다시 설치하려면 `--replace-existing`가 필요합니다. 향상 설치기로 설치한 기본 스킬과 기본 구성의 윤문 스킬은 이 배포 패키지의 로컬 파일에서 복사되므로, 이 스킬들을 갱신할 때도 최신 설치기를 다시 실행하세요.

동봉한 윤문 보강본과 도식 스킬의 고정 커밋을 유지하려면 설치기를 다시 실행합니다. `npx skills update`로 외부 스킬을 직접 갱신하면 실제 설치 버전이 이 프로젝트에서 검증한 조합과 달라질 수 있습니다. 설치 이력은 해당 범위의 `skills list`와 설치 도구의 기록에서 확인합니다.

### 저장소를 내려받은 경우

저장소 루트에서 설치 계획을 확인합니다.

```bash
node scripts/install.mjs --with-enhancements -a codex --dry-run
```

다른 작업 프로젝트에 설치하려면 `--project-dir`로 기존 폴더를 지정합니다. `--dry-run`을 빼면 같은 계획으로 설치합니다. npx로 설치기를 처음 실행하면 계획 확인 모드에서도 설치기 자체의 다운로드는 발생할 수 있습니다.

## 설치 확인과 사용

프로젝트 설치 목록을 확인합니다.

```bash
npx skills@1.7.5 list -a claude-code -a codex
```

사용자 공통 경로에 설치했다면 `-g`를 붙입니다.

```bash
npx skills@1.7.5 list -a claude-code -a codex -g
```

목록에 `korean-dev-writing`이 있는지 확인합니다. 향상 설치를 선택했다면 `humanize-korean`, `stack-diagram`도 확인한 뒤, 사용하는 도구에서 기본 스킬을 명시해 문서를 요청합니다.

Claude Code:

```text
/korean-dev-writing 이 저장소의 README를 처음 사용하는 개발자가 이해하고 실행할 수 있게 정리해 주세요.
```

Codex:

```text
$korean-dev-writing 다음 PR 설명을 다듬어 주세요. 원인 조사 상태와 테스트 실행 여부는 유지해 주세요.
```

설치 목록으로 파일이 지정한 경로에 있는지 확인할 수 있습니다. 실제 문서 요청에 스킬이 적용되는지는 사용하는 도구에서 확인합니다.

기본 스킬은 문서 작업에 필요한 경우 사용 가능한 향상 스킬을 함께 적용하도록 안내합니다. 실제 호출 여부는 에이전트의 판단과 환경에 달려 있습니다. 특정 작업에서 함께 사용하려면 각 도구의 방식으로 `humanize-korean` 또는 `stack-diagram`도 명시하세요. 스킬 파일의 설치는 Python·Playwright·Chromium 설치나 실제 문서·이미지 생성 완료를 뜻하지 않습니다.

## 업데이트

GitHub 원본에 대해 일반 `skills add` 명령으로 설치했다면 아래 명령으로 `korean-dev-writing`만 업데이트합니다. 프로젝트에 설치했다면 해당 프로젝트 폴더에서 `-p`로 범위를 지정합니다.

```bash
npx skills@1.7.5 update korean-dev-writing -p
```

사용자 공통 설치는 `-g`로 업데이트합니다.

```bash
npx skills@1.7.5 update korean-dev-writing -g
```

향상 설치기로 설치했다면 같은 프로젝트에서 최신 설치기를 다시 실행합니다. 기존 파일을 교체하므로 `--replace-existing`가 필요합니다.

```bash
npx --yes --package=github:hostkimjang/korean-dev-writing-skills korean-dev-writing-install --with-enhancements -a codex --replace-existing
```

처음 선택한 대상 도구·전역 여부·복사 방식을 다시 지정합니다. 사용자 지정 원본을 썼다면 `--humanize-source`, `--humanize-ref`, `--stack-source`, `--stack-ref`도 다시 전달하세요. 생략하면 이 배포 패키지에 동봉한 윤문 스킬과 기본 도식 원본의 커밋을 선택합니다. 표시된 설치 계획에서 실제 교체 대상을 확인할 수 있습니다.

수동으로 복사한 파일은 설치 도구의 관리 기록에 없을 수 있습니다. 수동 설치를 유지한다면 저장소의 최신 스킬 폴더를 다시 복사하세요.

## 삭제

프로젝트 폴더에서 다음 명령을 실행하면 지정한 두 도구의 `korean-dev-writing`을 삭제합니다. 한 도구에서만 제거하려면 그 도구의 `-a` 옵션만 남깁니다.

```bash
npx skills@1.7.5 remove korean-dev-writing -a claude-code -a codex
```

사용자 공통 설치를 삭제할 때는 `-g`를 붙입니다.

```bash
npx skills@1.7.5 remove korean-dev-writing -a claude-code -a codex -g
```

표시되는 대상과 설치 범위를 확인한 뒤 삭제를 확정합니다.

## 수동 설치

저장소를 내려받습니다.

```bash
git clone https://github.com/hostkimjang/korean-dev-writing-skills.git
```

내려받은 저장소의 `skills/korean-dev-writing/` 폴더 전체를 아래 위치에 복사합니다. `SKILL.md`뿐 아니라 `references/`, `agents/`, `LICENSE`도 함께 복사하세요. 같은 이름의 스킬을 직접 수정해 사용 중이라면 기존 내용을 비교하고 백업한 뒤 교체합니다.

| 도구와 범위 | 복사할 위치 |
| --- | --- |
| Claude Code: 현재 프로젝트 | `.claude/skills/korean-dev-writing/` |
| Claude Code: 사용자 공통 | `~/.claude/skills/korean-dev-writing/` |
| Codex: 현재 프로젝트 | `.agents/skills/korean-dev-writing/` |
| Codex: 사용자 공통 | `~/.agents/skills/korean-dev-writing/` |

표의 프로젝트 경로는 **이 스킬을 사용할 작업 프로젝트의 루트**를 기준으로 합니다. 복사 후 해당 경로에 `SKILL.md`와 참고 파일들이 있는지 확인하세요.

윤문 스킬도 수동 설치하려면 `skills/humanize-korean/` 전체를 같은 스킬 설치 경로 아래에 복사합니다. 참고 문서·스크립트·라이선스·기반 프로젝트 고지를 함께 유지합니다. 도식 스킬의 설치 출처와 실행 환경은 [향상 스킬 안내](enhancements.md)에 정리했습니다.

## 근거 문서

설치 명령과 경로는 2026-11-03에 다음 공식 자료를 확인해 작성했습니다. 설치 도구의 버전을 고정해 안내와 CI가 같은 버전을 사용하도록 했습니다.

- [skills 1.7.5 명령과 옵션](https://github.com/vercel-labs/skills/blob/v1.7.5/docs/commands.md)
- [skills 1.7.5 지원 도구와 설치 경로](https://github.com/vercel-labs/skills/blob/v1.7.5/docs/agents.md)
- [skills 1.7.5 Node.js 요구 버전](https://github.com/vercel-labs/skills/blob/v1.7.5/package.json)
- [skills 1.7.5 Git 저장소 가져오기 구현](https://github.com/vercel-labs/skills/blob/v1.7.5/src/git.ts)
- [Claude Code 스킬 사용 안내](https://code.claude.com/docs/en/skills)
- [Codex 스킬 사용 안내](https://learn.chatgpt.com/docs/build-skills)
