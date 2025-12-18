# Song Rating API

This is the server part of the Song Rating environment. It's an API
developped in Python using FastAPI and Uvicorn. The server is a centralized
way to store the leaderboard since you can run a Song Rating client on
different devices. The API exposes routes to get the leaderboard, vote for
a song, get info on the current rate of a song or artist, and see if a song 
has already been compared to an other. See `/docs` for all endpoints.

The server uses two main ways to create the leaderboard :
- **An Oriented graph** : the more a song has descendants, the better it is
- **An Elo rating system** : used in competitive games like chess, it's the
fastest way to get good results in the leaderboard

Since Song Rating is a personal project, it is not made for multiple users 
on the same instance of the environment. With that in mind, this API is 
made to be self-hosted on a home server or a cloud server. Also, an
unique authentication token needs to be generated and used by your clients
to work with this API.

## Installation
### 1. Install Python
If it's not already done, install Python on your server. I use Python 3.12.

### 2. Create the Python Environment
Create your Python environment and install the required packages
([see requirements.txt](https://github.com/chikatetsu/song-rating-server/blob/main/requirements.txt)) :
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Generate the authentication token
Now that the packages are installed, you can generate the `.env` file 
containing your personal authentication token.

**I highly recommend you to generate this token to protect the data on your server. Without the**
`.env` **file, the API will be accessible without any authentication token. If you are willing to take that risk and that your server is only accessible at your house, you can skip this step.**
```bash
python generate_token.py
```
A `.env` file should have been created with this format (or [see example](https://github.com/chikatetsu/song-rating-server/blob/main/.env-example)) :
```dotenv
AUTH_TOKEN=your_token_here
```
You can use this file in every Song Rating client to authenticate. You can
eather recreate this file or copy it from the server using the `scp`
command (see 
[documentation](https://linux.die.net/man/1/scp) and
[examples](https://learn.microsoft.com/en-us/azure/virtual-machines/copy-files-to-vm-using-scp)).

**Every time your authentication token seems compromised, you can rerun the**
`generate_token.py`
**script to erase your current token and recreate a new one. Don't forget to kill the API before running the script, and share the new**
`.env` **file to your Song Rating clients.**

### 4. Init the Database
Create an empty database by running the `build_schema_sql.sh` script :
```bash
./build_schema_sql.sh
```
A file named `rank.sql` should appear at the root of the project.

### 5. Load a database from a JSON file (optional)
In case you already runned the API from a previous version, you can keep your
previous leaderboard by loading the database with your old `rates_graph.json file` :
```bash
python app/db_connection.py
```

### 6. Run the API
You can now run the API using Uvicorn. Feel free to add more arguments to this
command if needed ([see documentation of Uvicorn](https://uvicorn.dev/#command-line-options)) :
```bash
uvicorn main:app
```
Your Song Rating server is now up and running, ready to rank your songs!

## Coming soon
- [ ] Pagination
- [ ] Enhancement for the graph leaderboard
- [ ] Single artist rank
