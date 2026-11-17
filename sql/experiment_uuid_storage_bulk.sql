-- Experiment 3 - Part B: UUID Bulk Storage Comparison
-- MariaDB Network Device Registry

-- Objective:
-- *Compare actual storage allocation for CHAR(36)
-- *and MariaDB's native UUID data type.

-- Number of test records: 10,000

-- IMPORTANT:
-- This script recreates only the three uuid_bulk_* tables.
-- It does not modify devices_baseline or devices_native.


-- PART 1: Prepare the experiment tables

DROP TABLE IF EXISTS uuid_bulk_baseline;
DROP TABLE IF EXISTS uuid_bulk_native;
DROP TABLE IF EXISTS uuid_bulk_seed;


-- Temporary source table for generating UUID values.

CREATE TABLE uuid_bulk_seed (
    id CHAR(36) PRIMARY KEY
) ENGINE=InnoDB;


-- Traditional UUID storage.

CREATE TABLE uuid_bulk_baseline (
    id CHAR(36) PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;


-- MariaDB-native UUID storage.

CREATE TABLE uuid_bulk_native (
    id UUID PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;


-- PART 2: Generate 10,000 UUID values

-- Generate UUIDs using four sets of digits.
-- 10 x 10 x 10 x 10 = 10,000 records.

INSERT INTO uuid_bulk_seed (id)
SELECT UUID()
FROM
    (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
     UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
     UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
     UNION ALL SELECT 9) AS a

CROSS JOIN
    (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
     UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
     UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
     UNION ALL SELECT 9) AS b

CROSS JOIN
    (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
     UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
     UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
     UNION ALL SELECT 9) AS c

CROSS JOIN
    (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2
     UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5
     UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
     UNION ALL SELECT 9) AS d;


-- PART 3: Insert data into both tables

-- Traditional implementation.

INSERT INTO uuid_bulk_baseline (id, hostname)
SELECT id, 'benchmark-device'
FROM uuid_bulk_seed;


-- MariaDB-native implementation.

INSERT INTO uuid_bulk_native (id, hostname)
SELECT id, 'benchmark-device'
FROM uuid_bulk_seed;


-- PART 4: Verify the number of records

SELECT COUNT(*) AS baseline_records
FROM uuid_bulk_baseline;

SELECT COUNT(*) AS native_records
FROM uuid_bulk_native;

-- PART 5: Update table statistics

ANALYZE TABLE uuid_bulk_baseline;
ANALYZE TABLE uuid_bulk_native;


-- PART 6: Compare allocated database storage

SELECT
    TABLE_NAME,
    ENGINE,
    DATA_LENGTH AS data_bytes,
    INDEX_LENGTH AS index_bytes,
    (DATA_LENGTH + INDEX_LENGTH) AS total_bytes,

    ROUND(
        (DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024,
        3
    ) AS total_mb

FROM INFORMATION_SCHEMA.TABLES

WHERE TABLE_SCHEMA = 'network_registry'

AND TABLE_NAME IN (
    'uuid_bulk_baseline',
    'uuid_bulk_native'
)

ORDER BY TABLE_NAME;


-- PART 7: Compare storage reduction

SELECT
    b.DATA_LENGTH + b.INDEX_LENGTH AS baseline_bytes,

    n.DATA_LENGTH + n.INDEX_LENGTH AS native_bytes,

    ROUND(
        100.0 *
        (
            (b.DATA_LENGTH + b.INDEX_LENGTH)
            -
            (n.DATA_LENGTH + n.INDEX_LENGTH)
        )
        /
        NULLIF(
            b.DATA_LENGTH + b.INDEX_LENGTH,
            0
        ),
        2
    ) AS observed_reduction_percent

FROM INFORMATION_SCHEMA.TABLES AS b

JOIN INFORMATION_SCHEMA.TABLES AS n

WHERE b.TABLE_SCHEMA = 'network_registry'
  AND n.TABLE_SCHEMA = 'network_registry'
  AND b.TABLE_NAME = 'uuid_bulk_baseline'
  AND n.TABLE_NAME = 'uuid_bulk_native';


-- End of Experiment 3 - Part B