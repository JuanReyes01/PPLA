int: num_tests;      % Number of tasks
int: num_machines;   % Number of machines
int: num_resources;  % Number of resources

array[1..num_tests] of int: durations;  % Processing time for each task
array[1..num_tests] of set of 1..num_machines: required_machines; % Required machines for each task
array[1..num_tests] of set of 1..num_resources: required_resources; % Resources required by each task

% Decision variables
array[1..num_tests] of var 1..num_machines: assigned_machine;  % Assigned machine for each task
array[1..num_tests] of var 0..: completion_time;  % Completion time for each task
array[1..num_tests] of var 0..: start_time;  % Start time for each task

% Objective: Minimize the makespan (total completion time)
var int: makespan = max([completion_time[t] | t in 1..num_tests]);

% Constraints
constraint forall(t in 1..num_tests) (
    assigned_machine[t] in required_machines[t]  % Ensure tasks are assigned to eligible machines
);

% Ensure completion times are correct
constraint forall(t in 1..num_tests) (
    completion_time[t] = start_time[t] + durations[t]
);

% No overlap: Tasks assigned to the same machine cannot overlap in time
constraint forall(i in 1..num_tests, j in 1..num_tests where i != j) (
    assigned_machine[i] = assigned_machine[j] -> 
    (start_time[i] >= completion_time[j] \/ start_time[j] >= completion_time[i])
);

% Resource constraint: No two tasks using the same resource can run in parallel
constraint forall(r in 1..num_resources) (
    forall(i, j in 1..num_tests where i != j /\ r in required_resources[i] /\ r in required_resources[j]) (
        start_time[i] >= completion_time[j] \/ start_time[j] >= completion_time[i]
    )
);

% Solve for minimum makespan
solve minimize makespan;

% Output
output [
  "Task assignment:\n",
  show(assigned_machine), "\n",
  "Task start times:\n",
  show(start_time), "\n",
  "Task completion times:\n",
  show(completion_time), "\n",
  "Makespan: \n",
  show(makespan)
];
