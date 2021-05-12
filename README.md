
# Fast API one time secret API 

https://github.com/MasonEgger/tech-talk-ots

This is from the Digtial Ocean Tech Talk on FastAPI  5/5/2021
https://www.digitalocean.com/community/tech_talks/getting-started-with-python-fastapi
https://www.youtube.com/watch?v=KVlqN0xNJxo


This API is for creating, storing, and sharing secrets. A user can securely store a secret with this API and send the passphrase and ID to a person who will be able to access the secret one time and one time only. The person creating the secret can also set an expiration time if the secret isn't viewed quickly enough. 
This is a remake of onetimesecret.com.
https://onetimesecret.com



## Original Flask version 

NOTE: the original flask version here:  https://github.com/do-community/python-ots-api



## Requirements 


### Redis 

NOTE: Uses redis - mostly because of the expire feature in REDIS which can automatically expire records


REDIS for Windows
https://dev.to/divshekhar/how-to-install-redis-on-windows-10-3e99
https://redislabs.com/blog/redis-on-windows-10/  (via WSL)

The `redis-cli ping` command works
Issue with the fastapi app hanging was due to forgetting to set the environment variable `export REDIS_SSL=false`
After setting this it worked.  (And don't forget to set env `SALT`)

https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04
https://stackoverflow.com/questions/55579342/why-systemd-is-disabled-in-wsl
https://stackoverflow.com/questions/54502444/why-systemctl-not-working-in-ubuntu-terminal-on-windows
https://stackoverflow.com/questions/52197246/system-has-not-been-booted-with-systemd-as-init-system-pid-1-cant-operate
`service redis-server start`
`service status --all`




REDIS for Mac
https://phoenixnap.com/kb/install-redis-on-mac  (with or without Homebrew)
(NOTE: this works without homebrew - downloaded the source and was able to compile it and total size was 27MB)

```
./redis-server -v
```
Redis server v=6.2.3 



### Python vritual environment

Set up your python virtual environment

```
python3 -m venv ~/.virtualenvs/fastapi

. ~/.virtualenvs/fastapi/bin/activate

pip install fastapi uvicorn redis cryptography python-multipart jinja2 requests

```

Or you could also install from requirements.txt
```
pip install -r requirements.txt
```


## Running 

NOTE: if you run locally, you will need to set the following environment variables:

```
export SALT="sammySammyDoDo"
export REDIS_SSL=False
```


The command to start the FastAPI app
```
uvicorn app:app --reload
```

NOTE: for this demo app you'll need a REDIS database.   You can run one locally or on a DO droplet.  If you run locally be sure to set `export REDIS_SSL=false`



## Using the API

NOTE: the following examples use HTTPie.  You could alternatively use `curl`

### Create secret

```
http POST localhost:8000/secrets message="Hello World" passphrase="loki"

http POST localhost:8000/secrets message="Hello World" passphrase="loki" expire_seconds=15
```



### Retrieve secret

Then to retrieve it via a POST request:
```
http POST localhost:8000/secrets/UUID_string passphrase=loki
```



## Web Form 

So it appears that I need to specify different endpoint paths for API calls and for the web form.
If I don't then request is sent with with json and not x-www-form-urlencoded.  


Reference
https://github.com/tiangolo/fastapi/issues/1989



References
https://stackoverflow.com/questions/61872923/supporting-both-form-and-json-encoded-bodys-with-fastapi
https://github.com/tiangolo/fastapi/issues/990
 
https://stackoverflow.com/questions/60127234/fastapi-form-data-with-pydantic-model
 
The following would have been an elegant solution, but it doesn't seem to work:
https://stackoverflow.com/questions/65120116/python-fastapi-post-unprocessable-entity-error
 

https://stackoverflow.com/questions/60127234/fastapi-form-data-with-pydantic-model/60670614#60670614
https://github.com/tiangolo/fastapi/issues/2387
 
 


#### Add copy functionality
https://stackoverflow.com/questions/36639681/how-to-copy-text-from-a-div-to-clipboard

