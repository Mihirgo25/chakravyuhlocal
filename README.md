
# Welcome to Dynamic Pricing Engine

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

### Using Envision CLI
Envision provides with a CLI, providing server,shell and more to come commands

Run these commands before we start
```
cd src
```
```
pip install --editable .
```

#### Develop

The `develop` command starts the development server if a port is busy it will select the next port. This server will continually watch for file changes and reload the server accordingly.

```bash
> envision server develop
```
#### Start

The `start` command starts a envision web server of production grade. It's an alias to the [uvicorn](https://www.uvicorn.org/) web server, it contains all of the options available with that server.

```bash
> envision server start --help
Usage: maps server start [OPTIONS] main:app

Options:
  --port INTEGER                  Bind socket to this port.  [default: 8000]
  --reload                        Enable auto-reload.
  --reload-dir TEXT               Sets reload directories explicitly, instead
                                  of using the current working directory.
  ...
```

#### Shell

The `shell` command is useful for development. It drops you into an python shell with the database connection.

```bash
> envision server shell
```

Envision shell has autoreload enabled, to disable it run

```
%autoreload 0
```

to enable it again run

```
%autoreload
```

to reload it just once run 

```
%autoreload 2
```


### Without using Envision CLI

```
$ python3 -m pip install --upgrade -r requirements.txt
```

pip3 freeze > requirements.txt

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!


## Start Celery

```
$ celery -A celery_worker.celery worker -B --loglevel=info -Q communication,critical,low,fcl_freight_rate

```

## Start Flower

```
$ celery -A celery_worker.celery flower --port=5555

```
