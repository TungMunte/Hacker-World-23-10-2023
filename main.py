"""
This is a module of the application that concerns itself with Data, Operations,
Node, Tree and Utils classes. It also contains the main function that runs the
application.
:const NUMBER_OF_TREES_TO_GENERATE: number of trees to generate
:const NUMBER_OF_TREES_TO_STORE: number of trees to store
:const RESULTS_FILE: path to the results CSV file
:const GROUND_TRUTH_FILE: path to the ground truth CSV file
:cls Data: class for all types of data: input CSVs, best trees generated, etc.
:cls Operations: class for all mathematical operations that tree nodes can be
                    randomly chosen from
:cls Node: class for tree node that stores value, operation and children list
:cls Tree: class for tree that stores root node and max_levels
:cls Utils: class for utility functions
:func main: main function that runs the application
"""

import functools
import operator
import os
import random
from enum import Enum
import pandas as pd
import numpy as np
from typing import List, Union, ForwardRef

NUMBER_OF_TREES_TO_GENERATE = 10
NUMBER_OF_TREES_TO_STORE = 5

RESULTS_FILE = 'input/train_algo-results.csv'
GROUND_TRUTH_FILE = 'input/train_ground-truth.csv'


class Data:
    """
    Class for all types of data: input CSVs, best trees generated, etc. Best
    trees generated may be a priority queue (ordered by tree's score).
    :attr results_df: str representing the path to the results CSV file
    :attr ground_truth_df: str representing the path to the ground truth CSV
                            file
    :meth __init__(res_file, gnd_file): constructor for Data class
    :meth read_csv_files: reads the CSV files and stores them inside the class
                            attributes
    """
    def __init__(self, res_file: str, gnd_file: str) -> None:
        """
        Constructor for Data class.
        :param res_file: str representing the path to the results CSV file
        :param gnd_file: str representing the path to the ground truth CSV file
        :return: None
        """
        self.results_df = None
        self.ground_truth_df = None
        self.read_csv_files(res_file, gnd_file)

    def read_csv_files(self, res_file: str, gnd_file: str) -> None:
        """
        Reads the CSV files and stores them inside the class attributes.
        :param res_file: str representing the path to the results CSV file
        :param gnd_file: str representing the path to the ground truth CSV file
        :return: None
        """
        self.results_df = pd.read_csv(res_file)
        self.ground_truth_df = pd.read_csv(gnd_file)


class Operations(Enum):
    """
    Class for all mathematical operations that tree nodes can be randomly chosen
    from.
    :const MIN: str representing the minimum operation
    :const MAX: str representing the maximum operation
    :const ARITHMETIC_MEAN: str representing the arithmetic mean operation
    :const GEOMETRIC_MEAN: str representing the geometric mean operation
    :const WEIGHTED_MEAN: str representing the weighted mean operation
    :const MEDIAN: str representing the median operation
    :const IF_ELSE: str representing the if-else operation
    """
    MIN = 'min'
    MAX = 'max'
    ARITHMETIC_MEAN = 'mean'
    GEOMETRIC_MEAN = 'geomean'
    WEIGHTED_MEAN = 'weightedmean'
    MEDIAN = 'median'
    IF_ELSE = 'ifelse'
    # self.CUSTOM_ARITHMETIC = 'custom_arithmetic'


class Node:
    """
    Class for tree node that stores value, operation and children list.
    :attr value: Union[None, np.float64] representing the threshold, for leaves,
                    or the computed result, for other nodes
    :attr operation: Union[None, Operations] containing None, for leaves, or a
                     randomly chosen operation, for other nodes
    :attr children: Union[None, List['Node']] representing the node's children
                    list
    :meth __init__(value, operation, children): constructor for Node class
    """
    def __init__(self, value: Union[None, np.float64] = None, operation: Union[None, Operations] = None, children: Union[None, List[ForwardRef('Node')]] = None) -> None:
        """
        :attr value: Union[None, np.float64] representing the threshold, for
                        leaves, or the computed result, for other nodes
        :attr operation: Union[None, Operations] containing None, for leaves,
                            or a randomly chosen operation, for other nodes
        :attr children: Union[None, List['Node']] representing the node's
                        children list
        """
        self.value = value
        self.operation = operation
        self.children = children or []


class Tree:
    """
    Class for tree that stores root node and max_levels.
    :attr root: Node representing the root node of the tree
    :attr max_levels: int representing the maximum number of levels that the
                        tree can have
    :meth __init__(thresholds): constructor for Tree class
    :meth _random_tree(max_levels, thresholds): generate a random tree
    :meth _evaluate_tree(node): evaluate the tree
    :meth print_tree(): print the tree
    :meth _print_tree(node, level): print the tree recursively
    """
    def __init__(self, thresholds: pd.DataFrame) -> None:
        """
        Constructor for Tree class.
        :param thresholds: pd.DataFrame object containing the thresholds
        :return: None
        """
        self.max_levels = random.randint(3, 7)
        self.root = self._random_tree(self.max_levels, thresholds)
        self._evaluate_tree(self.root)

    def _random_tree(self, max_levels: int, thresholds: pd.DataFrame) -> Node:
        """
        Generate a random tree.
        :param max_levels: int representing the maximum number of levels that
                            the tree can have
        :param thresholds: pd.DataFrame object containing the thresholds
        :return: Node object representing the root node of the tree
        """
        if max_levels == 0:
            value = random.choice(thresholds.iloc[0])
            return Node(value=value)

        operation = random.choice(list(Operations))
        num_children = random.randint(2, 10)
        children = [self._random_tree(max_levels - 1, thresholds) for _ in range(num_children)]

        return Node(operation=operation, children=children)

    def _evaluate_tree(self, node: Node) -> np.float64:
        """
        Evaluate the tree.
        :param node: Node object representing the root node of the tree
        :return: np.float64 representing the computed result
        """
        if not node.children:
            return node.value

        child_values = [self._evaluate_tree(child) for child in node.children]

        if node.operation == Operations.MIN:
            node.value = min(child_values)

        elif node.operation == Operations.MAX:
            node.value = max(child_values)

        elif node.operation == Operations.ARITHMETIC_MEAN:
            node.value = sum(child_values) / len(child_values)

        elif node.operation == Operations.GEOMETRIC_MEAN:
            node.value = (functools.reduce(operator.mul, child_values)) ** (1 / len(child_values))

        elif node.operation == Operations.WEIGHTED_MEAN:
            weights = random.choices(range(2, 11), k=len(child_values))
            node.value = sum(val * weight for val, weight in zip(child_values, weights)) / sum(weights)

        elif node.operation == Operations.MEDIAN:
            node.value = sorted(child_values)[len(child_values) // 2]

        elif node.operation == Operations.IF_ELSE:
            # Determine the number of conditions based on the assumption that
            # child values are organized in pairs
            num_conditions = len(child_values) // 2

            # Check if there is at least one condition-outcome pair
            if num_conditions > 0:

                # Pair conditions and outcomes for iteration using zip
                condition_outcome_pairs = zip(child_values[:num_conditions], child_values[num_conditions:])

                # Iterate through the condition-outcome pairs and assign outcome
                # to node value if condition is True
                for condition, outcome in condition_outcome_pairs:
                    if condition:
                        node.value = outcome
                        break

        # elif node.operation == 'custom_arithmetic':
        #     available_operations = ['x^2', '|x-0.5|', 'x+0.5', '2x', '0.5x', 'x*y', 'x+y', '|x-y|', 'x^y']
        #     operation = random.choice(available_operations)
        #     node.value = self._apply_custom_arithmetic(operation, child_values)

        return node.value

    def print_tree(self) -> None:
        """
        Print the tree.
        :return: None
        """
        self._print_tree(self.root)

    def _print_tree(self, node: Node, level: int = 0) -> None:
        """
        Print the tree recursively.
        :param node: Node object representing the root node of the tree that is
                        being printed recursively
        :param level: int representing the current level of the tree
        :return: None
        """
        if not node.children:
            print(" " * (4 * level) + str(node.value))
        else:
            print(" " * (4 * level) + str(node.operation))
            for child in node.children:
                self._print_tree(child, level + 1)


class Utils:
    """
    Class for utility functions.
    :meth create_human_readable_inputs(data): create human readable inputs
    """
    @staticmethod
    def create_human_readable_inputs(data: Data) -> None:
        """
        Create human readable inputs.
        :param data: Data object containing the results and ground truth CSVs
        :return: None
        """
        if os.stat("human_readable_input/results.txt").st_size == 0:
            with open('human_readable_input/results.txt', 'w+') as writer:
                writer.write(data.results_df.to_string())

        if os.stat("human_readable_input/ground-truth.txt").st_size == 0:
            with open('human_readable_input/train_ground-truth.txt', 'w+') as writer:
                writer.write(data.ground_truth_df.to_string())


def main() -> None:
    """
    Main function that runs the application.
    :return: None
    """
    # When running from the command-line
    # _, results_file, ground_truth_file = sys.argv

    data = Data(RESULTS_FILE, GROUND_TRUTH_FILE)
    Utils.create_human_readable_inputs(data)

    top_trees = []
    for _ in range(NUMBER_OF_TREES_TO_GENERATE):
        tree = Tree(data.results_df)
        if not top_trees or (tree.root.value is not None and
                             (t.root.value is None or tree.root.value >= t.root.value for t in top_trees)):
            top_trees.append(tree)
            if len(top_trees) > NUMBER_OF_TREES_TO_STORE:
                top_trees.remove(min(top_trees, key=lambda t: t.root.value))

    for i, tree in enumerate(top_trees):
        print(f"Tree {i + 1}:")
        tree.print_tree()


if __name__ == "__main__":
    main()
