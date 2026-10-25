from pathlib import Path
p=Path('tests/test_core.py');s=p.read_text(encoding='utf-8')
s=s.replace('import threading','import threading\nimport tempfile\nimport urllib.request\nimport urllib.error\nfrom http.server import ThreadingHTTPServer')
s=s.replace('from src.server import api_scheduling, api_producer_consumer','from src.server import api_scheduling, api_producer_consumer, Handler')
needle="    def test_single_api_has_result(self):\n"
# Extend one existing API case with HTTP file boundary regression.
s=s.replace(needle,needle+'''        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix='web-probe-',dir=root) as folder:
            Path(folder,'probe.txt').write_text('must not be served',encoding='utf-8')
            server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
            worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
            try:
                url=f'http://127.0.0.1:{server.server_port}/../{Path(folder).name}/probe.txt'
                with self.assertRaises(urllib.error.HTTPError) as caught: urllib.request.urlopen(url)
                self.assertEqual(caught.exception.code,403)
            finally:
                server.shutdown();server.server_close();worker.join()
''')
p.write_text(s,encoding='utf-8')
