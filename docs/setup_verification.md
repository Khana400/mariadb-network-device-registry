Checking that the project works
This page has two purposes: it records the setup checks that we actually completed and gives another student the commands to repeat those checks. The main [README](../README.md) explains the whole project.
Checks completed on 17 November 2026
We ran these checks using our existing Windows laptop with Ubuntu/WSL2 and the project's running MariaDB Docker container. To avoid touching the original experiment data, we created a separate database called network_registry_setup_check.

Our first verification on 17 November 2026 used a newly created database inside our existing MariaDB container. At that time, we had not tested the project using a fresh GitHub clone or a new Docker volume.

We completed that additional verification on 19 November 2026 using a separate clone, a new MariaDB container, and a separate Docker volume. The results are documented at the bottom of this file.

Docker and the project files — passed
The command docker compose config --quiet completed without errors. The repository was accessible on GitHub without logging in, and the team confirmed that its commits were uploaded.
Database creation — passed
We created network_registry_setup_check and ran the exact sql/baseline_schema.sql and sql/native_schema.sql files against it. The two expected tables were created.
Sample records — passed
We ran sql/sample_data.sql once against the separate database and checked the row counts. The output reported 2 records in devices_baseline and 2 in devices_native. The sample hostnames were router-01 and laptop-01.
SQL experiments — passed
We ran the following scripts against the separate database:
- experiment_ip_sorting.sql — showed text sorting in the baseline table and numerical ordering with INET4.
- experiment_ip_validation.sql — the baseline accepted 999.999.999.999 and MariaDB rejected the INET4 insertion with the expected ERROR 1292. The transaction was rolled back.
- experiment_returning.sql — returned inserted data and rolled back temporary records.
- experiment_intersect_except.sql — found shared hostnames and the two hostnames present in only one table, then rolled back temporary records.
Automated tests — passed on our main development database
After the team uploaded its commits, we ran `python -m unittest discover -s tests -v`. Our original five tests passed in 0.256 seconds. Later, we added three more tests covering invalid UUIDs, IPv4 boundary values, and duplicate hostnames. We ran the updated test suite on 17 November 2026, and all eight tests passed. These test runs used our existing development database, not the isolated setup-check database.
Saved benchmark results and graphs — available
The repository contains the 10,000- and 100,000-row benchmark CSV files, the UUID storage measurements, and five generated graphs. We created and reviewed the graphs during development. We did not rerun the full bulk-storage experiments or benchmarks as part of this separate database check.

## Follow-up verification

After our first database check on 17 November 2026, we still needed to test the project using a fresh GitHub clone and a separate Docker volume.

We completed this additional check on 19 November 2026. We created a new MariaDB container, set up both tables, inserted sample data, and successfully ran four SQL experiments.

We also ran all eight automated tests in the fresh environment. All eight passed in 0.227 seconds.

We did not repeat the large UUID storage experiments or performance benchmarks during this check. The computer specifications and benchmark settings are documented separately in `docs/experiment_results.md`.

First, open the right folder
On our development laptop, the repository is inside Ubuntu/WSL. Open an Ubuntu terminal and enter:
cd ~/projects/mariadb-network-device-registry
If you are using a separate computer, clone the repository instead:
git clone https://github.com/Khana400/mariadb-network-device-registry.git
cd mariadb-network-device-registry
Look for README.md, docker-compose.yml, sql, scripts, tests, and results. You should also have a docs folder with this guide and the other documentation.

A check of our existing laptop setup is not the same as a fresh installation. If you use the existing database, call it an existing-setup check. Do not erase the working database just to simulate a clean setup. It contains experiment tables and saved data. A genuinely fresh test should use a separate environment or an isolated database after a backup.
1. Check the tools
We need Docker, Docker Compose, Python, and Git. These commands show which versions are installed:
git --version
python3 --version
docker --version
docker compose version
Write the versions in the notes at the bottom. Our own development setup used MariaDB 11.8.9, Python 3.14.4, Docker Engine 29.8.2, and Docker Compose 5.5.1, but another person's versions can be different.
2. Check the password file and Docker configuration
The .env file is local because it contains the MariaDB root password. On a new installation, create it from the example:
cp .env.example .env
Edit .env and choose a password. Do not include the password in this guide or in any screenshot.

Then check the Docker configuration:
docker compose config --quiet
If the configuration is valid, this command normally returns without printing an error.
3. Start MariaDB and check the version
Make sure Docker Desktop or the Docker Engine is running. Start the container:
docker compose up -d
docker compose ps
The database container should appear as network-registry-db. Its database is called network_registry, and port 3307 on the computer connects to MariaDB inside Docker.

For a new database, it may take a little time to finish starting. Once it is ready, check the server version:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "SELECT VERSION();"'
If MariaDB is not starting, look at the [troubleshooting guide](troubleshooting.md) before making changes to the container or its storage.
4. Check the tables
On a genuinely new database, run the two schema files:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/baseline_schema.sql

docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/native_schema.sql
Check the structure:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry -e "SHOW TABLES; DESCRIBE devices_baseline; DESCRIBE devices_native;"'
Look for devices_baseline and devices_native. The baseline table should have CHAR(36) for the ID and VARCHAR(15) for the address. The native table should use UUID and INET4.

You may see other tables if you are working with an already-used database. That is normal because the storage and benchmark experiments create their own tables.
5. Check the sample records
If the database is new and empty, load the sample data once:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/sample_data.sql
Then display the two sets of devices:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry -e "SELECT hostname, ip_address FROM devices_baseline; SELECT hostname, ip_address FROM devices_native;"'
A fresh database should have router-01 with 192.168.1.1 and laptop-01 with 10.0.0.2 in both tables.

Do not run sample_data.sql again on a database that already has these records. It creates new UUIDs and inserts extra rows. If you find more than two records, note that in your results rather than deleting anything without checking with the team.
6. Run the Python tests
The project uses a Python virtual environment. If you do not have one yet:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
With MariaDB running, run:
python -m unittest discover -s tests -v
The eight tests cover the schema types, IPv4 validation, IP address ordering, INSERT ... RETURNING, INTERSECT/EXCEPT, invalid UUID validation, IPv4 boundary values, and duplicate hostname handling.

Our original five-test run passed in 0.256 seconds. After adding three more tests, all eight tests passed in 0.174 seconds on 17 November 2026. During our fresh-installation verification on 19 November 2026, all eight tests passed again in 0.227 seconds. Do not use these times as your own result; timing can be different on another machine. Record what your terminal says, even if a test fails. If it fails, save the error message so it can be fixed.

7. Check the saved measurements and graphs
The numbers used in our report are stored in CSV files. Confirm that the files exist:
ls -lh results/storage_measurements.csv results/benchmark_10000.csv results/benchmark_100000.csv
Generate the images again:
python scripts/plot_results.py
Then open results/graphs/ in VS Code. There should be five PNG files:
uuid_storage_comparison.png
uuid_storage_reduction.png
insertion_performance.png
uuid_lookup_performance.png
ip_sorting_performance.png
Check that the pictures open and the labels make sense. If any file is missing or a graph does not look right, write down the problem.

You do not need to rerun the entire performance benchmark to check that the saved graphs work. scripts/benchmark.py recreates benchmark tables and overwrites the chosen CSV file, so save a copy of previous results before repeating it.
8. Repeat a few SQL experiments (optional)
These commands let you check the shorter SQL demonstrations again:
# Invalid IPv4 test — an ERROR 1292 is expected here
docker compose exec -T mariadb sh -c 'mariadb --force -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/experiment_ip_validation.sql

# IPv4 ordering
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/experiment_ip_sorting.sql

# INSERT ... RETURNING
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/experiment_returning.sql

# INTERSECT and EXCEPT
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/experiment_intersect_except.sql
The first script intentionally uses an invalid address. Its error is part of the test, not a sign that the whole database is broken. The scripts use transactions to undo their temporary changes.

sql/experiment_explain.sql needs the benchmark tables to exist first, so do not run it on a brand-new database unless you have also run the benchmark.

See [our experiment notes](experiment_results.md) for the results you should be comparing with.
9. Check which files Git will ignore
Before uploading anything, check:
git status --short
git check-ignore .env .venv
These commands only show information; they do not upload files. .env and .venv should appear in the ignored list. The .env file must stay private because it contains the database password.
Repeating our isolated-database check (without deleting your data)
If you already have the MariaDB container running, these commands create a new database instead of modifying your original network_registry database. Run them from the project folder. If the check database already exists, do not insert the sample data again.

Create the separate database once:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" -e "CREATE DATABASE network_registry_setup_check;"'
Run the two schema scripts and the sample-data script against the separate database:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/baseline_schema.sql
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/native_schema.sql
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/sample_data.sql
Check the row counts:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' <<'SQL'
SELECT 'Traditional' AS implementation, COUNT(*) AS total_devices
FROM devices_baseline
UNION ALL
SELECT 'MariaDB Native', COUNT(*)
FROM devices_native;
SQL
The expected result is 2 rows in each table when run on a newly created database.

To repeat the four shorter SQL experiments against the check database:
# Intentional error 1292 is expected from INET4 validation
docker compose exec -T mariadb sh -c 'mariadb --force -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/experiment_ip_validation.sql

docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/experiment_ip_sorting.sql

docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/experiment_returning.sql

docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry_setup_check' < sql/experiment_intersect_except.sql
Important: --force is only used for the validation script because the rejected INET4 value is expected. For all other setup scripts, an error should be investigated.

## Fresh Installation Verification — 19 November 2026

We also tested our project using a completely fresh GitHub clone.

We cloned the repository into a separate folder and created a new MariaDB 11.8 container with its own Docker volume. To avoid conflicts with our original database, we used a separate Docker Compose configuration and port 3308 instead of 3307.

We successfully created both database tables and inserted the sample devices. Both tables contained two records.

We then ran the IPv4 sorting, IPv4 validation, INSERT ... RETURNING, and INTERSECT/EXCEPT experiments. All four produced the expected results.

Finally, we installed the Python requirements in a new virtual environment and ran all eight automated tests against the fresh database. We changed the test connection port to 3308 in the temporary clone so the tests would connect to the new container.

**Result: All 8 tests passed in 0.227 seconds, with no failures.**

This confirmed that our database setup and main SQL features worked in a fresh installation. We did not repeat the large UUID storage experiments or performance benchmarks during this check.