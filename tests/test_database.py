"""
Automated Tests - MariaDB Network Device Registry

Tests:
1. Database schema
2. IPv4 validation
3. IPv4 sorting
4. INSERT RETURNING
5. INTERSECT and EXCEPT
6. Invalid UUID validation
7. IPv4 boundary values
8. Duplicate hostnames with INTERSECT and EXCEPT

All temporary database changes are rolled back after testing.
"""

import os
import unittest
import uuid
from pathlib import Path

import pymysql
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Connect to MariaDB before each test."""

        self.connection = pymysql.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password=os.getenv("MARIADB_ROOT_PASSWORD"),
            database="network_registry",
            autocommit=False
        )

        self.connection.begin()

    def tearDown(self):
        """Remove temporary changes after each test."""

        self.connection.rollback()
        self.connection.close()

    # TEST 1: DATABASE STRUCTURE

    def test_1_schema(self):

        with self.connection.cursor() as cursor:

            cursor.execute("""
                SELECT COLUMN_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'network_registry'
                AND TABLE_NAME = 'devices_baseline'
                AND COLUMN_NAME = 'id'
            """)

            self.assertEqual(cursor.fetchone()[0], "char(36)")

            cursor.execute("""
                SELECT COLUMN_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'network_registry'
                AND TABLE_NAME = 'devices_native'
                AND COLUMN_NAME = 'id'
            """)

            self.assertEqual(cursor.fetchone()[0], "uuid")

            cursor.execute("""
                SELECT COLUMN_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = 'network_registry'
                AND TABLE_NAME = 'devices_native'
                AND COLUMN_NAME = 'ip_address'
            """)

            self.assertEqual(cursor.fetchone()[0], "inet4")

    # TEST 2: IPv4 VALIDATION

    def test_2_ip_validation(self):

        device_id = str(uuid.uuid4())

        with self.connection.cursor() as cursor:

            cursor.execute("""
                SELECT @@SESSION.sql_mode
            """)

            sql_mode = cursor.fetchone()[0]

            self.assertTrue(
                "STRICT_TRANS_TABLES" in sql_mode
                or "STRICT_ALL_TABLES" in sql_mode
            )

            cursor.execute("""
                INSERT INTO devices_baseline
                (id, hostname, ip_address)
                VALUES (%s, %s, %s)
            """, (
                device_id,
                "test-invalid-ip",
                "999.999.999.999"
            ))

            with self.assertRaises(
                pymysql.MySQLError
            ) as error:

                cursor.execute("""
                    INSERT INTO devices_native
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    device_id,
                    "test-invalid-ip",
                    "999.999.999.999"
                ))

            self.assertEqual(error.exception.args[0], 1292)

    # TEST 3: IPv4 SORTING

    def test_3_ip_sorting(self):

        addresses = [
            "10.0.0.2",
            "10.0.0.10",
            "10.0.0.100",
            "192.168.1.1"
        ]

        prefix = f"test-sort-{uuid.uuid4().hex[:8]}"

        with self.connection.cursor() as cursor:

            for i, address in enumerate(addresses):

                device_id = str(uuid.uuid4())
                hostname = f"{prefix}-{i}"

                for table in [
                    "devices_baseline",
                    "devices_native"
                ]:

                    cursor.execute(f"""
                        INSERT INTO {table}
                        (id, hostname, ip_address)
                        VALUES (%s, %s, %s)
                    """, (
                        device_id,
                        hostname,
                        address
                    ))

            cursor.execute("""
                SELECT ip_address
                FROM devices_baseline
                WHERE hostname LIKE %s
                ORDER BY ip_address
            """, (prefix + "%",))

            baseline = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                SELECT ip_address
                FROM devices_native
                WHERE hostname LIKE %s
                ORDER BY ip_address
            """, (prefix + "%",))

            native = [row[0] for row in cursor.fetchall()]

            self.assertEqual(
                baseline,
                [
                    "10.0.0.10",
                    "10.0.0.100",
                    "10.0.0.2",
                    "192.168.1.1"
                ]
            )

            self.assertEqual(
                native,
                [
                    "10.0.0.2",
                    "10.0.0.10",
                    "10.0.0.100",
                    "192.168.1.1"
                ]
            )

    # TEST 4: INSERT RETURNING

    def test_4_returning(self):

        device_id = str(uuid.uuid4())

        with self.connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO devices_native
                (id, hostname, ip_address)
                VALUES (%s, %s, %s)
                RETURNING hostname, ip_address
            """, (
                device_id,
                "test-returning",
                "192.168.5.10"
            ))

            result = cursor.fetchone()

            self.assertEqual(
                result,
                ("test-returning", "192.168.5.10")
            )

    # TEST 5: INTERSECT AND EXCEPT

    def test_5_set_operations(self):

        prefix = f"test-set-{uuid.uuid4().hex[:8]}"

        shared = prefix + "-shared"
        baseline_only = prefix + "-baseline"
        native_only = prefix + "-native"

        with self.connection.cursor() as cursor:

            test_rows = [
                ("devices_baseline", shared),
                ("devices_native", shared),
                ("devices_baseline", baseline_only),
                ("devices_native", native_only)
            ]

            for table, hostname in test_rows:

                cursor.execute(f"""
                    INSERT INTO {table}
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    hostname,
                    "10.10.10.1"
                ))

            cursor.execute("""
                SELECT hostname
                FROM devices_baseline
                WHERE hostname LIKE %s

                INTERSECT

                SELECT hostname
                FROM devices_native
                WHERE hostname LIKE %s
            """, (prefix + "%", prefix + "%"))

            common = {row[0] for row in cursor.fetchall()}

            self.assertEqual(common, {shared})

            cursor.execute("""
                SELECT hostname
                FROM devices_baseline
                WHERE hostname LIKE %s

                EXCEPT

                SELECT hostname
                FROM devices_native
                WHERE hostname LIKE %s
            """, (prefix + "%", prefix + "%"))

            missing = {row[0] for row in cursor.fetchall()}

            self.assertEqual(missing, {baseline_only})

    # TEST 6: INVALID UUID VALIDATION

    def test_6_invalid_uuid(self):

        invalid_id = "not-a-valid-uuid"

        with self.connection.cursor() as cursor:

            # The traditional table stores the ID as text.
            # It should accept this value.
            cursor.execute("""
                INSERT INTO devices_baseline
                (id, hostname, ip_address)
                VALUES (%s, %s, %s)
            """, (
                invalid_id,
                "test-invalid-uuid",
                "192.168.50.10"
            ))

            # The native UUID column should reject the same ID.
            with self.assertRaises(
                pymysql.MySQLError
            ) as error:

                cursor.execute("""
                    INSERT INTO devices_native
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    invalid_id,
                    "test-invalid-uuid",
                    "192.168.50.10"
                ))

            # MariaDB should return error 1292.
            self.assertEqual(error.exception.args[0], 1292)

    # TEST 7: IPv4 BOUNDARY VALUES

    def test_7_ipv4_boundaries(self):

        # These are the lowest and highest IPv4 addresses.
        valid_addresses = [
            "0.0.0.0",
            "255.255.255.255"
        ]

        with self.connection.cursor() as cursor:

            # Check that INET4 accepts both valid addresses.
            for i, address in enumerate(valid_addresses):

                cursor.execute("""
                    INSERT INTO devices_native
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    f"test-boundary-{uuid.uuid4().hex[:8]}-{i}",
                    address
                ))

                self.assertEqual(cursor.rowcount, 1)

            # Now try an invalid address.
            # An IPv4 number cannot be greater than 255.
            invalid_address = "256.1.1.1"

            with self.assertRaises(
                pymysql.MySQLError
            ) as error:

                cursor.execute("""
                    INSERT INTO devices_native
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    "test-invalid-boundary",
                    invalid_address
                ))

            # MariaDB should reject the invalid address.
            self.assertEqual(error.exception.args[0], 1292)

    # TEST 8: DUPLICATE HOSTNAMES WITH INTERSECT AND EXCEPT

    def test_8_duplicate_hostnames(self):

        prefix = f"test-duplicates-{uuid.uuid4().hex[:8]}"

        shared = prefix + "-shared"
        baseline_only = prefix + "-baseline"
        native_only = prefix + "-native"

        with self.connection.cursor() as cursor:

            # Insert duplicate hostnames into both tables.
            # Each record still has its own unique UUID.

            for table, hostname in [
                ("devices_baseline", shared),
                ("devices_baseline", shared),
                ("devices_native", shared),
                ("devices_native", shared),
                ("devices_baseline", baseline_only),
                ("devices_baseline", baseline_only),
                ("devices_native", native_only),
                ("devices_native", native_only)
            ]:

                cursor.execute(f"""
                    INSERT INTO {table}
                    (id, hostname, ip_address)
                    VALUES (%s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    hostname,
                    "192.168.10.10"
                ))

            # INTERSECT should return the shared hostname once.

            cursor.execute("""
                SELECT hostname
                FROM devices_baseline
                WHERE hostname LIKE %s

                INTERSECT

                SELECT hostname
                FROM devices_native
                WHERE hostname LIKE %s
            """, (prefix + "%", prefix + "%"))

            common = [row[0] for row in cursor.fetchall()]

            self.assertEqual(common, [shared])

            # EXCEPT should return the baseline-only
            # hostname once, even though it was inserted twice.

            cursor.execute("""
                SELECT hostname
                FROM devices_baseline
                WHERE hostname LIKE %s

                EXCEPT

                SELECT hostname
                FROM devices_native
                WHERE hostname LIKE %s
            """, (prefix + "%", prefix + "%"))

            baseline_missing = [
                row[0] for row in cursor.fetchall()
            ]

            self.assertEqual(baseline_missing, [baseline_only])

            # Check the opposite direction too.

            cursor.execute("""
                SELECT hostname
                FROM devices_native
                WHERE hostname LIKE %s

                EXCEPT

                SELECT hostname
                FROM devices_baseline
                WHERE hostname LIKE %s
            """, (prefix + "%", prefix + "%"))

            native_missing = [
                row[0] for row in cursor.fetchall()
            ]

            self.assertEqual(native_missing, [native_only])

if __name__ == "__main__":
    unittest.main()