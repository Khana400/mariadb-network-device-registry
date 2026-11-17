-- Traditional network device registry
-- UUIDs and IPv4 addresses are stored as strings.

CREATE TABLE IF NOT EXISTS devices_baseline (
    id CHAR(36) PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    device_type VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;