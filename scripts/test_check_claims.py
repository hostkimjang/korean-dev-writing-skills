"""Integrity regressions with temporary fixtures, not a model evaluation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
TEMP = TemporaryDirectory(prefix='korean-writing-claims-')
WORK = Path(TEMP.name)
SCRIPT = ROOT / 'scripts/check_claims.py'
CONTRACT = json.loads((ROOT / 'evaluations/contracts/preservation-v1.json').read_text())
CASES = {c['case_id']: c for c in CONTRACT['cases']}
results = []

def write(name, data):
    path = WORK / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return str(path)

def run(name, args, expected, contains=None):
    proc = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=WORK,
                          text=True, capture_output=True)
    output = proc.stdout + proc.stderr
    assert proc.returncode == expected, (name, proc.returncode, output)
    if contains:
        assert contains in output, (name, output)
    results.append({'test': name, 'exit_code': proc.returncode, 'result': 'pass'})

def indexed(case_id, label, path):
    return {'case_id': case_id, 'label': label, 'path': path,
            'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}

short = indexed('short_investigation_wait_log', 'fixture-short',
                'evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/08_short_log_pr.md')
edited = indexed('paragraph_edit', 'fixture-edit',
                 'evaluations/runs/2026-11-03-v0.3.0-refresh/outputs/latest/06_paragraph_edit.md')
short_index = write('short-index.json', {'documents': [short]})
both_index = write('both-index.json', {'documents': [short, edited]})
signal_path = WORK / 'short-signals.json'
run('frozen contract with default repository-relative path', [], 0)
run('real short PR signals', ['--output-index', short_index, '--write-signals', signal_path], 0)
signal_doc = json.loads(signal_path.read_text())['documents'][0]
assert signal_doc['characters'] == len((ROOT / short['path']).read_text()) == 397
name_signal = next(s for s in signal_doc['literal_signals'] if s['requirement_id'] == 'S01.target')
assert name_signal['present'] is False
assert all(key not in signal_doc for key in ['status', 'score', 'hard_fail'])
assert all(key not in signal_doc['literal_signals'][0] for key in ['status', 'score', 'hard_fail'])
results.append({'test': 'service absence is a signal, not an automatic semantic verdict', 'result': 'pass'})

text = (ROOT / short['path']).read_text()
paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
rows = []
for item in CASES[short['case_id']]['requirements']:
    if not item['required']:
        continue
    identifier = item['id']
    evidence = paragraphs[0] if identifier.startswith(('S01.', 'S02.', 'S06.')) else paragraphs[2] if identifier.startswith('S07.') else paragraphs[1]
    status = 'preserved'
    reason = '기존 리뷰와 원문을 대조하는 검사기 회귀용 기록이다. 인용에 해당 의미가 있다.'
    if identifier == 'S01.target':
        status, evidence, reason = 'missing', None, '출력에 대상 서비스명이 없다.'
    if identifier == 'S03.purpose':
        status, reason = 'partial', '관측 보강 목적은 있으나 다음 관측에서 항목 존속·소멸 시점을 비교한다는 구체적 목적은 없다.'
    if identifier == 'S06.reason':
        status, reason = 'partial', '실제 영향 미확정은 있으나 로그 이름·순서의 한계를 이유로 연결하지 않는다.'
    rows.append({'requirement_id': identifier, 'status': status,
                 'evidence': [evidence] if evidence else [], 'reason': reason})
qrows = []
for q in CASES[short['case_id']]['questions']:
    partial = q['id'] in {'SQ1', 'NAV1'}
    qrows.append({'question_id': q['id'], 'answer_status': 'partial' if partial else 'sufficient',
                  'entry_location': '첫 문단' if q['id'] in {'SQ1', 'SQ2'} else '변경 또는 검증 문단',
                  'additional_locations': [], 'local_condition_gap': '서비스명·구체 목적 또는 관측 한계의 이유가 빠져 있다.' if partial else '',
                  'answer_evidence': [paragraphs[0] if q['id'] in {'SQ1', 'SQ2'} else paragraphs[1] if q['id'] in {'SQ3', 'NAV1'} else paragraphs[2]],
                  'reason': '실제 원문의 대응 위치를 사용한 구조 검사 회귀용 기록이다.'})
review = {'case_id': short['case_id'], 'label': short['label'], 'requirements': rows,
          'questions': qrows, 'hard_fail': {'value': False, 'reason': '원인·해결·미실시 검증을 성공으로 확정하지 않는다.', 'evidence': []}}
short_review = write('short-review.json', {'documents': [review]})
run('valid partial/missing review passes structural checks', ['--output-index', short_index, '--reviews', short_review], 0)

# The second fixture is for cross-file coverage only, not a new substantive review.
body = (ROOT / edited['path']).read_text()
edit_review = {'case_id': edited['case_id'], 'label': edited['label'],
              'requirements': [{'requirement_id': item['id'], 'status': 'preserved', 'evidence': [body],
                                'reason': '문단 교정 원문의 해당 조건을 대조하기 위한 구조 검사 fixture다.'}
                               for item in CASES[edited['case_id']]['requirements'] if item['required']],
              'questions': [{'question_id': q['id'], 'answer_status': 'sufficient', 'entry_location': '본문',
                             'additional_locations': [], 'local_condition_gap': '', 'answer_evidence': [body],
                             'reason': '문단 본문의 원문 인용을 확인하는 fixture다.'}
                            for q in CASES[edited['case_id']]['questions']],
              'hard_fail': {'value': False, 'reason': 'fixture: 조건·버전의 원자료 대조', 'evidence': []}}
edit_review_path = write('edit-review.json', {'documents': [edit_review]})
run('two disjoint review files cover the complete index', ['--output-index', both_index, '--reviews', short_review, edit_review_path], 0)
run('missing review document across files', ['--output-index', both_index, '--reviews', short_review], 1, 'documents missing')
run('duplicate review document across files', ['--output-index', short_index, '--reviews', short_review, short_review], 1, 'duplicate review document')

mutant = copy.deepcopy(review)
mutant['requirements'].pop()
run('missing mandatory requirement', ['--output-index', short_index, '--reviews', write('missing-row.json', {'documents': [mutant]})], 1, 'missing required review rows')
mutant = copy.deepcopy(review)
mutant['questions'].pop()
run('missing question', ['--output-index', short_index, '--reviews', write('missing-question.json', {'documents': [mutant]})], 1, 'missing question review rows')
mutant = copy.deepcopy(review)
mutant['requirements'].append(copy.deepcopy(mutant['requirements'][1]))
run('duplicate requirement row', ['--output-index', short_index, '--reviews', write('duplicate-row.json', {'documents': [mutant]})], 1, 'duplicate requirement review')
mutant = copy.deepcopy(review)
mutant['requirements'][1]['evidence'] = ['검증이 모두 통과했습니다.']
run('invented or paraphrased quotation', ['--output-index', short_index, '--reviews', write('bad-quote.json', {'documents': [mutant]})], 1, 'not an exact contiguous substring')
mutant = copy.deepcopy(review)
mutant['hard_fail']['value'] = True
run('hard fail needs quoted evidence', ['--output-index', short_index, '--reviews', write('hard-fail-no-quote.json', {'documents': [mutant]})], 1, 'evidence must be a nonempty list')
mutant = copy.deepcopy(review)
mutant['requirements'][1]['status'] = 'omitted'
run('omitted is not a semantic status', ['--output-index', short_index, '--reviews', write('bad-status.json', {'documents': [mutant]})], 1, 'status must be one of')

mutant_index = copy.deepcopy(short)
mutant_index['sha256'] = '0' * 64
run('output SHA mismatch', ['--output-index', write('wrong-output-hash.json', {'documents': [mutant_index]})], 1, 'SHA-256 mismatch')
mutant_contract = copy.deepcopy(CONTRACT)
mutant_contract['cases'][0]['source_sha256'] = '0' * 64
run('source SHA mismatch', ['--contract', write('wrong-source-hash.json', mutant_contract)], 1, 'SHA-256 mismatch')
mutant_contract = copy.deepcopy(CONTRACT)
optional = next(r for r in mutant_contract['cases'][0]['requirements'] if r['id'] == 'RC8')
optional['required'] = True
run('optional legacy claim cannot be promoted', ['--contract', write('promoted-optional.json', mutant_contract)], 1, 'optional legacy claim cannot become required')
mutant_contract = copy.deepcopy(CONTRACT)
for item in mutant_contract['cases'][0]['requirements']:
    item['legacy_refs'] = [x for x in item['legacy_refs'] if x != 'verifiable_claims:RC2']
run('original required claim cannot lose coverage', ['--contract', write('lost-legacy.json', mutant_contract)], 1, 'original required obligations are not covered')
mutant_contract = copy.deepcopy(CONTRACT)
mutant_contract['cases'][0]['requirements'][0]['source_refs'] = ['R999']
run('dangling source reference', ['--contract', write('dangling-source.json', mutant_contract)], 1, 'unknown source_refs')
mutant_index = copy.deepcopy(short)
mutant_index['path'] = '../outside.md'
run('embedded paths cannot leave repository', ['--output-index', write('outside-path.json', {'documents': [mutant_index]})], 1, 'file path leaves the repository')
run('signals cannot overwrite read artifacts', ['--output-index', short_index, '--write-signals', short_index], 1, 'signals must not overwrite')

spec = importlib.util.spec_from_file_location('claim_checker_fixture', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assert module.literal_present('1', 'number', '범위는 1000이다.') is False
assert module.literal_present('1', 'number', '1부터 1000까지다.') is True
assert module.literal_present('--output', 'identifier', '--output-format') is False
assert module.literal_present('info', 'identifier', 'info이며') is True
assert module.literal_present('worker/pending_slots.py', 'path', '`worker/pending_slots.py`에') is True
assert module.literal_present('worker/pending_slots.py', 'path', 'worker/pending_slots.py.old') is False
results.append({'test': 'identifier, path, and numeric boundaries', 'result': 'pass'})
summary = {'tests_passed': len(results), 'tests': results,
           'scope': 'Regression fixtures only; not a published semantic review or new model evaluation.'}
(WORK / 'results.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False, indent=2))

TEMP.cleanup()
