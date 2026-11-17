-- Sample data for comparing traditional and native data types.

-- Generate a unique ID for our first device.
SET @device_id = UUID();

-- Insert the device into the traditional table.
INSERT INTO devices_baseline
(id, hostname, ip_address, device_type, location)
VALUES
(@device_id, 'router-01', '192.168.1.1', 'Router', 'Building A');

-- Insert the SAME device into the native table.
INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(@device_id, 'router-01', '192.168.1.1', 'Router', 'Building A');


-- Generate another unique ID.
SET @device_id = UUID();

-- Traditional table.
INSERT INTO devices_baseline
(id, hostname, ip_address, device_type, location)
VALUES
(@device_id, 'laptop-01', '10.0.0.2', 'Laptop', 'Library');

-- Native table.
INSERT INTO devices_native
(id, hostname, ip_address, device_type, location)
VALUES
(@device_id, 'laptop-01', '10.0.0.2', 'Laptop', 'Library');