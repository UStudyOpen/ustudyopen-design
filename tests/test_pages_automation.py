# SPDX-FileCopyrightText: 2026 ngulloa
# SPDX-License-Identifier: MIT
"""Publication authorization and synchronization regressions, with disposable fixtures."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tooling'))
import sync_course
from pages_authorization import authorized


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


class PagesAutomation(unittest.TestCase):
    def course(self):
        temp = tempfile.TemporaryDirectory(prefix='uso-pages-test-')
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'course.yml').write_text('{}\n')
        self.sync(root)
        return root

    def sync(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            sync_course.sync(root)

    def test_publication_event_matrix(self):
        for approved in (True, False, None, 'true'):
            for event in ('push', 'pull_request', 'pull_request_target', 'workflow_dispatch'):
                for ref in ('refs/heads/main', 'refs/heads/feature', 'refs/tags/main'):
                    for enabled in ('true', 'false', None):
                        for confirm in ('PUBLICAR', '', 'publicar'):
                            expected = (enabled == 'true' and ref == 'refs/heads/main' and
                                        ((event == 'push' and approved is True) or
                                         (event == 'workflow_dispatch' and confirm == 'PUBLICAR')))
                            with self.subTest(approved=approved, event=event, ref=ref,
                                              enabled=enabled, confirm=confirm):
                                self.assertEqual(authorized({'pages_automation_approved': approved},
                                                            event, ref, enabled, confirm), expected)

    def test_workflow_job_conditions_block_pr_other_branches_and_failed_builds(self):
        text = (ROOT / 'workflows/deploy.yml').read_text()
        conditions = re.findall(r"    if: \$\{\{ (.*?) \}\}", text)
        self.assertEqual(len(conditions), 2)
        def evaluate(expression, values):
            for key, value in values.items():
                expression = expression.replace(key, repr(value))
            expression = expression.replace('&&', ' and ').replace('||', ' or ')
            return eval(expression, {'__builtins__': {}}, {})
        for event, ref, confirm, allowed in [
                ('pull_request', 'refs/pull/1/merge', 'PUBLICAR', False),
                ('pull_request', 'refs/heads/main', 'PUBLICAR', False),
                ('push', 'refs/heads/feature', '', False),
                ('push', 'refs/heads/main', '', True),
                ('workflow_dispatch', 'refs/heads/main', '', False),
                ('workflow_dispatch', 'refs/heads/main', 'PUBLICAR', True)]:
            values = {'vars.USO_PAGES_ENABLED': 'true', 'github.ref': ref,
                      'github.event_name': event, 'inputs.confirm': confirm}
            self.assertEqual(evaluate(conditions[0], values), allowed)
        for result in ('failure', 'cancelled', 'skipped', 'success'):
            for authorization in ('true', '', 'false'):
                values = {'needs.build.result': result, 'needs.build.outputs.authorized': authorization,
                          'vars.USO_PAGES_ENABLED': 'true', 'github.ref': 'refs/heads/main'}
                self.assertEqual(evaluate(conditions[1], values),
                                 result == 'success' and authorization == 'true')
        self.assertIn('needs: build', text)
        self.assertIn('ref: ${{ github.sha }}', text)
        self.assertIn('cancel-in-progress: false', text)

    def test_sync_only_enables_push_for_boolean_approved_course(self):
        root = self.course()
        for approved in (None, 'true', True, False):
            (root / 'course.yml').write_text(json.dumps({'course': {'pages_automation_approved': approved}}))
            self.sync(root)
            text = (root / '.github/workflows/deploy.yml').read_text()
            self.assertEqual('  push:\n    branches: [main]' in text, approved is True)
            self.assertIn('workflow_dispatch:', text)
            self.assertIn("inputs.confirm == 'PUBLICAR'", text)
            self.assertIn("needs.build.result == 'success'", text)
            self.assertNotIn('always()', text)
            lock = json.loads((root / 'platform-vendor.json').read_text())['files']
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), lock['.github/workflows/deploy.yml'])
            before = snapshot(root)
            self.sync(root)
            self.assertEqual(snapshot(root), before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
