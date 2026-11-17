Our experiments and results
This file goes into a bit more detail about the experiments we ran for the Network Device Registry. The [README](../README.md) explains how to set up the database and run the scripts, so we won't repeat every command here. Instead, we'll focus on what we tested, what came out of it, and what the numbers mean.

The figures below are the results recorded during our development, not expected values that every computer must reproduce. The original SQL and Python files are in the repository if you want to run the tests yourself.
1. Trying an invalid IPv4 address
We first wanted to see whether the database could catch a bad IP address without writing a separate validation rule.

The test value was 999.999.999.999. It looks roughly like an IPv4 address, but the numbers are too large. An IPv4 address has four parts, each between 0 and 255.

When we inserted the address into the baseline table, the VARCHAR(15) column accepted it. This made sense once we thought about it: to that column, the address is just a string of characters.

The native table behaved differently. Its INET4 column rejected the value with:
ERROR 1292 (22007): Incorrect inet4 value
This happened with STRICT_TRANS_TABLES enabled. We used ROLLBACK afterward, so the temporary test rows were not kept.

For a device registry, we think this is a useful reason to choose INET4. Invalid addresses can cause problems later, and here the database itself helps catch them. This does not mean text columns can never be validated; they just need an extra rule or check.

File: sql/experiment_ip_validation.sql
2. Sorting IP addresses
The second test was about the order in which addresses appear. We inserted these four values into both tables:
10.0.0.2
10.0.0.10
10.0.0.100
192.168.1.1
We then ordered them using ORDER BY ip_address.

In the baseline table, the order was:
10.0.0.10
10.0.0.100
10.0.0.2
192.168.1.1
In the native table, the order was:
10.0.0.2
10.0.0.10
10.0.0.100
192.168.1.1
The difference is that the baseline column sorts text character by character. The native column understands the address as an IPv4 value and sorts it numerically.

We can still get numerical ordering from the baseline table by using INET_ATON(ip_address) in the ORDER BY clause. But that adds a conversion to the query. We looked at the performance effect of that choice later.

File: sql/experiment_ip_sorting.sql
3. How much space does UUID actually save?
This was one of the more interesting experiments because the first result was not what we expected from the theoretical sizes.

A UUID written as text normally takes 36 ASCII characters, including hyphens. MariaDB's UUID type stores it in 16 bytes. Looking at just the ID value, that is 20 bytes less, or a 55.56% difference compared with 36 bytes.

But tables also have other columns and internal storage, so we did a separate measurement with larger datasets. Both experimental tables received exactly the same generated UUIDs and hostnames. The ID column was CHAR(36) in one and UUID in the other.
10,000 records
Both versions reported 1,589,248 bytes, or 1.516 MiB. In other words, the measured difference was 0% at this size.

This does not mean the two UUID types use the same bytes internally. MariaDB's InnoDB engine allocates space in pages, so the reported size can be the same even when the individual values have different sizes.
100,000 records
The baseline table reported 7,913,472 bytes (7.547 MiB). The native table reported 5,783,552 bytes (5.516 MiB).

That was a 26.92% reduction in reported allocated space.
500,000 records
The baseline table reported 39,469,056 bytes (37.641 MiB). The native table reported 27,869,184 bytes (26.578 MiB).

The difference was 11,599,872 bytes, or about 11.06 MiB. The native table used 29.39% less reported allocated space in this test.
What this tells us
The gap grew more visible when we increased the number of rows. We think the larger tests show the storage advantage more clearly than a two-row example would.

There is an important limit to how we describe this result. We got the figures from INFORMATION_SCHEMA.TABLES, using its reported DATA_LENGTH and INDEX_LENGTH after analyzing the tables. These reflect InnoDB's page allocation; they are not exact measurements of the bytes occupied by every row. Also, the clustered primary key is included in DATA_LENGTH for these tables, even though INDEX_LENGTH can be zero.

We made one recorded storage measurement for each dataset size. We should not present these percentages as something every database would get.

The scripts are sql/experiment_uuid_storage.sql, sql/experiment_uuid_storage_bulk.sql, sql/experiment_uuid_storage_100k.sql, and sql/experiment_uuid_storage_500k.sql. The recorded measurements are saved in [`storage_measurements.csv`](../results/storage_measurements.csv).

4. The Python benchmark
After the correctness and storage tests, we wanted some actual timing results. We used scripts/benchmark.py, which connects to MariaDB with PyMySQL. The script generates matching data for two benchmark tables, repeats the test five times, and records the elapsed time with time.perf_counter().

We tested both 10,000 and 100,000 records. The order of the baseline and native runs was alternated, instead of always making one version go first. The results below are averages from the five rounds.
Inserting records
At 10,000 records, the baseline table took 0.2116 seconds on average, compared with 0.1681 seconds for native.

At 100,000 records, the averages were 1.2899 seconds for baseline and 0.9677 seconds for native.

So the native design had a lower average insertion time at both sizes we tested.

Finding records by UUID
This test measured the time for 200 UUID lookups in one round, not just one lookup.

With 10,000 records, the baseline average was 0.1107 seconds and native was 0.0769 seconds.

With 100,000 records, baseline was 0.0893 seconds and native was 0.0749 seconds.

Native was a little faster in both cases. The 100,000-record lookup did not simply take longer because the table was larger; short indexed queries can be affected by cached data and other conditions.

Sorting IP addresses numerically
Here the task was to get the first 1,000 numerically sorted IPv4 addresses.

The baseline query used ORDER BY INET_ATON(ip_address), because the IP address was stored as text. The native query used ORDER BY ip_address, since the column was already INET4.

For 10,000 records, the baseline average was 0.0074 seconds and native was 0.0020 seconds.

For 100,000 records, baseline was 0.0425 seconds and native was 0.0019 seconds.

This was the largest difference in our benchmark. To understand it better, we checked the query plans instead of just looking at the stopwatch.

Checking the sorting queries with EXPLAIN
EXPLAIN shows how MariaDB plans to run a query. For our 100,000-record sorting test, both versions reported the idx_ip index, but there was a difference in the extra work they needed.

The baseline query reported Using index; Using filesort, a key length of 62, and roughly 103,331 estimated rows. MariaDB still had to sort the converted text addresses.

The native query reported Using index, key length 4, and roughly 1,000 estimated rows. It did not report an additional filesort.

This explains why sorting directly on an indexed INET4 column helped in our test. The numbers from EXPLAIN are optimizer estimates, not a count of exactly how many rows MariaDB read.
What the benchmark cannot prove
Although native had lower average times in all the operations we measured, we cannot claim that UUID by itself made all of them faster. The baseline and native tables differ in both the ID type and IP address type. The sorting queries also use different query plans. On top of that, our timings include some Python and database connection overhead, and we only ran five rounds at each size.

This makes the benchmark a useful comparison of our two designs, not a universal rule for MariaDB performance.

You can find the raw files in [`benchmark_10000.csv`](../results/benchmark_10000.csv) and [`benchmark_100000.csv`](../results/benchmark_100000.csv). The SQL plan is in sql/experiment_explain.sql.
5. INSERT ... RETURNING
For this experiment, the question was whether we really need to insert a new device and then send another query just to read back the values we inserted.

We tested an INSERT followed by a SELECT, then compared it with INSERT ... RETURNING. Both approaches gave us the inserted details. The first used two main SQL statements; the second did the job in one.

That is useful if an application needs to show the newly added record. We did not run a separate performance benchmark for this feature, so we are only claiming that it simplifies the SQL in this case, not that we measured a speed increase.

The test rows were removed using ROLLBACK.

File: sql/experiment_returning.sql
Screenshot: results/screenshots/experiment_5_returning.png
6. INTERSECT and EXCEPT
This experiment used the two registries as if they were lists maintained by different people. We wanted to see which device names appeared in both lists, and which appeared in only one.

Both tables started with router-01 and laptop-01. We temporarily put legacy-printer only in the baseline table and new-switch only in the native table.

With INTERSECT, we got router-01 and laptop-01. With EXCEPT going from baseline to native, we got legacy-printer. Reversing the EXCEPT query gave new-switch.

For comparison, we tried INNER JOIN to find shared hostnames and NOT EXISTS to find missing ones. They gave the same answers in this example.

We liked how directly INTERSECT and EXCEPT describe the comparison. Still, this example only compares hostnames, not whole device records, and it was not a speed test. The extra rows were rolled back afterward.

File: sql/experiment_intersect_except.sql
Screenshot: results/screenshots/experiment_6_intersect_except.png
7. Automated checks and final thoughts
The test file tests/test_database.py has five automated checks: database column types, invalid IPv4 validation, IP sorting, INSERT ... RETURNING, and INTERSECT/`EXCEPT`. We recorded a run where all five passed in 0.159 seconds. We still recommend running them again after any changes:
python -m unittest discover -s tests -v
Looking back at all the results, INET4 was especially useful for this kind of database, since IP addresses are not really ordinary text. Native UUID storage also helped on the larger datasets we tested. For the performance experiment, we learned that reading the query plan matters: a faster time is interesting, but knowing that one query avoids a filesort helps explain it.

If you repeat the experiments on another machine, please record the MariaDB version, the dataset size, and the results you actually get. The timings and page allocations may differ. Also, be aware that the Python benchmark recreates its own tables and overwrites the selected result CSV, so keep a copy if you want to compare runs.