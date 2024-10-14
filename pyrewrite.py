import sys
import minizinc

import time
import asyncio

def test(name, duration, machines, resources):
    return {
        'name': name,
        'duration': duration,
        'machines': machines,
        'resources': resources
    }

def parse_input(input_file):
    # Can be file or standard input
    if input_file:
        file = open(input_file, 'r')
    else:
        file = sys.stdin

    tests_comment = file.readline()
    num_tests = int(tests_comment.split(':')[1].strip())

    machines_comment = file.readline()
    num_machines = int(machines_comment.split(':')[1].strip())

    resources_comment = file.readline()
    num_resources = int(resources_comment.split(':')[1].strip())

    test_durations = [0] * num_tests
    test_machine_set = [set() for _ in range(num_tests)]
    test_resource_set = [set() for _ in range(num_tests)]

    for line in file:
        line = line.strip()
        if line.startswith('test'):
            args = eval(line)

            test_index = int(args['name'][1:]) - 1
            test_durations[test_index] = args['duration']

            # machines can be empty, this means all machines are eligible
            # machine names are strings, for example 'm1'
            if len(args['machines']) > 0:
                for machine in args['machines']:
                    machine_index = int(machine[1:])
                    test_machine_set[test_index].add(machine_index)

            # resources can be empty, this means no resources are required
            # resource names are strings, for example 'r1'
            if len(args['resources']) > 0:
                for resource in args['resources']:
                    resource_index = int(resource[1:])
                    test_resource_set[test_index].add(resource_index)

    nums = [num_tests, num_machines, num_resources]
    arrays = [test_durations, test_machine_set, test_resource_set]

    file.close()
    return nums, arrays


def solve_tsp(nums, arrays, duration):
    model = minizinc.Model()
    model.add_file("newnew.mzn")

    solver = minizinc.Solver.lookup("gecode")
    instance = minizinc.Instance(solver, model)

    # Load data
    num_tests, num_machines, num_resources = nums
    processing_time, eligible_machines, required_resources = arrays

    instance["num_tests"] = num_tests
    instance["num_machines"] = num_machines
    instance["num_resources"] = num_resources

    instance["processing_time"] = processing_time
    instance["eligible_machines"] = eligible_machines
    instance["required_resources"] = required_resources

    # Debug print
    print(f"Number of tests: {instance['num_tests']}", file=sys.stderr)
    print(f"Number of machines: {instance['num_machines']}", file=sys.stderr)
    print(f"Number of resources: {instance['num_resources']}\n", file=sys.stderr)
    print(f"Processing times: {instance['processing_time']}", file=sys.stderr)
    print(f"Eligible machines: {str(instance['eligible_machines']).replace('set()', '{}')}", file=sys.stderr)
    print(f"Required resources: {str(instance['required_resources']).replace('set()', '{}')}\n", file=sys.stderr)

    from datetime import timedelta
    return instance.solve_async(timeout=timedelta(seconds=duration), intermediate_solutions=True)

def write_output(output_file, solution):
    if output_file is None:
        output_file = sys.stdout

    for m in solution:
        m[2] = sorted(m[2], key=lambda x: x[1])
        print(f"machine( {m[0]}, {m[1]}, {m[2]} )", file=output_file)

async def main():
    # Allow optional input/output file arguments
    # If not provided, use standard input/output
    input_file = None
    output_file = None
    duration = 10 # seconds

    if len(sys.argv) > 3:
        print("Usage: python pyrewrite.py <input_file> <output_file | duration>")
        sys.exit(1)

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        # check if output is an integer
        if sys.argv[2].isdigit():
            duration = int(sys.argv[2])
        else:
            output_file = sys.argv[2]

    # Parse the input and get the number of machines and resources dynamically
    nums, arrays = parse_input(input_file)
    print(nums, arrays, file=sys.stderr)

    # Solve the TSP problem with the correct number of machines and resources
    solution = solve_tsp(nums, arrays, duration)

    task = asyncio.ensure_future(solution)
    start = time.time()

    while not task.done():
        elapsed = time.time() - start
        progress = min(1.0, elapsed / duration)
        bar = "#" * int(progress * 50)
        print(f"\rProgress: [{bar:<50}] {int(progress * 100)}%", end="", file=sys.stderr)
        await asyncio.sleep(0.1)
    print(file=sys.stderr)

    output = (await task)[-1]
    print(f"% Makespan :\t{output.objective}")
    solution = list()
    for m in range(1, nums[1]+1):
        solution.append([f"m{m}", 0, []])
        for i, (am, st) in enumerate(zip(output.assigned_machine, output.start_time)):
            if am == m:
                solution[m-1][1] +=1
                solution[m-1][2].append((f"t{i+1}", st))

    # Write the solution to the output file
    write_output(output_file, solution)

asyncio.run(main())
#if __name__ == "__main__":
#    main()
