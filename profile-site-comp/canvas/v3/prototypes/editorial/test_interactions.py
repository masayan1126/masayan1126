"""Regressions for shared selected/focus rules when removing hover paint."""
import unittest
from interactions import motion_only_css


class HoverAppearanceTests(unittest.TestCase):
    def test_plain_hover_loses_paint_but_keeps_lift(self):
        result = motion_only_css('a:hover {color:red;background:#eee;box-shadow:0 2px #333;--action-lift-y:-4px;transform:translateY(-4px)}')
        self.assertNotIn('color:', result)
        self.assertNotIn('background:', result)
        self.assertNotIn('box-shadow:', result)
        self.assertRegex(result, r'--action-lift-y:\s*-4px')
        self.assertIn('translateY(-4px)', result)

    def test_selected_branch_keeps_its_background(self):
        result = motion_only_css('button[aria-selected=true],button:hover {background:#ddd}')
        self.assertIn('button[aria-selected=true]', result)
        self.assertIn('background: #ddd', result)
        self.assertNotIn(':hover', result)

    def test_focus_outline_is_retained(self):
        result = motion_only_css('a:hover,a:focus-visible {outline:3px solid black;color:red}')
        self.assertIn('a:focus-visible', result)
        self.assertIn('outline: 3px solid black', result)
        self.assertNotIn(':hover', result)

    def test_function_arguments_are_not_selector_branches(self):
        result = motion_only_css(':is(.primary,.secondary):hover {color:red;translate:0 -4px}')
        self.assertIn(':is(.primary, .secondary):hover', result)
        self.assertNotIn('color:', result)
        self.assertIn('translate: 0 -4px', result)

    def test_nested_media_and_selected_choices(self):
        result = motion_only_css('body { @media(hover:hover) { .choice:hover {background:red;--action-lift-y:-4px} } .choice:has(input:checked) {background:#ddd} }')
        self.assertIn('@media', result)
        self.assertRegex(result, r'--action-lift-y:\s*-4px')
        self.assertIn(':has(input:checked)', result)
        self.assertIn('background: #ddd', result)
        self.assertNotIn('background: red', result)

    def test_data_url_and_nonlift_transform_are_removed(self):
        result = motion_only_css('a:hover {background:url("data:image/svg+xml;a,b");filter:brightness(.8);transform:scale(1.02);cursor:pointer}')
        self.assertNotIn('data:image', result)
        self.assertNotIn('filter:', result)
        self.assertNotIn('transform:', result)
        self.assertIn('cursor: pointer', result)


if __name__ == '__main__':
    unittest.main()
