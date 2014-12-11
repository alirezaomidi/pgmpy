from pgmpy.factors import Factor
from pgmpy.models import MarkovModel
from pgmpy.tests import help_functions as hf
import numpy as np
import unittest


class TestBaseModelCreation(unittest.TestCase):
    def setUp(self):
        self.graph = MarkovModel()

    def test_class_init_without_data(self):
        self.assertIsInstance(self.graph, MarkovModel)

    def test_class_init_with_data_string(self):
        self.g = MarkovModel([('a', 'b'), ('b', 'c')])
        self.assertListEqual(sorted(self.g.nodes()), ['a', 'b', 'c'])
        self.assertListEqual(hf.recursive_sorted(self.g.edges()),
                             [['a', 'b'], ['b', 'c']])

    def test_class_init_with_data_nonstring(self):
        self.g = MarkovModel([(1, 2), (2, 3)])

    def test_add_node_string(self):
        self.graph.add_node('a')
        self.assertListEqual(self.graph.nodes(), ['a'])

    def test_add_node_nonstring(self):
        self.graph.add_node(1)

    def test_add_nodes_from_string(self):
        self.graph.add_nodes_from(['a', 'b', 'c', 'd'])
        self.assertListEqual(sorted(self.graph.nodes()), ['a', 'b', 'c', 'd'])

    def test_add_nodes_from_non_string(self):
        self.graph.add_nodes_from([1, 2, 3, 4])

    def test_add_edge_string(self):
        self.graph.add_edge('d', 'e')
        self.assertListEqual(sorted(self.graph.nodes()), ['d', 'e'])
        self.assertListEqual(hf.recursive_sorted(self.graph.edges()),
                             [['d', 'e']])
        self.graph.add_nodes_from(['a', 'b', 'c'])
        self.graph.add_edge('a', 'b')
        self.assertListEqual(hf.recursive_sorted(self.graph.edges()),
                             [['a', 'b'], ['d', 'e']])

    def test_add_edge_nonstring(self):
        self.graph.add_edge(1, 2)

    def test_add_edge_selfloop(self):
        self.assertRaises(ValueError, self.graph.add_edge, 'a', 'a')

    def test_add_edges_from_string(self):
        self.graph.add_edges_from([('a', 'b'), ('b', 'c')])
        self.assertListEqual(sorted(self.graph.nodes()), ['a', 'b', 'c'])
        self.assertListEqual(hf.recursive_sorted(self.graph.edges()),
                             [['a', 'b'], ['b', 'c']])
        self.graph.add_nodes_from(['d', 'e', 'f'])
        self.graph.add_edges_from([('d', 'e'), ('e', 'f')])
        self.assertListEqual(sorted(self.graph.nodes()),
                             ['a', 'b', 'c', 'd', 'e', 'f'])
        self.assertListEqual(hf.recursive_sorted(self.graph.edges()),
                             hf.recursive_sorted([('a', 'b'), ('b', 'c'),
                                                  ('d', 'e'), ('e', 'f')]))

    def test_add_edges_from_nonstring(self):
        self.graph.add_edges_from([(1, 2), (2, 3)])

    def test_add_edges_from_self_loop(self):
        self.assertRaises(ValueError, self.graph.add_edges_from,
                          [('a', 'a')])

    def test_number_of_neighbors(self):
        self.graph.add_edges_from([('a', 'b'), ('b', 'c')])
        self.assertEqual(len(self.graph.neighbors('b')), 2)

    def tearDown(self):
        del self.graph


class TestMarkovModelMethods(unittest.TestCase):
    def setUp(self):
        self.graph = MarkovModel()

    def test_add_factor_raises_error(self):
        self.graph.add_edges_from([('Alice', 'Bob'), ('Bob', 'Charles'),
                                   ('Charles', 'Debbie'), ('Debbie', 'Alice')])
        factor = Factor(['Alice', 'Bob', 'John'], [2, 2, 2], np.random.rand(8))
        self.assertRaises(ValueError, self.graph.add_factors, factor)

    def test_factor_graph(self):
        from pgmpy.models import FactorGraph

        phi1 = Factor(['Alice', 'Bob'], [3, 2], np.random.rand(6))
        phi2 = Factor(['Bob', 'Charles'], [3, 2], np.random.rand(6))
        self.graph.add_edges_from([('Alice', 'Bob'), ('Bob', 'Charles')])
        self.graph.add_factors(phi1, phi2)

        factor_graph = self.graph.to_factor_graph()
        self.assertIsInstance(factor_graph, FactorGraph)
        self.assertListEqual(sorted(factor_graph.nodes()),
                             ['Alice', 'Bob', 'Charles', 'phi_Alice_Bob',
                              'phi_Bob_Charles'])
        self.assertListEqual(hf.recursive_sorted(factor_graph.edges()),
                             [['Alice', 'phi_Alice_Bob'], ['Bob', 'phi_Alice_Bob'],
                              ['Bob', 'phi_Bob_Charles'], ['Charles', 'phi_Bob_Charles']])
        self.assertListEqual(factor_graph.get_factors(), [phi1, phi2])

    def test_factor_graph_raises_error(self):
        self.graph.add_edges_from([('Alice', 'Bob'), ('Bob', 'Charles')])
        self.assertRaises(ValueError, self.graph.to_factor_graph)

    def test_junction_tree(self):
        self.graph.add_edges_from([('a', 'b'), ('b', 'c'), ('c', 'd'),
                                   ('d', 'a')])
        phi1 = Factor(['a', 'b'], [2, 3], np.random.rand(6))
        phi2 = Factor(['b', 'c'], [3, 4], np.random.rand(12))
        phi3 = Factor(['c', 'd'], [4, 5], np.random.rand(20))
        phi4 = Factor(['d', 'a'], [5, 2], np.random.random(10))
        self.graph.add_factors(phi1, phi2, phi3, phi4)

        junction_tree = self.graph.to_junction_tree()
        self.assertListEqual(hf.recursive_sorted(junction_tree.nodes()),
                             [['a', 'b', 'd'], ['b', 'c', 'd']])
        self.assertEqual(len(junction_tree.edges()), 1)

    def test_markov_blanket(self):
        self.graph.add_edges_from([('a', 'b'), ('b', 'c')])
        self.assertListEqual(self.graph.markov_blanket('a'), ['b'])
        self.assertListEqual(sorted(self.graph.markov_blanket('b')),
                             ['a', 'c'])

    def test_local_independencies(self):
        from pgmpy.independencies import Independencies

        self.graph.add_edges_from([('a', 'b'), ('b', 'c')])
        independencies = self.graph.get_local_independecies()

        self.assertIsInstance(independencies, Independencies)
        self.assertEqual(len(independencies.get_independencies()), 2)

        string = ''
        for assertion in sorted(independencies.get_independencies(),
                                key=lambda x: list(x.event1)):
            string += str(assertion) + '\n'

        self.assertEqual(string, 'a _|_ c | b\nc _|_ a | b\n')

    def test_bayesian_model(self):
        from pgmpy.models import BayesianModel
        import networkx as nx

        self.graph.add_edges_from([('a', 'b'), ('b', 'c'), ('c', 'd'),
                                   ('d', 'a')])
        phi1 = Factor(['a', 'b'], [2, 3], np.random.rand(6))
        phi2 = Factor(['b', 'c'], [3, 4], np.random.rand(12))
        phi3 = Factor(['c', 'd'], [4, 5], np.random.rand(20))
        phi4 = Factor(['d', 'a'], [5, 2], np.random.random(10))
        self.graph.add_factors(phi1, phi2, phi3, phi4)

        bm = self.graph.to_bayesian_model()
        self.assertIsInstance(bm, BayesianModel)
        self.assertListEqual(sorted(bm.nodes()), ['a', 'b', 'c', 'd'])
        self.assertTrue(nx.is_chordal(bm.to_undirected()))

    def tearDown(self):
        del self.graph

