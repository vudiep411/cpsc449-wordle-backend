# CPSC 449 Group 21 Project 2
<p><b>Group Member:</b> Vu Diep, Sreevidya Sreekantham, <p/>

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
./start.sh
```
<br/>

6. Configure your Nginx similar to [nginx.config](nginx.config)

<br/>
<br/>


> ⚠ The development server for User service will be started at http://127.0.0.1:5100/ <br/>
> ⚠ The 3 development servers for Game service will be started at <br/>
http://127.0.0.1:5000/  <br/>
http://127.0.0.1:5001/  <br/>
http://127.0.0.1:5002/  <br/>

## Documentation

<p>After starting the server with foreman start, go to http://127.0.0.1:5000/docs and http://127.0.0.1:5100/docs for all REST API routes example</p>
