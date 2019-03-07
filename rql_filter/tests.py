import unittest

from rql_filter.parser import parse_rql


class TestRQLParser(unittest.TestCase):
    def test_simple_comparisons(self):
        tests = (
            ('a==b', [['a', 'exact', 'b']]),
            ('a=="b"', [['a', 'exact', 'b']]),
            ('a=="b b"', [['a', 'exact', 'b b']]),
            ('a=le=b', [['a', 'lte', 'b']]),
            ('a=lt=b', [['a', 'lt', 'b']]),
            ('a=ge=b', [['a', 'gte', 'b']]),
            ('a=gt=b', [['a', 'gt', 'b']]),
        )
        for test, result in tests:
            self.assertEqual(parse_rql(test), result)

    def test_in_expressions(self):
        tests = (
            ('a=in=(1,2,3)', [['a', 'in', ['1', '2', '3']]]),
            ('a=in=(1,2,hello)', [['a', 'in', ['1', '2', 'hello']]]),
        )
        for test, result in tests:
            self.assertEqual(parse_rql(test), result)

    def test_and_or_expressions(self):
        tests = (
            ('a=in=(1,2,3),b==4',
             [['a', 'in', ['1', '2', '3']], 'OR', ['b', 'exact', '4']]),
            ('a=in=(1,2,3);b==4',
             [['a', 'in', ['1', '2', '3']], 'AND', ['b', 'exact', '4']]),
        )
        for test, result in tests:
            self.assertEqual(parse_rql(test), result)

    def test_nested_expressions(self):
        tests = (
            ('(a=in=(1,2,3),b==4);c=lt=5',
             [[['a', 'in', ['1', '2', '3']], 'OR', ['b', 'exact', '4']], 'AND',
              ['c', 'lt', '5']]),
            ('a=in=(1,2,3);(b==4,c=lt=5)',
             [['a', 'in', ['1', '2', '3']], 'AND', [['b', 'exact', '4'], 'OR',
              ['c', 'lt', '5']]]),
        )
        for test, result in tests:
            self.assertEqual(parse_rql(test), result)
