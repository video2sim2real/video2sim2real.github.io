#!/usr/bin/env python3
"""Local preview server: `python3 -m http.server` plus HTTP Range support.

    python3 tools/serve.py          # http://localhost:8000
    python3 tools/serve.py 9000     # another port
    python3 tools/serve.py --lan    # also reachable from a phone on the same Wi-Fi

Why not plain `python3 -m http.server`?  GitHub Pages answers byte-range requests; Python's
built-in server ignores them. Without ranges Chrome cannot fetch just a video's metadata and
hang up, so it keeps every <video> download open and stalled. With ~20 clips on this page that
uses up Chrome's 6 connections per host, and whatever is requested later -- e.g. figures further
down the page -- waits forever and shows up blank. (Seeking in a video fails too.) This server
behaves like the real host, and it tells the browser to revalidate files, so an ordinary
refresh always shows your latest edit.
"""
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    _range = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def send_head(self):
        self._range = None
        path = self.translate_path(self.path)
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", "").strip())
        if not m or not (m.group(1) or m.group(2)) or not os.path.isfile(path):
            return super().send_head()      # no (usable) Range header: the stock behaviour

        f = open(path, "rb")
        stat = os.fstat(f.fileno())
        size = stat.st_size
        if m.group(1):                      # bytes=START-[END]
            start = int(m.group(1))
            end = min(int(m.group(2)), size - 1) if m.group(2) else size - 1
        else:                               # bytes=-N  (the last N bytes)
            start, end = max(size - int(m.group(2)), 0), size - 1
        if start >= size or end < start:
            f.close()
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Last-Modified", self.date_time_string(stat.st_mtime))
        self.end_headers()
        self._range = (start, end - start + 1)
        return f

    def copyfile(self, source, outputfile):
        if self._range is None:
            return super().copyfile(source, outputfile)
        start, remaining = self._range
        source.seek(start)
        while remaining > 0:
            chunk = source.read(min(64 * 1024, remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            remaining -= len(chunk)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # Browsers drop video connections all the time (seeking, pausing, leaving the page).
        if isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            return
        super().handle_error(request, client_address)


if __name__ == "__main__":
    args = sys.argv[1:]
    host = "0.0.0.0" if "--lan" in args else "127.0.0.1"
    port = next((int(a) for a in args if a.isdigit()), 8000)
    print(f"Serving {ROOT}\n  ->  http://localhost:{port}/   (Ctrl+C to stop)")
    try:
        Server((host, port), Handler).serve_forever()
    except KeyboardInterrupt:
        print()
