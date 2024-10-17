% Input parameters

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

array[TESTS] of var MACHINES: assigned_machine;
array[TESTS] of var 0..sum(processing_time): start_time;

var int: makespan = max([start_time[t] + processing_time[t] | t in TESTS]);

% Constraints

constraint
    forall(t1, t2 in TESTS where t1 < t2) (
        % Condition for task overlap based on machine and resource usage
        ((assigned_machine[t1] = assigned_machine[t2] \/ 
          card(required_resources[t1] intersect required_resources[t2]) > 0) -> 
          no_overlap(start_time[t1], processing_time[t1], start_time[t2], processing_time[t2])
        )
    ) /\
    % Ensure tasks are assigned to eligible machines and each machine has at least one task
    forall(t in TESTS) (
        assigned_machine[t] in eligible_machines[t] \/ card(eligible_machines[t]) == 0
    ) /\
    forall(m in MACHINES) (
        exists(t in TESTS) (assigned_machine[t] = m)
    ) /\
    % Makespan definition
    makespan = max([start_time[t] + processing_time[t] | t in TESTS]);

solve :: seq_search([
            int_search(assigned_machine, smallest, indomain_random),
            int_search(start_time, first_fail, indomain_min),
        ])
      :: restart_linear(1)
    minimize makespan;

% Output

output [
    "Task assignment:\n", show(assigned_machine), "\n",
    "Task start times:\n", show(start_time), "\n",
    "% Makespan: ", show(makespan)
];
