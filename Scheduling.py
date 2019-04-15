'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy
from queue import Queue

input_file = 'input4.txt'


class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.burst_time_copy = burst_time
        self.predicted_burst_time = 5

    # for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]' % (self.id, self.arrive_time, self.burst_time))


def FCFS_scheduling(process_list):
    # store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


# Input: process_list, time_quantum (Positive Integer)
# Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    list_size, current_time, waiting_time, schedule, p_list = len(process_list), 0, 0, [], copy.deepcopy(process_list)
    queue = Queue()
    queue.put(p_list[0])
    p_list.remove(p_list[0])

    while not queue.empty():
        current_process = queue.get()
        executed_time = current_process.burst_time if current_process.burst_time < time_quantum else time_quantum
        current_process.burst_time = current_process.burst_time - executed_time
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time

        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))

        current_time = current_time + executed_time

        for process in p_list:
            if process.arrive_time <= current_time:
                queue.put(process)

        p_list = [x for x in p_list if x.arrive_time > current_time]

        if current_process.burst_time != 0:
            queue.put(current_process)
        else:
            waiting_time = waiting_time + (
                    current_time - current_process.arrive_time - current_process.burst_time_copy)

        if queue.empty() and len(p_list) > 0:
            queue.put(p_list[0])
            current_time = p_list[0].arrive_time
            p_list.remove(p_list[0])

    return schedule, float(waiting_time) / list_size


def SRTF_scheduling(process_list):
    list_size, current_time, waiting_time, schedule, list, p_list = len(process_list), 0, 0, [], [], copy.deepcopy(
        process_list)
    current_process = p_list[0]
    list.append(p_list[0])
    p_list.remove(p_list[0])

    while len(list) > 0:
        current_process.burst_time = current_process.burst_time - 1
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time

        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))

        current_time += 1

        if current_process.burst_time == 0:
            list.remove(current_process)
            waiting_time = waiting_time + (
                    current_time - current_process.arrive_time - current_process.burst_time_copy)

        for process in p_list:
            if process.arrive_time <= current_time:
                list.append(process)

        if len(p_list) > 0 and len(list) == 0:
            current_time = p_list[0].arrive_time
            list.append(p_list[0])

        p_list = [x for x in p_list if x.arrive_time > current_time]

        if len(list) > 0:
            current_process = min(list, key=lambda p: p.burst_time)

    return schedule, float(waiting_time) / list_size


def SJF_scheduling(process_list, alpha):
    list_size, current_time, waiting_time, schedule, list, p_list = len(process_list), 0, 0, [], [], copy.deepcopy(
        process_list)
    list.append(p_list[0])
    p_list.remove(p_list[0])
    history = dict()

    while len(list) > 0:
        list = sorted(list, key=lambda p: p.predicted_burst_time)
        current_process = list.pop(0)

        # If the process does not start from 0
        if current_time < current_process.arrive_time:
            current_time = current_process.arrive_time

        if len(schedule) == 0 or schedule[len(schedule) - 1][1] != current_process.id:
            schedule.append((current_time, current_process.id))

        current_time += current_process.burst_time
        current_process.burst_time = 0

        last_predicted_burst_time = history[
            current_process.id] if current_process.id in history else current_process.predicted_burst_time
        predicted_burst_time = (alpha * current_process.burst_time_copy) + ((1 - alpha) * last_predicted_burst_time)
        history[current_process.id] = predicted_burst_time

        waiting_time = waiting_time + (current_time - current_process.arrive_time - current_process.burst_time_copy)

        for process in p_list:
            if process.arrive_time <= current_time:
                if process.id in history:
                    process.predicted_burst_time = history[process.id]
                list.append(process)

        if len(p_list) > 0 and len(list) == 0:
            current_time = p_list[0].arrive_time
            list.append(p_list[0])

        p_list = [x for x in p_list if x.arrive_time > current_time]

    return schedule, float(waiting_time) / list_size


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array) != 3):
                print("wrong input format")
                exit()
            result.append(Process(int(array[0]), int(array[1]), int(array[2])))
    return result


def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n' % avg_waiting_time)


def main(argv):
    process_list = read_input()
    print("printing input ----")
    for process in process_list:
        print(process)

    print("\nsimulating FCFS ----")
    # print("Check output file FCFS.txt")
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)
    print("average waiting time %.2f" % FCFS_avg_waiting_time)

    print("\nsimulating RR ----")
    # print("Check output file RR.txt")
    RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum=4)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time)

    solution = [[], float('inf'), 0.0]
    for i in range(1, 20):
        RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum=i)
    if RR_avg_waiting_time < solution[1]:
        solution[0], solution[1], solution[2] = RR_schedule, RR_avg_waiting_time, i
    print("Optimal alpha: %.1f, average waiting time: %.2f" % (solution[2], solution[1]))

    print("\nsimulating SRTF ----")
    # print("Check output file SRTF.txt")
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)
    print("average waiting time %.2f" % SRTF_avg_waiting_time)

    print("\nsimulating SJF ----")
    # print("Check output file SJF.txt")
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha=0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time)

    solution = [[], float('inf'), 0.0]
    for i in range(1, 101):
        alpha = i / 100
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha=alpha)
    if SJF_avg_waiting_time < solution[1]:
        solution[0], solution[1], solution[2] = SJF_schedule, SJF_avg_waiting_time, alpha
    print("Optimal alpha: %.1f, average waiting time: %.2f" % (solution[2], solution[1]))


if __name__ == '__main__':
    main(sys.argv[1:])