-- Experiment 3 - Part C
-- UUID Storage Comparison: 500,000 Records
-- MariaDB Network Device Registry

-- Objective:
-- *Compare the allocated storage of CHAR(36)
-- *and MariaDB's native UUID data type
-- *using 500,000 identical identifiers.

-- IMPORTANT:
-- This script only recreates the dedicated 500k tables.
-- It does not modify the original device registry
-- or the previous 10k and 100k experiments.


-- PART 1: Create the experiment tables

DROP TABLE IF EXISTS uuid_bulk_baseline_500k;
DROP TABLE IF EXISTS uuid_bulk_native_500k;
DROP TABLE IF EXISTS uuid_bulk_seed_500k;

-- Seed table containing the generated UUIDs.

CREATE TABLE uuid_bulk_seed_500k (
    id CHAR(36) PRIMARY KEY
) ENGINE=InnoDB;

-- Traditional implementation.

CREATE TABLE uuid_bulk_baseline_500k (
    id CHAR(36) PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- MariaDB-native implementation.

CREATE TABLE uuid_bulk_native_500k (
    id UUID PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;


-- PART 2: Prepare data generation

-- Create a temporary table containing digits 0-9.

DROP TEMPORARY TABLE IF EXISTS uuid_digits_500k;

CREATE TEMPORARY TABLE uuid_digits_500k (
    n TINYINT PRIMARY KEY
);

INSERT INTO uuid_digits_500k VALUES
(0),(1),(2),(3),(4),(5),(6),(7),(8),(9);


-- PART 3: Generate 500,000 UUID values

-- Five sets of ten rows and one set of five rows:
--
-- 10 x 10 x 10 x 10 x 10 x 5 = 500,000

INSERT INTO uuid_bulk_seed_500k (id)

SELECT UUID()

FROM uuid_digits_500k a

CROSS JOIN uuid_digits_500k b

CROSS JOIN uuid_digits_500k c

CROSS JOIN uuid_digits_500k d

CROSS JOIN uuid_digits_500k e

CROSS JOIN (
    SELECT 0 AS n
    UNION ALL SELECT 1
    UNION ALL SELECT 2
    UNION ALL SELECT 3
    UNION ALL SELECT 4
) AS f;


-- PART 4: Insert identical data into both tables


-- Traditional CHAR(36) table.

INSERT INTO uuid_bulk_baseline_500k
(id, hostname)

SELECT
    id,
    'benchmark-device'

FROM uuid_bulk_seed_500k;


-- Native UUID table.

INSERT INTO uuid_bulk_native_500k
(id, hostname)

SELECT
    id,
    'benchmark-device'

FROM uuid_bulk_seed_500k;


-- PART 5: Verify record counts


SELECT COUNT(*) AS baseline_records
FROM uuid_bulk_baseline_500k;

SELECT COUNT(*) AS native_records
FROM uuid_bulk_native_500k;


-- PART 6: Update table statistics

ANALYZE TABLE uuid_bulk_baseline_500k;

ANALYZE TABLE uuid_bulk_native_500k;


-- PART 7: Measure allocated storage

SELECT
    TABLE_NAME,

    ENGINE,

    DATA_LENGTH AS data_bytes,

    INDEX_LENGTH AS index_bytes,

    (DATA_LENGTH + INDEX_LENGTH) AS total_bytes,

    ROUND(
        (DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024,
        3
    ) AS total_mib

FROM INFORMATION_SCHEMA.TABLES

WHERE TABLE_SCHEMA = 'network_registry'

AND TABLE_NAME IN (
    'uuid_bulk_baseline_500k',
    'uuid_bulk_native_500k'
)

ORDER BY TABLE_NAME;


-- PART 8: Calculate observed storage reduction

SELECT

    b.DATA_LENGTH + b.INDEX_LENGTH
        AS baseline_bytes,

    n.DATA_LENGTH + n.INDEX_LENGTH
        AS native_bytes,

    (
        (b.DATA_LENGTH + b.INDEX_LENGTH)
        -
        (n.DATA_LENGTH + n.INDEX_LENGTH)
    ) AS bytes_saved,

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
    ON b.TABLE_SCHEMA = n.TABLE_SCHEMA

WHERE b.TABLE_SCHEMA = 'network_registry'

AND b.TABLE_NAME = 'uuid_bulk_baseline_500k'

AND n.TABLE_NAME = 'uuid_bulk_native_500k';


-- PART 9: Clean up temporary digit table

DROP TEMPORARY TABLE IF EXISTS uuid_digits_500k;


-- End of Experiment 3 - Part C
