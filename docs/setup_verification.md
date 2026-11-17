Checking that the project works
This is the guide I would use if I had to open the repository on another computer and check whether it is ready to submit. The main [README](../README.md) tells you how to set everything up. Here, the focus is on checking the setup and writing down what actually happened.

The project was tested during development, including a run where all five Python tests passed. However, we have not yet recorded a complete installation test from a separate, clean environment. The spaces at the end of this page are intentionally blank. Whoever performs the checks should fill them in with the real results rather than marking everything as passed in advance.
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
The five tests cover the schema types, IPv4 validation, IP address ordering, INSERT ... RETURNING, and INTERSECT/`EXCEPT`.

The earlier development run passed all five tests in 0.159 seconds. Do not use that number as your own test result. Record what your terminal says, even if a test fails. If it fails, save the error message so it can be fixed.
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
Verification notes — fill these in after running the commands
Person checking: __________________________
Date: __________________________
Existing setup or separate fresh setup? __________________________
Computer / operating system: __________________________
Git version: __________________________
Python version: __________________________
Docker and Compose versions: __________________________
MariaDB version: __________________________

Project folders found: Not checked / Passed / Failed
Docker configuration: Not checked / Passed / Failed
Container started: Not checked / Passed / Failed
Database schemas: Not checked / Passed / Failed
Sample records: Not checked / Passed / Failed
Five Python tests: Not checked / Passed / Failed
Five graphs: Not checked / Passed / Failed
SQL experiments (optional): Not checked / Passed / Failed / Not run
Git ignore check: Not checked / Passed / Failed

Test output or screenshot filename: __________________________
Any error messages: __________________________
What you changed to fix an issue: __________________________
Anything that still needs to be fixed: __________________________

