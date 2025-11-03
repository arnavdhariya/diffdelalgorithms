from collections import deque

denial_constraints = [
    [('t1.education', '!=', 't2.education'), ('t1.education_num', '==', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '!=', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '>', 't2.education_num')],
    [('t1.education', '==', 't2.education'), ('t1.education_num', '<', 't2.education_num')],
    [('t1.capital_gain', '>', 't2.capital_gain'), ('t1.capital_loss', '>', 't2.capital_loss')],
    [('t1.capital_gain', '<', 't2.capital_gain'), ('t1.capital_loss', '<', 't2.capital_loss')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'), ('t1.relationship', '==', 't2.relationship'), ('t1.sex', '!=', 't2.sex'), ('t1.native_country', '==', 't2.native_country')],
    [('t1.age', '==', 't2.age'), ('t1.fnlwgt', '==', 't2.fnlwgt'), ('t1.education', '==', 't2.education'), ('t1.occupation', '!=', 't2.occupation'), ('t1.race', '!=', 't2.race')],
]


def build_graph_data(denial_constraints):

    boundary_edges = []
    internal_edges = []
    boundary_cells = set()

    for dc in denial_constraints:
        attrs = {x for triple in dc for x in triple[::2]}
        t1_attrs = {a.strip("'") for a in attrs if a.startswith("t1.")}
        t2_attrs = {a.strip("'") for a in attrs if a.startswith("t2.")}

        if t1_attrs and t2_attrs:
            boundary_edges.append(attrs)
            boundary_cells.update(attrs)
        else:
            internal_edges.append(attrs)

    return boundary_edges, internal_edges, boundary_cells


# Algorithm 1
def find_explanations_alg1(internal_hypergraph, target_cell, boundary_cells, theta):
    queue = deque([(target_cell, {target_cell}, 0)])

    explanations = []

    visited = set()
    visited.add((target_cell, 0))

    while queue:
        curr_cell, path, depth = queue.popleft()

        if curr_cell in boundary_cells:
            explanations.append(path)
            continue
        # if depth >= theta:
        #     continue
        for rule in internal_hypergraph:
            if curr_cell in rule:
                for next_cell in rule:
                    if next_cell == curr_cell:
                        continue

                    # If we haven't visited this new cell at the next depth...
                    if (next_cell, depth + 1) not in visited:
                        visited.add((next_cell, depth + 1))
                        new_path = path.union({next_cell})
                        queue.append((next_cell, new_path, depth + 1))

    return explanations

boundary_edges, internal_edges, boundary_cells = build_graph_data(denial_constraints)

print(f"Total Boundary Edges: {len(boundary_edges)}")
print(f"Total Internal Edges: {len(internal_edges)}")
print(f"Internal Edges (The Hypergraph): {internal_edges}")
print(f"Total Boundary Cells: {len(boundary_cells)}")

print("-" * 20)

target = 't1.age'
max_depth = 3 # Set max search depth (theta)

print(f"Target Cell (ct): {target}")
print(f"Max Depth (theta): {max_depth}")

paths = find_explanations_alg1(internal_edges, target, boundary_cells, max_depth)

if paths:
    print(f"Found {len(paths)} explanations (paths) connecting '{target}' to the boundary:")
    for p in paths:
        print(f"  Path: {p}")
else:
    print(f"No paths found from '{target}' to the boundary within {max_depth} steps.")