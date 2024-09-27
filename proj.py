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
                if len(list(test_data[2])) == 0:
                    test_data[2] = {int(i) for i in range(1, num_machines + 1)}
                else:
                    data = set()
                    for i in test_data[2]:
                        data.add(int(i.replace('m', '')))
                    test_data[2] = data
                # Parse the resource data
                # If no resources are specified, then no resources are needed
                if len(list(test_data[3])) == 0:
                    test_data[3] = {}
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
    print(f"num_tests: {num_tests}")
    instance["num_machines"] = num_machines
    print(f"num_machines: {num_machines}")
    instance["num_resources"] = num_resources
    print(f"num_resources: {num_resources}")
    instance["durations"] = [test['duration'] for test in tests]
    print(f"durantions: {[test['duration'] for test in tests]}")
    instance["required_machines"] = [test['machines'] for test in tests]
    print(f"required_machines: {[test['machines'] for test in tests]}")
    instance["required_resources"] = [test['resources'] for test in tests]
    print(f"required_resources: {[test['resources'] for test in tests]}")


    # Solve and get the result
    result = instance.solve()
    return result


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
    #write_output(output_file, solution)

if __name__ == "__main__":
    main()

