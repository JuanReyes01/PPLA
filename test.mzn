% Input parameters

int: max_makespan;
int: num_tests;
int: num_machines;
int: num_resources;

set of int: TESTS = 1..num_tests;
set of int: MACHINES = 1..num_machines;
set of int: RESOURCES = 1..num_resources;

array[TESTS] of int: processing_time;
array[TESTS] of set of MACHINES: eligible_machines;
array[TESTS] of set of RESOURCES: required_resources;

% Decision variables

array[1..num_tests] of var 1..num_machines: assigned_machine;
array[1..num_tests] of var 0..max_makespan: start_time;

var int: makespan = max([start_time[t] + processing_time[t] | t in TESTS]);

% Constraints

% Ensure tests are assigned to eligible machines and all machines have assigned tests
constraint forall(t in TESTS) (assigned_machine[t] in eligible_machines[t] \/ card(eligible_machines[t]) == 0);
constraint forall(m in MACHINES) (exists([assigned_machine[t] = m | t in TESTS]));

predicate no_overlap(var int: si, int: pi, var int: sj, int: pj) =
    si >= sj + pj \/ sj >= si + pi;

% Overlapping tests must not share resources nor machines
constraint forall(t1,t2 in TESTS where t1 < t2)
    (not no_overlap(start_time[t1], processing_time[t1], start_time[t2], processing_time[t2]) ->
    (card(required_resources[t1] intersect required_resources[t2]) = 0) /\ (assigned_machine[t1] != assigned_machine[t2]));

solve :: seq_search([
            int_search(assigned_machine, input_order, indomain_random),
            int_search(start_time, input_order, indomain_min),
        ])
      :: restart_linear(1)
      minimize makespan;

% Output

output [
    "Task assignment:\n", show(assigned_machine), "\n",
    "Task start times:\n", show(start_time), "\n",
    "Makespan: ", show(makespan), "\n"
];