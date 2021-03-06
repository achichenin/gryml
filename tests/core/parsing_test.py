import unittest
from pathlib import Path

from jinja2 import Undefined
from ruamel.yaml.comments import CommentedMap

from gryml.cli import init_parser
from gryml.core import Gryml


class ParsingTest(unittest.TestCase):

    def setUp(self):
        self.parser = init_parser()
        self.path = Path(__file__).parent.resolve()
        self.gryml = Gryml()

    def test_iterate_path(self):
        definition_file = self.path / '../fixtures/core/tag_placement.yaml'
        stream = self.gryml.iterate_path(Path(definition_file))
        directory, definition, tags = next(stream)

        self.assertEqual(definition_file, directory)
        self.assertIsInstance(definition, CommentedMap)
        self.assertTrue(str(definition.ca.items['rules'][2].value).startswith("#[append]{rbac.extraClusterRoleRules}"))

        result_values = self.gryml.process(definition, dict(tags=tags))

        self.assertIsInstance(result_values, dict)

    def test_expressions_raw(self):
        values_file = self.path / '../fixtures/core/values.yaml'
        values = self.gryml.load_values(values_file)
        self.gryml.set_values(values)

        self.assertIsInstance(self.gryml.eval('badValue'), Undefined)
        self.assertEqual("grafana", self.gryml.eval('chart.app'))
        self.assertEqual(2, self.gryml.eval('chart.labels.release + 1'))
        self.assertEqual(self.gryml.values['chart']['labels']['chart'] + "-suffix",
                         self.gryml.eval('chart.labels.chart + "-suffix"'))
        self.assertEqual(True, self.gryml.eval('not badValue'))

    def test_expressions_during_processing(self):
        definition_file = self.path / '../fixtures/core/tag_placement.yaml'
        values_file = self.path / '../fixtures/core/values.yaml'

        stream = self.gryml.iterate_path(Path(definition_file))
        values = self.gryml.load_values(values_file)
        self.gryml.set_values(values)

        directory, definition, tags = next(stream)

        result_values = self.gryml.process(definition, dict(tags=tags))
        self.gryml.print(result_values)
