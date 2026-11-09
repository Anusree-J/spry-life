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

    def test_link_preview_points_at_a_packaged_image(self):
        with urlopen(self.origin) as response:
            html = response.read().decode()
        self.assertIn('<link rel="canonical" href="https://sprylife.org/" />', html)
        self.assertIn(
            '<meta property="og:image" content="https://sprylife.org/og-image.png" />',
            html,
        )
        image = (ROOT / "dist" / "og-image.png").read_bytes()
        self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
        width = int.from_bytes(image[16:20], "big")
        height = int.from_bytes(image[20:24], "big")
        self.assertEqual((width, height), (1200, 630))

    def test_font_is_self_hosted_woff2(self):
        css = (ROOT / "dist" / "style.css").read_text()
        self.assertIn('url("/inter.woff2")', css)
        self.assertNotIn("fonts.googleapis", css)
        self.assertEqual((ROOT / "dist" / "inter.woff2").read_bytes()[:4], b"wOF2")

    def test_not_found_page_links_home(self):
        html = (ROOT / "dist" / "404.html").read_text()
        self.assertIn('<meta name="robots" content="noindex" />', html)
        self.assertIn('href="/"', html)
        self.assertNotIn("<script", html)

    def test_assets_are_served_intact(self):
        for name in (
            "404.html",
            "style.css",
            "favicon.svg",
            "og-image.png",
            "inter.woff2",
        ):
            with self.subTest(name=name), urlopen(self.origin + "/" + name) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.read(), (ROOT / "site" / name).read_bytes())

    def test_only_public_files_are_packaged(self):
        self.assertEqual(
            {p.name for p in (ROOT / "dist").iterdir()},
            {
                "index.html",
                "404.html",
                "style.css",
                "favicon.svg",
                "og-image.png",
                "inter.woff2",
                ".nojekyll",
            },
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
