"""Exercise catalog compatibility and native search/selection state."""
import runpy
import unittest
from pathlib import Path

agent = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'theme-picker-agent'))


class PickerTests(unittest.TestCase):
    def test_entire_catalog_parses(self):
        paths = list(agent['GENERIC_THEMES'].glob('*.sh'))
        self.assertGreaterEqual(len(paths), 606)
        for path in paths:
            with self.subTest(theme=path.stem):
                theme = agent['parse_theme'](path)
                self.assertIsNotNone(theme)
                self.assertTrue((agent['TERMINAL_THEMES'] / (theme.name + '.terminal')).is_file())
                for value in theme.colors + [theme.background, theme.foreground]:
                    self.assertRegex(value, r'^[0-9a-fA-F]{6}$')

    def test_search_and_actions(self):
        from AppKit import NSApplication
        NSApplication.sharedApplication()
        picker = agent['Agent'].alloc().init()
        picker.themes = sorted(filter(None, (agent['parse_theme'](p) for p in agent['GENERIC_THEMES'].glob('*.sh'))), key=lambda t: t.name.casefold())
        picker.filtered = picker.themes
        picker.target_tty = None
        picker.make_panel()
        picker.search.setStringValue_('atom dark')
        picker.controlTextDidChange_(None)
        self.assertTrue(picker.filtered)
        self.assertTrue(all('atom' in t.name.lower() and 'dark' in t.name.lower() for t in picker.filtered))
        self.assertFalse(picker.apply.isEnabled())
        picker.target_tty = '/dev/test'
        picker.update_actions()
        self.assertTrue(picker.apply.isEnabled())
        picker.search.setStringValue_('no-such-theme-123456')
        picker.controlTextDidChange_(None)
        self.assertFalse(picker.filtered)
        self.assertTrue(picker.preview.isHidden())
        self.assertFalse(picker.empty.isHidden())
        self.assertFalse(picker.apply.isEnabled())
        self.assertFalse(picker.color_test.isEnabled())
        picker.panel.close()
