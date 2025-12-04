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
First, clone the repository on your server as usual :
```bash
git repo clone chikatetsu/SongRating
```
Then, install Python if it's not already done (I use Python 3.12).

Create your Python environment and install the required packages
([see requirements.txt](https://github.com/chikatetsu/song-rating-server/blob/main/requirements.txt)) :
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Now that the packages are installed, you can generate the `.env` file 
containing your personal authentication token :
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
