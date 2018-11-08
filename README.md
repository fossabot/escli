# Escli 
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fwuha-team%2Fescli.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fwuha-team%2Fescli?ref=badge_shield)


Escli is a CLI tool for Elasticsearch. It should prevent Elasticsearch operators to use huge `curl` commands with complex bodies like

```bash
curl -XPUT --user "john:doe" 'http://elasticsearch.example.com:9200/_cluster/settings' -d '{
    "transient" : {
        "cluster.routing.allocation.enable": "none"
    }
}'
```

The equivalent with `escli` is

```bash
escli cluster routing allocation enable none
```


# Usage

Even if you can use command-line credentials (using `-u` and `-p`), you should create a file name `~/.esclirc` containing escli's config :

```yaml
clusters:
  bar:
    servers:
    - https://bar.example.com

users:
  john-doe:
    username: john
    password: doe

contexts:
  foo:
    user: john-doe
    cluster: bar

default-context: foo
```


# License

`escli` is licensed under the GNU GPLv3. See [LICENCE]() file.



[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fwuha-team%2Fescli.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fwuha-team%2Fescli?ref=badge_large)

# Developing

### Run

```bash
python3 setup.py install --user --prefix= >> /dev/null && escli
```

### Run tests

```bash
python3 setup.py install --user --prefix= >> /dev/null && pytest -s
```