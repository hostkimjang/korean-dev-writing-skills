# 봄바람 구성 로더 설정 가이드

봄바람 구성 로더(`breeze-worker`)는 **설정 항목마다 CLI → 환경 변수 → YAML → 기본값 순서로 처음 존재하는 값**을 선택합니다. 항목별로 선택하므로 `timeout_ms`와 `log_level`의 출처는 서로 다를 수 있습니다.

## 설정 이름과 허용값

| 설정 | CLI | 환경 변수 | YAML | 기본값·허용값 |
| --- | --- | --- | --- | --- |
| 제한 시간 | `--timeout-ms N` | `WORKER_TIMEOUT_MS` | `timeout_ms` | 기본값 `5000`. 밀리초 단위 정수, `10`~`30000` 포함 |
| 로그 수준 | `--log-level LEVEL` | `WORKER_LOG_LEVEL` | `log_level` | 기본값 `info`. 소문자 `debug`, `info`, `warn`, `error` |

`WORKER_TIMEOUT_MS`에는 10진 정수를 나타내는 숫자 문자열을 넣습니다. 값을 고른 뒤에는 **선택된 값만 검증**합니다. 선택값이 잘못되면 시작 오류가 나며 하위 출처의 값으로 대체하지 않습니다. 높은 우선순위의 선택값이 유효하면, 선택되지 않은 하위 값이 잘못되어도 해당 설정의 시작 오류는 나지 않습니다.

## 빈 환경 변수와 파일 읽기 오류

환경 변수 미설정과 빈 문자열은 다릅니다. 빈 문자열도 존재하는 값이므로, 더 높은 CLI 값이 없으면 선택되어 오류가 납니다. 예를 들어 `WORKER_TIMEOUT_MS`가 비어 있고 `--timeout-ms`가 없으면 YAML의 값이 유효해도 오류입니다.

- `--config PATH`로 지정한 YAML을 읽을 수 없으면 오류입니다. 두 설정을 모두 CLI로 제공했어도 이 오류는 발생합니다.
- `--config`를 생략하면 현재 작업 디렉터리의 `./worker.yaml`을 찾습니다. 이 기본 파일이 없으면 다른 출처나 기본값을 사용합니다. 파일 부재의 예외를 모든 읽기 실패에 적용해서는 안 됩니다.

## 실행 전에 적용값과 출처 확인하기

대괄호는 선택 사항이며 실제로 입력하지 않습니다.

```text
breeze-worker [--config PATH] [--timeout-ms N] [--log-level LEVEL] config inspect [--show-origin]
```

`config inspect`는 설정을 읽고 선택·검증한 값을 표시합니다. 워커를 시작하거나 파일을 수정하지 않습니다. `--show-origin`을 붙이면 출처를 `cli`, `env`, `file`, `default`로 확인할 수 있습니다. 오류가 나면 선택값과 파일 읽기 조건을 확인합니다.

현재 작업 디렉터리에 다음 `worker.yaml`이 이미 있다고 가정합니다.

```yaml
timeout_ms: 8000
log_level: warn
```

아래 명령은 `WORKER_LOG_LEVEL`이 설정되지 않은 환경에서 사용하며, `--log-level`도 지정하지 않습니다. `WORKER_TIMEOUT_MS=9000`은 이 명령에만 적용합니다.

```sh
WORKER_TIMEOUT_MS=9000 breeze-worker --timeout-ms 12000 config inspect --show-origin
```

확인할 값은 `timeout_ms=12000`과 출처 `cli`, `log_level=warn`과 출처 `file`입니다. 제한 시간은 CLI가 환경 변수와 파일보다 우선합니다. 로그 수준은 상위 출처에 값이 없어 파일에서 선택됩니다.
