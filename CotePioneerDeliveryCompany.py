# =============================================================================
#  Pioneer Delivery Company - Algorithm Portfolio, Part I: Greedy Algorithms
#  CS 413 - Analysis of Algorithms
#  Author: Jeremiah Cote
#
#  Task A: Max number of deliveries ONE driver can do      (interval scheduling)
#  Task B: Min number of drivers to do EVERY delivery      (interval partitioning)
#  Task C: Min number of deliveries we must REJECT          (LeetCode 435)
#  Task D: Counterexample showing a greedy strategy fails  (see README.md)
#
#  How to run:
#      python CotePioneerDeliveryCompany.py                  <- uses default file
#      python CotePioneerDeliveryCompany.py DeliveryOrders.txt
#
#  Every delivery is stored as a tuple:  (deliveryId, startTime, finishTime)
#      index 0 -> deliveryId   e.g. "D01"
#      index 1 -> startTime    e.g. 10
#      index 2 -> finishTime   e.g. 13
# =============================================================================

import os
import sys
import heapq                        # Python's built-in min-heap (used in Task B)
from itertools import permutations  # only used to brute-force check Task D

# If no file is given on the command line, use DeliveryOrders.txt from the
# same folder as this script (so it works on any computer).
DEFAULT_FILENAME = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "DeliveryOrders.txt")


# -----------------------------------------------------------------------------
#  Reading the input file
# -----------------------------------------------------------------------------
def read_deliveries(filename):
    """
    Read delivery requests from a text file.

    File format: one delivery per line, three values separated by spaces:
        <id> <start_time> <finish_time>
    Example line:
        D01 10 13

    Returns a list of tuples: [(id, start, finish), ...]
    """
    deliveryData = []

    with open(filename, "r") as file:
        for line in file:
            # Skip blank lines (e.g. an empty line at the end of the file)
            if not line.strip():
                continue

            # Split "D01 10 13" into the three pieces
            deliveryId, startTime, finishTime = line.split()

            # Store times as integers so we can compare them numerically
            deliveryData.append((
                deliveryId,
                int(startTime),
                int(finishTime),
            ))

    return deliveryData


# -----------------------------------------------------------------------------
#  TASK A - Maximum deliveries for one driver
# -----------------------------------------------------------------------------
def max_deliveries_one_driver(deliveries):
    """
    Greedy algorithm (Earliest Finish Time first).

    Greedy choice: out of all deliveries that do not overlap what we've already
    picked, always take the one that FINISHES EARLIEST. Finishing early leaves
    the driver as much free time as possible for the rest of the day.

    Steps:
        1. Sort deliveries by finish time            -> O(n log n)
        2. Walk through them once, keeping track of when the driver is
           next free (lastFinish). Take a delivery if it starts at or after
           lastFinish.                               -> O(n)
    Total: O(n log n)

    Returns the list of selected deliveries.
    """
    # Step 1: sort by finish time (index 2). Ties broken by start time (index 1)
    # just so the output is predictable - it doesn't affect correctness.
    sortedByFinish = sorted(deliveries, key=lambda d: (d[2], d[1]))

    selected = []
    # The driver starts the day free. -infinity means "any start time is OK".
    lastFinish = float("-inf")

    # Step 2: one pass through the sorted list
    for delivery in sortedByFinish:
        deliveryId, startTime, finishTime = delivery

        # Compatible if it starts at or after the last chosen delivery ends.
        # We use >= (not >) because the assignment says a driver CAN finish
        # one delivery at time t and start the next one at time t.
        if startTime >= lastFinish:
            selected.append(delivery)
            lastFinish = finishTime   # driver is now busy until this time

        # Otherwise it overlaps something we already took -> skip it

    return selected


# -----------------------------------------------------------------------------
#  TASK B - Minimum number of drivers to complete every delivery
# -----------------------------------------------------------------------------
def min_drivers(deliveries):
    """
    Greedy algorithm using a priority queue (min-heap).

    Idea: process deliveries in order of START time. Keep a min-heap holding
    one entry per driver: (time that driver becomes free, driver number).
    The top of the heap is always the driver who frees up the EARLIEST.

    For each delivery:
        - If the earliest-free driver is free by the time this delivery
          starts, give it to that driver (reuse them).
        - Otherwise EVERY driver is busy right now, so hire a new driver.

    Steps:
        1. Sort by start time                              -> O(n log n)
        2. For each delivery, one heap peek + one push/pop -> O(log n) each
    Total: O(n log n)

    Returns a list of driver schedules, e.g.
        [ [D02, D05, ...],   <- driver 1's deliveries
          [D04, ...],        <- driver 2's deliveries
          ... ]
    The number of drivers is just len(result).
    """
    # Step 1: sort by start time (index 1). Ties broken by finish time.
    sortedByStart = sorted(deliveries, key=lambda d: (d[1], d[2]))

    # driverSchedules[k] = list of deliveries given to driver k (0-based)
    driverSchedules = []

    # The min-heap. Each entry is a tuple (freeAtTime, driverIndex).
    # heapq compares tuples element by element, so the driver with the
    # smallest freeAtTime is always at freeDrivers[0].
    freeDrivers = []

    for delivery in sortedByStart:
        deliveryId, startTime, finishTime = delivery

        # Peek at the driver who becomes free soonest (if we have any drivers).
        # Again <= because finishing at t and starting at t is allowed.
        if freeDrivers and freeDrivers[0][0] <= startTime:
            # --- Reuse an existing driver ---
            # heapreplace = pop the smallest entry, then push the new one,
            # in a single O(log n) operation.
            freeAt, driverIndex = freeDrivers[0]
            heapq.heapreplace(freeDrivers, (finishTime, driverIndex))
            driverSchedules[driverIndex].append(delivery)
        else:
            # --- Every current driver is still busy: add a new driver ---
            driverIndex = len(driverSchedules)       # next driver number
            driverSchedules.append([delivery])       # their first delivery
            heapq.heappush(freeDrivers, (finishTime, driverIndex))

    return driverSchedules


# -----------------------------------------------------------------------------
#  TASK C - Minimum number of deliveries to reject (one driver)
# -----------------------------------------------------------------------------
def min_rejected(deliveries):
    """
    If we keep the LARGEST possible set of compatible deliveries (Task A),
    then we reject the SMALLEST possible number. So:

        rejected = n - k     where k = answer from Task A

    Running time is the same as Task A: O(n log n).

    Returns (number rejected, list of rejected deliveries).
    """
    kept = max_deliveries_one_driver(deliveries)

    # Use a set of kept IDs so each "is this kept?" check is O(1)
    keptIds = set(d[0] for d in kept)
    rejected = [d for d in deliveries if d[0] not in keptIds]

    return len(deliveries) - len(kept), rejected


# -----------------------------------------------------------------------------
#  TASK D - Counterexample check (written answer is in README.md)
# -----------------------------------------------------------------------------
def schedule_value(jobs, slots):
    """
    Value of a schedule for Task D.
    jobs  = list of (name, readyTime, profit)
    slots = list of time slots, slots[i] is the slot for jobs[i]
    Value of one job = profit / (1 + delay), where delay = slot - readyTime
    """
    total = 0
    for (name, ready, profit), slot in zip(jobs, slots):
        delay = slot - ready
        total += profit / (1 + delay)
    return total


def place_in_order(order):
    """
    Put jobs into time slots one at a time, in the given order.
    Each job goes in the earliest FREE slot at or after its ready time.
    Returns a dict {jobName: slot}.
    """
    usedSlots = set()
    assignment = {}
    for name, ready, profit in order:
        slot = ready
        while slot in usedSlots:      # move right until we find a free slot
            slot += 1
        usedSlots.add(slot)
        assignment[name] = slot
    return assignment


def greedy_g(jobs):
    """
    The manager's greedy strategy G:
    take jobs in DECREASING profit order, each in its earliest free slot.
    """
    return place_in_order(sorted(jobs, key=lambda j: -j[2]))


def best_schedule_brute_force(jobs):
    """
    Try every possible ordering of the jobs (fine for tiny examples only)
    and return (best value, {jobName: slot}). Used to show that G is not
    optimal on our counterexample.
    """
    bestValue = float("-inf")
    bestAssignment = None
    for order in permutations(jobs):
        assignment = place_in_order(order)
        value = schedule_value(jobs, [assignment[j[0]] for j in jobs])
        if value > bestValue:
            bestValue, bestAssignment = value, assignment
    return bestValue, bestAssignment


def run_task_d():
    """Print the Task D counterexample: greedy G vs. a better schedule."""
    # (name, readyTime R, profit P)  - all profits distinct, as required
    jobs = [("A", 0, 10), ("B", 0, 6), ("C", 1, 5)]

    print("=" * 60)
    print("TASK D - Counterexample to greedy strategy G")
    print("=" * 60)
    for name, ready, profit in jobs:
        print(f"  Delivery {name}: R = {ready}, P = {profit}")

    greedy = greedy_g(jobs)
    greedyValue = schedule_value(jobs, [greedy[j[0]] for j in jobs])
    print("\n  Greedy G schedule:", greedy, f"-> V(G) = {greedyValue:.4f}")

    bestValue, best = best_schedule_brute_force(jobs)
    print("  Best schedule S:  ", best, f"-> V(S) = {bestValue:.4f}")

    if bestValue > greedyValue:
        print("  V(S) > V(G), so greedy G is NOT always optimal.")
    print()


# -----------------------------------------------------------------------------
#  Printing helpers
# -----------------------------------------------------------------------------
def print_task_a(deliveries):
    selected = max_deliveries_one_driver(deliveries)
    print("Task A - Maximum deliveries for one driver")
    for deliveryId, startTime, finishTime in selected:
        print(f"  {deliveryId:<5} start {startTime:>3}   finish {finishTime:>3}")
    print(f"  Total deliveries completed: {len(selected)}\n")


def print_task_b(deliveries):
    schedules = min_drivers(deliveries)
    print("Task B - Minimum number of drivers")
    for i, schedule in enumerate(schedules, start=1):
        ids = " ".join(d[0] for d in schedule)
        print(f"  Driver {i}: {ids}")
    print(f"  Minimum drivers required: {len(schedules)}\n")


def print_task_c(deliveries):
    count, rejected = min_rejected(deliveries)
    print("Task C - Minimum deliveries to reject")
    if rejected:
        print("  Rejected:", " ".join(d[0] for d in rejected))
    print(f"  Minimum rejected: {count}\n")


# -----------------------------------------------------------------------------
#  Safety check (used by the tests to prove the answers are VALID,
#  not just the right size)
# -----------------------------------------------------------------------------
def is_compatible(schedule):
    """True if no two deliveries in this schedule overlap."""
    ordered = sorted(schedule, key=lambda d: d[1])   # sort by start time
    for earlier, later in zip(ordered, ordered[1:]):
        if later[1] < earlier[2]:     # next one starts before previous ends
            return False
    return True


# -----------------------------------------------------------------------------
#  Required test cases from the assignment
# -----------------------------------------------------------------------------
def make_deliveries(intervals):
    """Turn [(1,3), (3,5)] into [("T1",1,3), ("T2",3,5)] so they have IDs."""
    return [(f"T{i}", s, f) for i, (s, f) in enumerate(intervals, start=1)]


def run_required_tests():
    """Run every test case from the PDF and print PASS/FAIL for each."""
    # Each test: (list of intervals, expected answer)
    testsA = [
        ([], 0),
        ([(1, 3)], 1),
        ([(1, 3), (3, 5), (5, 7)], 3),
        ([(1, 5), (2, 6), (3, 7)], 1),
        ([(5, 7), (1, 3), (3, 5), (2, 4)], 3),
        ([(1, 4), (2, 4), (4, 6)], 2),
    ]
    testsB = [
        ([], 0),
        ([(1, 3)], 1),
        ([(1, 3), (3, 5), (5, 7)], 1),
        ([(1, 5), (2, 6), (3, 7)], 3),
        ([(1, 4), (2, 5), (4, 7), (5, 8)], 2),
        ([(5, 8), (1, 4), (2, 5), (4, 6), (6, 9)], 2),
    ]
    testsC = [
        ([], 0),
        ([(1, 3)], 0),
        ([(1, 3), (3, 5), (5, 7)], 0),
        ([(1, 5), (2, 6), (3, 7)], 2),
        ([(5, 7), (1, 3), (3, 5), (2, 4)], 1),
        ([(1, 2), (2, 3), (3, 4), (1, 3)], 1),
    ]

    allPassed = True

    print("=" * 60)
    print("REQUIRED TEST CASES")
    print("=" * 60)

    # ---- Task A ----
    print("Task A (maximum selected)")
    for num, (intervals, expected) in enumerate(testsA, start=1):
        selected = max_deliveries_one_driver(make_deliveries(intervals))
        # Correct size AND the chosen deliveries really don't overlap
        ok = len(selected) == expected and is_compatible(selected)
        allPassed &= ok
        chosen = [(d[1], d[2]) for d in selected]
        print(f"  Test {num}: expected {expected}, got {len(selected)} "
              f"{chosen}  {'PASS' if ok else 'FAIL'}")

    # ---- Task B ----
    print("Task B (minimum drivers)")
    for num, (intervals, expected) in enumerate(testsB, start=1):
        deliveries = make_deliveries(intervals)
        schedules = min_drivers(deliveries)
        # Correct count, every driver's day is overlap-free,
        # and every delivery was assigned exactly once
        assignedCount = sum(len(s) for s in schedules)
        ok = (len(schedules) == expected
              and all(is_compatible(s) for s in schedules)
              and assignedCount == len(deliveries))
        allPassed &= ok
        drivers = [[(d[1], d[2]) for d in s] for s in schedules]
        print(f"  Test {num}: expected {expected}, got {len(schedules)} "
              f"{drivers}  {'PASS' if ok else 'FAIL'}")

    # ---- Task C ----
    print("Task C (minimum rejected)")
    for num, (intervals, expected) in enumerate(testsC, start=1):
        count, rejected = min_rejected(make_deliveries(intervals))
        ok = count == expected
        allPassed &= ok
        dropped = [(d[1], d[2]) for d in rejected]
        print(f"  Test {num}: expected {expected}, got {count} "
              f"rejected {dropped}  {'PASS' if ok else 'FAIL'}")

    print("\nALL TESTS PASSED\n" if allPassed else "\nSOME TESTS FAILED\n")
    return allPassed


# -----------------------------------------------------------------------------
#  Main program
# -----------------------------------------------------------------------------
def main():
    # Use the file from the command line if one was given, otherwise default
    filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILENAME

    deliveryData = read_deliveries(filename)

    print("=" * 60)
    print(f"RESULTS FOR {filename}  ({len(deliveryData)} deliveries)")
    print("=" * 60)
    print_task_a(deliveryData)
    print_task_b(deliveryData)
    print_task_c(deliveryData)

    run_required_tests()
    run_task_d()


# Only run main() when this file is executed directly (not when imported)
if __name__ == "__main__":
    main()
