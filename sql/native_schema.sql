-- MariaDB-native network device registry
-- Uses specialized UUID and INET4 data types.

CREATE TABLE IF NOT EXISTS devices_native (
    id UUID PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address INET4 NOT NULL,
    device_type VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;