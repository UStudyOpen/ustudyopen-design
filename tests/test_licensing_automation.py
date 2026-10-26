# REUSE-IgnoreStart
"""Rights/provenance and automation regressions; only disposable courses."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tooling'))
import licensing
import sync_course
import create_course
import legal_distribution


class Automation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='uso-license-test-')
        self.addCleanup(self.tmp.cleanup)
        self.work=Path(self.tmp.name)
        self.root=self.work/'course'
        with contextlib.redirect_stdout(io.StringIO()):
            create_course.create(ROOT.parent/'ustudyopen-template',self.root,'Autora verificada','Prueba',authorized=True)

    def local(self, edit):
        p=self.root/'licensing.json';data=json.loads(p.read_text());edit(data)
        p.write_text(json.dumps(data,indent=2)+'\n')
        with contextlib.redirect_stdout(io.StringIO()): sync_course.sync(self.root)

    def test_01_default_new_course(self):
        self.assertEqual(licensing.load(self.root,'course.yml')['course']['license'],'CC-BY-NC-4.0')
        self.assertFalse((self.root/'.git').exists())
        self.assertEqual(licensing.validate(self.root,True),[])

    def test_02_other_author_and_license(self):
        with contextlib.redirect_stdout(io.StringIO()):
            root=create_course.create(ROOT.parent/'ustudyopen-template',self.work/'other','Otra autora','Otro','CC-BY-4.0',True)
        self.assertEqual(licensing.load(root,'course.yml')['course']['authorship'],'Otra autora')
        self.assertEqual(licensing.validate(root,True),[])
        with self.assertRaisesRegex(ValueError,'authorization'):
            create_course.create(ROOT.parent/'ustudyopen-template',self.work/'denied','ngulloa','No')

    def test_03_original_qmd_needs_no_legal_edit(self):
        before=(self.root/'REUSE.toml').read_bytes(),(self.root/'LICENSE').read_bytes()
        (self.root/'lecciones').mkdir();(self.root/'lecciones/new.qmd').write_text('---\nustudy-reviewed: false\n---\nOriginal lesson\n')
        self.assertEqual(licensing.validate(self.root,True),[])
        self.assertEqual(before,((self.root/'REUSE.toml').read_bytes(),(self.root/'LICENSE').read_bytes()))
        self.assertIn('false',(self.root/'lecciones/new.qmd').read_text())

    def test_04_authorized_platform_script(self):
        (self.root/'original.py').write_text('# UStudyOpen-Original-Authorized\n# SPDX-FileCopyrightText: 2026 Autora verificada\n# SPDX-License-Identifier: MIT\nprint(1)\n')
        self.assertEqual(licensing.validate(self.root,True),[])
        (self.root/'alternative.js').write_text('// fictional alternative grants\n')
        self.local(lambda d:d['groups'].append({'paths':['alternative.js'],'license':'MIT OR CC-BY-NC-4.0','copyright':'2026 Autora verificada'}))
        self.assertEqual(licensing.validate(self.root,True),[])
        (self.root/'combined.js').write_text('// fictional combined components\n')
        self.local(lambda d:d['groups'].append({'paths':['combined.js'],'license':'MIT AND Apache-2.0','copyright':'2026 Autora verificada'}))
        self.assertEqual(licensing.validate(self.root,True),[])
        (self.root/'unknown.py').write_text('print(2)\n')
        self.assertTrue(any('unclassified' in x for x in licensing.validate(self.root)))

    def dependency(self, license_id):
        dest=self.root/'vendor';dest.mkdir()
        (dest/'lib.js').write_text('// upstream library https://example.org/upstream\n')
        text=ROOT/'LICENSES'/f'{license_id}.txt'
        target=self.root/'LICENSES'/f'{license_id}.txt'
        if not target.exists(): shutil.copy2(text,target)
        entry={'origin':'https://example.org/upstream','version':'1.2.3','paths':['vendor/lib.js'],
               'notice_files':[], 'license':license_id,'copyright':'2026 Upstream author','reviewed':True,
               'license_file':f'LICENSES/{license_id}.txt','sha256':hashlib.sha256(text.read_bytes()).hexdigest()}
        self.local(lambda d:d['third_party'].append(entry))
        return target

    def test_05_apache_dependency(self):
        self.dependency('Apache-2.0');self.assertEqual(licensing.validate(self.root,True),[])
        notice=self.root/'LICENSES/upstream-NOTICE.txt';notice.write_text('Upstream attribution required')
        self.local(lambda d:d['third_party'][0].update({'notice_files':[{'path':'LICENSES/upstream-NOTICE.txt','sha256':hashlib.sha256(notice.read_bytes()).hexdigest()}]}))
        self.assertEqual(licensing.validate(self.root),[])
        notice.unlink()
        self.assertTrue(any('NOTICE missing' in x for x in licensing.validate(self.root)))

    def test_06_unlicense_dependency(self):
        self.dependency('Unlicense');self.assertEqual(licensing.validate(self.root,True),[])

    def test_07_unknown_dependency_blocks(self):
        (self.root/'vendor').mkdir();(self.root/'vendor/unknown.js').write_text('// no origin\n')
        self.assertTrue(any('human rights review' in x for x in licensing.validate(self.root)))
        (self.root/'lecciones').mkdir()
        (self.root/'lecciones/remote.qmd').write_text('<script src="https://example.org/unknown.js"></script>')
        self.assertTrue(any('unregistered remote resource' in x for x in licensing.validate(self.root)))
        self.local(lambda d:d['third_party'].append({'origin':'unknown','paths':['vendor/unknown.js'],'reviewed':False}))
        self.assertTrue(any('human rights review' in x for x in licensing.validate(self.root)))

    def test_08_policy_change_preview_and_update(self):
        central=self.work/'central';shutil.copytree(ROOT,central,ignore=shutil.ignore_patterns('.git','_site','artifacts','.quarto','__pycache__'))
        p=central/'LICENSES/policy.json';d=json.loads(p.read_text());d['version']='1.0.1';p.write_text(json.dumps(d)+'\n')
        before=(self.root/'tests/licensing-policy.json').read_bytes()
        with patch.object(sync_course,'SOURCE',central),contextlib.redirect_stdout(io.StringIO()):
            self.assertIn('tests/licensing-policy.json',sync_course.sync(self.root,dry_run=True))
            self.assertEqual(before,(self.root/'tests/licensing-policy.json').read_bytes())
            sync_course.sync(self.root)
        self.assertEqual(licensing.load(self.root,'tests/licensing-policy.json')['version'],'1.0.1')

    def test_09_local_exceptions_preserved(self):
        self.local(lambda d:d.update({'conditions':['Specific local restriction; no new rights granted']}))
        before=(self.root/'licensing.json').read_bytes()
        with contextlib.redirect_stdout(io.StringIO()):sync_course.sync(self.root)
        self.assertEqual(before,(self.root/'licensing.json').read_bytes())

    def test_10_unmanaged_overwrite_rejected(self):
        p=self.root/'platform-vendor.json';d=json.loads(p.read_text());del d['files']['tests/licensing.py'];p.write_text(json.dumps(d))
        before=(self.root/'tests/licensing.py').read_bytes()
        with self.assertRaisesRegex(SystemExit,'Unmanaged platform file'):
            sync_course.sync(self.root)
        self.assertEqual(before,(self.root/'tests/licensing.py').read_bytes())

    def test_11_partial_failure_restores_legal_update(self):
        self.local(lambda d:d['groups'].append({'paths':['new/*.qmd'],'category':'academic'}))
        # Change generated declarations without touching source or legal rights.
        p=self.root/'licensing.json';d=json.loads(p.read_text());d['groups'].append({'paths':['other/*.qmd'],'category':'academic'});p.write_text(json.dumps(d))
        before=(self.root/'REUSE.toml').read_bytes();real=os.replace
        def fail(source,target):
            if '/new/REUSE.toml' in str(source): raise OSError('fixture promotion failure')
            return real(source,target)
        with patch.object(sync_course.os,'replace',side_effect=fail),self.assertRaisesRegex(SystemExit,'fixture promotion failure'),contextlib.redirect_stdout(io.StringIO()):
            sync_course.sync(self.root)
        self.assertEqual(before,(self.root/'REUSE.toml').read_bytes())

    def test_12_noop_twice_preserves_mtimes(self):
        before={str(p):p.stat().st_mtime_ns for p in self.root.rglob('*') if p.is_file()}
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(sync_course.sync(self.root),[]);self.assertEqual(sync_course.sync(self.root),[])
        self.assertEqual(before,{str(p):p.stat().st_mtime_ns for p in self.root.rglob('*') if p.is_file()})

    def test_13_caches_and_generated_are_excluded(self):
        for name in ['docs','_site','.cache','node_modules','__pycache__']:
            (self.root/name).mkdir(exist_ok=True);(self.root/name/'unknown.js').write_text('unknown dependency')
        self.assertEqual(licensing.validate(self.root),[])

    def test_14_html_has_policy_and_notices(self):
        (self.root/'_site').mkdir();(self.root/'_site/index.html').write_text('<html><body>lesson</body></html>')
        legal_distribution.prepare(self.root);errors=[];legal_distribution.output_checks(self.root,errors)
        self.assertEqual(errors,[])
        self.assertTrue((self.root/'_site/legal/local-resources.json').is_file())
        (self.root/'_site/site_libs').mkdir()
        (self.root/'_site/site_libs/unknown.js').write_text('// no provenance')
        artifact_errors=[];legal_distribution.output_checks(self.root,artifact_errors)
        self.assertTrue(any('unregistered incorporated' in x for x in artifact_errors))
        (self.root/'_site/legal/extension/LICENSE').unlink();errors=[];legal_distribution.output_checks(self.root,errors)
        self.assertTrue(errors)

    def test_15_original_attribution_retained(self):
        self.assertIn('ngulloa',(self.root/'_extensions/ustudyopen-design/LICENSE').read_text())
        self.assertIn('ngulloa',(self.root/'tests/LICENSE-platform.txt').read_text())
        self.assertIn('ngulloa',(self.root/'LICENSING.md').read_text())

    def test_16_contradictory_license_and_copyright(self):
        (self.root/'lecciones').mkdir()
        p=self.root/'lecciones/conflict.qmd';p.write_text('SPDX-License-Identifier: MIT\nCopyright 2026 Other author\n')
        errors=licensing.validate(self.root)
        self.assertTrue(any('contradictory SPDX' in x for x in errors))
        self.assertTrue(any('contradictory copyright' in x for x in errors))

if __name__=='__main__':unittest.main(verbosity=2)

# REUSE-IgnoreEnd
