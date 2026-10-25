"""Read-only multi-repository update proposal; no Git or remote mutations."""
from pathlib import Path
import argparse
import json
import sync_course


def proposal(root):
    writes, manifests, removals, original = sync_course.inspect(root)
    changes = sorted([n for n, (_, sha) in writes.items() if original[n] != sha] + list(removals))
    old = root / 'tests/licensing-policy.json'
    before = json.loads(old.read_text()) if old.exists() else None
    after = json.loads((sync_course.SOURCE/'LICENSES/policy.json').read_text())
    return {'repository':str(root),'affected':bool(changes),'files':changes,'policy_before':before,
            'policy_after':after,'review_required':True,'draft_title':'Update UStudyOpen Design and legal policy',
            'validation':['tests/licensing.py --reuse','tests/render_clean.py','tests/run_course.py','tests/platform_validate.py --release'],
            'remote_actions_enabled':False,'auto_merge':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('courses',nargs='+',type=Path)
    print(json.dumps([proposal(x.resolve()) for x in p.parse_args().courses],ensure_ascii=False,indent=2))
