-- Experiment 4: Query Execution Plan Analysis
-- MariaDB Network Device Registry

-- Objective:
-- *Investigate why native INET4 sorting performs
-- *differently from VARCHAR-based numerical IP sorting.

-- Traditional implementation
-- Converts text addresses to numerical values.
-- Expected: additional sorting operation.

EXPLAIN
SELECT ip_address
FROM benchmark_baseline
ORDER BY INET_ATON(ip_address)
LIMIT 1000;


-- MariaDB-native implementation
-- Sorts directly using the indexed INET4 column.
-- Expected: index-based ordering without filesort.

EXPLAIN
SELECT ip_address
FROM benchmark_native
ORDER BY ip_address
LIMIT 1000;

-- End of execution plan analysis.
