"""Serve the same review tab and the canonical site's routes on localhost."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit, unquote
HERE=Path(__file__).resolve().parent
SITE=HERE/'site'
REVIEW=HERE.parents[1]/'output/3d-mode/review.html'
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        clean=unquote(urlsplit(path).path)
        if clean=='/review.html':return str(REVIEW)
        if clean=='/pricing-review/':return str(REVIEW.parent/'pricing-review.html')
        resolved=(SITE/clean.lstrip('/')).resolve()
        return str(resolved if resolved.is_relative_to(SITE.resolve()) else SITE/'404.html')
    def end_headers(self):
        self.send_header('Cache-Control','no-cache')
        super().end_headers()
    def log_message(self,format,*args):pass
if __name__=='__main__':
    print('Review ready: http://127.0.0.1:8776/review.html',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8776),Handler).serve_forever()
