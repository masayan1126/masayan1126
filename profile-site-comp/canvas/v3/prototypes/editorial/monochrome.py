"""Neutralize paint colors in the local study, preserving selectors and URLs."""
import re
from PIL import ImageColor

HEX = re.compile(r'#[0-9a-fA-F]{8}(?![\w-])|#[0-9a-fA-F]{6}(?![\w-])|#[0-9a-fA-F]{4}(?![\w-])|#[0-9a-fA-F]{3}(?![\w-])')
RGB = re.compile(r'rgba?\([^)]*\)', re.I)
DECLARATION = re.compile(r'((?:^|[;{])\s*[-\w]+\s*:)([^;{}]*)')
URL = re.compile(r'url\([^)]*\)', re.I)


def grey_hex(value):
    red, green, blue, alpha = ImageColor.getcolor(value, 'RGBA')
    grey = round(.2126 * red + .7152 * green + .0722 * blue)
    return f'#{grey:02x}{grey:02x}{grey:02x}' + (f'{alpha:02x}' if len(value) in (5, 9) else '')


def grey_rgb(match):
    value = match.group(0)
    channels = value[value.index('(') + 1:-1].replace(',', ' ').replace('/', ' ').split()
    if len(channels) not in (3, 4):
        raise ValueError(f'Unsupported paint color: {value}')
    rgb = [float(part[:-1]) * 2.55 if part.endswith('%') else float(part) for part in channels[:3]]
    grey = round(.2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2])
    alpha = ', ' + channels[3] if len(channels) == 4 else ''
    return f'{"rgba" if alpha else "rgb"}({grey}, {grey}, {grey}{alpha})'


def neutralize_paint(value):
    value = HEX.sub(lambda match: grey_hex(match.group(0)), value)
    return RGB.sub(grey_rgb, value)


def neutralize_value(value):
    urls = []

    def keep_url(match):
        url = match.group(0)
        if 'data:image/svg+xml' in url:
            url = re.sub(r'%23([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])',
                         lambda m: '%23' + grey_hex('#' + m.group(1))[1:], url)
        urls.append(url)
        return f'__MONO_URL_{len(urls) - 1}__'

    result = neutralize_paint(URL.sub(keep_url, value))
    for index, url in enumerate(urls):
        result = result.replace(f'__MONO_URL_{index}__', url)
    return result


def neutralize_css(css):
    return DECLARATION.sub(lambda match: match.group(1) + neutralize_value(match.group(2)), css)
