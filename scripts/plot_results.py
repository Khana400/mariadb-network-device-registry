"""
MariaDB Network Device Registry
Experimental Results Visualization

Generates graphs comparing traditional and
MariaDB-native database implementations.

Graphs:
1. UUID storage comparison
2. UUID storage reduction
3. Insertion performance
4. UUID lookup performance
5. IPv4 sorting performance
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. Project directories
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_DIR = PROJECT_ROOT / "results"

GRAPHS_DIR = RESULTS_DIR / "graphs"

GRAPHS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Load storage measurements
# --------------------------------------------------

storage_file = RESULTS_DIR / "storage_measurements.csv"

storage_data = []

with storage_file.open(newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        storage_data.append({
            "records": int(row["records"]),
            "baseline": int(row["baseline_bytes"]),
            "native": int(row["native_bytes"])
        })

storage_data.sort(key=lambda row: row["records"])


# --------------------------------------------------
# 3. Graph 1: UUID storage comparison
# --------------------------------------------------

labels = [f'{row["records"]:,}' for row in storage_data]

baseline_storage = [
    row["baseline"] / (1024 ** 2)
    for row in storage_data
]

native_storage = [
    row["native"] / (1024 ** 2)
    for row in storage_data
]

positions = list(range(len(labels)))
width = 0.35

plt.figure(figsize=(9, 5))

plt.bar(
    [x - width / 2 for x in positions],
    baseline_storage,
    width,
    label="Traditional CHAR(36)"
)

plt.bar(
    [x + width / 2 for x in positions],
    native_storage,
    width,
    label="MariaDB Native UUID"
)

plt.xticks(positions, labels)

plt.xlabel("Number of Records")
plt.ylabel("Allocated Storage (MiB)")

plt.title("UUID Storage Comparison")

plt.legend()
plt.grid(axis="y", alpha=0.25)

plt.tight_layout()

plt.savefig(
    GRAPHS_DIR / "uuid_storage_comparison.png",
    dpi=200
)

plt.close()


# --------------------------------------------------
# 4. Graph 2: UUID storage reduction
# --------------------------------------------------

reductions = []

for row in storage_data:

    baseline = row["baseline"]
    native = row["native"]

    reduction = (
        (baseline - native) / baseline
    ) * 100

    reductions.append(reduction)

plt.figure(figsize=(9, 5))

bars = plt.bar(labels, reductions)

plt.xlabel("Number of Records")
plt.ylabel("Storage Reduction (%)")

plt.title("Observed UUID Storage Reduction")

plt.bar_label(
    bars,
    labels=[f"{value:.2f}%" for value in reductions],
    padding=4
)

plt.ylim(0, max(reductions) * 1.2 if max(reductions) > 0 else 1)

plt.grid(axis="y", alpha=0.25)

plt.tight_layout()

plt.savefig(
    GRAPHS_DIR / "uuid_storage_reduction.png",
    dpi=200
)

plt.close()


# --------------------------------------------------
# 5. Load performance measurements
# --------------------------------------------------

performance_data = defaultdict(list)

dataset_sizes = [10000, 100000]

for size in dataset_sizes:

    filename = RESULTS_DIR / f"benchmark_{size}.csv"

    with filename.open(
        newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            key = (
                size,
                row["operation"],
                row["variant"]
            )

            performance_data[key].append(
                float(row["seconds"])
            )


# --------------------------------------------------
# 6. Function for performance graphs
# --------------------------------------------------

def create_performance_graph(
    operation,
    title,
    filename,
    multiplier,
    unit
):

    baseline_means = []
    native_means = []

    baseline_std = []
    native_std = []

    for size in dataset_sizes:

        baseline = performance_data[
            (size, operation, "baseline")
        ]

        native = performance_data[
            (size, operation, "native")
        ]

        if len(baseline) != 5 or len(native) != 5:
            raise ValueError(
                f"Expected 5 rounds for {operation} "
                f"at dataset size {size}"
            )

        baseline_means.append(
            statistics.mean(baseline) * multiplier
        )

        native_means.append(
            statistics.mean(native) * multiplier
        )

        baseline_std.append(
            statistics.stdev(baseline) * multiplier
        )

        native_std.append(
            statistics.stdev(native) * multiplier
        )

    positions = list(range(len(dataset_sizes)))

    width = 0.35

    plt.figure(figsize=(9, 5))

    plt.bar(
        [x - width / 2 for x in positions],
        baseline_means,
        width,
        yerr=baseline_std,
        capsize=4,
        label="Traditional"
    )

    plt.bar(
        [x + width / 2 for x in positions],
        native_means,
        width,
        yerr=native_std,
        capsize=4,
        label="MariaDB Native"
    )

    plt.xticks(
        positions,
        [f"{size:,}" for size in dataset_sizes]
    )

    plt.xlabel("Dataset Size")
    plt.ylabel(f"Execution Time ({unit})")

    plt.title(title + "\nMean ± Standard Deviation (5 Rounds)")

    plt.legend()
    plt.grid(axis="y", alpha=0.25)

    plt.tight_layout()

    plt.savefig(
        GRAPHS_DIR / filename,
        dpi=200
    )

    plt.close()


# --------------------------------------------------
# 7. Graph 3: Insertion performance
# --------------------------------------------------

create_performance_graph(
    operation="insert",
    title="Database Insertion Performance",
    filename="insertion_performance.png",
    multiplier=1,
    unit="seconds"
)


# --------------------------------------------------
# 8. Graph 4: UUID lookup performance
# --------------------------------------------------

create_performance_graph(
    operation="uuid_lookup",
    title="UUID Lookup Performance (200 Lookups)",
    filename="uuid_lookup_performance.png",
    multiplier=1000,
    unit="milliseconds"
)


# --------------------------------------------------
# 9. Graph 5: IPv4 sorting performance
# --------------------------------------------------

create_performance_graph(
    operation="ip_sort",
    title="Numerical IPv4 Sorting (LIMIT 1000)",
    filename="ip_sorting_performance.png",
    multiplier=1000,
    unit="milliseconds"
)


# --------------------------------------------------
# 10. Finish
# --------------------------------------------------

print("All five graphs generated successfully!")

print(f"Graphs saved to: {GRAPHS_DIR}")