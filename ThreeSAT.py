# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 19:09:36 2018
@author: Devon Fulcher
"""
from hashlib import sha256
import time
import itertools
import math
import json
import random
random.seed(2)
#change from solution dict to solution bitstring

'''
generates a random instance of the boolean satisfiability problem as a 
list of tuples. The tuples are clauses. The variables are represented as nonzero integers with
negative integers representing negated variables. 
Example output with num_clauses=7, num_variables_per_instance=4, num_variables_per_clause=3:
[(2, 3, -4), (-4, 2, 4), (-4, -1, 3), (-1, 1, 1), (4, 4, -2), (4, 3, -2), (3, 4, -2)]
'''
def generate_random_sat(num_clauses=100, num_variables_per_instance=15, num_variables_per_clause=3):
    clauses = []
    for _ in range(num_clauses):
        clause = []
        clauses = random.sample(range(num_variables_per_instance), num_variables_per_clause)
        for _ in range(num_variables_per_clause):
            variable = random.randint(1, num_variables_per_instance)
            negation = random.randint(0, 1)
            if negation:
                variable = -variable
            clause = clause + (variable,)
        clauses.append(clause)
    return clauses

'''
Solves at least 1 - 1 / 2**num_variables_per_clause of the clauses of an instance of boolean satisfiability. Returns
a dictionary of the variable values used to solve the instance, the solution  in a list of
tuples of the values of the variables, and the number of attempts it took to satisfy the instance by assigning random
values to each variable
'''
def randomized_approximate_sat(clauses):
    assert len(clauses) > 0
    num_variables_per_clause = len(clauses[0])
    sat_approximated = False
    num_attempts = 0
    while not sat_approximated:
        num_attempts += 1
        solution_dict = {}
        candidate_solution = []
        for clause in clauses:
            candidate_clause = ()
            for variable in clause:
                if variable in solution_dict:
                    value = solution_dict.get(variable)
                elif -variable in solution_dict:
                    value = (solution_dict.get(-variable) + 1) % 2
                else:
                    value = random.randint(0, 1)
                    solution_dict[variable] = value
                candidate_clause = candidate_clause + (value,)
            candidate_solution.append(candidate_clause)
        num_clauses_satisfied = 0
        for values in candidate_solution:
            for value in values:
                if value == 1:
                    num_clauses_satisfied += 1
                    break
        if num_clauses_satisfied / len(clauses) >= 1 - 1 / 2**num_variables_per_clause:
            sat_approximated = True
    return solution_dict, candidate_solution, num_attempts


def brute_force_approximate_sat(clauses, num_variables_per_instance):
    assert len(clauses) > 0
    num_variables_per_clause = len(clauses[0])
    product = itertools.product(range(2), repeat=num_variables_per_instance)
    for bitstring in product:
        candidate_solution = []
        for clause in clauses:
            candidate_clause = ()
            for variable in clause:
                if variable > 0:
                    value = bitstring[variable - 1]
                else:
                    value = (bitstring[-variable - 1] + 1) % 2
                candidate_clause = candidate_clause + (value,)
            candidate_solution.append(candidate_clause)
        num_clauses_satisfied = 0
        for values in candidate_solution:
            for value in values:
                if value == 1:
                    num_clauses_satisfied += 1
                    break
        if num_clauses_satisfied / len(clauses) >= 1 - 1 / 2**num_variables_per_clause:
            solution_dict = {}
            this_variable = 1
            for i in bitstring:
                solution_dict[this_variable] = i
                this_variable += 1
            return solution_dict, candidate_solution
    return False


def dictionary_to_sat(variables_and_values, num_variables_per_clause):
    num_variables_per_instance = len(variables_and_values)
    #this formula calculates the number of bits required to encode a clause
    #the 2 comes from the fact that each variable can have 2 states, positive or negative.
    #the log2 comes from binary. It is based off the formula for combinations with repetition
    num_combinations_of_clauses = math.factorial(2 * num_variables_per_instance + num_variables_per_clause - 1) / \
                                  (math.factorial(num_variables_per_clause) *
                                   math.factorial((2 * num_variables_per_instance - 1)))
    num_bits_required = math.ceil(math.log2(num_combinations_of_clauses))
    block_string = json.dumps(variables_and_values, sort_keys=True)
    digest = sha256(block_string.encode()).hexdigest()
    digest_in_binary = bin(int(digest, 16))[2:].zfill(256)
    all_variables = []
    for i in range(num_variables_per_instance):
        all_variables.append(i + 1)
        all_variables.insert(0, -i - 1)
    all_possible_clauses = list(itertools.combinations_with_replacement(all_variables, num_variables_per_clause))
    new_clauses = []
    current_binary_subset = ""
    for i in range(len(digest_in_binary)):
        if i % num_bits_required == 0 and i != 0:
            location_of_clause = int(current_binary_subset, 2)
            if location_of_clause < len(all_possible_clauses):
                new_clauses.append(all_possible_clauses[location_of_clause])
            current_binary_subset = ""
        current_binary_subset += (digest_in_binary[i])
    return new_clauses


def print_results(solution_dict, solution_list, attempts):
    sorted_keys = sorted(list(solution_dict.keys()))
    sorted_solution_dict = []
    for i in sorted_keys:
        sorted_solution_dict.append({i: solution_dict.get(i)})
    print("solution list: ", solution_list, "\nclauses: ", clauses, "\nnum clauses: ", len(clauses),
          "\nsorted solution dict: ", sorted_solution_dict, "\nattempts", attempts)


if __name__ == "__main__":
    num_clauses = 7
    num_variables_per_instance = 4
    num_variables_per_clause = 3
    num_instances = 1000
    assert num_variables_per_instance <= num_variables_per_clause * num_clauses
    assert num_variables_per_clause >= 3
    clauses = generate_random_sat(num_clauses, num_variables_per_instance, num_variables_per_clause)
    print(brute_force_approximate_sat([(-4, 2, 2), (-1, -1, 3), (-4, 1, 3), (-3, -2, 3), (-3, 2, 3),
                                 (-4, 1, 4), (1, 1, 1), (-3, 2, 3), (-3, -1, 2), (-4, 2, 4),
                                 (-3, -3, 4), (-2, -2, 1), (-4, -2, 1), (2, 4, 4), (-3, 2, 2),
                                 (-2, -1, 1), (-1, -1, 4), (-3, -2, 4), (-3, -2, 3), (-2, -2, -2),
                                 (1, 3, 4), (-1, -1, 2), (-4, -2, -2), (-4, -1, -1), (-4, -3, 2),
                                 (2, 2, 2), (-1, -1, 3), (-1, 4, 4), (-1, 1, 2), (-4, -2, -2), (-3, 2, 2)], 4))
    # for i in range(num_instances):
    #     print("\n\n", i)
    #     if not brute_force_approximate_sat(clauses, num_variables_per_instance):
    #         print(clauses, num_variables_per_instance)
    #         input()
    #     else:
    #         solution_dict, _ = brute_force_approximate_sat(clauses, num_variables_per_instance)
    #     #print_results(solution_dict, solution_list, num_attempts)
    #     clauses = dictionary_to_sat(solution_dict, num_variables_per_clause)
