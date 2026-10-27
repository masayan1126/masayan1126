"""Keep hover feedback limited to the adopted lift, across every CSS layer."""
from functools import lru_cache
from pathlib import Path
import re
import subprocess

ESBUILD = Path(__file__).resolve().parents[4] / 'node_modules/esbuild/bin/esbuild'
LEAF_RULE = re.compile(r'([^{}]+)\{([^{}]*)\}')
PAINT_PREFIXES = ('background', 'border', 'outline', 'font', 'text-decoration')
PAINT_PROPERTIES = {'color', 'box-shadow', 'text-shadow', 'opacity', 'filter',
                    'backdrop-filter', 'fill', 'stroke', 'text-underline-offset'}


def split_css(value, separator):
    """Split lists without splitting function arguments, strings or data URLs."""
    parts, start, depth, quote, escaped, comment = [], 0, 0, None, False, False
    for index, char in enumerate(value):
        if comment:
            if value[index - 1:index + 1] == '*/':
                comment = False
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if value[index:index + 2] == '/*':
            comment = True
        elif char in ('"', "'"):
            quote = char
        elif char in '([':
            depth += 1
        elif char in ')]':
            depth -= 1
        elif char == separator and depth == 0:
            parts.append(value[start:index])
            start = index + 1
    return parts + [value[start:]]


def hover_declaration_allowed(declaration):
    declaration = re.sub(r'/\*.*?\*/', '', declaration, flags=re.S).strip()
    if not declaration or ':' not in declaration:
        return True
    name, value = declaration.split(':', 1)
    name = name.strip().lower()
    if name.startswith('--'):
        return name == '--action-lift-y'
    if name == 'transform':
        return bool(re.fullmatch(r'\s*(?:none|translateY\(-4px\))\s*(?:!important)?\s*', value))
    return name not in PAINT_PROPERTIES and not name.startswith(PAINT_PREFIXES)


def strip_hover_appearance(flat_css):
    """Input is flattened by esbuild; only declaration-only leaf rules match.

    Split mixed selector lists so selected/focused branches retain their paint.
    The common lift variable and the extension's image-only lift stay intact.
    """
    def replace(match):
        selectors, body = match.groups()
        if ':hover' not in selectors:
            return match.group(0)
        prefix = re.match(r'\s*(?:/\*.*?\*/\s*)*', selectors, flags=re.S).group()
        selectors = selectors[len(prefix):]
        branches = split_css(selectors, ',')
        normal = [branch for branch in branches if ':hover' not in branch]
        hovered = [branch for branch in branches if ':hover' in branch]
        motion = ';'.join(item for item in split_css(body, ';') if hover_declaration_allowed(item)).strip('; \n')
        result = ','.join(normal) + '{' + body + '}' if normal else ''
        if motion:
            result += ','.join(hovered) + '{' + motion + ';}'
        return prefix + result
    return LEAF_RULE.sub(replace, flat_css)


@lru_cache(maxsize=64)
def motion_only_css(css):
    # Flatten nesting with the same compiler/target already used for publishing.
    flat = subprocess.run([str(ESBUILD), '--loader=css', '--target=safari15', '--log-level=warning'],
                          input=css, text=True, capture_output=True, check=True).stdout
    return strip_hover_appearance(flat)
