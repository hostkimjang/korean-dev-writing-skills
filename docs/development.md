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

## 재현 가능한 패키지

```bash
python scripts/package.py --version 0.2.0
python scripts/package.py --version 0.2.0 --output-dir dist/recheck
```

기본 결과는 `dist/korean-dev-writing-v0.2.0.zip`입니다. ZIP 최상위에는 `korean-dev-writing/` 폴더 한 개가 있고 다음 다섯 파일만 포함됩니다.

- `SKILL.md`
- `LICENSE`
- `agents/openai.yaml`
- `references/before-after-guide.md`
- `references/document-types.md`

파일 순서, 시간과 권한 메타데이터를 고정하고 무압축 ZIP을 사용합니다. 같은 입력 바이트로 생성하면 같은 ZIP 바이트가 나옵니다. 저장소용 문서, 평가 자료, `.git`, 숨김 파일은 재귀 복사하지 않습니다. 배포 자료를 추가할 때는 `scripts/check.py`의 명시적 파일 목록도 갱신해야 합니다.

## 스킬을 수정할 때

1. 실제로 불편했던 문서와 목적을 기록합니다. 추측한 문제만으로 규칙을 늘리지 않습니다.
2. 수정할 규칙과 예시를 함께 확인합니다. 의미 보존이 필요한 문장을 금지어 교정으로 바꾸지 않습니다.
3. 기존 평가 입력을 바꿔 수정본에 유리하게 만들지 않습니다. 새 실패 사례는 새 버전의 사례로 추가합니다.
4. 새 스킬 해시와 실행 조건을 기록하고, 같은 입력의 미적용 결과와 비교합니다.
5. 이전 생성 결과를 덮어쓰지 않고 별도 실행 디렉터리에 남깁니다.

## CI

GitHub Actions는 Python 3.12에서 구조 검사와 패키지 생성 두 번을 실행한 뒤 바이트를 비교합니다. 사용한 외부 Action은 확인한 릴리스의 커밋으로 고정했습니다. 워크플로는 저장소 읽기 권한만 요청합니다.

로컬 검사가 성공했다는 사실과 원격 CI가 실행됐다는 사실은 구분합니다. 실제 원격 실행 상태는 GitHub Actions 기록으로 확인합니다. 이 CI는 모델을 호출하거나 자연스러움 점수를 자동으로 산출하지 않습니다.
