def parse_input(input_file):
    tests = []
    num_machines = 0
    num_resources = 0
    with open(input_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('% Number of machines'):
                num_machines = int(line.split(':')[1].strip())
            if line.startswith('% Number of resources'):
                num_resources = int(line.split(':')[1].strip())
            if line.startswith('test'):
                test_data = eval(line.replace('test', ''))
                test_data = list(test_data)
                # Parse the machine data
                # If no machines are specified, then all machines can handle the task
                if len(set(test_data[2])) == 0:
                    test_data[2] = {int(i) for i in range(1, num_machines + 1)}
                else:
                    data = set()
                    for i in test_data[2]:
                        data.add(int(i.replace('m', '')))
                    test_data[2] = data
                # Parse the resource data
                # If no resources are specified, then no resources are needed
                if len(set(test_data[3])) == 0:
                    test_data[3] = {}
                    #test_data[3] = str(test_data[3]).replace("set()", "{}")

                else:
                    data = set()
                    for i in test_data[3]:
                        data.add(int(i.replace('r', '')))
                    test_data[3] = data
                
                
                tests.append({
                    'duration': test_data[1],
                    'machines': test_data[2],
                    'resources': test_data[3]
                })
    return tests, num_machines, num_resources

import minizinc

def solve_tsp(tests, num_machines, num_resources):
    # Define MiniZinc model
    model = minizinc.Model()
    model.add_file("test_schedule.mzn")

    # Set up MiniZinc instance
    solver = minizinc.Solver.lookup("gecode")
    instance = minizinc.Instance(solver, model)

    # Load data
    num_tests = len(tests)
    instance["num_tests"] = num_tests
    instance["num_machines"] = num_machines
    instance["num_resources"] = num_resources

    # Durations - already a list of integers
    instance["durations"] = [test['duration'] for test in tests]

    # Required machines - pass sets of machines directly
    instance["required_machines"] = [test['machines'] for test in tests]

    # Required resources - ensure that empty sets are passed correctly
    required_resources = []
    for res_set in [test['resources'] for test in tests]:
        if not res_set:
            required_resources.append(set())  # MiniZinc-compatible empty set
        else:
            required_resources.append(res_set)

    instance["required_resources"] = required_resources

    # Debug print
    print(f"Durations: {instance['durations']}")
    print(f"Required Machines: {instance['required_machines']}")
    print(f"Required Resources: {instance['required_resources']}")

    # Solve and get the result
    try:
        result = instance.solve()
        return result
    except minizinc.error.MiniZincError as e:
        print(f"Error in solving the MiniZinc model: {e}")
        raise





def write_output(output_file, solution):
    with open(output_file, 'w') as file:
        file.write(f"% Makespan: {solution['makespan']}\n")
        for machine in solution['machines']:
            file.write(f"machine({machine['id']}, {len(machine['tests'])}, {machine['tests']})\n")

import sys

def main():
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Parse the input and get the number of machines and resources dynamically
    tests, num_machines, num_resources = parse_input(input_file)
    
    # Solve the TSP problem with the correct number of machines and resources
    solution = solve_tsp(tests, num_machines, num_resources)

    # Write the solution to the output file
    # write_output(output_file, solution)

if __name__ == "__main__":
    main()

