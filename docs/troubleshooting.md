Problems we ran into (and things to check)
We made this page so that someone trying the project does not have to guess what went wrong if a command fails. Some of the problems below happened while we were working on the registry, especially the Docker/WSL connection issue. Others are possible problems we wanted to warn readers about.

The normal setup steps are in the [README](../README.md). If you are checking the project for submission, also use the [verification guide](setup_verification.md).

Before changing anything: Do not delete your Docker database volume just because an error appears. docker compose down -v can remove the data that the container stores. For an ordinary stop, use docker compose stop instead.
Docker doesn't work in Ubuntu
At one point, our Ubuntu terminal could not find Docker even though we had already installed Docker Desktop on Windows. If you get docker: command not found, start by checking whether Docker Desktop is open and running.

In Docker Desktop, check Settings → Resources → WSL Integration and make sure your Ubuntu distribution has integration enabled. Then go back to Ubuntu and try:
docker --version
docker compose version
If Windows says WSL needs to be updated, open Windows PowerShell, not Ubuntu, and run:
wsl --update
You can also close the Ubuntu terminals, then run this from PowerShell:
wsl --shutdown
Afterward, restart Docker Desktop and reopen Ubuntu. Restarting the environment restored the connection in our case. If the message you get is different, check that specific error instead of assuming the same fix will work.
MariaDB doesn't start after docker compose up -d
First, make sure Docker is actually running. Then check the container and its recent messages:
docker compose ps
docker compose logs --tail=50 mariadb
Read the error in the logs. It might be a port conflict, an incorrect .env file, or an issue starting the database.

Our project uses port 3307 on the computer and 3306 inside Docker. If another application is already using port 3307, the container might not start. You can change the host port, but then the Python connection settings need to match too. Do not stop or delete unrelated containers just to make the port available.
The database password is rejected
First check whether .env exists. On a new installation, create it with:
cp .env.example .env
The file needs the MARIADB_ROOT_PASSWORD setting. You can check whether the Compose file is valid without displaying the password:
docker compose config --quiet
There is one detail that is easy to miss: the root password is set when MariaDB first creates its database files. If you already have a Docker volume with an initialized database, editing the password in .env does not automatically reset the password inside that database.

If an existing database rejects the new password, check which password was originally used. Do not delete the volume to reset it unless you have intentionally decided to lose that data and have a safe backup.

Also check that the container is running:
docker compose ps
The tables aren't there
If SHOW TABLES does not include devices_baseline and devices_native, we may not have run the schema files yet. Make sure the terminal is in the project's main folder and run:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/baseline_schema.sql

docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/native_schema.sql
Then check:
docker compose exec -T mariadb sh -c 'mariadb -u root -p"$MARIADB_ROOT_PASSWORD" network_registry -e "SHOW TABLES;"'
If you see extra tables, those may be from the storage or benchmark experiments. That does not mean the main registry is wrong.
There are more than two sample devices
The initial sample-data script inserts router-01 and laptop-01 into both tables. It generates new UUIDs each time it runs. If it is run twice, it creates more records instead of replacing the old ones.

Before rerunning sql/sample_data.sql, check whether those devices are already there. Do not delete records just to force the count back to two, especially if someone on the team has already added data.
The IPv4 experiment shows an SQL error
In this one case, an error is exactly what we were testing. The script tries to insert 999.999.999.999 into an INET4 column. We expect MariaDB to reject that address with ERROR 1292 under strict SQL mode.

The command uses --force so the client can keep going after the expected error and finish the rollback:
docker compose exec -T mariadb sh -c 'mariadb --force -u root -p"$MARIADB_ROOT_PASSWORD" network_registry' < sql/experiment_ip_validation.sql
Do not copy --force into every command. For normal setup, an unexpected SQL error is something we want to see and fix, not hide.
Python says a library is missing
If you see something like No module named pymysql, dotenv, or matplotlib, Python probably cannot find the project's installed packages.

From the main project folder, run:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
Then try your command again. When the virtual environment is active, the terminal usually shows (.venv) before the prompt. If installing packages gives another error, read the complete message; that may be a separate Python or network issue.
The automated tests fail
The test program needs to connect to MariaDB, so make sure the container is running and .env contains the correct password.
docker compose ps
python -m unittest discover -s tests -v
Run the tests from the project folder with the virtual environment active. We have a recorded development run where all five tests passed, but that does not mean every future test run will automatically pass.

If a test fails, keep the whole error output. The name of the failing test usually tells you whether the issue is with a connection, a data type, or a particular SQL operation.
A command can't find sql/ or results/
This often happens when the terminal is in the wrong folder. In Ubuntu, try:
cd ~/projects/mariadb-network-device-registry
pwd
ls
You should see docker-compose.yml, sql, scripts, and results.

On Windows, our project is inside WSL rather than the usual Documents folder. You can open that location in File Explorer using a path similar to:
\\wsl.localhost\Ubuntu\home\<your-linux-username>\projects\mariadb-network-device-registry
The username and the Ubuntu distribution name may be different on another computer.
The benchmark replaced an older CSV
scripts/benchmark.py writes its measurements to a selected CSV file. Running it again with the same filename overwrites the previous measurements. It also recreates its own benchmark tables.

If you want to compare two runs, make a copy of the old CSV first and give the new run a different output name. The benchmark is not supposed to delete devices_baseline or devices_native, but don't use its temporary tables for anything you need to keep.
The graphs won't appear
First, check that the input files are present:
ls -lh results/storage_measurements.csv results/benchmark_10000.csv results/benchmark_100000.csv
Then run:
python scripts/plot_results.py
The program should save five PNG files under results/graphs/. If it stops with an error, check whether the CSVs are missing, their columns have changed, or Matplotlib is not installed.

Don't change the results just to make a graph run. It is better to correct a filename or script error than to make the measurements inaccurate.
Someone gets different results
That can happen, especially with timings. The tests were run on a local development computer, and performance changes with caching, background processes, the database version, and the computer itself.

The UUID storage measurements are based on InnoDB's reported page allocation, so those may vary too. Our 10,000-row storage comparison even reported the same size for both tables, while the larger tables showed a difference.

If you repeat a run, record the actual numbers, the dataset size, and the MariaDB version. A different result is something to investigate, not something to edit until it matches the README.
Git shows ?? next to files
?? simply means Git sees a new file that has not been added to a commit. It does not mean anything has been uploaded.

These two commands are safe checks:
git status --short
git check-ignore .env .venv
The second command should show that .env and .venv are ignored. This matters because .env contains the database password, which must stay private.

git push is what uploads committed changes to GitHub. Team members should commit the work they genuinely contributed, including any later corrections or testing notes.
Stopping the database safely
When you're finished for the day, use:
docker compose stop
To start it again:
docker compose up -d
The Docker volume keeps the data between normal stops and restarts. Be careful with docker compose down -v, because it removes project volumes.

If your issue isn't listed here
Keep the command that failed and the full error message, but hide passwords or other private information. Write down whether the problem came from Docker, MariaDB, Python, or Git, and what you already tried.


