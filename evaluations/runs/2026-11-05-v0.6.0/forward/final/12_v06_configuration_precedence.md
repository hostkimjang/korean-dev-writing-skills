# 봄바람 구성 로더 설정 안내

봄바람 구성 로더(`breeze-worker`)는 각 설정 항목마다 **CLI → 환경 변수 → YAML → 기본값** 순서로 처음 존재하는 값을 선택합니다. 예를 들어 `timeout_ms`는 CLI에서, `log_level`은 YAML에서 선택할 수 있습니다.

## 설정 항목과 허용값

| 설정·YAML 키 | CLI 옵션 | 환경 변수 | 기본값 | 허용값 |
| --- | --- | --- | --- | --- |
| `timeout_ms` | `--timeout-ms N` | `WORKER_TIMEOUT_MS` | `5000` | 10~30000 정수, 단위 ms, 양 끝값 포함 |
| `log_level` | `--log-level LEVEL` | `WORKER_LOG_LEVEL` | `info` | 소문자 `debug`, `info`, `warn`, `error` |

`WORKER_TIMEOUT_MS`에는 정수를 나타내는 10진 숫자 문자열을 넣습니다.

## YAML 파일 선택과 읽기 오류

`--config PATH`를 지정하면 해당 YAML 파일을 읽습니다. 지정한 파일을 읽을 수 없으면 두 설정을 모두 CLI로 지정했더라도 오류가 발생합니다.

`--config`를 생략하면 현재 디렉터리의 `./worker.yaml`을 찾습니다. 이 파일이 없으면 나머지 설정 출처와 기본값을 사용합니다.

## 실행 전 적용값과 출처 확인

`config inspect`는 설정을 읽고 값을 선택·검증한 뒤 적용값을 표시합니다. 워커를 시작하거나 파일을 수정하지 않습니다.

```text
breeze-worker [--config PATH] [--timeout-ms N] [--log-level LEVEL] config inspect [--show-origin]
```

`--show-origin`은 출처를 `cli`, `env`, `file`, `default`로 표시합니다.

### 프로젝트 디렉터리에서 확인하는 예

프로젝트 디렉터리의 `worker.yaml`은 다음과 같습니다.

```yaml
timeout_ms: 8000
log_level: warn
```

`WORKER_LOG_LEVEL`은 설정하지 않았고, CLI에도 `--log-level`을 지정하지 않은 상태에서 다음 명령을 실행합니다. `WORKER_TIMEOUT_MS=9000`은 이 명령에만 적용됩니다.

```bash
WORKER_TIMEOUT_MS=9000 breeze-worker --timeout-ms 12000 config inspect --show-origin
```

| 설정 | 적용값 | 출처 |
| --- | --- | --- |
| `timeout_ms` | `12000` ms | `cli` |
| `log_level` | `warn` | `file` |

## 선택값 검증 오류와 빈 환경 변수

값을 선택한 뒤에는 **선택된 값만 검증**합니다. 선택값이 유효하지 않으면 시작 오류가 발생하며, 우선순위가 낮은 값으로 대체하지 않습니다. 반대로 유효한 상위 값이 선택됐다면 하위 값이 유효하지 않아도 해당 설정의 시작 오류를 일으키지 않습니다.

환경 변수를 설정하지 않은 상태와 빈 문자열로 설정한 상태는 다릅니다. 빈 환경 변수도 존재하는 값이므로 상위 CLI 값이 없으면 선택되며, 검증에서 오류가 납니다.

예를 들어 CLI에 `--timeout-ms`가 없고 `WORKER_TIMEOUT_MS`가 빈 문자열이면, YAML의 `timeout_ms`가 유효해도 오류가 발생합니다. 검증 오류가 나면 선택된 출처의 값과 허용값을 확인합니다.
