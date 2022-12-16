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

<p>4. In var directory create primary/data and primary/mount, secondary1/data and secondary1/mount, secondary2/data and secondary2/mount </p>

<p>5. Start the server with foreman</p>

```sh
foreman start
```

> ⚠ leaderboard service will try to connect but won't be able to until database is initilized in the next step

<p>6. Setting up the database</p>

```sh
./bin/init.sh
```

<p>7. Start redis server if haven't</p>

```sh
./redis.sh
```
<br/>

8. Configure your Nginx similar to [nginx.confg](nginx.confg)

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
