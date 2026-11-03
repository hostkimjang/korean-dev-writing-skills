# 개발과 검증

이 저장소는 설치용 스킬과 평가 자료를 분리합니다. 설치 대상은 `skills/korean-dev-writing/`이며, 루트 안내문과 `evaluations/`는 배포·검토를 위한 자료입니다.

## 구조 검사

저장소 루트에서 실행합니다. 현재 로컬 확인 환경은 Python 3.12.14입니다.

```bash
python scripts/check.py
python scripts/check.py --skill-only
```

전체 검사는 배포에 포함되는 파일, 스킬 메타데이터, 단순한 상대 링크, Markdown 펜스와 제목 간격, 사례 JSON과 평가 기준의 구조를 확인합니다. `--skill-only`는 스킬 폴더만 검사하므로 문서와 평가 자료를 작성 중일 때 사용할 수 있습니다.

이 검사기는 Python 표준 라이브러리만 사용하며 완전한 YAML·Markdown 파서가 아닙니다. YAML은 이 저장소에서 사용하는 `name`·`description`과 단순한 `interface` 문자열을 대상으로 합니다. Markdown은 0~3칸 들여쓴 코드 펜스, ATX 제목 뒤 빈 줄, 일반적인 한 줄 링크를 확인합니다. 인용문이나 복잡한 목록 안의 코드 펜스, HTML, 제목 앵커, 복잡한 괄호·이스케이프 링크는 확인 범위에 포함하지 않습니다. 외부 URL을 자동으로 접속해 검사하지도 않습니다.

`evaluations/runs/`의 생성 문서는 평가 원자료입니다. 문체나 형식이 기대와 달라도 원본을 수정하지 않으며, 저장소 문서의 형식 검사에서 제외합니다. 생성 결과의 사실성과 자연스러움은 별도 평가로 확인합니다.

각주 정의의 본문을 파일 경로로 검사하지 않습니다. 각주 안에 명시한 일반 Markdown 링크는 검사하지만, 각주 번호와 참조의 대응 관계 자체는 이 검사기의 범위 밖입니다.

## 의미 보존 검토의 무결성 검사

v0.4.0부터 필수 의미와 탐색 질문을 [별도 계약](evaluation-contract.md)에 고정합니다. 문자열 존재 여부는 자동 신호로 기록하고, 의미 판정은 원자료와 문맥을 대조한 검토 기록으로 남깁니다.

```bash
python scripts/check_claims.py
python scripts/check_claims.py \
  --output-index evaluations/runs/2026-11-03-v0.4.0/output-index.json \
  --reviews \
  evaluations/runs/2026-11-03-v0.4.0/reviews/core.json \
  evaluations/runs/2026-11-03-v0.4.0/reviews/long.json \
  evaluations/runs/2026-11-03-v0.4.0/reviews/onboarding.json \
  evaluations/runs/2026-11-03-v0.4.0/reviews/transfer.json
```

첫 명령은 계약의 ID·참조와 원자료·입력 해시를 검사합니다. 두 번째 명령은 지정한 문서 20개의 출력 해시, 필수 항목과 질문의 판정행, 인용이 실제 원문에 있는지까지 확인합니다. 검사 범위는 `output-index.json`에 선언한 문서입니다. 일부 문서만 넣은 별도 인덱스도 검사할 수 있으므로, 전체 실행을 검증할 때는 실행 기록의 문서 수와 인덱스 범위를 함께 확인합니다.

검사 통과는 글의 품질이나 사실 보존의 합격을 뜻하지 않습니다. 누락·충돌을 정확히 기록한 리뷰도 무결성 검사를 통과합니다. `--write-signals PATH`를 추가하면 문자 수와 정확 문자열의 존재 신호를 별도 JSON에 저장합니다. 이 값으로 의미 보존이나 치명적 오류를 자동 판정하지 않습니다.

검사기 자체의 회귀 검사는 다음 명령으로 실행합니다. 임시 검토 자료를 만들어 필수 항목·문서의 누락과 중복, 잘못된 인용·해시·참조, 기존 선택 명제의 필수 승격, 저장소 밖 경로, 입력 덮어쓰기를 탐지하는지 확인합니다. 정상적인 부분보존·누락 판정은 통과해야 합니다. 이 검사용 판정은 실제 문서 평가 결과에 포함하지 않습니다.

```bash
python scripts/test_check_claims.py
```

## 재현 가능한 패키지

```bash
python scripts/package.py --version 0.4.0
python scripts/package.py --version 0.4.0 --output-dir dist/recheck
```

기본 결과는 `dist/korean-dev-writing-v0.4.0.zip`입니다. ZIP 최상위에는 `korean-dev-writing/` 폴더 한 개가 있고 다음 여섯 파일만 포함됩니다.

- `SKILL.md`
- `LICENSE`
- `agents/openai.yaml`
- `references/before-after-guide.md`
- `references/document-types.md`
- `references/reading-flow.md`

파일 순서, 시간과 권한 메타데이터를 고정하고 무압축 ZIP을 사용합니다. 같은 입력 바이트로 생성하면 같은 ZIP 바이트가 나옵니다. 저장소용 문서, 평가 자료, `.git`, 숨김 파일은 재귀 복사하지 않습니다. 배포 자료를 추가할 때는 `scripts/check.py`의 명시적 파일 목록도 갱신해야 합니다.

## 스킬을 수정할 때

1. 실제로 불편했던 문서와 목적을 기록합니다. 추측한 문제만으로 규칙을 늘리지 않습니다.
2. 수정할 규칙과 예시를 함께 확인합니다. 의미 보존이 필요한 문장을 금지어 교정으로 바꾸지 않습니다.
3. 기존 평가 입력을 바꿔 수정본에 유리하게 만들지 않습니다. 새 실패 사례는 새 버전의 사례로 추가합니다.
4. 새 스킬 해시와 실행 조건을 기록하고, 같은 입력의 미적용 결과와 비교합니다.
5. 이전 생성 결과를 덮어쓰지 않고 별도 실행 디렉터리에 남깁니다.

## 설치 검증

Node.js 22.20 이상, npm/npx, Git이 있는 환경에서 실행합니다. npm 레지스트리에 접속할 수 있어야 합니다.

```bash
python scripts/check_install.py
```

이 검사는 `skills@1.7.5`로 현재 체크아웃을 임시 프로젝트에 설치합니다. 기본 설치와 `--copy` 설치를 각각 실행한 뒤, Claude Code와 Codex의 설치 경로에 배포 파일 여섯 개가 원본과 같은 바이트로 들어갔는지 확인합니다. 따라서 PR에서도 공개 저장소의 이전 버전이 아니라 검토 중인 파일을 검사합니다.

설치 대상은 임시 프로젝트이며 `-g`를 사용하지 않습니다. 검증 중 CLI 사용 통계 전송을 끄고 npm 캐시도 임시 디렉터리에 둡니다. 검사가 끝나면 임시 디렉터리를 정리합니다. 에이전트의 스킬 자동 선택이나 실제 글쓰기 품질은 이 검사 범위에 포함하지 않습니다.

공개 GitHub에서 내려받는 경로까지 확인하려면, 로컬 파일과 공개 저장소의 스킬 버전이 같을 때 다음과 같이 실행합니다.

```bash
python scripts/check_install.py --source hostkimjang/korean-dev-writing-skills
```

## CI

GitHub Actions는 Python 3.12에서 구조 검사, 현재 평가 계약과 검토 인용의 무결성 검사, 패키지 생성 두 번을 실행한 뒤 패키지 바이트를 비교합니다. Node.js 24에서는 위 설치 검증을 실행합니다. 사용한 외부 Action은 확인한 릴리스의 커밋으로 고정했습니다. 워크플로는 저장소 읽기 권한만 요청합니다.

`main`에 게시한 경우에는 해당 커밋의 GitHub 주소로도 설치합니다. 이동하는 브랜치의 최신 파일 대신 실행 대상 커밋을 지정해, 로컬 체크아웃 검사와 공개 다운로드 검사에서 같은 내용을 비교합니다.

로컬 검사가 성공했다는 사실과 원격 CI가 실행됐다는 사실은 구분합니다. 실제 원격 실행 상태는 GitHub Actions 기록으로 확인합니다. 이 CI는 모델을 호출하거나 자연스러움 점수를 자동으로 산출하지 않습니다.
