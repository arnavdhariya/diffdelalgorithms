from collections import deque, defaultdict
import sys


# --- Your Denial Constraints ---
denial_constraints = [
    [('t1.education', '!=', 't2.education'), ('t1.education_num', '==', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '!=', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '>', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '<', 't2.education_num')],
    [('t1.capital_gain', '>', 't2.capital_gain'), ('t1.capital_loss', '>', 't2.capital_loss')],
    [('t1.capital_gain', '<', 't2.capital_gain'), ('t1.capital_loss', '<', 't2.capital_loss')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'),
     ('t1.relationship', '==', 't2.relationship'), ('t1.sex', '!=', 't2.sex'),
     ('t1.native_country', '==', 't2.native_country')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'),
     ('t1.education', '==', 't2.education'), ('t1.occupation', '!=', 't2.occupation'),
     ('t1.race', '!=', 't2.race')],
]


# --- Hypergraph Data Structures ---

class Hyperedge:
    """
    Represents a single dependency rule, r: Tail(r) -> Head(r).
    """

    def __init__(self, tail, head):
        # We only care about 't1' attributes for the user's graph
        self.tail = frozenset(t.replace('t1.', '') for t in tail)
        self.head = frozenset(h.replace('t1.', '') for h in head)

    # def __repr__(self):
    #     return f"{set(self.tail)} -> {set(self.head)}"


class Hypergraph:
    """
    Represents the User Dependency Hypergraph.
    Contains all rules and helper methods for traversal.
    """

    def __init__(self):
        self.rules = []
        self.all_cells = set()
        self._rules_deriving_cell = defaultdict(list)
        self._rules_with_cell_in_tail = defaultdict(list)
        self._leafs = None

    def build_from_dcs(self, dcs):
        """
        Parses the denial constraints to build the hypergraph.

        Logic: A DC involving {A, B, C} implies 3 rules:
        {A, B} -> {C}
        {A, C} -> {B}
        {B, C} -> {A}
        """
        for dc in dcs:
            # 1. Find all 't1' attributes in this constraint
            t1_attrs = set()
            for pred in dc:
                for item in pred:
                    if isinstance(item, str) and item.startswith('t1.'):
                        t1_attrs.add(item)

            self.all_cells.update(t.replace('t1.', '') for t in t1_attrs)

            # 2. Create permutation rules (if 2+ attrs)
            if len(t1_attrs) < 2:
                continue

            attrs_list = list(t1_attrs)
            for i in range(len(attrs_list)):
                head = {attrs_list[i]}
                tail = set(attrs_list[:i] + attrs_list[i + 1:])

                rule = Hyperedge(tail = tail, head = head)
                self.add_rule(rule)

        print(f"Built hypergraph with {len(self.rules)} rules from {len(dcs)} DCs.")

    def add_rule(self, rule):
        self.rules.append(rule)
        for h in rule.head:
            self._rules_deriving_cell[h].append(rule)
        for t in rule.tail:
            self._rules_with_cell_in_tail[t].append(rule)

    def get_leafs(self):
        """
        Returns all cells that are never in the Head of any rule.
        These are the "leafs" from Algorithm 2.
        """
        if self._leafs is None:
            derived_cells = set(self._rules_deriving_cell.keys())
            self._leafs = self.all_cells - derived_cells
        return self._leafs

    def get_rules_with_cell_in_head(self, cell):
        """Returns all rules 𝛿− where cell ∈ Head(𝛿−)"""
        return self._rules_deriving_cell.get(cell, [])

    def get_rules_with_cell_in_tail(self, cell):
        """Returns all rules 𝛿− where cell ∈ Tail(𝛿−)"""
        return self._rules_with_cell_in_tail.get(cell, [])


# --- Algorithm 2 (OptPath) Implementation ---

def calculate_costs(graph: Hypergraph) -> dict:
    """
    Implements Algorithm 2, lines 2-13.

    This is a backward pass (reverse topological sort) from the leafs
    to calculate the "cheapest path cost" for every node.

    Cost(attf) = 1 (for itself) + MIN(cost of cheapest tail child)
    """
    print("\n--- Part 1: Calculating Costs (Lines 2-13) ---")
    costs = {}

    # Initialize costs for all nodes
    for cell in graph.all_cells:
        costs[cell] = float('inf')  # Cost unknown

    # Queue for reverse topological sort
    queue = deque()

    # 1. Initialize leafs (Line 2)
    for leaf in graph.get_leafs():
        costs[leaf] = 1  # Cost(leaf) = 1 (Line 7)
        queue.append(leaf)

    print(f"Found {len(graph.get_leafs())} leafs: {graph.get_leafs()}")

    # 2. Perform backward traversal
    seen_in_queue = set(graph.get_leafs())

    while queue:
        cell = queue.popleft()  # This is 'attf'

        # 3. Find all rules where 'cell' is in the TAIL
        # (This implements the traversal from Line 13)
        for rule in graph.get_rules_with_cell_in_tail(cell):

            # 4. Check all parents (Head cells) of this rule
            for parent_cell in rule.head:
                if parent_cell in seen_in_queue:
                    continue  # Already processed or in queue

                # Check if all children (tail) of this rule have known costs
                all_children_costs_known = True
                for tail_cell in rule.tail:
                    if costs[tail_cell] == float('inf'):
                        all_children_costs_known = False
                        break

                # If all children have costs, we can calculate cost for parent
                if all_children_costs_known:
                    # Find cheapest tail cost for *this specific rule*
                    min_tail_cost = min(costs[t] for t in rule.tail)

                    # Update parent cost (Line 11)
                    # The cost is 1 (for itself) + cost of cheapest path below it
                    # We take the MIN over all rules that can derive this parent
                    new_cost = 1 + min_tail_cost
                    costs[parent_cell] = min(costs[parent_cell], new_cost)

                    # Add parent to queue to continue traversal
                    if parent_cell not in seen_in_queue:
                        seen_in_queue.add(parent_cell)
                        queue.append(parent_cell)

    print("Finished cost calculation.")
    return costs


def find_optimal_path(graph: Hypergraph, target_cell: str, costs: dict) -> set:
    """
    Implements Algorithm 2, lines 14-24.

    This is a forward pass from the target cell, which greedily
    follows the path of the "cheapest child" (using the pre-computed costs).
    """
    print(f"\n--- Part 2: Finding Optimal Path (Lines 14-24) ---")
    print(f"Target cell: {target_cell}")

    T = {target_cell}  # Deletion set (Line 14)
    Q = deque([target_cell])  # Traversal queue (Line 14)
    S = set()  # Seen cells (Line 14)

    while Q:
        attf = Q.popleft()  # (Line 16)

        if attf in S:  # (Line 17)
            continue
        S.add(attf)  # (Line 18)

        # Find all rules that *derive* this cell (Line 18-20)
        rules_deriving_attf = graph.get_rules_with_cell_in_head(attf)

        if not rules_deriving_attf:
            print(f"  -> Path ends at '{attf}' (it's a leaf or has no rules)")
            continue

        # Find the single cheapest child across all rules
        cheapest_child = None
        min_cost = float('inf')

        for rule in rules_deriving_attf:
            if not rule.tail: continue  # Should not happen, but safe

            # Find the cheapest child *in this rule's tail* (Line 21)
            for tail_cell in rule.tail:
                if costs[tail_cell] < min_cost:
                    min_cost = costs[tail_cell]
                    cheapest_child = tail_cell

        if cheapest_child:
            print(
                f"  -> Traversing from '{attf}' to cheapest child '{cheapest_child}' (cost {min_cost})")
            T.add(cheapest_child)  # (Line 22)
            Q.append(cheapest_child)  # (Line 23)
        else:
            print(f"  -> Path ends at '{attf}' (no valid children)")

    return T


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Build the hypergraph from your DCs
    graph = Hypergraph()
    graph.build_from_dcs(denial_constraints)

    # 2. Specify a target cell to delete
    # (Must be one of the attributes from your constraints)
    target = "education"

    if target not in graph.all_cells:
        print(f"Error: Target cell '{target}' not found in any constraints.")
        print(f"Available cells: {graph.all_cells}")
        sys.exit()

    # 3. Run Part 1 of Algorithm 2
    costs = calculate_costs(graph)

    # 4. Run Part 2 of Algorithm 2
    deletion_set = find_optimal_path(graph, target, costs)

    print("\n--- FINAL RESULTS ---")
    print(f"Target: {target}")
    print(f"Final Deletion Set (T): {deletion_set}")
    print(f"Total cells deleted: {len(deletion_set)}")
