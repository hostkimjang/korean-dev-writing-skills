# 배포본 출처와 유지관리 범위

이 디렉터리는 `korean-dev-writing-skills` 저장소에서 유지하는 개발 문서 보강판입니다. 아래 원본의 이름·저작권과 기존 규칙 ID를 보존하며, 개발 전용 `DEV-` 규칙·사전·예제·확인 목록과 경어체 설명을 추가했습니다. 원본 프로젝트가 이 변경을 검토하거나 배포했다는 뜻은 아닙니다.

| 구분 | 고정 원본 | 이 배포본의 사용 범위 |
| --- | --- | --- |
| 자체 실행이 가능한 기본 구현 | [nathankim0/humanize-korean](https://github.com/nathankim0/humanize-korean/tree/b51aa5985be0a94a645788f1395b29a118bc9c33), `b51aa5985be0a94a645788f1395b29a118bc9c33` | 원래 스킬 구조·일반 교정 규칙과 세 Python 스크립트를 사용합니다. 스크립트 원문과 기존 규칙 ID를 보존합니다. |
| 상세 분류와 참조 문서 구성 | [epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai/tree/501bc125052fd24be3d02e3196af57353985fa7f), `501bc125052fd24be3d02e3196af57353985fa7f` | `SKILL.md`, `quick-rules.md`, `rewriting-playbook.md`, `ai-tell-taxonomy.md`를 읽고 문맥별 예외·규칙 연결·확인 목록 구성을 참고했습니다. 요청된 파일명에 맞춰 개발 문서용 내용을 작성했습니다. |

기본 구현의 라이선스는 [LICENSE](LICENSE)에 그대로 포함합니다. 아래에는 기본 구현이 제공한 서드파티 고지를 원문 그대로 남기고, 추가로 참고한 버전과 이 저장소 변경분의 MIT 고지를 이어서 제공합니다. 원본의 외부 에이전트 실행 절차나 빠른 규칙 생성기를 이 배포본의 사용 요건으로 가져오지 않았습니다.

## 기본 구현에서 보존한 고지

# Third-party notices

This skill combines and adapts ideas, taxonomies, workflows, and examples from the following MIT-licensed projects.

## im-not-ai

- Source: https://github.com/epoko77-ai/im-not-ai
- Revision reviewed: `3120cb81e3b9910ba393cd8289864c583f0ac50a`

MIT License

Copyright (c) 2026 epoko77-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## im-ai-copyeditor

- Source: https://github.com/Turtle-Hwan/im-ai-copyeditor
- Revision reviewed: `84d5a2af1335815a160bbc0dc2d4b4aea85c43c0`
- Adapted components: granular proofreading, sentence, AI-style, honorific and register rules; sentence worksheet segmentation and guarded reassembly workflow; interactive collaborative editing workflow

MIT License

Copyright (c) 2026 Turtle-Hwan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## yoonmoon

- Source: https://github.com/amondnet/yoonmoon
- Revision reviewed: `6091a8d5681b02f39ef7fa67b95d56dec9b0692e`

MIT License

Copyright (c) 2026 Minsu Lee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 추가로 참고한 im-not-ai 버전

- Source: https://github.com/epoko77-ai/im-not-ai
- Revision reviewed: `501bc125052fd24be3d02e3196af57353985fa7f`
- Adapted components: development-document rule routing, quick-rule reference layout, contextual rewriting safeguards, taxonomy/checklist synchronization

MIT License

Copyright (c) 2026 epoko77-ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 이 저장소 변경분의 라이선스

MIT License

Copyright (c) 2026 hostkimjang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
