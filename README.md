# CPSC 449 Group 21 Project 3
<p><b>Group Member:</b> Vu Diep, Shridhar Bhardwaj, Anvit Rajesh Patil</p>

## Installations
<p>1. Clone the repository</p>

```sh
git clone https://github.com/vudiep411/cpsc449-wordle-backend.git
```
<p>2. cd into the root directory</p>

```sh
cd cpsc449-wordle-backend/
```
<p>3. Install libraries needed</p>

```sh
./bin/requirements.sh
```
<p>4. Setting up the database</p>

```sh
./bin/init.sh
```
<p>5. Start the server with foreman</p>

```sh
foreman start
```

<p>6. Start redis server</p>
```sh
./redis.sh
```
<br/>

6. Configure your Nginx similar to [nginx.confg](nginx.confg)

<br/>
<br/>


> ⚠ The development server for User service will be started at http://127.0.0.1:5000/ <br/>
> ⚠ The 3 development servers for Game service will be started at <br/>
http://127.0.0.1:5100/  <br/>
http://127.0.0.1:5200/  <br/>
http://127.0.0.1:5300/  <br/>
> ⚠ Leaderboard service will be started at http://127.0.0.1:5400/ <br/>

To access leaderboard data through nginx, visit http://tuffix-vm/leaders

## Documentation

<p>After starting the server with foreman start, go to http://127.0.0.1:5000/docs, http://127.0.0.1:5100/docs, and http://127.0.0.1:5400/docs for all REST API routes example</p>
