#!/usr/bin/env python3
"""Build comparison Markdown from frozen, reviewed documents.

Usage: python scripts/build_docs.py [--run evaluations/runs/RUN] [--check]
The check mode verifies source integrity and byte-for-byte freshness of outputs.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os

DEFAULT_REPO = Path(__file__).resolve().parents[1]
DEFAULT_RUN = 'evaluations/runs/2026-11-05-v0.6.0'
CONDITIONS = ('baseline', 'previous', 'latest')
SNAPSHOT_FILES = {
    'LICENSE', 'SKILL.md', 'agents/openai.yaml',
    'references/before-after-guide.md', 'references/document-types.md',
    'references/reading-flow.md',
}
GROUPS = {
    'long-documents.md': ('긴 문서 교정 전후', ['event_architecture', 'storage_adr', 'incident_runbook'], 9),
    'reading-flow.md': ('읽기 흐름과 짧은 PR 교정 전후', ['long_onboarding_index_refresh', 'short_investigation_wait_log'], 6),
    'transfer-checks.md': ('설정배포 안내와 작업 보고 교정 전후', ['v04_new_a_config_rollout', 'v04_new_b_thumbnail_report'], 4),
}


def build_docs(repo=DEFAULT_REPO, check=False, run=DEFAULT_RUN):
    root = Path(repo).resolve()
    RUN_PATH = Path(run).as_posix().rstrip("/")
    sources = {}

    def read(relative):
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
            raise ValueError(f'Invalid repository source path: {relative!r}')
        absolute = (root / relative).resolve()
        if not absolute.is_relative_to(root):
            raise ValueError(f'Source is outside repository: {relative}')
        if relative not in sources:
            data = absolute.read_bytes()
            sources[relative] = (data, data.decode('utf-8'))
        return sources[relative]

    manifest_path = RUN_PATH + '/manifest.json'
    manifest = json.loads(read(manifest_path)[1])
    if manifest.get('run_id') != RUN_PATH.split('/')[-1]:
        raise ValueError('Run directory and manifest run_id differ.')
    VERSION = manifest['skill_version']
    previous_labels = {c.get('previous_label') for c in manifest.get('cases', [])}
    if len(previous_labels) != 1 or not next(iter(previous_labels), None):
        raise ValueError('All comparison cases must declare the same previous_label.')
    PREVIOUS = 'v' + manifest['previous_version'] if manifest.get('previous_version') else next(iter(previous_labels))
    date = manifest.get('date', manifest['run_id'][:10])
    report_path = manifest.get('report_path', 'docs/repairs-v' + VERSION + '.md')
    archive_path = 'docs/evaluation-' + PREVIOUS + '.md'
    snapshot_path = manifest['skill_snapshot_path']
    if set(manifest.get('skill_files', {})) != SNAPSHOT_FILES:
        raise ValueError('Expected the six named frozen skill files.')
    for relative, expected in manifest['skill_files'].items():
        data, _ = read(snapshot_path + '/' + relative)
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Frozen skill snapshot SHA-256 mismatch: {relative}')

    hashes = {}
    for name in ('frozen_files', 'artifact_hashes'):
        values = manifest.get(name, {})
        if not isinstance(values, dict):
            raise ValueError(f'{name} must be a path-to-SHA-256 object.')
        for relative, digest in values.items():
            if relative in hashes and hashes[relative] != digest:
                raise ValueError(f'Conflicting recorded SHA-256: {relative}')
            hashes[relative] = digest

    observation_path = RUN_PATH + '/observations.json'
    observations = json.loads(read(observation_path)[1]).get('cases')
    if not isinstance(observations, dict):
        raise ValueError('observations.json must contain a cases object.')
    cases = manifest.get('cases', []) + manifest.get('transfer_cases', [])
    if not cases or len({c.get('id') for c in cases}) != len(cases):
        raise ValueError('Cases must be nonempty and have unique IDs.')
    document_count = sum(sum(bool(c.get(k)) for k in CONDITIONS) for c in cases)
    baseline_count = sum(bool(c.get('baseline')) for c in cases)
    seen_files = set()
    for c in cases:
        for required in ('id', 'title', 'file', 'source', 'input', 'previous', 'latest', 'previous_label'):
            if not isinstance(c.get(required), str) or not c[required]:
                raise ValueError(f'{c.get("id")}: missing string field {required}.')
        if c['previous_label'] != PREVIOUS:
            raise ValueError(f'{c["id"]}: expected previous_label={PREVIOUS}.')
        if Path(c['file']).name != c['file'] or not c['file'].endswith('.md') or c['file'] in seen_files:
            raise ValueError(f'Invalid or duplicate example filename: {c["file"]}')
        seen_files.add(c['file'])
        if not c['latest'].startswith(RUN_PATH + '/outputs/revised/'):
            raise ValueError(f'{c["id"]}: latest must be a final outputs/revised document.')
        if c['latest'] not in hashes:
            raise ValueError(f'Final document has no recorded SHA-256: {c["latest"]}')
        for relative in [c['source'], c['input'], *[c[k] for k in CONDITIONS if c.get(k)]]:
            data, _ = read(relative)
            if relative in hashes and hashlib.sha256(data).hexdigest() != hashes[relative]:
                raise ValueError(f'Recorded source SHA-256 mismatch: {relative}')
        if c.get('review_report'):
            read(c['review_report'])
        obs = observations.get(c['id'])
        if not isinstance(obs, dict) or not isinstance(obs.get('summary'), str) or not obs['summary'].strip():
            raise ValueError(f'Missing observations summary: {c["id"]}')
        for key in ('strengths', 'limitations', 'excerpts'):
            if not isinstance(obs.get(key), list):
                raise ValueError(f'{c["id"]}: observations.{key} must be an array.')
        if 'factual_findings' not in obs:
            raise ValueError(f'{c["id"]}: missing factual_findings.')
        for i, excerpt in enumerate(obs['excerpts']):
            for condition in ('previous', 'latest'):
                quote = excerpt.get(condition)
                if not isinstance(quote, str) or not quote or quote not in read(c[condition])[1]:
                    raise ValueError(f'Excerpt is not an exact substring: {c["id"]}/{condition}/{i}')

    if set(observations) != {c['id'] for c in cases}:
        raise ValueError('Observation case IDs must match the manifest cases exactly.')

    def link(target, page):
        return Path(os.path.relpath(root / target, (root / page).parent)).as_posix()

    def count(c, condition):
        return len(read(c[condition])[1])

    def label(condition):
        return {'baseline': '스킬 미적용 참고 원문', 'previous': '이전 ' + PREVIOUS, 'latest': '현재 v' + VERSION}[condition]

    def structured(value):
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return '\n'.join('- ' + structured(item).replace('\n', '\n  ') for item in value)
        if isinstance(value, dict):
            return '\n'.join(f'- **{key}:** {structured(item)}' for key, item in value.items())
        return str(value)

    def metadata(page):
        return (f'갱신일: {date} · 적용한 스킬: **v{VERSION}** · '
                f'[고정한 스킬 파일]({link(snapshot_path, page)})\n\n')

    def methods(page):
        return ('## 작성과 확인 방법\n\n'
                f'{PREVIOUS} 문서와 같은 원자료를 대조해 필요한 부분을 고쳤습니다. v{VERSION} 지침으로 교정한 문서와 수정할 필요가 없어 보존한 문서를 사례별로 구분합니다. '
                '현재 본문은 검토와 수정을 거친 최종본입니다. 이전 원문과 수정 이력은 별도로 보존했고, 완성 예제는 최종본의 바이트를 그대로 복사했습니다.\n\n'
                f'이는 조건을 가린 단회 생성 비교가 아닙니다. 미적용 문서가 있는 {baseline_count}개 사례에서는 과거 원문을 참고용으로 함께 싣습니다. '
                '검토 결과는 사실·조건의 보존과 문서 구성에 관한 판단이며, 실제 독자의 이해도·기억·읽는 시간·피로를 측정한 결과는 아닙니다. '
                '사례는 공개용 가상 자료입니다. 문자 수는 공백·개행·Markdown 문법을 포함하며, 길이 자체를 품질 점수로 사용하지 않습니다.\n\n'
                f'- [교정 절차와 수정 이력]({link(RUN_PATH + "/protocol.md", page)})\n'
                f'- [원문·버전·SHA-256 기록]({link(manifest_path, page)})\n'
                f'- [사례별 수정 관찰]({link(observation_path, page)})\n'
                f'- [수정 결과 보고서]({link(report_path, page)})\n'
                f'- [{PREVIOUS} 당시 평가 보존본]({link(archive_path, page)})\n')

    def size_table(selected, page):
        have_baseline = any(c.get('baseline') for c in selected)
        columns = (['baseline'] if have_baseline else []) + ['previous', 'latest']
        lines = ['| 사례 | ' + ' | '.join(label(k) for k in columns) + ' |',
                 '| --- | ' + ' | '.join('---:' for _ in columns) + ' |']
        for c in selected:
            values = [f'[{count(c, k):,}자]({link(c[k], page)})' if c.get(k) else '해당 없음' for k in columns]
            lines.append('| ' + ' | '.join([f'[{c["title"]}](#{c["id"]})'] + values) + ' |')
        return '\n'.join(lines) + '\n\n'

    def findings(c, page):
        obs = observations[c['id']]
        result = obs['summary'] + '\n\n'
        if obs['strengths']:
            result += '**수정하고 확인한 내용**\n\n' + structured(obs['strengths']) + '\n\n'
        if obs['limitations']:
            result += '**추가 확인 범위**\n\n' + structured(obs['limitations']) + '\n\n'
        if obs['factual_findings']:
            result += '**사실·조건 대조**\n\n' + structured(obs['factual_findings']) + '\n\n'
        review = c.get('review_report', report_path)
        result += (f'[교정 완료본 바로 읽기]({link("docs/examples/" + c["file"], page)}) · '
                   f'[보존 검토 기록]({link(review, page)}) · [공통 입력]({link(c["input"], page)})\n\n')
        for excerpt in obs['excerpts']:
            result += '### ' + excerpt.get('label', '실제 수정 문장') + '\n\n'
            for condition in ('previous', 'latest'):
                result += '**' + label(condition) + '**\n\n'
                result += '\n'.join('> ' + line if line else '>' for line in excerpt[condition].splitlines()) + '\n\n'
            if excerpt.get('note'):
                result += structured(excerpt['note']) + '\n\n'
        return result

    def full_documents(c):
        result = '### 전체 본문\n\n'
        for condition in CONDITIONS:
            if not c.get(condition):
                continue
            relative = c[condition]
            data, raw = read(relative)
            digest = hashlib.sha256(data).hexdigest()
            # Raw bytes stay between source markers, including whether a final LF exists.
            result += f'<details>\n<summary>{label(condition)} · {len(raw):,}자</summary>\n\n'
            result += f'<!-- BEGIN SOURCE {relative} SHA256 {digest} -->\n' + raw + '<!-- END SOURCE -->\n\n</details>\n\n'
        return result

    outputs = {}
    page = 'docs/evaluation.md'
    text = f'# v{VERSION} 문서 개선 결과\n\n' + metadata(page)
    text += (f'기존 문서 {len(cases)}개를 대조해 필요한 부분을 교정했습니다. 각 문서에서 무엇을 고쳤는지, 사실과 조건을 어떻게 보존했는지를 아래에서 확인할 수 있습니다.\n\n'
             f'[현재 문서 {len(cases)}개 바로 읽기](examples/README.md) · [수정 결과 보고서]({link(report_path,page)}) · '
             '[교정 전후를 나란히 보기](comparisons/index.html)\n\n'
             '## 사례별 수정 결과\n\n'
             '| 문서 | 교정 전 | 교정 완료 | 수정 결과 |\n| --- | ---: | ---: | --- |\n')
    for c in cases:
        summary = observations[c['id']]['summary'].replace('|', '\\|').replace('\n', ' ')
        text += (f'| [{c["title"]}](examples/{c["file"]}) | [{count(c,"previous"):,}자]({link(c["previous"],page)}) '
                 f'| [{count(c,"latest"):,}자]({link(c["latest"],page)}) | {summary} |\n')
    text += ('\n## 전문 비교\n\n'
             '- [아키텍처·ADR·장애 대응 절차: 전문 9개](comparisons/long-documents.md)\n'
             '- [온보딩·짧은 관측 PR: 전문 6개](comparisons/reading-flow.md)\n'
             '- [설정배포 안내·썸네일 작업 보고: 전문 4개](comparisons/transfer-checks.md)\n\n'
             f'HTML에는 {len(cases)}개 사례의 본문 {document_count}개와 입력 {len(cases)}개를 포함했습니다. 이전 {PREVIOUS} 문서와 현재 v{VERSION} 문서를 기본으로 비교하고, '
             f'미적용 원문이 있는 {baseline_count}개 사례에서는 그 원문도 선택할 수 있습니다.\n\n')
    if manifest.get('new_topic_examples'):
        text += ('## 새 주제의 최초 작성본 비교\n\n'
                 '로그 보관 정책과 구성 값 우선순위를 이전 출력 없이 각각 작성했습니다. '
                 '[두 버전의 본문·필수 의미 판정·읽기 관찰](comparisons/new-topics.md)을 별도로 공개합니다.\n\n')
    text += methods(page)
    outputs[page] = text.encode('utf-8')

    for filename, (title, ids, expected) in GROUPS.items():
        page = 'docs/comparisons/' + filename
        selected = [next(c for c in cases if c['id'] == cid) for cid in ids]
        actual = sum(sum(bool(c.get(k)) for k in CONDITIONS) for c in selected)
        if actual != expected:
            raise ValueError(f'{filename}: expected {expected} source documents; found {actual}.')
        text = '# ' + title + f': {PREVIOUS} → v{VERSION}\n\n' + metadata(page)
        text += (f'문서 {len(selected)}개의 수정 내용과 전문 {actual}개를 담았습니다. '
                 f'[현재 문서 목록](../examples/README.md) · [전체 수정 결과]({link(report_path,page)}) · [나란히 보기](index.html)\n\n'
                 '## 한눈에 보는 문서\n\n')
        text += size_table(selected, page)
        for c in selected:
            text += f'<a id="{c["id"]}"></a>\n\n## {c["title"]}\n\n' + findings(c, page) + full_documents(c)
        text += methods(page)
        outputs[page] = text.encode('utf-8')

    new_topic_embeds = 0
    if manifest.get('new_topics_path'):
        page = 'docs/comparisons/new-topics.md'
        study_path = manifest['new_topics_path']
        study_data, study_raw = read(study_path)
        if hashlib.sha256(study_data).hexdigest() != hashes.get(study_path):
            raise ValueError('New-topic comparison record SHA-256 mismatch.')
        study = json.loads(study_raw)
        review_data, review_raw = read(study['review_path'])
        contract_data, contract_raw = read(study['contract_path'])
        for relative, data in [(study['review_path'], review_data), (study['contract_path'], contract_data)]:
            if hashlib.sha256(data).hexdigest() != hashes.get(relative):
                raise ValueError('New-topic review/contract SHA-256 mismatch: ' + relative)
        review_lookup = {(d['case_id'], d['label']): d for d in json.loads(review_raw)['documents']}
        contract_lookup = {c['case_id']: c for c in json.loads(contract_raw)['cases']}
        text = '# 새 주제의 최초 작성본 비교\n\n' + metadata(page)
        text += (study['method'] + '\n\n'
                 f'[현재 문서만 읽기](../examples/README.md#새-주제로-작성한-문서) · '
                 f'[버전을 가린 검토]({link(study["review_path"],page)}) · '
                 f'[판정·본문 대응 기록]({link(study_path,page)})\n\n')
        for entry in study['cases']:
            for relative in (entry['source'], entry['input']):
                data, _ = read(relative)
                if hashlib.sha256(data).hexdigest() != hashes.get(relative):
                    raise ValueError('New-topic source/input SHA-256 mismatch: ' + relative)
            text += '## ' + entry['title'] + '\n\n'
            text += structured(entry['findings']) + '\n\n'
            for excerpt in entry.get('excerpts', []):
                condition = excerpt['condition']
                if condition not in ('previous', 'current'):
                    raise ValueError('Unknown new-topic excerpt condition.')
                if not excerpt['quote'] or excerpt['quote'] not in read(entry['documents'][condition])[1]:
                    raise ValueError('New-topic excerpt is not an exact substring.')
                version = PREVIOUS if condition == 'previous' else 'v' + VERSION
                text += '**' + version + ' 최초 작성본에서 확인한 부분**\n\n'
                text += '\n'.join('> ' + line if line else '>' for line in excerpt['quote'].splitlines()) + '\n\n'
                text += excerpt['note'] + '\n\n'
            text += '| 최초 작성에 적용한 스킬 | 문자 수 | 필수 의미 보존 | 독자 질문에 충분한 답 |\n| --- | ---: | ---: | ---: |\n'
            for condition, version in [('previous', PREVIOUS), ('current', 'v' + VERSION)]:
                relative = entry['documents'][condition]
                data, raw = read(relative)
                if hashlib.sha256(data).hexdigest() != hashes.get(relative):
                    raise ValueError('New-topic document SHA-256 mismatch: ' + relative)
                result = entry['review_summary'][condition]
                case_contract = contract_lookup[entry['id']]
                record = review_lookup[(entry['id'], entry['review_labels'][condition])]
                required_ids = {r['id'] for r in case_contract['requirements'] if r['required']}
                computed = {
                    'preserved': sum(r['requirement_id'] in required_ids and r['status'] == 'preserved' for r in record['requirements']),
                    'required': len(required_ids),
                    'sufficient': sum(q['answer_status'] == 'sufficient' and not q['local_condition_gap'] for q in record['questions']),
                    'questions': len(case_contract['questions']),
                }
                if result != computed:
                    raise ValueError('New-topic summary differs from recorded review: ' + entry['id'] + '/' + condition)
                text += (f'| {version} | {len(raw):,} | {result["preserved"]}/{result["required"]} '
                         f'| {result["sufficient"]}/{result["questions"]} |\n')
            text += ('\n단어 존재율이나 자연스러움 점수가 아니라 원자료와 문맥을 대조한 판정 개수입니다. '
                     '글자 수에는 공백·개행·Markdown 문법이 포함됩니다.\n\n')
            if entry.get('publication_note'):
                text += entry['publication_note'] + '\n\n'
            text += (f'[원자료]({link(entry["source"],page)}) · [공통 요청]({link(entry["input"],page)}) · '
                     f'[현재 완성 문서]({link(entry["example"],page)})\n\n')
            for condition, version in [('previous', PREVIOUS), ('current', 'v' + VERSION)]:
                relative = entry['documents'][condition]
                data, raw = read(relative)
                digest = hashlib.sha256(data).hexdigest()
                text += f'<details>\n<summary>{version} 최초 작성본 전체 · {len(raw):,}자</summary>\n\n'
                text += f'<!-- BEGIN SOURCE {relative} SHA256 {digest} -->\n' + raw + '<!-- END SOURCE -->\n\n</details>\n\n'
                new_topic_embeds += 1
        text += ('## 확인 범위\n\n' + study['scope'] + '\n\n'
                 f'[자료·계약 고정 기록]({link(RUN_PATH+"/source-freeze.json",page)}) · '
                 f'[전체 실행 절차]({link(RUN_PATH+"/protocol.md",page)})\n')
        outputs[page] = text.encode('utf-8')

    index = ('# 교정 완료 문서 예제\n\n'
             f'공개용 가상 자료로 만든 현재 문서 {len(cases)}개입니다. v{VERSION}에서 필요한 부분을 교정하고, 내용이 충분한 문서는 보존했습니다. 문서 제목을 누르면 비교 설명 없이 본문부터 읽을 수 있습니다.\n\n'
             f'[수정 결과 보고서]({link(report_path,"docs/examples/README.md")}) · [교정 전후 비교](../comparisons/index.html) · [작성과 확인 방법](../evaluation.md)\n\n'
             '| 문서 | 최종본 문자 수 | 원자료 |\n| --- | ---: | --- |\n')
    for c in cases:
        target = 'docs/examples/' + c['file']
        outputs[target] = read(c['latest'])[0]
        index += f'| [{c["title"]}]({c["file"]}) | {count(c,"latest"):,}자 | [입력]({link(c["input"],"docs/examples/README.md")}) |\n'
    extra_examples = manifest.get('new_topic_examples', [])
    if extra_examples:
        index += ('\n## 새 주제로 작성한 문서\n\n'
                  '기존 출력 없이 원자료와 스킬로 새로 작성한 뒤 검토·교정한 두 주제의 현재 문서입니다. '
                  '[v0.5.0·v0.6.0의 최초 작성본 비교](../comparisons/new-topics.md)에서 작성 조건과 검토 결과도 볼 수 있습니다.\n\n'
                  '| 문서 | 문자 수 | 원자료 |\n| --- | ---: | --- |\n')
        for entry in extra_examples:
            filename = entry['file']
            if Path(filename).name != filename or not filename.endswith('.md') or filename in seen_files:
                raise ValueError('Invalid or duplicate new-topic example filename.')
            seen_files.add(filename)
            data, raw = read(entry['latest'])
            if hashlib.sha256(data).hexdigest() != hashes.get(entry['latest']):
                raise ValueError('New-topic example SHA-256 mismatch: ' + entry['latest'])
            outputs['docs/examples/' + filename] = data
            index += (f'| [{entry["title"]}]({filename}) | {len(raw):,}자 | '
                      f'[입력]({link(entry["input"],"docs/examples/README.md")}) |\n')

    index += ('\n이 디렉터리의 본문은 실행 기록에 지정한 검토 완료본과 바이트 단위로 같습니다. '
              '수정 과정과 이전 원문은 [실행 기록](../../' + RUN_PATH + ')에서 확인할 수 있습니다.\n')
    outputs['docs/examples/README.md'] = index.encode('utf-8')

    if check:
        stale = [relative for relative, data in outputs.items()
                 if not (root / relative).is_file() or (root / relative).read_bytes() != data]
        if stale:
            raise ValueError('Generated documents are stale; run build_docs.py: ' + ', '.join(stale))
    else:
        for relative, data in outputs.items():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    return {
        'checked_only': check, 'cases': len(cases), 'source_documents': document_count,
        'markdown_embeds': sum(g[2] for g in GROUPS.values()) + new_topic_embeds, 'examples': len(cases) + len(extra_examples), 'written_files': list(outputs),
        'input_source_files': len(sources),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=DEFAULT_REPO)
    parser.add_argument('--run', default=DEFAULT_RUN)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(build_docs(args.repo, args.check, args.run), ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, StopIteration) as error:
        parser.exit(1, 'Build stopped before publication: ' + str(error) + '\n')
