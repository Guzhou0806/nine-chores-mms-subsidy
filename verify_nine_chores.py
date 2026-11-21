"""Verify the sharp subsidy bound for nine indivisible chores using exact arithmetic."""

import argparse
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import file_digest
from itertools import product
from math import lcm
from pathlib import Path
from time import perf_counter


NINE = 0x1ff
TARGET = Fraction(1, 24)
PAIRS = ((0, 1), (0, 2), (1, 2))


def verify(condition, context):
    if not condition:
        raise ValueError(context)


def digest(path):
    with path.open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def disjoint_partition(masks, full):
    return (len(masks) == 3 and all(type(m) is int and 0 <= m <= full for m in masks)
            and masks[0] | masks[1] | masks[2] == full
            and all(not masks[i] & masks[j] for i, j in PAIRS))


def canonical(masks):
    first = next(mask for mask in masks if mask & 1)
    return (first, *sorted(mask for mask in masks if (mask & 1) == 0))


@cache
def geometry(items=9):
    full = (1 << items) - 1
    parts = []
    for first in range(1, full+1, 2):
        rem = full ^ first
        second = rem
        while True:
            third = rem ^ second
            if second <= third:
                parts.append((first, second, third))
            if not second:
                break
            second = (second - 1) & rem
    parts.sort()
    independent_set = set()
    for owners in product(range(3), repeat=items):
        masks = [0, 0, 0]
        for item, owner in enumerate(owners):
            masks[owner] |= 1 << item
        independent_set.add(canonical(masks))
    verify(set(parts) == independent_set and len(parts) == (3281 if items == 9 else 1094), 'unordered partitions')

    prefixes = [tuple((m & ((1 << k) - 1)).bit_count() for k in range(1, items+1))
                for m in range(full+1)]
    below = [{a for a, counts in enumerate(prefixes) if all(x <= y for x, y in zip(counts, bounds))}
             for bounds in prefixes]
    incomparable = [sum(1 << b for b in range(full+1) if a not in below[b] and b not in below[a])
                    for a in range(full+1)]
    part_masks = [sum(1 << bag for bag in set(part)) for part in parts]
    edges = []
    neighbors = defaultdict(set)
    for i, (a, b, c) in enumerate(parts):
        compatible = incomparable[a] & incomparable[b] & incomparable[c]
        if not compatible:
            continue
        for j in range(i+1, len(parts)):
            if part_masks[j] & compatible == part_masks[j]:
                edges.append((i, j))
                neighbors[i].add(j)
                neighbors[j].add(i)
    triangles = [(i, j, k) for i, j in edges for k in sorted(neighbors[i] & neighbors[j]) if k > j]
    if items == 9:
        verify((len(edges), len(neighbors), len(triangles)) == (1130, 220, 91), 'graph counts')
    return parts, below, edges, triangles


def bag_gap(agent, bag):
    verify(type(agent) is int and 0 <= agent <= 2 and type(bag) is int and 0 <= bag <= NINE,
           ('agent and bag', agent, bag))
    terms = {(agent, item): 1 for item in range(9) if bag & (1 << item)}
    terms[('mu', agent)] = -1
    return terms


def negatives(terms):
    return {coordinate: -value for coordinate, value in terms.items()}


class OneRecipientAudit:
    def __init__(self, below):
        self.below = below
        self.records = Counter()
        self.row_types = Counter()
        self.tree_details = {}
        self.maximum_denominator = 1
        self.maximum_full_denominator = 1
        self.maximum_tree_depth = 0

    def row(self, claim, partitions, good, path, kind):
        row_type = claim['type']
        self.row_types[row_type] += 1
        if row_type in ('cap', 'nonnegative', 'order'):
            agent = claim['agent']
            verify(type(agent) is int and 0 <= agent < 3, claim)
            if row_type == 'order':
                item = claim['left']
                verify(type(item) is int and 0 <= item < 8, claim)
                return {(agent, item): -1, (agent, item + 1): 1}, 0
            item = claim['item']
            verify(type(item) is int and 0 <= item < 9, claim)
            capped = row_type == 'cap'
            return {(agent, item): 1 if capped else -1}, int(capped)
        if row_type in ('positive_threshold', 'tau_lower'):
            verify(Fraction(claim['threshold']) == TARGET, claim)
            if row_type == 'positive_threshold':
                verify(kind == 'tree', claim)
                return {'tau': -1, 'delta': 1}, -TARGET
            verify(kind == 'conditional', claim)
            return {'tau': -1}, -TARGET
        agent = claim.get('paid_agent') if row_type == 'one_recipient_allocation' else claim['agent']
        verify(type(agent) is int and 0 <= agent < 3, claim)
        if row_type == 'mms':
            verify(claim['bag'] in partitions[agent], claim)
            return bag_gap(agent, claim['bag']), 0
        if row_type in ('cross_good', 'cross_bad'):
            divider = claim['divider']
            verify(type(divider) is int and 0 <= divider < 3 and divider != agent, claim)
            bag = claim['bag']
            verify(bag in partitions[divider] and (bag == good[divider]) == (row_type == 'cross_good'), claim)
            gap = bag_gap(agent, bag)
            if row_type == 'cross_good':
                return gap, 0
            return negatives(gap) | {'tau': 1}, 0
        if row_type == 'one_recipient_allocation':
            allocation = claim['allocation']
            verify(disjoint_partition(allocation, NINE), claim)
            for other in range(3):
                if other == agent:
                    continue
                accepted = (*partitions[other], *(good[k] for k in range(3) if k != other))
                verify(any(allocation[other] in self.below[free] for free in accepted), claim)
            return negatives(bag_gap(agent, allocation[agent])) | {'tau': 1}, 0

        verify(kind == 'tree', claim)
        step = claim['step']
        verify(type(step) is int and 0 <= step < len(path), claim)
        allocation, choice = path[step]
        gap = bag_gap(agent, allocation[agent])
        if row_type == 'branch_strict_positive':
            verify(choice >= 3 and agent in PAIRS[choice - 3], claim)
            return negatives(gap) | {'delta': 1}, 0
        if row_type == 'branch_free':
            verify(choice < 3 and choice != agent, claim)
            return gap, 0
        verify(row_type == 'branch_single_cash' and choice == agent, claim)
        return negatives(gap) | {'tau': 1}, 0

    def identity(self, proof, goal, threshold, partitions, good, path=(), kind='root'):
        rhs = Fraction(0)
        lhs = defaultdict(Fraction)
        denominator = 1
        right_denominator = 1
        verify(bool(proof['dual']), 'empty identity')
        for term in proof['dual']:
            verify(type(term['weight']) is str, term)
            weight = Fraction(term['weight'])
            verify(weight > 0, term)
            coefficients, bound = self.row(term['meaning'], partitions, good, path, kind)
            denominator = lcm(denominator, weight.denominator, Fraction(bound).denominator)
            for coordinate, coefficient in coefficients.items():
                lhs[coordinate] += coefficient * weight
            weighted_rhs = weight * bound
            rhs += weighted_rhs
            right_denominator = lcm(right_denominator, weighted_rhs.denominator)
            self.records['positive_multipliers'] += 1
        verify({k: v for k, v in lhs.items() if v} == goal, ('coefficient identity', dict(lhs), goal))
        verify(rhs == Fraction(proof['bound']) and rhs <= threshold, ('right side', rhs, threshold))
        self.maximum_denominator = max(self.maximum_denominator, denominator)
        self.maximum_full_denominator = max(self.maximum_full_denominator, lcm(denominator, right_denominator))
        return str(rhs)

    def tree(self, root_id, proof, partitions, good):
        nodes = proof['nodes']
        verify(proof['complete'] is True and proof['remaining_nodes'] == 0 and bool(nodes), root_id)
        links = defaultdict(dict)
        for index, node in enumerate(nodes):
            verify(type(node['id']) is int and node['id'] == index, (root_id, index))
            parent, choice = node['parent'], node['child_number']
            if index == 0:
                verify(parent is None and choice is None, root_id)
                continue
            verify(type(parent) is int and 0 <= parent < index and type(choice) is int
                   and 0 <= choice < 6 and choice not in links[parent], (root_id, index, parent, choice))
            links[parent][choice] = index

        visited = set()
        results = Counter()
        stack = [(0, ())]
        while stack:
            index, path = stack.pop()
            verify(index not in visited, (root_id, index))
            visited.add(index)
            node = nodes[index]
            verify(node['path'] == [dict(allocation=bags, choice=choice) for bags, choice in path],
                   (root_id, index, 'stored path'))
            self.maximum_tree_depth = max(self.maximum_tree_depth, len(path))
            results['maximum_depth'] = max(results['maximum_depth'], len(path))
            if node['kind'] == 'leaf':
                verify(not links[index], (root_id, index, 'leaf with children'))
                try:
                    self.identity(node, {'delta': 1}, 0, partitions, good, path, 'tree')
                except ValueError as exc:
                    raise ValueError((root_id, index, 'leaf', str(exc))) from exc
                results['leaves'] += 1
            else:
                verify(node['kind'] == 'split' and set(links[index]) == set(range(6)), (root_id, index))
                bags = node['allocation']
                verify(disjoint_partition(bags, NINE), (root_id, index, bags))
                stack.extend((child, (*path, (bags, choice))) for choice, child in links[index].items())
                results['six_way_splits'] += 1
        verify(len(visited) == len(nodes), (root_id, 'unreachable nodes'))
        results['nodes'] = len(visited)
        self.tree_details[root_id] = dict(results)


def check_upper_bound(path, example):
    start = perf_counter()
    certificate = json.loads(path.read_bytes())
    verify(certificate['schema'] == 'nine-item-one-recipient-exact-v1'
           and Fraction(certificate['target']) == TARGET, 'one-recipient certificate schema')
    partitions, below, edges, triangles = geometry()
    triples = [[list(partitions[index]) for index in triangle] for triangle in triangles]
    verify(triples == certificate['triangle_partitions'], 'triangle identities')
    expected = {(i, labels) for i in range(len(triples)) for labels in product(range(3), repeat=3)}
    covered = set()
    audit = OneRecipientAudit(below)
    verify(certificate['matching_lower_bound'] == example,
           'certificate and example matrices differ')
    fixed = []
    for root in certificate['roots']:
        index = root['root_id']
        triangle = root['triangle_id']
        labels = tuple(root['good'])
        key = triangle, labels
        verify(type(index) is int and type(triangle) is int and all(type(k) is int for k in labels)
               and key in expected and key not in covered
               and index == triangle * 27 + 9 * labels[0] + 3 * labels[1] + labels[2], ('root', index, key))
        covered.add(key)
        parts = triples[triangle]
        good = [parts[agent][label] for agent, label in enumerate(labels)]
        proof = root['proof']
        kind = root['kind']
        audit.records[kind] += 1
        try:
            if kind == 'root_bound':
                audit.identity(proof, {'tau': 1}, TARGET, parts, good)
            elif kind == 'conditional':
                bags = proof['allocation']
                paid = proof['paid_agent']
                verify(Fraction(proof['threshold']) == TARGET and disjoint_partition(bags, NINE)
                       and (paid is None or type(paid) is int and 0 <= paid < 3), 'conditional context')
                proved = set()
                upper = {}
                for claim in proof['agent_proofs']:
                    agent = claim['agent']
                    verify(type(agent) is int and 0 <= agent < 3 and agent not in proved
                           and claim['bag'] == bags[agent], 'conditional agent proof')
                    proved.add(agent)
                    upper[agent] = audit.identity(claim, bag_gap(agent, bags[agent]),
                                                  TARGET if agent == paid else 0, parts, good, kind='conditional')
                verify(proved == {0, 1, 2}, 'conditional missing agent')
                fixed.append({'root': index, 'allocation_masks': bags, 'recipient': paid, 'bounds': upper})
            else:
                verify(kind == 'six_case_tree', kind)
                audit.tree(index, proof, parts, good)
        except ValueError as exc:
            raise ValueError(('one-recipient root', index, str(exc))) from exc
    verify(covered == expected, ('missing roots', len(expected - covered)))
    return {'state': 'PASS', 'certificate': path.name, 'certificate_sha256': digest(path),
            'partitions': len(partitions), 'empty_bundle_partitions': sum(0 in p for p in partitions),
            'edges': len(edges), 'triangles': len(triangles), 'roots': len(covered),
            'root_records': dict(audit.records), 'conditional_witnesses': fixed,
            'tree_details': audit.tree_details, 'tree_totals': {k: sum(t[k] for t in audit.tree_details.values())
                for k in ('nodes', 'six_way_splits', 'leaves')}, 'tree_depth': audit.maximum_tree_depth,
            'largest_common_denominator': audit.maximum_denominator, 'rows_by_type': dict(audit.row_types),
            'largest_full_common_denominator': audit.maximum_full_denominator,
            'compiled_weights': audit.records['positive_multipliers'],
            'seconds': perf_counter() - start}


def check_example(data):
    denominator, matrix = data['D'], data['A']
    verify(type(denominator) is int and denominator > 0 and len(matrix) == 3
           and all(len(row) == 9 and all(type(x) is int and 0 <= x <= denominator for x in row)
                   for row in matrix), 'example format')
    table = [[sum(cost for j, cost in enumerate(row) if mask & (1 << j)) for mask in range(512)]
             for row in matrix]
    parts, *_ = geometry()
    mms_witness = [min(parts, key=lambda p: max(row[b] for b in p)) for row in table]
    mms = [max(row[b] for b in p) for row, p in zip(table, mms_witness)]
    opt = {}
    counts = Counter()
    witnesses = {}
    for owners in product(range(3), repeat=9):
        masks = [0, 0, 0]
        for item, owner in enumerate(owners):
            masks[owner] |= 1 << item
        costs = [table[i][masks[i]] for i in range(3)]
        paid = [max(0, costs[i] - mms[i]) for i in range(3)]
        recipients = [i for i, cash in enumerate(paid) if cash]
        keys = ['sigma']
        if len(recipients) <= 1:
            keys.append('sigma_1')
            keys.extend(f'E{i+1}' for i in (recipients or range(3)))
        for key in keys:
            cash = sum(paid)
            if key not in opt or cash < opt[key]:
                opt[key] = cash
                counts[key] = 1
                witnesses[key] = {'bundles': [[j+1 for j in range(9) if mask & (1 << j)] for mask in masks],
                                  'cost_numerators': costs, 'payment_numerators': paid}
            elif cash == opt[key]:
                counts[key] += 1
    return {'common_denominator': denominator, 'mms_numerators': mms,
            'mms_witness_masks': mms_witness, 'd_numerators': [max(row) for row in matrix],
            'allocations': 3 ** 9, 'value': {k: str(Fraction(v, denominator)) for k, v in opt.items()},
            'optimal_counts': dict(counts), 'witnesses': witnesses}


def main():
    root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=root / "certificates" / "nine_chores.json")
    parser.add_argument("--example", type=Path, default=root / "examples" / "nine_chores.json")
    args = parser.parse_args()
    example = json.loads(args.example.read_bytes())
    upper = check_upper_bound(args.certificate, example)
    attainment = check_example(example)
    verify(max(attainment["d_numerators"]) == attainment["common_denominator"], "example normalization")
    verify(attainment["value"]["sigma"] == attainment["value"]["sigma_1"] == str(TARGET),
           "the example must attain both bounds")
    print(json.dumps({"status": "PASS", "upper_bound": str(TARGET), "proof": upper, "example": attainment},
                     ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
