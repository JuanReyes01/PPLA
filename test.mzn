int: num_tasks;      % Number of tasks
int: num_machines;   % Number of machines
int: num_resources;  % Number of resources

array[1..num_tasks] of int: processing_time;  % Processing time for each task
array[1..num_tasks] of set of 1..num_machines: eligible_machines; % Eligible machines for each task
array[1..num_tasks] of set of 1..num_resources: required_resources; % Resources required by each task

% Decision variables
array[1..num_tasks] of var 1..num_machines: assigned_machine;  % Assigned machine for each task
array[1..num_tasks] of var 0..: completion_time;  % Completion time for each task
array[1..num_tasks] of var 0..: start_time;  % Start time for each task

% Objective: Minimize the makespan (total completion time)
var int: makespan = max([completion_time[t] | t in 1..num_tasks]);

% Constraints
constraint forall(t in 1..num_tasks) (
    assigned_machine[t] in eligible_machines[t]  % Ensure tasks are assigned to eligible machines
);

% Ensure completion times are correct
constraint forall(t in 1..num_tasks) (
    completion_time[t] = start_time[t] + processing_time[t]
);

% No overlap: Tasks assigned to the same machine cannot overlap in time
constraint forall(i in 1..num_tasks, j in 1..num_tasks where i != j) (
    assigned_machine[i] = assigned_machine[j] -> 
    (start_time[i] >= completion_time[j] \/ start_time[j] >= completion_time[i])
);

% Resource constraint: No two tasks using the same resource can run in parallel
constraint forall(r in 1..num_resources) (
    forall(i, j in 1..num_tasks where i != j /\ r in required_resources[i] /\ r in required_resources[j]) (
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
