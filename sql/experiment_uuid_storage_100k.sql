-- Experiment 3 - Part B: UUID Storage (100,000 Records)
-- MariaDB Network Device Registry

-- Objective:
-- *Compare storage allocation for 100,000 UUIDs
-- *using CHAR(36) and MariaDB's native UUID type.

-- This experiment does not modify the original
-- network device tables or the 10,000-record test.

-- PART 1: Create experiment tables

DROP TABLE IF EXISTS uuid_bulk_baseline_100k;
DROP TABLE IF EXISTS uuid_bulk_native_100k;
DROP TABLE IF EXISTS uuid_bulk_seed_100k;

CREATE TABLE uuid_bulk_seed_100k (
    id CHAR(36) PRIMARY KEY
) ENGINE=InnoDB;

CREATE TABLE uuid_bulk_baseline_100k (
    id CHAR(36) PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE uuid_bulk_native_100k (
    id UUID PRIMARY KEY,
    hostname VARCHAR(50) NOT NULL
) ENGINE=InnoDB;


-- PART 2: Generate 100,000 UUIDs

-- Create a temporary table containing digits 0-9.

CREATE TEMPORARY TABLE uuid_digits_100k (
    n TINYINT PRIMARY KEY
);

INSERT INTO uuid_digits_100k VALUES
(0),(1),(2),(3),(4),(5),(6),(7),(8),(9);

-- Five sets of ten rows produce 100,000 records.

INSERT INTO uuid_bulk_seed_100k (id)
SELECT UUID()
FROM uuid_digits_100k a
CROSS JOIN uuid_digits_100k b
CROSS JOIN uuid_digits_100k c
CROSS JOIN uuid_digits_100k d
CROSS JOIN uuid_digits_100k e;


-- PART 3: Insert identical data into both tables

INSERT INTO uuid_bulk_baseline_100k
(id, hostname)
SELECT id, 'benchmark-device'
FROM uuid_bulk_seed_100k;

INSERT INTO uuid_bulk_native_100k
(id, hostname)
SELECT id, 'benchmark-device'
FROM uuid_bulk_seed_100k;


-- PART 4: Verify record counts

SELECT COUNT(*) AS baseline_records
FROM uuid_bulk_baseline_100k;

SELECT COUNT(*) AS native_records
FROM uuid_bulk_native_100k;


-- PART 5: Update statistics

ANALYZE TABLE uuid_bulk_baseline_100k;
ANALYZE TABLE uuid_bulk_native_100k;


-- PART 6: Measure storage

SELECT
    TABLE_NAME,
    DATA_LENGTH AS data_bytes,
    INDEX_LENGTH AS index_bytes,
    DATA_LENGTH + INDEX_LENGTH AS total_bytes,
    ROUND(
        (DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024,
        3
    ) AS total_mib
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'network_registry'
AND TABLE_NAME IN (
    'uuid_bulk_baseline_100k',
    'uuid_bulk_native_100k'
);


-- PART 7: Calculate the storage difference

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

FROM INFORMATION_SCHEMA.TABLES b

JOIN INFORMATION_SCHEMA.TABLES n
    ON b.TABLE_SCHEMA = n.TABLE_SCHEMA

WHERE b.TABLE_SCHEMA = 'network_registry'
AND b.TABLE_NAME = 'uuid_bulk_baseline_100k'
AND n.TABLE_NAME = 'uuid_bulk_native_100k';


-- PART 8: Clean up the temporary digit table

DROP TEMPORARY TABLE uuid_digits_100k;

-- End of Experiment
