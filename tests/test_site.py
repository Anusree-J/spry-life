"""Check the actual deploy artifact and its public HTTP surface."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["python3", str(ROOT / "scripts/build.py")], check=True)
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "dist"))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_page_has_approved_mission_and_sunny_link(self):
        with urlopen(self.origin) as response:
            html = response.read().decode()
            self.assertEqual(response.status, 200)
        self.assertIn("Helping elders live well and live longer.", html)
        self.assertIn('href="https://mysunny.world/"', html)
        self.assertNotIn("<script", html)

    def test_assets_are_served_intact(self):
        for name in ("style.css", "favicon.svg"):
            with self.subTest(name=name), urlopen(self.origin + "/" + name) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.read(), (ROOT / "site" / name).read_bytes())

    def test_only_public_files_are_packaged(self):
        self.assertEqual(
            {p.name for p in (ROOT / "dist").iterdir()},
            {"index.html", "style.css", "favicon.svg", ".nojekyll"},
        )
        for path in (ROOT / "site").iterdir():
            self.assertFalse(path.is_symlink())
            self.assertTrue(path.is_file())
        for path in ("/README.md", "/package.json", "/not-found"):
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.origin + path)
            self.assertEqual(error.exception.code, 404)
            error.exception.close()


if __name__ == "__main__":
    unittest.main()
