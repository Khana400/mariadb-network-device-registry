-- Feature 4: INTERSECT and EXCEPT
-- MariaDB Network Device Registry

-- Objective:
-- *Compare two device registries and identify:
-- 1. Devices present in both registries
-- 2. Devices missing from the native registry
-- 3. Devices missing from the baseline registry

START TRANSACTION;

-- PART 1: Prepare test data

-- Add a device only to the traditional registry.

SET @baseline_id = UUID();

INSERT INTO devices_baseline
(id, hostname, ip_address, device_type, location)
VALUES
(
    @baseline_id,
    'legacy-printer',
    '192.168.1.50',
    'Printer',
    'Library'
);

-- Add a different device only to the native registry.

SET @native_id = UUID();

INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(
    @native_id,
    'new-switch',
    '192.168.1.60',
    'Switch',
    'Building A'
);

-- PART 2: INTERSECT

-- Find device hostnames present in both registries.

SELECT hostname
FROM devices_baseline

INTERSECT

SELECT hostname
FROM devices_native;


-- PART 3: EXCEPT

-- Find devices missing from the native registry.

SELECT hostname
FROM devices_baseline

EXCEPT

SELECT hostname
FROM devices_native;


-- Find devices missing from the traditional registry.

SELECT hostname
FROM devices_native

EXCEPT

SELECT hostname
FROM devices_baseline;


-- PART 4: Traditional SQL comparison

-- Find common devices using INNER JOIN.

SELECT DISTINCT b.hostname
FROM devices_baseline b
INNER JOIN devices_native n
    ON b.hostname = n.hostname;


-- Find devices missing from the native registry
-- using NOT EXISTS.

SELECT DISTINCT b.hostname
FROM devices_baseline b
WHERE NOT EXISTS (
    SELECT 1
    FROM devices_native n
    WHERE n.hostname = b.hostname
);


-- PART 5: Clean up

ROLLBACK;

-- Verify original records remain.

SELECT COUNT(*) AS baseline_count
FROM devices_baseline;

SELECT COUNT(*) AS native_count
FROM devices_native;

-- End of Feature 4
