A project for area 1, "SQL that saves you work" for the [MariaDB student database projects, 2026-09](https://mariadb.org/bachelor_hackathon_2026-09/).

# MariaDB Network Device Registry

## Project Overview

This project explores how MariaDB-specific SQL features can improve database design compared with traditional approaches.

We are building a Network Device Registry for storing information about devices such as routers, laptops, servers, printers, and access points.

The project focuses mainly on two MariaDB-native data types:

- `UUID`
- `INET4`

These features will be compared with traditional approaches that use:

- `CHAR(36)` for UUID values
- `VARCHAR(15)` for IPv4 addresses

Our goal is to investigate whether MariaDB-native data types provide advantages in validation, sorting, storage, indexing, query simplicity, and performance.

---

## Research Question

How do MariaDB's native `UUID` and `INET4` data types improve the design of a network-device database compared with storing UUIDs and IPv4 addresses as strings?

---

## Team

This project is being developed by a group of four students.

- **Member 1:** Kevin Kotarja
- **Member 2:** Eda Zekjiri
- **Member 3:** Rasul Sharifov
- **Member 4:** Elena Lazic

---

## Project Features

The project will focus primarily on:

### UUID

MariaDB provides a native `UUID` data type that can be used instead of storing UUID values as text.

We will compare:

```sql
CHAR(36)
```

with:

```sql
UUID
```

We will investigate differences in:

- Storage requirements
- Validation
- Indexing
- Query performance
- Ease of use

---

### INET4

MariaDB provides the `INET4` data type for storing IPv4 addresses.

We will compare:

```sql
VARCHAR(15)
```

with:

```sql
INET4
```

We will investigate differences in:

- IP address validation
- Sorting
- Storage requirements
- Search performance
- Indexing
- Handling invalid IP addresses

---

## Example Database

The project will contain two implementations of the same device registry.

### Traditional Implementation

The traditional version stores identifiers and IP addresses as strings.

Example:

```sql
CREATE TABLE devices_baseline (
    id CHAR(36) PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address VARCHAR(15) NOT NULL,
    device_type VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### MariaDB-Native Implementation

The MariaDB version uses native MariaDB data types.

Example:

```sql
CREATE TABLE devices_native (
    id UUID PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address INET4 NOT NULL,
    device_type VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Example Device Data

The database will contain devices such as:

| Hostname | IP Address | Device Type | Location |
|---|---|---|---|
| router-01 | 192.168.1.1 | Router | Building A |
| laptop-01 | 10.0.0.2 | Laptop | Room 101 |
| laptop-02 | 10.0.0.10 | Laptop | Room 102 |
| server-01 | 172.16.1.5 | Server | Server Room |
| printer-01 | 192.168.1.20 | Printer | Library |

Larger datasets will later be generated automatically for performance experiments.

---

## Planned Experiments

We will perform controlled experiments comparing the traditional implementation with the MariaDB-native implementation.

### Experiment 1 — IP Address Validation

We will test how both databases handle valid and invalid IPv4 addresses.

For example:

```text
192.168.1.10
10.0.0.5
999.999.999.999
```

The purpose is to determine whether the database itself can detect invalid IP addresses.

---

### Experiment 2 — IP Address Sorting

We will compare how IP addresses are sorted when stored as:

```text
VARCHAR
```

versus:

```text
INET4
```

Example addresses:

```text
10.0.0.2
10.0.0.10
10.0.0.100
192.168.1.1
```

---

### Experiment 3 — UUID Storage

We will compare UUID values stored using:

```text
CHAR(36)
```

and:

```text
UUID
```

We will investigate differences in storage size and database behavior.

---

### Experiment 4 — Query Performance

Using a larger dataset, we will compare operations such as:

- Inserts
- Searches
- Sorting
- Indexed lookups

Each experiment will be repeated several times so that the results are more reliable.

---

## Technology

The project is expected to use:

- MariaDB
- Docker
- Docker Compose
- SQL
- Python
- Git
- GitHub

A simple Python application may also be added later to demonstrate how an application interacts with both database designs.

---

## MariaDB Version

The exact MariaDB version used for the project will be recorded here once the development environment is configured.

```text
MariaDB version: TODO
```

---

## Project Structure

The repository is planned to use the following structure:

```text
mariadb-network-device-registry/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── sql/
│   ├── baseline_schema.sql
│   ├── native_schema.sql
│   ├── sample_data.sql
│   └── experiments.sql
│
├── scripts/
│   ├── generate_data.py
│   ├── load_data.py
│   └── benchmark.py
│
├── app/
│   └── main.py
│
├── tests/
│   └── test_database.py
│
└── results/
    ├── benchmark.csv
    └── screenshots/
```

This structure may change as the project develops.

---

## Installation

The project will be designed so that another student can reproduce the database environment locally.

### Requirements

Before running the project, install:

- Git
- Docker Desktop
- Docker Compose

Python may also be required for data-generation and benchmark scripts.

---

## Running the Project

The final project should be runnable using Docker.

The expected setup process will be similar to:

```bash
git clone YOUR_REPOSITORY_URL
cd mariadb-network-device-registry
docker compose up -d
```

Additional setup instructions will be added as development continues.

---

## Generating Test Data

A Python script will be provided to automatically generate network-device records.

The generated data will include:

- UUIDs
- Hostnames
- IPv4 addresses
- Device types
- Locations

This will allow the same experiments to be reproduced using datasets of different sizes.

Example dataset sizes may include:

```text
1,000 devices
10,000 devices
100,000 devices
```

---

## Results

Experiment results will be added to this section.

Results may include:

- Tables
- Performance measurements
- Storage measurements
- Screenshots
- Charts
- Error examples
- Query output

Example comparison:

| Test | Traditional | MariaDB Native |
|---|---|---|
| UUID storage | `CHAR(36)` | `UUID` |
| IP storage | `VARCHAR(15)` | `INET4` |
| Invalid IP validation | To be tested | To be tested |
| IP sorting | To be tested | To be tested |
| Storage usage | To be measured | To be measured |
| Query performance | To be measured | To be measured |

---

## Limitations

The project will not only investigate the advantages of MariaDB-native features.

We will also examine situations where these features may not provide a significant advantage.

Questions we plan to investigate include:

- Does native UUID storage always improve performance?
- Does the difference matter for very small databases?
- What happens when invalid data is imported?
- Are there situations where storing an IP address as text is more appropriate?
- How do indexes behave with the different data types?

Any limitations discovered during testing will be documented here.

---

## Expected Outcome

The goal of this project is not simply to demonstrate that MariaDB supports `UUID` and `INET4`.

Instead, we want to determine:

1. What problems these features solve.
2. How they compare with traditional approaches.
3. What measurable differences they produce.
4. When developers should use them.
5. When they may not be necessary.

The final repository should act as both a working database project and a tutorial that another student can reproduce and learn from.
