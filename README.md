# Microhorario Downloader

Descrição a adicionar


## Uso

Instale a biblioteca: 
```shell
# ainda nao disponivel
# pip install microhorario-dl

pip install -i https://test.pypi.org/simple/ microhorario-dl-leinadium==0.1
```

Importe e baixe os dados:

```pycon
>>> from microhorario_dl import Microhorario

>>> micro = Microhorario.download()
<Microhorario object at ...>

>>> micro.disciplinas
[<Disciplina [ACN[1000>, <Disciplina[ACN1002]], ...]
```

Exporte para um json:

```pycon
>>> import json

>>> print(json.dumps(micro.as_json(), indent=2))
{
    "periodo": "20221",
    "emissao": "05/04/2022 22:57 h",
    # ...
    "disciplinas": [
        # ...
    ]
}
```