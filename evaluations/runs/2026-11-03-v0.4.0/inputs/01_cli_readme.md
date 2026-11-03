제공 자료로 요청한 한국어 문서를 작성하세요. 최종 문서 본문만 작성하세요.

{
  "user_prompt": "아래 프로젝트 메모를 바탕으로 한국어 README 초안을 써 주세요. 팀에 새로 온 개발자가 이 도구로 로컬 로그를 확인하려고 합니다. 설치부터 첫 실행까지 따라 할 수 있게 하고, 자주 쓰는 옵션과 사용 중 알아둘 점도 담아 주세요. 저장소에 바로 넣을 수 있는 Markdown이면 좋겠습니다.",
  "audience": {
    "primary": "팀에 합류해 로컬 로그를 확인하려는 백엔드 개발자",
    "prior_knowledge": "터미널과 Python 패키지 설치에는 익숙하지만 이 도구는 처음 사용한다.",
    "use_context": "저장소의 README를 보며 설치하고 로그에서 오류 항목을 찾는다."
  },
  "document_purpose": "도구의 역할, 설치, 첫 실행, 주요 옵션과 입력 오류 처리 방식을 빠르게 안내한다.",
  "source_facts": [
    {
      "id": "R1",
      "text": "프로젝트와 실행 명령 이름은 trace-slice다. 로컬 JSON Lines 로그 파일에서 지정한 최소 심각도 이상의 항목을 골라 내는 CLI다. 네트워크로 로그를 전송하지 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "R2",
      "text": "이번 README가 설명하는 배포 버전은 0.4.2다. 프로젝트의 Python 요구 버전은 3.10 이상으로 선언되어 있다. 실제로 설치와 기본 동작을 확인한 환경은 Ubuntu 22.04의 Python 3.11이다. 다른 운영체제에서의 검증 기록은 없다.",
      "certainty": "confirmed"
    },
    {
      "id": "R3",
      "text": "버전을 고정해 설치하는 명령은 python -m pip install trace-slice==0.4.2다. 설치 후 trace-slice --help로 도움말을 볼 수 있다.",
      "certainty": "confirmed"
    },
    {
      "id": "R4",
      "text": "사용 형식은 trace-slice INPUT [--level LEVEL] [--output PATH]다. INPUT은 로컬 JSON Lines 파일의 경로이며 필수 위치 인수다.",
      "certainty": "confirmed"
    },
    {
      "id": "R5",
      "text": "--level의 기본값은 info다. 허용되는 값은 debug, info, warn, error이며 이 순서로 심각도가 높아진다. 지정한 값과 그보다 높은 심각도의 항목이 출력된다.",
      "certainty": "confirmed"
    },
    {
      "id": "R6",
      "text": "--output을 생략하면 결과를 표준 출력으로 내보낸다. --output PATH를 지정하면 해당 파일에 결과를 쓰며, 파일이 이미 있으면 덮어쓴다.",
      "certainty": "confirmed"
    },
    {
      "id": "R7",
      "text": "예제 파일 경로는 ./logs/api.jsonl이다. trace-slice ./logs/api.jsonl --level error는 error 항목을 표준 출력으로 내보내는 유효한 명령이다.",
      "certainty": "confirmed"
    },
    {
      "id": "R8",
      "text": "각 정상 로그 행에는 level 필드가 있다. JSON 구문이 잘못된 행은 건너뛰고, 건너뛴 행 수를 표준 오류로 알린다. 그 이유만으로 실행이 실패하지는 않는다.",
      "certainty": "confirmed"
    },
    {
      "id": "R9",
      "text": "INPUT 파일을 읽을 수 없으면 오류를 표준 오류로 알리고 종료 코드 2로 끝난다.",
      "certainty": "confirmed"
    },
    {
      "id": "R10",
      "text": "0.4.2에는 실행 중 늘어나는 로그를 계속 따라가는 기능과 날짜 범위를 지정하는 옵션이 없다.",
      "certainty": "confirmed"
    }
  ],
  "source_draft": null
}
