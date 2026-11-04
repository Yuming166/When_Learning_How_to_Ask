"""Build the local review draft and check layout/citation markers, not science."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tectonic', default=shutil.which('tectonic'))
    args = parser.parse_args()
    if not args.tectonic:
        parser.error('provide an installed Tectonic compiler with --tectonic')
    artifact = HERE/'artifacts'
    artifact.mkdir(exist_ok=True)
    subprocess.run([sys.executable, '-B', str(HERE/'make_results.py')], cwd=HERE, check=True)
    command = [args.tectonic, '--keep-logs', '--keep-intermediates', 'main.tex']
    process = subprocess.run(command, cwd=HERE, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
    (artifact/'build-output.txt').write_text(process.stdout)
    if process.returncode:
        raise RuntimeError('compiler failed; inspect artifacts/build-output.txt')
    initial_rerun_warning = 'TeX rerun seems needed' in process.stdout
    followup = {'performed': False, 'initial_rerun_warning': initial_rerun_warning}
    if initial_rerun_warning:
        # Tectonic's bundled bibliography driver can request reruns despite a
        # stable .bbl. Finish the standard TeX pass, and verify stability rather
        # than suppressing the diagnostic or forcing a smaller rerun count.
        before = {ext: sha(HERE / ('main.' + ext)) for ext in ('aux', 'bbl')}
        follow_command = [args.tectonic, '--pass', 'tex', '--keep-logs',
                          '--keep-intermediates', 'main.tex']
        process = subprocess.run(follow_command, cwd=HERE, text=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (artifact/'tex-followup-output.txt').write_text(process.stdout)
        if process.returncode:
            raise RuntimeError('TeX follow-up failed')
        followup.update(performed=True, command=follow_command,
                        stable_aux=before['aux'] == sha(HERE/'main.aux'),
                        stable_bibliography=before['bbl'] == sha(HERE/'main.bbl'))
        if not followup['stable_aux'] or not followup['stable_bibliography']:
            raise RuntimeError('Follow-up changed labels or bibliography; inspect build')
    info = subprocess.check_output(['pdfinfo', str(HERE/'main.pdf')], text=True)
    pages = int(re.search(r'^Pages:\s+(\d+)', info, flags=re.M).group(1))
    text = subprocess.check_output(['pdftotext', '-layout', str(HERE/'main.pdf'), '-'], text=True)
    (artifact/'paper-text.txt').write_text(text)
    log = (HERE/'main.log').read_text(errors='replace')
    aux = (HERE/'main.aux').read_text()
    unresolved_aux = bool(re.search(r'\\newlabel\{[^}]+\}\{\{\?\?', aux))
    checks = {'pages_including_references':pages,
              'within_four_pages':pages <= 4,
              'missing_reference_or_citation_markers':bool(re.search(r'\?\?|\[\?\]', text)),
              'unresolved_aux_labels':unresolved_aux,
              'overfull_hboxes':len(re.findall(r'Overfull \\hbox', log)),
              'overfull_vboxes':len(re.findall(r'Overfull \\vbox', log)),
              'compiler_rerun_warning':'TeX rerun seems needed' in process.stdout,
              'placeholders_in_manuscript':bool(re.search(r'placeholder|TODO|TBD',text,re.I))}
    files = ['main.tex','references.bib','results.tex','make_results.py','RESULTS_SOURCE.json',
             'main.pdf','../../research/catalogue_paper_mainline_20261104/PROOF_COMPANION.md',
             '../../research/catalogue_paper_mainline_20261104/STRUCTURE_CHECKS.json',
             '../../experiments/decision_value_bridge_20261105/FREEZE.json',
             '../../experiments/decision_value_bridge_20261105/results/analysis.json',
             '../../research/decision_value_bridge_20261105/BRIDGE_PROPOSITIONS.md',
             '../../research/decision_value_bridge_20261105/EXACT_CERTIFICATES.json',
             '../../experiments/fashion_evidence_snapshot_20261105/results/RECOMPUTED.json']
    record = {'status':'ANONYMOUS_AUTHOR_REVIEW_DRAFT_NOT_SUBMITTED',
              'command':command,'compiler_exit':process.returncode,
              'compiler_version':subprocess.check_output([args.tectonic,'--version'],text=True).strip(),
              'acmart_version':'2022/02/19 v1.83 (local Tectonic bundle)',
              'current_submission_template_recompile_required':True,
              'bibliography_followup':followup,
              'font_size_or_page_geometry_overridden':False,
              'checks':checks,'source_and_artifact_sha256':{name:sha(HERE/name) for name in files},
              'citation_count':len(set(re.findall(r'\\bibcite\{([^}]+)',aux))),
              'bibliography_metadata_warnings':(HERE/'main.blg').read_text().count('Warning--'),
              'new_model_calls':0,'training_runs':0,
              'limits':['No formal proof-assistant certificate or external peer review',
                        'Finite-policy tests do not certify ideal allocation optimality',
                        'Seven numerical KL failures retained; one-step DV does not beat decision-IG',
                        'Historical Luna field-answer replay is not human or dialogue validity',
                        'Fashion outcome replay is released; full source dataset/profile regeneration is not bundled']}
    old = HERE/'BUILD_RECEIPT.json'
    if old.exists():
        prior = json.loads(old.read_text())
        if 'visual_review' in prior and prior.get('source_and_artifact_sha256',{}).get('main.pdf') == sha(HERE/'main.pdf'):
            record['visual_review'] = prior['visual_review']
    old.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(checks,indent=2))
    if not checks['within_four_pages'] or checks['missing_reference_or_citation_markers'] or unresolved_aux or checks['placeholders_in_manuscript']:
        raise SystemExit('manuscript structural check failed')


if __name__ == '__main__':
    main()
