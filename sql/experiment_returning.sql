-- Feature 3: INSERT ... RETURNING
-- MariaDB Network Device Registry

-- Objective:
-- *Compare traditional INSERT + SELECT
-- *with INSERT ... RETURNING.

START TRANSACTION;

-- PART 1: Traditional approach

SET @traditional_id = UUID();

-- First statement: Register a device.

INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(
    @traditional_id,
    'returning-test-1',
    '192.168.10.10',
    'Router',
    'Test Lab'
);

-- Second statement: Retrieve the registered device.

SELECT id, hostname, ip_address, created_at
FROM devices_native
WHERE id = @traditional_id;


-- PART 2: MariaDB RETURNING approach

SET @returning_id = UUID();

-- Register and retrieve a device in one statement.

INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(
    @returning_id,
    'returning-test-2',
    '192.168.10.20',
    'Router',
    'Test Lab'
)
RETURNING id, hostname, ip_address, created_at;


-- PART 3: Compare the approaches

SELECT
    'Traditional INSERT + SELECT' AS approach,
    2 AS statements_required

UNION ALL

SELECT
    'INSERT RETURNING' AS approach,
    1 AS statements_required;


-- PART 4: Clean up

ROLLBACK;

-- Confirm the original records remain.

SELECT COUNT(*) AS remaining_devices
FROM devices_native;

-- End of Feature 3