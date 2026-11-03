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

## 설치 확인과 사용

프로젝트 설치 목록을 확인합니다.

```bash
npx skills@1.7.5 list -a claude-code -a codex
```

사용자 공통 경로에 설치했다면 `-g`를 붙입니다.

```bash
npx skills@1.7.5 list -a claude-code -a codex -g
```

목록에 `korean-dev-writing`이 있는지 확인한 뒤, 사용하는 도구에서 스킬을 명시해 문서를 요청합니다.

Claude Code:

```text
/korean-dev-writing 이 저장소의 README를 처음 사용하는 개발자가 이해하고 실행할 수 있게 정리해 주세요.
```

Codex:

```text
$korean-dev-writing 다음 PR 설명을 다듬어 주세요. 원인 조사 상태와 테스트 실행 여부는 유지해 주세요.
```

설치 목록으로 파일이 지정한 경로에 있는지 확인할 수 있습니다. 실제 문서 요청에 스킬이 적용되는지는 사용하는 도구에서 확인합니다.

## 업데이트

아래 명령은 `korean-dev-writing`만 업데이트합니다. 프로젝트에 설치했다면 해당 프로젝트 폴더에서 `-p`로 범위를 지정합니다.

```bash
npx skills@1.7.5 update korean-dev-writing -p
```

사용자 공통 설치는 `-g`로 업데이트합니다.

```bash
npx skills@1.7.5 update korean-dev-writing -g
```

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

## 근거 문서

설치 명령과 경로는 2026-11-03에 다음 공식 자료를 확인해 작성했습니다. 설치 도구의 버전을 고정해 안내와 CI가 같은 버전을 사용하도록 했습니다.

- [skills 1.7.5 명령과 옵션](https://github.com/vercel-labs/skills/blob/v1.7.5/docs/commands.md)
- [skills 1.7.5 지원 도구와 설치 경로](https://github.com/vercel-labs/skills/blob/v1.7.5/docs/agents.md)
- [skills 1.7.5 Node.js 요구 버전](https://github.com/vercel-labs/skills/blob/v1.7.5/package.json)
- [skills 1.7.5 Git 저장소 가져오기 구현](https://github.com/vercel-labs/skills/blob/v1.7.5/src/git.ts)
- [Claude Code 스킬 사용 안내](https://code.claude.com/docs/en/skills)
- [Codex 스킬 사용 안내](https://learn.chatgpt.com/docs/build-skills)
