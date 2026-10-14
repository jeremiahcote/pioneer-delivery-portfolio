# =============================================================================
#  Generates a test data file for the Pioneer Delivery project, in the same
#  format as the example in the assignment:
#
#      D01 10 13
#      D02 2 5
#      ...
#
#  Times are small integers on a 24-hour clock (0 = midnight, 13 = 1 PM).
#  The file starts with the 7 example deliveries from the assignment
#  (D01-D07), then adds random deliveries that last 1-8 hours each.
#
#  How to run:
#      python generate_deliveries.py                 <- writes DeliveryOrders.txt
#      python generate_deliveries.py myfile.txt 200  <- custom file name / count
# =============================================================================

import sys
import random

NUM_DELIVERIES = 99
DAY_LENGTH = 24           # every delivery fits between time 0 and time 24
MIN_DURATION = 1          # shortest delivery
MAX_DURATION = 8          # longest delivery
SEED = 413                # fixed seed -> same file every time you run it

# The example deliveries from the assignment PDF, kept exactly as given
ASSIGNMENT_EXAMPLE = [
    ("D01", 10, 13),
    ("D02", 2, 5),
    ("D03", 4, 7),
    ("D04", 1, 8),
    ("D05", 8, 11),
    ("D06", 11, 14),
    ("D07", 13, 16),
]


def generate_deliveries(count):
    """Return the assignment example plus random deliveries, count in total."""
    deliveries = list(ASSIGNMENT_EXAMPLE[:count])

    # Keep numbering where the example left off (D08, D09, ...)
    for i in range(len(deliveries) + 1, count + 1):
        duration = random.randint(MIN_DURATION, MAX_DURATION)
        # Latest possible start still lets the delivery finish by DAY_LENGTH
        start = random.randint(0, DAY_LENGTH - duration)
        finish = start + duration
        deliveries.append((f"D{i:02d}", start, finish))
    return deliveries


def write_deliveries(filename, deliveries):
    """Write one delivery per line:  <id> <start> <finish>"""
    with open(filename, "w") as file:
        for deliveryId, start, finish in deliveries:
            file.write(f"{deliveryId} {start} {finish}\n")


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "DeliveryOrders.txt"
    count = int(sys.argv[2]) if len(sys.argv) > 2 else NUM_DELIVERIES

    random.seed(SEED)
    write_deliveries(filename, generate_deliveries(count))
    print(f"Wrote {count} deliveries to {filename}")
