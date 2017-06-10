[![Docker Automated buil](https://img.shields.io/docker/automated/jrottenberg/ffmpeg.svg)](https://hub.docker.com/r/fgouteroux/platus/)

## What is Platus

Platus is an python flask app to check **platform's health.** The name come from **platform** and **status**.
You defines wich services you want to monitor and host it on your own server. Services check are based on plugin system.

Currently supported plugins:

- HTTP Rest
- MongoDB
- Celery
- AWS EC2


## Usage

**Web** 

In a browser: *http://localhost:5001*

![platus](images/platus.gif)

**Api**

Request:

    curl -u "admin:admin" http://localhost:5001/api/v1.0/status

Response:

```json
{
  "result": [
    {
      "checked": "2017-04-30 16:57:57.459312",
      "last_state": "operational",
      "name": "myapp03",
      "node": "abou.gitlab.com",
      "retries": 14,
      "state": "unknown",
      "type": "App"
    },
    {
      "checked": "2017-04-30 16:58:04.687229",
      "elapsed": "0:00:00.729046",
      "last_state": "operational",
      "name": "myapp01",
      "node": "status.aws.amazon.com",
      "retries": 18,
      "state": "unhealthy",
      "type": "App"
    },
    {
      "checked": "2017-04-30 16:58:06.625887",
      "elapsed": "0:00:00.857806",
      "last_state": "operational",
      "name": "myapp02",
      "node": "status.github.com",
      "retries": 0,
      "state": "operational",
      "type": "App"
    },
    {
      "checked": "2017-04-30 16:58:05.451147",
      "last_state": "operational",
      "name": "EC2 Instance",
      "node": "i-0ee58c9d8db8be69b",
      "nodename": "test",
      "retries": 2,
      "state": "down",
      "type": "Infra"
    }
  ]
}
```

**Users**

Manage users and roles in **users.yaml** (default path in **/data/config.yaml**).

Use **roles** to grant permissions to get services status defined in **services.yaml**


```yaml
admin:
    role:
        - admin
    password: admin

user1:
    role:
        - dev
    password: pass

user2:
    role:
        - dev
        - app
    password: pass
```

**Services**

Create **services.yaml** (default path in **/data/config.yaml**).

```yaml
resource01:
    role: dev
    type: plugin_to_call
    properties:
        host: resource1.lan
        port: 80
        protocol: http
    data:
        type: App
        name: myapp01

resource02:
    role:
        - app
        - dev
    type: plugin_to_call
    properties:
        host: resource2.lan
        port: 80
        protocol: http
    data:
        type: App
        name: myapp02
```

## Notifications

Send a notification if a service status changed. Enable it in config.yaml:

```yaml
    notify: True
```
When a service state is down or unhealthy, platus will check 3 times before sending a notification to avoid having too many notifications.

This setting could be overriden in config.yaml:

```yaml
    retries_before_notify: 2
```

**Need storage feature enabled.**

Platus support multiple notifications backend:
- slack
- email

### Slack

```yaml
notify_backend:
  type: slack
  data:
    url: slack-hook-url
```

### Email

```yaml
  notify_backend:
    type: email
      data:
        fr: team1@example.org
        to: team2@mexamle.org
        host: mail.smtp.com
        username: user
        password: pass
        subject: "Services status changed"
```

## Backends

Store services status in a storage backend. Enable it in config.yaml:

```yaml
  persistent_data: True
```

Platus support multiple storage backend:
- redis
- mongodb (coming soon)

### Redis

```yaml
  persistent_data_backend:
    type: redis
    data:
      host: redis
```
## Vault

Store services secret in [vault](https://www.vaultproject.io/) and let's platus ask the secret when necessary.

**How it works:**

- Platus ask to vault **the secret** corresponding to the key
- Vault respond with the **decrypted secret**
- Platus use **this secret** to check the service status

Enable it in **config.yaml**:

```yaml
  vault: False
  vault_backend:
    host: vault
    port: 8200
    protocol: http
    token: "vault-token"
    path: /v1/secret/
```

To use vault secrets, prepend each service property desired with "**vault_**"

*Example:*

```yaml
resource01:
    type: rest_http
    properties:
        host: resource1.lan
        port: 80
        protocol: http
        vault_username: resource01_username
        vault_password: resource01_password
```
---
**How to test**

1/ Add vault container in **docker-compose.yml**:

```yaml
  vault:
    image: vault
    ports:
      - "8200:8200"
    volumes:
      - /tmp/vault:/home/vault:Z
    cap_add:
      - IPC_LOCK
```

2/ Get the **vault root token**:
- from container log
- from volume shared in **/tmp/vault/.vault-token**

3/ Update the vault config in **config.yaml**

**Note:**

Use the python script to write severals vault secrets in one time:

- write vault secrets in **vaults_secrets.yml**
- update **write_vault_secrets.py** with **vault credentials**

```python
    client = login(
                host="localhost",
                port=8200,
                protocol="http",
                token="b4169582-e3d1-b752-64e7-d3ad453a67eb",
                path="/v1/secret/")
```

- write the secrets in vault
```
    python write_vault_secrets.py
```

## Plugins Usage

### rest_http plugin

To perform a simple check (status code 200):

```yaml
resource01:
    type: rest_http
    properties:
        host: resource1.lan
        port: 80
        protocol: http
        username: user
        password: pass
    data:
        type: App
        name: myapp01
        url: /api/v1.0/health
```

To perform an advanced check and **search for a string** in response:

```yaml
gitlab:
    type: rest_http
    properties:
        host: gitlab.lan
        port: 80
        protocol: http
    data:
        type: Git
        name: gitlab
        url: /health_check?token=token123456
        search: success
```

To perform an advanced check **with a regex**:

*Example: Search for an address email*

```yaml
gitlab:
    type: rest_http
    properties:
        host: about.gitlab.com
        port: 443
        protocol: http
    data:
        type: Git
        name: gitlab
        url: /contact/
        search: (\w+[.|\w])*@(\w+[.])*\w+
```

To perform an advanced check and **search for a dict** in response:
If **"search" dict** is not in **response dict**, resource state become **unhealthy**

```yaml
    resource2:
        type: rest_http
        properties:
            host: resource1.lan
            port: 80
            protocol: http
        data:
            type: App
            name: myapp02
            url: /api/v1.0/health
            search:
                db: up
                status: healthy
```

**Auth methods:**

- **token**: http token header
- **auth**: username and password
- **cert**: cert and key (string content)

**Other options**:

- **request_headers**: update http headers request.

**Examples:**

With cert:

```yaml
resource02:
    type: rest_http
    properties:
        host: host02.lan
        port: 8140
        protocol: https
        request_headers:
            "Content-Type": "text/pson"
        cert: "-----BEGIN CERTIFICATE-----\n-----END CERTIFICATE-----"
        key: "-----BEGIN RSA PRIVATE KEY-----\n-----END RSA PRIVATE KEY-----"
    data:
        type: App
        name: app02
        url: /check_health
```

With auth

```yaml
resource01:
    type: rest_http
    properties:
        host: resource1.lan
        port: 80
        protocol: http
        username: user
        password: pass
    data:
        type: App
        name: myapp01
        url: /api/v1.0/health
```

With token (add **PRIVATE-TOKEN** in headers)

```yaml
resource01:
    type: rest_http
    properties:
        host: resource1.lan
        port: 80
        protocol: http
        request_headers:
            "PRIVATE-TOKEN": token123456
    data:
        type: App
        name: myapp01
        url: /api/v1.0/health
```

### mongodb plugin

The mongodb plugin returns the status of the replica set from the point of view of the current server.
More info: https://docs.mongodb.com/manual/reference/command/replSetGetStatus/

This plugin support **one or more servers** in host properties.

```yaml
mongodb:
    type: mongodb
    properties:
        host:
            - host1.lan
            - host2.lan
            - host3.lan
        username: user
        password: pass
        port: 27017
        protocol: mongodb
    data:
        type: Database
        name: mongodb
```

### celery worker plugin

This plugin returns the workers state in celery app.
More info: http://docs.celeryproject.org/en/latest/reference/celery.app.control.html

```yaml
celery:
    type: celery_worker
    properties:
        host: celery.lan
        port: 5672
        transport: amqp
        username: user
        password: pass
    data:
        type: Worker
        name: celery_w
```

### AWS EC2 plugin

This plugin returns aws ec2 instances state.
More info: http://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_InstanceState.html

Get all ec2 instances status:

```yaml
aws:
    type: aws_ec2
    properties:
        region: "eu-central-1"
        access_key: "myaccesskey"
        secret_key: "mysecretkey"
    data:
        type: Infra
        name: EC2 Instance
```

Get specific instances with ids:

```yaml
aws:
    type: aws_ec2
    properties:
        region: "eu-central-1"
        access_key: "myaccesskey"
        secret_key: "mysecretkey"
    data:
        type: Infra
        name: EC2 Instance
        ec2_instance_ids:
            - i-xxxxxxxxxdb9ba68f
            - i-xxxxxxxxxdb8be69b
```

Get ec2 instances with filter(s):

*Get instance with tag: name=test*

 ```yaml
aws:
    type: aws_ec2
    properties:
        region: "eu-central-1"
        access_key: "myaccesskey"
        secret_key: "mysecretkey"
    data:
        type: Infra
        name: EC2 Instance
        ec2_filters:
            - Name: tag:Name
              Values:
                  - test
```

For more examples on filters usage, see http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html 

## How to test

With docker:

    docker-compose up

Or:

    pip install -r requirements.txt
    python app.py


## More plugins

Adding a plugin is very simple just create a new file in **platus/plugins** folder.

**new_plugin.py:**

```python

def login(host, protocol="https", port=443, **kwargs):
    [..]
    return client

def logout(client):
    [...]

def check_health(client, data):
    response = [...]
    status = None
    try:
        if response.status_code == 200:
            status = {"type": data["type"],
                      "name": data["name"],
                      "node": client.host,
                      "state": "operational",
                      "checked": str(datetime.now()),
                      "elapsed": str(response.elapsed)
                     }
        else:
            status = {"type": data["type"],
                      "name": data["name"],
                      "node": client.host,
                      "state": "down",
                      "checked": str(datetime.now()),
                      "elapsed": str(response.elapsed)
                     }
        if status:
            return status
    except Exception as error_msg:

            return {"type": data["type"],
                    "name": data["name"],
                    "node": client.host,
                    "state": "unknown",
                    "checked": str(datetime.now())
                   }
```


The **check_health** function must return a **dict** or a **list of dict** with following mandatory attributes:

- type
- name
- node
- state
- checked

## Todo
- Unit tests

## How to contribute

Pull requests are welcome.

1. Fork the project
2. Make one or more well commented and clean commits to the repository. You can make a new branch here if you are modifying more than one part or feature.
3. Perform a pull request


## Contributors
- Ahmet Demir ([flask-skeleton](https://github.com/ahmet2mir/flask-skeleton)) | [e-mail](mailto:ahmet2mir+github@gmail.com) | [Twitter](https://twitter.com/ahmet2mir) | [GitHub](https://github.com/ahmet2mir)


License
-------

Copyright 2016 - `François Gouteroux <http://fgouteroux.github.io>`

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
