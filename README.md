## Platus

Platus is an python flask app to check **platform's health.** The name come from **platform** and **status**.
You defines wich services you want to monitor and host it on your own server. Services check are based on plugin system.

Currently supported plugins:

- rest_http
- mongodb
- celery_worker


## Usage

**Web** 

In a browser: *http://localhost:5001*

![platus](screenshots/platus_ok.png)

![platus](screenshots/platus_nok.png)

**Api**

Request:

    curl -u "admin:admin" http://localhost:5001/api/v1.0/status

Response:

```json
{
  "result": [ 
    {
      "checked": "2016-10-14 11:17:46.351426", 
      "elapsed": "0:00:00.011404", 
      "name": "mongodb", 
      "node": "db01.lan", 
      "state": "down", 
      "type": "Database"
    }, 
    {
      "checked": "2016-10-14 11:17:49.873978", 
      "elapsed": "0:00:00.871908", 
      "name": "docker01", 
      "node": "docker01.lan", 
      "state": "operational", 
      "type": "Docker"
    }
  ]
}
```

**Platus Users**

Manage users and roles in **users.yaml** (default path in main.py).

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

**Platus services**

Create **services.yaml** (default path in main.py).

    application.config['services'] = "services.yaml"

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

- **request_format**: set Content-Type and Accept headers (default: application/json)

**Examples:**

With cert:

```yaml
resource02:
    type: rest_http
    properties:
        host: host02.lan
        port: 8140
        protocol: https
        request_format: text/pson
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
        token: token123456
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

## How to test

    pip install -r requirements.txt
    python main.py


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
    
    if response['health']:
        status = {"type": data["type"],
                      "name": data["name"],
                      "node": client.host,
                      "state": "down",
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
    else:
        raise RuntimeError("Cannot get plugin status")
```


The **check_health** function must return a **dict** or a **list of dict** with following mandatory attributes:

- type
- name
- node
- state
- checked

## Todo
- Notification system (email, slack...)
- Storage backend to store services status
- Secure sensitive infos in services.yaml
- rest_http search improvements, regex...
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
