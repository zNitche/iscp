## iscep

![tests status](https://github.com/zNitche/iscep/actions/workflows/tests.yml/badge.svg)

inter service command execution protocol

### Description
While working on [yamcsr](https://github.com/zNitche/yamcsr) I had to find a way to call scripts
(which are part of `yamcsr` codebase) from outside of its containerized environment (without code/volumes duplication).

At first I wanted to use python built-in [socketserver](https://docs.python.org/3/library/socketserver.html),
but when it came to expanding codebase build on it, I find it quite difficult and non-intuitive,
that's why I decided to build my own solution.

That is how this project came to life. It is quite simple but was a nice exercise is using python sockets and multithreading.

### Features
- multithreaded socket server.
- limiting max threads/connections that can be handled at the same time.
- client implementation.
- support loging (access, error, commands).
- SSL/TLS communication encryption.
- token based packets authentication.
- built-in CLI to manage authentication tokens.
- fully type hinted.

#### Packet structure
| Size    | Type    | Content | Checksum / Hash |
|---------|---------|---------|-----------------|
| 4 bytes | 2 bytes | x bytes | 32 bytes        |

### How to use it
package can be installed via `pip` just add following line to your
`requirements.txt` (remember to specify proper version).

```
iscep @ git+https://github.com/zNitche/iscep.git@<version>
```

### Examples
`Client` and `Server` example scripts can be found in `/examples` directory.

### Auth tokens management
Following command will add token to `$PWD/tokens.json` for user `<user_name>`.

```
python3 -m iscep.tokens_management --tokens-path tokens.json --add user_name
```

### SSL/TLS
`iscep` supports connection encryption (see `/examples/client.py` and `/examples/server.py`), to use it
certificate and key have to be generated with following command:

```
openssl req -x509 -newkey rsa:2048 -nodes -out cert.pem -keyout key.pem -days 365
```

paths to `cert.pem` and `key.pem` must be specified in `Client` and `Server` instance.

### Dependencies
In order to run tests or build package, project development dependencies have to be installed.

```
pip3 install -r requirements-dev.txt
```

### Building package
To build package, that can be installed manually can be done with following command.

```
python3 -m build
```

### Tests
project's test suit can be run via

```
pytest -v tests/
```
