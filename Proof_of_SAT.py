# -*- coding: utf-8 -*-
"""
Methods to generate and solve random instances of SAT and instances of SAT that are deterministically and pseudo-randomly
generated from the solutions of previous MAX-SAT instances. This is a prototype of how a proof of work algorithm can be
derived from a relevant problem.
https://github.com/DevonFulcher/Proof-of-SAT
@author: Devon Fulcher
"""
from hashlib import sha256
import itertools
import json
import random


# Generates all possible clauses of the boolean satisfiability problem with given parameters as a
# list of clauses. The variables are represented as nonzero integers with
# negative integers representing negated variables.
def all_possible_clauses(num_variables_per_clause, num_variables_per_instance):
    positive_or_negative = itertools.product(range(2), repeat=num_variables_per_instance)
    all_possible_clauses = []
    for combination in positive_or_negative:
        literals = []
        for variable in range(num_variables_per_instance):
            if combination[variable] == 1:
                literals.append(variable + 1)
            else:
                literals.append(-(variable + 1))
        clauses = list(itertools.combinations(literals, num_variables_per_clause))
        for clause in clauses:
            if clause not in all_possible_clauses:
                all_possible_clauses.append(clause)
    num_bits_required = len(bin(len(all_possible_clauses))[2:])
    return all_possible_clauses, num_bits_required


# Returns a random instance of SAT with the given number of clauses
def random_sat(all_possible_clauses, num_clauses):
    sat_instance = []
    for _ in range(num_clauses):
        sat_instance.append(all_possible_clauses[random.randint(0, len(all_possible_clauses))])
    return sat_instance


# Solves at least 1 - 1 / 2**num_variables_per_clause fraction of the clauses of an instance of boolean satisfiability. Returns
# a list of bits corresponding to the values of each variable that satisfy the MAX-Sat instance. If randomized = True
# then this method will check variable assignments at random else it will check variable assignments with brute force
def max_sat_solver(clauses, num_variables_per_instance, randomized=True):
    if randomized:
        def variable_assignment(num_assignment_attempts):
            assignment = ()
            for _ in range(num_variables_per_instance):
                assignment += random.randint(0, 1),
            return assignment
    else:
        product = list(itertools.product(range(2), repeat=num_variables_per_instance))
        def variable_assignment(num_assignment_attempts):
            return product[num_assignment_attempts]
    max_sat_solved = False
    num_assignment_attempts = 0
    while not max_sat_solved:
        assignment = variable_assignment(num_assignment_attempts)
        num_clauses_satisfied = 0
        for clause in clauses:
            for literal in clause:
                if literal > 0:
                    if assignment[literal - 1] == 1:
                        num_clauses_satisfied += 1
                        break
                else:
                    if assignment[-literal - 1] == 0:
                        num_clauses_satisfied += 1
                        break
        num_assignment_attempts += 1
        if num_clauses_satisfied / len(clauses) >= 1 - 1 / 2**num_variables_per_clause:
            max_sat_solved = True
    return assignment, num_assignment_attempts


# Turns a list of binary digits, as representation of an assignment of variables in the
# MAX-SAT problem, into a deterministically pseudo-random instance of the SAT problem
def solution_to_sat(assignment, all_possible_clauses, num_bits_required):
    block_string = json.dumps(assignment)
    digest = sha256(block_string.encode()).hexdigest()
    # this is the bitstring that will encode the new instance of SAT
    digest_in_binary = bin(int(digest, 16))[2:].zfill(256)
    new_clauses = []
    current_binary_substring = ""
    bit_index = 0
    while bit_index < len(digest_in_binary) and len(new_clauses) <= len(all_possible_clauses):
        current_binary_substring += digest_in_binary[bit_index]
        if len(current_binary_substring) == num_bits_required:
            location_of_clause = int(current_binary_substring, 2)
            while location_of_clause >= len(all_possible_clauses):
                bit_index += 1
                if bit_index == len(digest_in_binary):
                    break
                current_binary_substring = current_binary_substring[1:] + digest_in_binary[bit_index]
                location_of_clause = int(current_binary_substring, 2)
            if location_of_clause < len(all_possible_clauses):
                new_clauses.append(all_possible_clauses[location_of_clause])
            current_binary_substring = ""
        bit_index += 1
    return new_clauses


# Replaces each variable in an instance of SAT with a boolean assignment of that variable
def assignment_in_clauses(clauses, assignment):
    assignment_in_clauses = []
    for clause in clauses:
        assignment_in_clause = []
        for literal in clause:
            if literal > 0:
                if assignment[literal - 1] == 1:
                    assignment_in_clause.append(1)
                else:
                    assignment_in_clause.append(0)
            else:
                if assignment[-literal - 1] == 1:
                    assignment_in_clause.append(0)
                else:
                    assignment_in_clause.append(1)
        assignment_in_clauses.append(assignment_in_clause)
    return assignment_in_clauses


if __name__ == "__main__":
    random.seed(1)
    num_starting_clauses = 7
    num_variables_per_instance = 7
    num_variables_per_clause = 3
    num_instances = 10
    print_display = True
    assert num_variables_per_clause >= 3
    assert num_variables_per_instance >= num_variables_per_clause
    all_possible_clauses, num_bits_required = all_possible_clauses(num_variables_per_clause, num_variables_per_instance)
    assert num_starting_clauses < len(all_possible_clauses)
    clauses = random_sat(all_possible_clauses, num_starting_clauses)
    for i in range(num_instances):
        if print_display:
            print("clauses:", clauses)
        assignment, num_assignment_attempts = max_sat_solver(clauses, num_variables_per_instance, True)
        if print_display:
            print("assignment:", assignment)
            print("num_assignment_attempts", num_assignment_attempts)
            print("assignment_in_clauses", assignment_in_clauses(clauses, assignment), "\n")
        clauses = solution_to_sat(assignment, all_possible_clauses, num_bits_required)