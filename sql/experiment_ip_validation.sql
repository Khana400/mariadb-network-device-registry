-- Experiment 1: IPv4 Address Validation
-- MariaDB Network Device Registry

-- Objective:
-- *Compare how VARCHAR(15) and INET4 handle
-- *invalid IPv4 addresses.

-- Display the current SQL mode.
SELECT @@SESSION.sql_mode AS active_sql_mode;

-- Start a transaction to keep the database clean.
START TRANSACTION;

-- Generate a unique identifier for the test device.
SET @test_id = UUID();

-- PART 1: Traditional VARCHAR(15) Validation

-- Insert an invalid IPv4 address into the baseline table.

INSERT INTO devices_baseline
(id, hostname, ip_address, device_type, location)
VALUES
(@test_id, 'validation-demo', '999.999.999.999',
 'Router', 'Test Lab');

-- Check whether the invalid address was accepted.

SELECT hostname, ip_address
FROM devices_baseline
WHERE hostname = 'validation-demo';

-- PART 2: MariaDB-Native INET4 Validation

-- Attempt to insert the same invalid IPv4 address.
-- Under strict SQL mode, this should produce ERROR 1292.

INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(@test_id, 'validation-demo', '999.999.999.999',
 'Router', 'Test Lab');

-- Check whether the invalid record was stored.

SELECT hostname, ip_address
FROM devices_native
WHERE hostname = 'validation-demo';

-- PART 3: Clean Up

-- Remove temporary test data.
ROLLBACK;

-- Verify that the original records remain.

SELECT COUNT(*) AS baseline_count
FROM devices_baseline;

SELECT COUNT(*) AS native_count
FROM devices_native;

-- End of Experiment 1
