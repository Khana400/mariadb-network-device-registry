-- Experiment 2: IPv4 Address Sorting
-- MariaDB Network Device Registry

-- Objective:
-- Compare how IPv4 addresses are sorted when stored
-- as VARCHAR(15) versus MariaDB's native INET4 type.

-- Start a transaction so test records can be removed.
START TRANSACTION;

-- Generate unique identifiers for four test devices.
SET @id1 = UUID();
SET @id2 = UUID();
SET @id3 = UUID();
SET @id4 = UUID();

-- PART 1: Insert data into the traditional table

INSERT INTO devices_baseline
(id, hostname, ip_address, device_type, location)
VALUES
(@id1, 'sort-demo-1', '10.0.0.2', 'Router', 'Test Lab'),
(@id2, 'sort-demo-2', '10.0.0.10', 'Router', 'Test Lab'),
(@id3, 'sort-demo-3', '10.0.0.100', 'Router', 'Test Lab'),
(@id4, 'sort-demo-4', '192.168.1.1', 'Router', 'Test Lab');

-- PART 2: Insert the same data into the native table

INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(@id1, 'sort-demo-1', '10.0.0.2', 'Router', 'Test Lab'),
(@id2, 'sort-demo-2', '10.0.0.10', 'Router', 'Test Lab'),
(@id3, 'sort-demo-3', '10.0.0.100', 'Router', 'Test Lab'),
(@id4, 'sort-demo-4', '192.168.1.1', 'Router', 'Test Lab');

-- PART 3: Traditional VARCHAR sorting

SELECT hostname, ip_address
FROM devices_baseline
WHERE hostname LIKE 'sort-demo-%'
ORDER BY ip_address;

-- PART 4: MariaDB-native INET4 sorting

SELECT hostname, ip_address
FROM devices_native
WHERE hostname LIKE 'sort-demo-%'
ORDER BY ip_address;

-- PART 5: Remove temporary test data

ROLLBACK;

-- End of Experiment 2