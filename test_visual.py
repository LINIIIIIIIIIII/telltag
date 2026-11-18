"""Consistency tests for SVG illustrations, not food chemistry validation."""
import unittest
from visual import package_svg, stack_svg

class TestVisualization(unittest.TestCase):
    def test_scene_foods(self):
        for food in ('Beef', 'Chicken', 'Fish'):
            svg = package_svg(food, 'Inside sealed package', '#68428F', 10, 30, True, True)
            self.assertIn(food, svg)
            self.assertIn('#68428F', svg)
            self.assertIn('TELLTAG', svg)
            self.assertIn('Schematic only', svg)

    def test_stack_package_layer_visibility(self):
        inside = stack_svg('Inside sealed package', 50, 20, '#ffee00', True, True)
        outside = stack_svg('Outside sealed package', 50, 20, '#ffee00', True, True)
        self.assertNotIn('Package film', inside)
        self.assertIn('Package film', outside)
        self.assertIn('50 µm', inside)

    def test_visual_only_layers(self):
        stack=stack_svg('Inside sealed package', 50, 20, '#ffee00', False, False)
        self.assertNotIn('Viewing layer', stack)
        self.assertNotIn('Adhesive / edge seal', stack)

if __name__ == '__main__':
    unittest.main()
