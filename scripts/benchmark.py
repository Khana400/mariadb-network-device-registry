"""
Experiment 4: MariaDB Performance Benchmarking

Project: MariaDB Network Device Registry

This script compares traditional string-based storage
with MariaDB-native UUID and INET4 data types.

Operations tested:
1. Bulk insertions
2. Primary-key UUID lookups
3. Numerical IPv4 sorting

Each experiment is repeated five times.
Results are saved to results/benchmark.csv.
"""

import csv
import ipaddress
import os
import random
import statistics
import time
import uuid

from collections import defaultdict
from pathlib import Path

import pymysql
from dotenv import load_dotenv


# -----------------------------------------------------
# 1. Configuration
# -----------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

DB_PASSWORD = os.getenv("MARIADB_ROOT_PASSWORD")

if not DB_PASSWORD:
    raise RuntimeError(
        "Database password is missing from the .env file."
    )

RECORD_COUNT = 100000
ROUNDS = 5
BATCH_SIZE = 250
LOOKUP_COUNT = 200
SORT_LIMIT = 1000

RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RESULTS_FILE = RESULTS_DIR / "benchmark_100000.csv"


# -----------------------------------------------------
# 2. Connect to MariaDB
# -----------------------------------------------------

connection = pymysql.connect(
    host="127.0.0.1",
    port=3307,
    user="root",
    password=DB_PASSWORD,
    database="network_registry",
    charset="utf8mb4",
    autocommit=False,
)

print("Connected to MariaDB successfully!")


# -----------------------------------------------------
# 3. Generate identical test data
# -----------------------------------------------------

print("Generating test devices...")

devices = []

for i in range(RECORD_COUNT):

    device_id = str(uuid.uuid4())

    hostname = f"device-{i:06d}"

    ip_address = str(
        ipaddress.IPv4Address(0x0A000000 + i + 1)
    )

    devices.append(
        (device_id, hostname, ip_address)
    )

random_generator = random.Random(2026)

lookup_ids = random_generator.sample(
    [device[0] for device in devices],
    LOOKUP_COUNT,
)

print(f"Generated {len(devices)} devices.")


# -----------------------------------------------------
# 4. Create dedicated benchmark tables
# -----------------------------------------------------

# Only the two benchmark_* tables are recreated.
# Original device tables and bulk experiments
# are not modified.

TABLES = {
    "baseline": "benchmark_baseline",
    "native": "benchmark_native",
}

with connection.cursor() as cursor:

    cursor.execute(
        "DROP TABLE IF EXISTS benchmark_baseline"
    )

    cursor.execute(
        "DROP TABLE IF EXISTS benchmark_native"
    )

    cursor.execute("""
        CREATE TABLE benchmark_baseline (
            id CHAR(36) PRIMARY KEY,
            hostname VARCHAR(100) NOT NULL,
            ip_address VARCHAR(15) NOT NULL,
            INDEX idx_ip (ip_address)
        ) ENGINE=InnoDB
    """)

    cursor.execute("""
        CREATE TABLE benchmark_native (
            id UUID PRIMARY KEY,
            hostname VARCHAR(100) NOT NULL,
            ip_address INET4 NOT NULL,
            INDEX idx_ip (ip_address)
        ) ENGINE=InnoDB
    """)

connection.commit()

print("Benchmark tables created.")


# -----------------------------------------------------
# 5. Run performance experiments
# -----------------------------------------------------

results = []

try:

    for run in range(1, ROUNDS + 1):

        print(f"\nStarting benchmark round {run}/{ROUNDS}")

        # Alternate execution order to reduce
        # systematic first-run advantages.

        order = (
            ["baseline", "native"]
            if run % 2 == 1
            else ["native", "baseline"]
        )

        for variant in order:

            table = TABLES[variant]

            with connection.cursor() as cursor:

                # -------------------------------------
                # A. Insertion benchmark
                # -------------------------------------

                cursor.execute(f"TRUNCATE TABLE {table}")

                start = time.perf_counter()

                for batch_start in range(
                    0, RECORD_COUNT, BATCH_SIZE
                ):

                    batch = devices[
                        batch_start:batch_start + BATCH_SIZE
                    ]

                    cursor.executemany(
                        f"""
                        INSERT INTO {table}
                        (id, hostname, ip_address)
                        VALUES (%s, %s, %s)
                        """,
                        batch,
                    )

                connection.commit()

                insert_time = time.perf_counter() - start

                cursor.execute(
                    f"SELECT COUNT(*) FROM {table}"
                )

                count = cursor.fetchone()[0]

                assert count == RECORD_COUNT, (
                    f"Incorrect record count in {table}"
                )

                results.append({
                    "round": run,
                    "variant": variant,
                    "operation": "insert",
                    "seconds": insert_time,
                })

                print(
                    f"{variant} insertion: "
                    f"{insert_time:.4f} seconds"
                )

                # -------------------------------------
                # B. UUID lookup benchmark
                # -------------------------------------

                query = (
                    f"SELECT hostname FROM {table} "
                    "WHERE id = %s"
                )

                # Small warm-up before timing.

                for device_id in lookup_ids[:10]:
                    cursor.execute(query, (device_id,))
                    assert cursor.fetchone() is not None

                start = time.perf_counter()

                for device_id in lookup_ids:

                    cursor.execute(query, (device_id,))

                    row = cursor.fetchone()

                    assert row is not None

                lookup_time = time.perf_counter() - start

                results.append({
                    "round": run,
                    "variant": variant,
                    "operation": "uuid_lookup",
                    "seconds": lookup_time,
                })

                print(
                    f"{variant} UUID lookups: "
                    f"{lookup_time:.4f} seconds"
                )

                # -------------------------------------
                # C. IPv4 sorting benchmark
                # -------------------------------------

                # Both queries produce numerical IPv4
                # ordering, making their results
                # functionally comparable.

                if variant == "baseline":

                    sort_query = f"""
                        SELECT ip_address
                        FROM {table}
                        ORDER BY INET_ATON(ip_address)
                        LIMIT {SORT_LIMIT}
                    """

                else:

                    sort_query = f"""
                        SELECT ip_address
                        FROM {table}
                        ORDER BY ip_address
                        LIMIT {SORT_LIMIT}
                    """

                start = time.perf_counter()

                cursor.execute(sort_query)

                sorted_rows = cursor.fetchall()

                sort_time = time.perf_counter() - start

                assert len(sorted_rows) == SORT_LIMIT

                results.append({
                    "round": run,
                    "variant": variant,
                    "operation": "ip_sort",
                    "seconds": sort_time,
                })

                print(
                    f"{variant} IP sorting: "
                    f"{sort_time:.4f} seconds"
                )

finally:

    connection.close()


# -----------------------------------------------------
# 6. Save results to CSV
# -----------------------------------------------------

with RESULTS_FILE.open(
    "w", newline="", encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "round",
            "variant",
            "operation",
            "seconds",
        ],
    )

    writer.writeheader()

    writer.writerows(results)

print(f"\nResults saved to {RESULTS_FILE}")


# -----------------------------------------------------
# 7. Calculate summary statistics
# -----------------------------------------------------

grouped = defaultdict(list)

for result in results:

    key = (
        result["operation"],
        result["variant"],
    )

    grouped[key].append(result["seconds"])


print("\nBENCHMARK SUMMARY")
print("=" * 50)

for operation in [
    "insert",
    "uuid_lookup",
    "ip_sort",
]:

    print(f"\nOperation: {operation}")

    for variant in ["baseline", "native"]:

        measurements = grouped[
            (operation, variant)
        ]

        average = statistics.mean(measurements)

        median = statistics.median(measurements)

        deviation = statistics.stdev(measurements)

        print(
            f"{variant}: "
            f"mean={average:.4f}s, "
            f"median={median:.4f}s, "
            f"stdev={deviation:.4f}s"
        )


print("\nExperiment 4 completed successfully!")
