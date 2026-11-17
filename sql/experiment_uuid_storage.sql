
-- Experiment 3: UUID Storage Comparison
-- MariaDB Network Device Registry

-- Objective:
--  *Compare storing UUIDs as CHAR(36)
--  *versus MariaDB's native UUID data type.

-- PART 1: Examine the column data types


SELECT
    TABLE_NAME,
    COLUMN_NAME,
    COLUMN_TYPE,
    CHARACTER_SET_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'network_registry'
  AND TABLE_NAME IN ('devices_baseline', 'devices_native')
  AND COLUMN_NAME = 'id';


-- PART 2: Examine the stored UUID values

-- Traditional implementation

SELECT id, hostname
FROM devices_baseline;

-- MariaDB-native implementation

SELECT id, hostname
FROM devices_native;


-- PART 3: Compare theoretical identifier sizes

-- A standard UUID represented as ASCII text
-- contains 36 bytes, including hyphens.
-- MariaDB's native UUID type uses 16 bytes.

SELECT
    36 AS uuid_text_ascii_bytes,
    16 AS uuid_native_bytes,
    36 - 16 AS bytes_saved_per_identifier,
    ROUND(((36 - 16) / 36) * 100, 2)
        AS percentage_reduction;


-- PART 4: Check the number of records


SELECT COUNT(*) AS baseline_records
FROM devices_baseline;

SELECT COUNT(*) AS native_records
FROM devices_native;


-- End of Experiment 3 - Part A
