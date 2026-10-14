# Pioneer Delivery Company: Algorithm Portfolio, Part I (Greedy Algorithms)

CS 413, Analysis of Algorithms

## Language

Python 3 (tested with Python 3.14). Uses only the standard library (`heapq`, `itertools`, `sys`).

## How to run

No compiling needed. From this folder:

```
python CotePioneerDeliveryCompany.py DeliveryOrders.txt
```

If no file name is given, the program uses `DeliveryOrders.txt` from the same folder as the script.

The program prints:
1. Task A, B and C results for the input file
2. Every required test case from the assignment, with PASS/FAIL
3. The Task D counterexample, computed and checked by brute force

## Input file format

One delivery per line, three values separated by whitespace:

```
<id> <start_time> <finish_time>
```

Example (first lines of `DeliveryOrders.txt`, which has 99 deliveries):

```
D01 10 13
D02 2 5
D03 4 7
D04 1 8
D05 8 11
D06 11 14
D07 13 16
D08 5 13
```

The file starts with the 7 example deliveries from the assignment (D01–D07). D08–D99 are random deliveries with integer times between 0 and 24, each lasting 1–8 time units. The file was made with `generate_deliveries.py` (fixed random seed, so running it again produces the same file):

```
python generate_deliveries.py
```

Times are integers and `start_time < finish_time`. Blank lines are ignored. A delivery ending at time `t` and another starting at time `t` are compatible.

## Program organization

`generate_deliveries.py` creates the test data file. Everything else is in `CotePioneerDeliveryCompany.py`, split into functions:

| Function | Purpose |
|---|---|
| `read_deliveries(filename)` | Parses the input file into a list of `(id, start, finish)` tuples |
| `max_deliveries_one_driver(deliveries)` | **Task A**: earliest-finish-time greedy |
| `min_drivers(deliveries)` | **Task B**: interval partitioning with a min-heap |
| `min_rejected(deliveries)` | **Task C**: `n - (Task A answer)` |
| `greedy_g`, `place_in_order`, `schedule_value`, `best_schedule_brute_force`, `run_task_d` | **Task D**: run strategy G and compare it to the true optimum |
| `print_task_a/b/c` | Format the output for each task |
| `is_compatible(schedule)` | Checks that a schedule has no overlaps (used by the tests) |
| `make_deliveries`, `run_required_tests` | Runs the required test cases from the assignment |
| `main()` | Reads the file, prints results, runs the tests and Task D |

---

## Task A: Maximum deliveries for one driver

**Algorithm.** Sort the deliveries by finish time. Track `lastFinish`, the time the driver is next free (starting at negative infinity). Go through the sorted list and select each delivery whose `start >= lastFinish`, then set `lastFinish` to its finish time.

**1. Greedy choice.** Among the deliveries compatible with those already chosen, always pick the one that **finishes earliest**.

**2. Why it is optimal (exchange argument).** Let `g1, g2, ..., gk` be the greedy picks and `o1, o2, ..., om` be an optimal schedule, both sorted by finish time. Since `g1` finishes earliest of all deliveries, `finish(g1) <= finish(o1)`. Replacing `o1` with `g1` keeps the optimal schedule valid, because `g1` ends no later than `o1` did, so it cannot overlap `o2`. Applying this step by step shows that greedy "stays ahead": for every `i`, `finish(gi) <= finish(oi)`. If the optimal schedule had more deliveries (`m > k`), then `o(k+1)` would start after `finish(ok) >= finish(gk)`. That means it was compatible with the greedy schedule, and greedy would have picked it, which is a contradiction. So `k = m`.

**3. Running time.** Sorting takes O(n log n) and the single pass takes O(n), so the total is **O(n log n)**.

## Task B: Minimum number of drivers

**Algorithm.** Sort the deliveries by start time. Keep a min-heap with one entry per driver. For each delivery, look at the top of the heap (the driver who becomes free soonest). If that driver is free by the delivery's start time, assign the delivery to them and update their free time. Otherwise, add a new driver.

**1. What is stored in the priority queue.** One tuple per driver: `(time this driver becomes free, driver number)`. The heap is ordered by free time, so the top is the driver who finishes their current delivery earliest.

**2. How a driver is selected.** For each new delivery (in start-time order), we check the earliest-free driver. If `freeTime <= start`, that driver takes the delivery (`heapreplace` pops them and pushes them back with the new finish time). If even the earliest-free driver is still busy, every driver is busy, so a new driver is created and pushed onto the heap.

**3. Why this uses the minimum number of drivers.** Define the **depth** `d` as the largest number of deliveries that are all in progress at the same moment. Any valid schedule needs at least `d` drivers, since those `d` deliveries all overlap each other. The algorithm only adds a new driver (say driver number `d'`) when a delivery starts at a time when all `d' - 1` existing drivers are busy. Each of those drivers is busy with a delivery that started at or before this one (because we process in start order) and has not finished yet. Together with the new delivery, that is `d'` deliveries overlapping at that start time, so `d' <= d`. The algorithm therefore never uses more than `d` drivers, which matches the lower bound. It is optimal.

(Check on our data file: an independent sweep over the start/finish events found a maximum overlap of 34 deliveries at one moment, and the algorithm used exactly 34 drivers.)

**4. Running time.** Sorting takes O(n log n). Each of the n deliveries does one heap peek (O(1)) and one push or replace (O(log n)). The total is **O(n log n)**.

## Task C: Minimum deliveries to reject

**1. Relation to Task A.** Rejecting the fewest deliveries is the same as keeping the most. The deliveries we keep must be mutually compatible, which is exactly Task A's problem. So we run Task A and reject everything it didn't select.

**2. If the maximum compatible set has size k,** then exactly **n − k** deliveries must be rejected. We can't reject fewer than that, because keeping more than `k` compatible deliveries is impossible.

**3. Running time.** Running Task A takes O(n log n). Building the rejected list with a set of kept IDs takes O(n). The total is **O(n log n)**.

This is the same idea as LeetCode 435, *Non-overlapping Intervals*.

## Task D: When a greedy choice fails

Strategy G: consider deliveries in decreasing order of profit, and put each one in the earliest free time slot at or after its ready time.

**1. Counterexample instance**

| Delivery | Ready time R | Profit P |
|---|---|---|
| A | 0 | 10 |
| B | 0 | 6 |
| C | 1 | 5 |

**2. Greedy G schedule.** Order by profit: A (10), B (6), C (5).
- A goes in slot 0. Delay 0, value 10/1 = **10**
- B is ready at 0, but slot 0 is taken, so it goes in slot 1. Delay 1, value 6/2 = **3**
- C is ready at 1, but slot 1 is taken, so it goes in slot 2. Delay 1, value 5/2 = **2.5**

V(G) = 10 + 3 + 2.5 = **15.5**

**3. Better schedule S**
- A in slot 0. Delay 0, value 10/1 = **10**
- C in slot 1. Delay 0, value 5/1 = **5**
- B in slot 2. Delay 2, value 6/3 = **2**

V(S) = 10 + 5 + 2 = **17**

(The program checks every possible ordering by brute force and confirms that 17 is the optimum for this instance.)

**4. Why this proves G is not always optimal.** G is supposed to produce an optimal schedule on every input. Here it produced a schedule worth 15.5, and a valid schedule worth 17 exists. One instance where G loses is enough to show it is not correct in general. G fails because it only looks at profit: placing B right after A delays C, which was ready at time 1 and loses half its value. Pushing B back costs only 1 unit (3 down to 2), while serving C on time gains 2.5 (2.5 up to 5).

---

## Results of required test cases

Output of `python CotePioneerDeliveryCompany.py DeliveryOrders.txt` (test section):

```
Task A (maximum selected)
  Test 1: expected 0, got 0 []  PASS
  Test 2: expected 1, got 1 [(1, 3)]  PASS
  Test 3: expected 3, got 3 [(1, 3), (3, 5), (5, 7)]  PASS
  Test 4: expected 1, got 1 [(1, 5)]  PASS
  Test 5: expected 3, got 3 [(1, 3), (3, 5), (5, 7)]  PASS
  Test 6: expected 2, got 2 [(1, 4), (4, 6)]  PASS
Task B (minimum drivers)
  Test 1: expected 0, got 0 []  PASS
  Test 2: expected 1, got 1 [[(1, 3)]]  PASS
  Test 3: expected 1, got 1 [[(1, 3), (3, 5), (5, 7)]]  PASS
  Test 4: expected 3, got 3 [[(1, 5)], [(2, 6)], [(3, 7)]]  PASS
  Test 5: expected 2, got 2 [[(1, 4), (4, 7)], [(2, 5), (5, 8)]]  PASS
  Test 6: expected 2, got 2 [[(1, 4), (4, 6), (6, 9)], [(2, 5), (5, 8)]]  PASS
Task C (minimum rejected)
  Test 1: expected 0, got 0 rejected []  PASS
  Test 2: expected 0, got 0 rejected []  PASS
  Test 3: expected 0, got 0 rejected []  PASS
  Test 4: expected 2, got 2 rejected [(2, 6), (3, 7)]  PASS
  Test 5: expected 1, got 1 rejected [(2, 4)]  PASS
  Test 6: expected 1, got 1 rejected [(1, 3)]  PASS

ALL TESTS PASSED
```

For Task B, the tests check more than the driver count. They also confirm that no driver has overlapping deliveries and that every delivery was assigned exactly once.

## Results on `DeliveryOrders.txt` (99 deliveries)

- **Task A:** 11 deliveries for one driver: D82, D59, D63, D62, D78, D86, D46, D06, D48, D95, D52
- **Task B:** 34 drivers minimum (matches the maximum overlap of 34 deliveries at one moment)
- **Task C:** 88 deliveries rejected (99 − 11)
