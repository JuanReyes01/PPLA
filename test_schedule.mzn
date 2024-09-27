% Existing definitions
int: num_tests;                % Number of tasks
int: num_machines;             % Number of machines
int: num_resources;            % Number of resources
array[1..num_tests] of int: durations;  % Durations of each task
array[1..num_tests] of set of int: required_machines;  % Machines eligible for each task
array[1..num_tests] of set of int: required_resources;  % Resources required for each task

% Assignment matrix: 1 if task i is assigned to machine j, 0 otherwise
array[1..num_tests, 1..num_machines] of var 0..1: assg;

% Variables for makespan, completion times, and start times
var 0..: makespan;
array[1..num_machines] of var 0..: completion_times;  % Completion times for each machine
array[1..num_tests] of var 0..: start_times;           % Start times for each task

% Resource usage matrix: 1 if task i uses resource j, 0 otherwise
array[1..num_tests, 1..num_resources] of var 0..1: resource_usage;

% Each task must be assigned to exactly one eligible machine
constraint
  forall(i in 1..num_tests) (
    sum(j in 1..num_machines where j in required_machines[i]) (assg[i,j]) = 1
  );

% Calculate start times for each task based on assigned machines
constraint
  forall(i in 1..num_tests) (
    start_times[i] = sum(j in 1..num_machines) (
      (assg[i,j] = 1) * completion_times[j]
    )
  );

% Update completion times based on assigned tasks
constraint
  forall(j in 1..num_machines) (
    completion_times[j] = sum(i in 1..num_tests where assg[i,j] = 1) (
      start_times[i] + durations[i]
    )
  );

% Makespan definition
constraint
  makespan = max(j in 1..num_machines) (completion_times[j]);

% Resource constraint: ensure no overlapping use of scarce resources
constraint
  forall(r in 1..num_resources) (
    forall(i in 1..num_tests, j in 1..num_tests where i < j) (
      resource_usage[i, r] = 1 /\ resource_usage[j, r] = 1 -> 
      (start_times[i] + durations[i] <= start_times[j] \/ 
       start_times[j] + durations[j] <= start_times[i])
    )
  );

% New machine overlapping constraint: ensure no two machines execute tasks at the same time
constraint
  forall(i in 1..num_tests, j in 1..num_tests where i < j) (
    forall(k in 1..num_machines) (
      (assg[i, k] = 1 /\ assg[j, k] = 1) -> 
      (start_times[i] + durations[i] <= start_times[j] \/ 
       start_times[j] + durations[j] <= start_times[i])
    )
  );

% Minimize makespan
solve minimize makespan;

% Find the machine index for a given task
function var int: machine_index(int: task) =
    sum(j in 1..num_machines) (assg[task, j] * j);
