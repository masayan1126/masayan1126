"""Promote the approved design while retaining the complete quote asset archive."""
from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
import posixpath
import re
import shutil
import subprocess
import tempfile

from build import build, PROJECT, PAGES

BASE = 'https://studio.msyn.me'
MODULE_REF = re.compile(r'''(["'])([^"'\s]+\.mjs)\1''')


def publish(source, destination):
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    # Original hashed files remain available to already-open pages. Never write
    # transformed bytes at their previous immutable addresses.
    shutil.copytree(source, destination, dirs_exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='studio-production-') as directory:
        overlay = Path(directory)
        build(source_root=source, output_root=overlay, production=True)
        originals = {str(p.relative_to(source)): p.read_text() for p in source.rglob('*.mjs')}
        modules = dict(originals)
        modules.update({str(p.relative_to(overlay)): p.read_text() for p in overlay.rglob('*.mjs')})
        resolved, visiting = {}, set()

        def module(path):
            if path in resolved:
                return resolved[path]
            if path in visiting:
                raise ValueError(f'Cyclic module dependency: {path}')
            visiting.add(path)

            def dependency(match):
                quote, reference = match.groups()
                if not reference.startswith(('.', '/')):
                    return match.group()
                dependency_path = posixpath.normpath(reference.lstrip('/') if reference.startswith('/') else posixpath.join(posixpath.dirname(path), reference))
                if dependency_path not in modules:
                    return match.group()
                name, _ = module(dependency_path)
                if reference.startswith('/'):
                    updated = '/' + name
                else:
                    updated = posixpath.relpath(name, posixpath.dirname(path) or '.')
                    if not updated.startswith('.'):
                        updated = './' + updated
                return quote + updated + quote

            text = MODULE_REF.sub(dependency, modules[path])
            changed = path not in originals or text != originals[path]
            name = path
            if changed:
                stem = re.sub(r'\.[a-f0-9]{12}$', '', str(Path(path).with_suffix('')))
                name = stem + '.' + hashlib.sha256(text.encode()).hexdigest()[:12] + '.mjs'
                target = destination / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
            resolved[path] = name, text
            visiting.remove(path)
            return name, text

        for path in modules:
            module(path)
        replacements = {'/' + path: '/' + record[0] for path, record in resolved.items() if path != record[0]}
        esbuild = PROJECT / 'node_modules/esbuild/bin/esbuild'
        for path in overlay.rglob('*.css'):
            relative = str(path.relative_to(overlay))
            compiled = subprocess.run([str(esbuild), '--loader=css', '--target=safari15', '--log-level=warning'], input=path.read_text(), text=True, capture_output=True, check=True).stdout
            name = str(Path(relative).with_suffix('')) + '.' + hashlib.sha256(compiled.encode()).hexdigest()[:12] + '.css'
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(compiled)
            replacements['/' + relative] = '/' + name

        for path in overlay.rglob('*'):
            if not path.is_file() or path.suffix in ('.mjs', '.css') or path.name.endswith('.json'):
                continue
            relative = path.relative_to(overlay)
            assert '__review' not in relative.parts
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == '.html':
                text = path.read_text()
                for old, new in sorted(replacements.items(), key=lambda item: -len(item[0])):
                    text = text.replace(old, new)
                if str(relative.parent) in ('media', 'activities', 'services'):
                    soup = BeautifulSoup(text, 'html.parser')
                    for canonical in soup.select('link[rel="canonical"]'):
                        canonical['href'] = BASE + canonical['href'].split('#')[0]
                    text = str(soup)
                target.write_text(text)
            else:
                shutil.copyfile(path, target)

        routes = ['/' + (page + '/' if page else '') for page in PAGES]
        (destination / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + BASE + route + '</loc></url>' for route in routes) + '</urlset>\n')
        (destination / 'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /__review/\nSitemap: ' + BASE + '/sitemap.xml\n')
        for forbidden in ('__review', 'review.html', 'build.json'):
            assert not (destination / forbidden).exists(), forbidden
        manifest = {'routes': routes, 'module_replacements': {path: record[0] for path, record in resolved.items() if path != record[0]}, 'public': str(destination), 'forms_send': True, 'review_included': False}
        record = PROJECT / 'output/public-release/build.json'
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('Published design export:', destination)
