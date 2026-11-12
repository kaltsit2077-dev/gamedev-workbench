import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UpstreamReviewTests(unittest.TestCase):
    def test_inspected_sources_stay_pinned_and_unrun(self):
        records = json.loads((ROOT/'docs/upstream-review-v09.json').read_text(encoding='utf-8'))['records']
        catalog = {r['id']: r for r in json.loads((ROOT/'skills/gamedev-workbench/catalog/resources.json').read_text(encoding='utf-8'))}
        for row in records:
            self.assertRegex(row['commit'], r'^[a-f0-9]{40}$')
            self.assertIs(type(row['stars_at_check']), int)
            self.assertTrue(row['inspected'])
            for source in row['inspected']:
                self.assertRegex(source['blob_sha'], r'^[a-f0-9]{40}$')
                self.assertEqual(source['url'], 'https://github.com/'+row['repository']+'/blob/'+row['commit']+'/'+source['path'])
            if row['catalog_id']:
                entry = catalog[row['catalog_id']]
                self.assertEqual(entry['local_verification'], 'not-run')
                self.assertEqual(entry['url'], 'https://github.com/'+row['repository']+'/tree/'+row['commit'])
            else:
                self.assertTrue(row['archived'])
