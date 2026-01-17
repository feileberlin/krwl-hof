"""Minimal CDN inliner compatibility wrapper for tests."""

from pathlib import Path
import urllib.request
import urllib.error

from .site_generator import DEPENDENCIES, SiteGenerator


class CDNInliner:
    """Compatibility wrapper for legacy CDN fallback tests."""

    def __init__(self, config, base_path):
        self.config = config
        self.base_path = Path(base_path)
        self.dependencies_dir = self.base_path / 'lib'

    def read_local_file(self, path: Path) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                return handle.read()
        except FileNotFoundError:
            return ''

    def _fetch_url(self, url: str) -> str:
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read().decode('utf-8')
        except (urllib.error.URLError, UnicodeDecodeError):
            return ''

    def _leaflet_file_url(self, suffix: str) -> str:
        config = DEPENDENCIES['leaflet']
        base_url = config['base_url'].format(version=config['version'])
        return f"{base_url}{suffix}"

    def get_leaflet_css(self) -> str:
        content = self._fetch_url(self._leaflet_file_url('/leaflet.css'))
        return content or self.read_local_file(self.dependencies_dir / 'leaflet' / 'leaflet.css') or '/* Leaflet CSS unavailable */'

    def get_leaflet_js(self) -> str:
        content = self._fetch_url(self._leaflet_file_url('/leaflet.js'))
        return content or self.read_local_file(self.dependencies_dir / 'leaflet' / 'leaflet.js') or '// Leaflet JS unavailable'

    def generate_inline_html(self) -> str:
        public_html = self.base_path / 'public' / 'index.html'
        if public_html.exists():
            return self.read_local_file(public_html)
        generator = SiteGenerator(self.base_path)
        generator.generate_site(skip_lint=True)
        return self.read_local_file(public_html)
