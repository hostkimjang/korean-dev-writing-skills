# trace-slice

`trace-slice`는 로컬 JSON Lines 로그 파일에서 지정한 최소 심각도 이상의 항목을 골라 내는 CLI입니다. 오류 로그만 터미널에서 확인하거나, 경고 이상의 로그를 파일로 저장할 때 사용할 수 있습니다. 로그를 네트워크로 전송하지 않습니다.

이 문서는 **0.4.2** 버전을 기준으로 합니다.

## 설치

Python **3.10 이상**이 필요합니다. 설치와 기본 동작을 확인한 환경은 **Ubuntu 22.04 / Python 3.11**이며, 다른 운영체제에서의 검증 기록은 없습니다.

다음 명령으로 0.4.2 버전을 설치합니다.

```bash
python -m pip install trace-slice==0.4.2
```

설치 후 도움말을 확인합니다.

```bash
trace-slice --help
```

## 첫 실행: 오류 로그 확인

확인할 로컬 JSON Lines 파일을 준비합니다. 각 정상 로그 행에는 `level` 필드가 있어야 합니다.

아래 예제는 로그 파일이 `./logs/api.jsonl`에 있다고 가정합니다. 실제 파일이 다른 위치에 있다면 경로를 바꿔 실행하세요.

```bash
trace-slice ./logs/api.jsonl --level error
```

`error` 항목이 표준 출력으로 나옵니다. 터미널에서 실행하면 결과를 바로 확인할 수 있습니다.

## 사용 형식과 주요 옵션

```text
trace-slice INPUT [--level LEVEL] [--output PATH]
```

| 인수·옵션 | 설명 | 생략 시 동작 |
| --- | --- | --- |
| `INPUT` | 읽을 로컬 JSON Lines 파일의 경로 | 필수 위치 인수이므로 생략할 수 없습니다. |
| `--level LEVEL` | 출력할 최소 심각도. `debug`, `info`, `warn`, `error` 중 하나를 지정합니다. | `info` |
| `--output PATH` | 결과를 저장할 파일 경로 | 표준 출력으로 내보냅니다. |

심각도는 `debug` → `info` → `warn` → `error` 순으로 높아집니다. 지정한 값과 그보다 높은 심각도의 항목이 모두 출력됩니다.

| `--level` 값 | 출력 대상 |
| --- | --- |
| `debug` | `debug`, `info`, `warn`, `error` |
| `info` | `info`, `warn`, `error` |
| `warn` | `warn`, `error` |
| `error` | `error` |

### 기본 심각도로 확인

`--level`을 생략하면 `info` 이상의 항목을 출력합니다.

```bash
trace-slice ./logs/api.jsonl
```

### 경고 이상의 로그를 파일로 저장

**출력 파일이 이미 있으면 덮어씁니다.** 보관해야 할 파일과 경로가 겹치지 않는지 확인한 뒤 실행하세요.

```bash
trace-slice ./logs/api.jsonl --level warn --output ./warnings.jsonl
```

`warn`과 `error` 항목이 `./warnings.jsonl`에 저장됩니다.

## 입력 오류 처리

| 상황 | 동작 |
| --- | --- |
| JSON 구문이 잘못된 행이 있음 | 해당 행을 건너뛰고, 건너뛴 행 수를 표준 오류로 알립니다. 이 이유만으로 실행이 실패하지는 않습니다. |
| `INPUT` 파일을 읽을 수 없음 | 오류를 표준 오류로 알리고 종료 코드 `2`로 끝납니다. |

결과는 표준 출력 또는 `--output`으로 지정한 파일에 기록되며, 위 안내와 오류는 표준 오류로 나옵니다. 잘못된 JSON 행이 있다는 안내를 받았다면, 해당 행은 필터링 결과에 포함되지 않았다는 점을 확인하세요.

## 0.4.2에서 지원하지 않는 기능

- 실행 중 늘어나는 로그를 계속 따라가는 기능
- 날짜 범위를 지정하는 옵션
