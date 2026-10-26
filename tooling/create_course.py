"""Create a local course atomically from the template; never initializes Git."""
from pathlib import Path
import argparse
import json
import shutil
import tempfile
import licensing
import sync_course
from safe_paths import checked_path, project_files


def create(template, target, author, name, license_id=None, authorized=False):
    template, target = Path(template), Path(target)
    if not authorized or not author.strip() or '\n' in author:
        raise ValueError('Explicit rights authorization and verified author required')
    if license_id is None:
        license_id = licensing.load(sync_course.SOURCE, 'LICENSES/policy.json')['categories']['academic_default']
    from license_expression import get_spdx_licensing
    if get_spdx_licensing().validate(license_id,strict=True).errors:
        raise ValueError('Invalid SPDX license')
    legal = checked_path(sync_course.SOURCE, 'LICENSES/'+license_id+'.txt')
    if not legal.is_file():
        raise ValueError('Reviewed full license text required centrally: '+license_id)
    if target.exists() or target.is_symlink():
        raise ValueError('Destination must not exist')
    project_files(template, licensing.SKIP | {'docs'}, exclude_env=True)
    with tempfile.TemporaryDirectory(prefix='uso-new-course-',dir=target.parent) as temp:
        work = Path(temp)/'course'
        shutil.copytree(template,work,ignore=lambda d,n:[x for x in n if x in licensing.SKIP | {'docs'} or x.startswith('.env')])
        course = licensing.load(work,'course.yml')
        course['course'].update({'authorship':author,'license':license_id,'name':name,'slug':target.name})
        (work/'course.yml').write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n')
        local = licensing.load(work,'licensing.json')
        # Template samples retain ngulloa MIT. New lessons in an explicit original-only
        # namespace use the incoming author's grant; imports require their own entry.
        local['is_template'] = False
        local['groups'].append({'paths':['lecciones/*.qmd','lecciones/**/*.qmd','LICENSE'],'category':'academic'})
        local['original_rights_authorization']={'author':author,'license':license_id,'confirmed':True}
        (work/'licensing.json').write_text(json.dumps(local,ensure_ascii=False,indent=2)+'\n')
        (work/'LICENSE').write_bytes(legal.read_bytes())
        # Append scope, retaining the complete approved template notices.
        with (work/'LICENSING.md').open('a') as out:
            out.write('\n## Configuración de esta asignatura\n\n'+name+': contenido académico original nuevo en `lecciones/` por '+author+', bajo '+license_id+'.\nLos ejemplos heredados conservan MIT de ngulloa. Las importaciones se registran separadamente.\n')
        config = work / '_quarto.yml'
        text = config.read_text().replace('Asignatura de ejemplo', name)
        text = text.replace("'Autoría y licencia: completar antes de publicar'", json.dumps(author+' · '+license_id,ensure_ascii=False))
        config.write_text(text)
        # Sample pages and template software remain under MIT in LICENSES/MIT.txt.
        with (work/'LICENSING.md').open('a') as out:
            out.write('En este curso, el texto MIT citado por la plantilla se conserva en `LICENSES/MIT.txt`; el `LICENSE` raíz documenta '+license_id+' para las lecciones nuevas autorizadas.\n')
        sync_course.sync(work)
        errors = licensing.validate(work,reuse=True)
        if errors:
            raise ValueError('; '.join(errors))
        work.rename(target)
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('target',type=Path)
    parser.add_argument('--template',type=Path,default=sync_course.SOURCE.parent/'ustudyopen-template')
    parser.add_argument('--author',required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--license')
    parser.add_argument('--authorize-original-content',action='store_true')
    a=parser.parse_args()
    create(a.template,a.target,a.author,a.name,a.license,a.authorize_original_content)
