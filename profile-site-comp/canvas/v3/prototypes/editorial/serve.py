"""Serve the private design study on a separate origin with existing asset paths."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
PREVIEW = PROJECT / 'output/editorial-concept/site'
PUBLIC = PROJECT / 'canvas/v3/site'


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        clean = unquote(urlsplit(path).path).lstrip('/')
        for root in (PREVIEW, PUBLIC):
            resolved = (root / clean).resolve()
            if resolved.is_relative_to(root.resolve()) and resolved.exists():
                return str(resolved)
        return str(PREVIEW / '__missing__')

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Robots-Tag', 'noindex, nofollow')
        super().end_headers()

    def do_POST(self):
        self.send_error(405, 'Local design preview does not send messages')

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    print('Design study ready: http://127.0.0.1:8777/', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8777), Handler).serve_forever()
