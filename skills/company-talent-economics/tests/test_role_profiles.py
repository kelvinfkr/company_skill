"""Evidence, date precision, comparison and report integration checks."""
import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
from role_profiles import compile_profiles, experience_phase, validate_bundle, validate_section


class RoleProfilesTest(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads((SKILL / 'examples/role_profiles/profiles.json').read_text())
        self.candidate = json.loads((SKILL / 'examples/role_profiles/candidate.json').read_text())

    def section(self, candidate=None):
        return compile_profiles(self.bundle, candidate)['role_profiles']

    def test_current_cases_rank_by_content_date(self):
        result = self.section()
        self.assertEqual([p['id'] for p in result['current_cases']], ['P1', 'P3', 'P2'])
        self.assertEqual(result['sample_count'], 3)
        self.assertEqual({p['id'] for p in result['other_cases']}, {'P4', 'P5'})

    def test_access_date_does_not_refresh_old_content(self):
        before = self.section()['current_cases']
        self.bundle['sources'][1]['accessed_date'] = '2023-01-01'
        after = self.section()['current_cases']
        self.assertEqual([p['ranking'] for p in before], [p['ranking'] for p in after])

    def test_verified_content_update_changes_order(self):
        self.bundle['sources'][1]['updated_date'] = '2026-10-12'
        result = self.section()['current_cases']
        self.assertEqual(result[1]['id'], 'P2')
        self.assertEqual(result[1]['ranking']['as_of'], '2026-10-12')

    def test_mirrors_do_not_raise_weight(self):
        with_mirror = self.section()['current_cases'][-1]['ranking']['score']
        self.bundle['profiles'][1]['role']['evidence_ids'].remove('S2-copy')
        self.assertEqual(self.section()['current_cases'][-1]['ranking']['score'], with_mirror)

    def test_newer_repost_does_not_refresh_original_statement(self):
        before = self.section()['current_cases'][-1]['ranking']
        mirror = next(s for s in self.bundle['sources'] if s['id'] == 'S2-copy')
        mirror.update(source_type='company_page', updated_date='2026-10-12')
        self.assertEqual(self.section()['current_cases'][-1]['ranking'], before)

    def test_original_source_must_be_present(self):
        self.bundle['sources'][0]['origin_id'] = 'missing'
        self.assertTrue(validate_bundle(self.bundle))

    def test_historical_education_is_not_decayed(self):
        before = self.section()['comparison'][0]['pre_entry_examples']
        self.bundle['profiles'][0]['experiences'][0].update(start_date='2009', end_date='2013')
        self.assertEqual(self.section()['comparison'][0]['pre_entry_examples'], before)

    def test_post_entry_work_does_not_become_entry_requirement(self):
        leadership = self.section()['comparison'][2]
        self.assertEqual(leadership['case_count'], 0)
        self.assertEqual(leadership['requirements'], [])
        self.assertEqual(self.section()['current_cases'][0]['experiences'][2]['phase'], 'post_entry')

    def test_partial_dates_remain_uncertain(self):
        self.assertEqual(experience_phase({'start_date': '2024', 'end_date': '2024'}, '2024-06'), 'unknown')
        self.assertEqual(experience_phase({'end_date': '2023'}, '2024'), 'pre_entry')
        self.assertEqual(experience_phase({'start_date': '2025'}, '2024'), 'post_entry')
        self.assertEqual(experience_phase({'end_date': '2023'}, None), 'unknown')

    def test_missing_cv_evidence_is_not_an_ability_verdict(self):
        result = self.section(self.candidate)['comparison']
        self.assertEqual(result[0]['candidate_status'], 'not_documented')
        self.assertEqual(result[1]['candidate_status'], 'documented')
        self.assertEqual(result[1]['candidate_examples'][0]['resume_reference'],
                         'Fictional CV, Projects, item 1')
        self.assertEqual(self.section()['comparison'][0]['candidate_status'], 'not_supplied')

    def test_role_mismatch_is_rejected(self):
        self.bundle['profiles'][0]['role']['company'] = 'Another Company'
        self.assertTrue(validate_bundle(self.bundle))
        self.bundle['profiles'][0]['role']['match'] = 'excluded'
        self.assertFalse(validate_bundle(self.bundle))
        self.assertNotIn('P1', [p['id'] for p in self.section()['current_cases']])

    def test_geography_mismatch_is_rejected(self):
        self.bundle['profiles'][0]['role']['geography'] = 'Japan'
        self.assertTrue(validate_bundle(self.bundle))

    def test_unknown_evidence_is_rejected(self):
        self.bundle['profiles'][0]['experiences'][0]['evidence_ids'] = ['missing']
        self.assertTrue(validate_bundle(self.bundle))

    def test_invalid_and_future_dates_are_rejected(self):
        for value in ['2026-02-30', '2027-01-01']:
            with self.subTest(value=value):
                self.bundle['sources'][0]['published_date'] = value
                self.assertTrue(validate_bundle(self.bundle))

    def test_boss_sources_are_rejected(self):
        for host in ['www.zhipin.com', 'm.bosszhipin.com']:
            self.bundle['sources'][0]['url'] = 'https://' + host + '/profile'
            self.assertTrue(validate_bundle(self.bundle))

    def test_same_person_cannot_be_counted_twice(self):
        self.bundle['profiles'][1]['person_key'] = 'P1'
        with self.assertRaisesRegex(ValueError, 'duplicate person_key'):
            self.section()

    def test_requirements_need_a_job_posting(self):
        self.bundle['requirements'][0]['evidence_ids'] = ['S1']
        self.assertTrue(validate_bundle(self.bundle))

    def test_publication_affiliation_does_not_confirm_current_employment(self):
        self.bundle['sources'][0]['source_type'] = 'publication'
        self.assertTrue(validate_bundle(self.bundle))

    def test_section_must_match_company_report_scope(self):
        meta = dict(self.bundle['meta'], company='Another company')
        self.assertTrue(validate_section(self.section(), meta))

    def test_candidate_next_steps_need_sources(self):
        self.candidate['next_steps'][0]['evidence_ids'] = []
        self.assertTrue(validate_bundle(self.bundle, self.candidate))

    def test_non_string_dates_are_rejected(self):
        self.bundle['profiles'][0]['joined_date'] = 2024
        self.assertTrue(validate_bundle(self.bundle))

    def test_malformed_source_types_are_reported(self):
        self.bundle['sources'][0]['source_type'] = []
        self.assertTrue(validate_bundle(self.bundle))

    def test_unknown_candidate_capabilities_are_rejected(self):
        self.candidate['experiences'][0]['capability_ids'] = ['made-up']
        self.assertTrue(validate_bundle(self.bundle, self.candidate))

    def test_input_is_preserved(self):
        original = copy.deepcopy(self.bundle)
        self.section(self.candidate)
        self.assertEqual(self.bundle, original)

    def test_edited_derived_section_is_rejected(self):
        section = self.section(self.candidate)
        self.assertFalse(validate_section(section))
        section['sample_count'] = 99
        self.assertTrue(validate_section(section))

    def test_empty_search_is_reportable(self):
        self.bundle['profiles'] = []
        self.assertEqual(self.section()['sample_count'], 0)

    def test_invalid_policy_is_rejected(self):
        for policy in [{'half_life_days': 0}, {'undated_weight': 2}, {'half_life_days': float('nan')}]:
            self.bundle['policy'] = policy
            self.assertTrue(validate_bundle(self.bundle))

    def test_cli_build_and_attach_preserve_existing_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            existing = {'meta': self.bundle['meta'], 'career': {'internal_path': ['Keep this path']}}
            report = root / 'company.json'
            report.write_text(json.dumps(existing))
            result = subprocess.run([sys.executable, str(SKILL / 'scripts/role_profiles.py'), 'build',
                                     str(SKILL / 'examples/role_profiles/profiles.json'), '--candidate',
                                     str(SKILL / 'examples/role_profiles/candidate.json'), '--out',
                                     str(root / 'out'), '--report', str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            attached = json.loads(report.read_text())
            self.assertEqual(attached['career'], existing['career'])
            self.assertFalse(validate_section(attached['role_profiles']))
            ledger = [json.loads(line) for line in (root / 'out/evidence.jsonl').read_text().splitlines()]
            self.assertTrue(ledger)
            self.assertTrue(all(e['claim_type'] == 'observed_fact' for e in ledger))
            with (root / 'out/source_manifest.csv').open() as stream:
                manifest = list(csv.DictReader(stream))
            self.assertTrue(any(row['status'] == 'searched, not found' for row in manifest))

    def test_mismatched_attachment_does_not_write(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            report = root / 'report.json'
            original = json.dumps({'meta': {'company': 'Another company'}})
            report.write_text(original)
            result = subprocess.run([sys.executable, str(SKILL / 'scripts/role_profiles.py'), 'build',
                                     str(SKILL / 'examples/role_profiles/profiles.json'), '--out',
                                     str(root / 'out'), '--report', str(report)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report.read_text(), original)
            self.assertFalse((root / 'out').exists())

    def test_render_extension_in_every_locale(self):
        import render_report
        from docx import Document
        report = compile_profiles(self.bundle, self.candidate)
        with tempfile.TemporaryDirectory() as td:
            for locale in sorted((SKILL / 'locales').glob('*.json')):
                with self.subTest(locale=locale.stem):
                    path = Path(td) / (locale.stem + '.docx')
                    render_report.build_docx(report, path, locale.stem, profiles_only=True)
                    doc = Document(path)
                    text = '\n'.join(p.text for p in doc.paragraphs)
                    text += '\n'.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
                    self.assertIn('Alex Example', text)
                    self.assertIn('https://example.invalid/S1', text)
                    self.assertIn('Fictional CV, Projects, item 1', text)
                    self.assertEqual(sum(section.text == render_report.section('role_profiles')[0]
                                         for section in doc.paragraphs), 1)

    def test_full_report_keeps_existing_sections_and_appends_cases(self):
        import render_report
        from docx import Document
        report = json.loads((SKILL / 'examples/demo_report.json').read_text())
        report['meta'].update(self.bundle['meta'])
        baseline = copy.deepcopy(report)
        report['role_profiles'] = self.section(self.candidate)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'full.docx'
            render_report.build_docx(report, path)
            text = '\n'.join(p.text for p in Document(path).paragraphs)
            self.assertIn(render_report.section('executive')[0], text)
            self.assertIn(render_report.section('evidence')[0], text)
            self.assertIn(render_report.section('role_profiles')[0], text)
            self.assertIn('Alex Example', text)
        self.assertEqual({k: v for k, v in report.items() if k != 'role_profiles'}, baseline)


if __name__ == '__main__':
    unittest.main()
