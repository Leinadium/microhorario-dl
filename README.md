# Microhorario Downloader

Biblioteca destinada ao download e utilização de dados provenientes do [Microhorario](https://www.puc-rio.br/microhorario)
 da PUC-Rio.

Essa biblioteca permite baixar todos os dados, e disponibiliza modelos para a utilização destes.

A biblioteca não tem poder de alterar nenhum dado, somente baixar os dados e manipular localmente.


Além disso, é possível baixar as ementas automaticamente de todas as disciplinas disponíveis.


## Funcionamento

O microhorário não disponibiliza nenhuma API para poder fazer um download automático das disciplinas. Por isso, 
é necessário fazer requests específicos para conseguir simular um usuário baixando os dados.

Para baixar os dados, um usuário precisa carregar a página inicial, fazer uma consulta sem nenhum filtro, e depois
baixar os dados no formato CSV. Essa biblioteca simula essas três simulações atráves de um GET e dois POSTS.

Para poder baixar o CSV, é preciso fazer um POST enviando os dados do formulário, assim como variáveis de ASP.NET. Essas
variáveis são adquiridas ao fazer uma consulta sem filtro, por isso é necessário fazer um POST usando os dados do formulário
para fazer essa consulta. Porém, essa consulta também utiliza variáveis de ASP.NET e um id de sessão adquiridos ao entrar
na página. Por isso, é necessário fazer um GET na página inicial para poder adquirir essas variáveis e esse id.

Portanto, são feitos três requests, nomeados `consulta_inicial`, `consulta_intermediaria`, e `consulta_final`:

```text
consulta inicial (GET https://puc-rio.br/microhorario):
    recebe:
        cookies
        id da sessao
        nomes e códigos dos departamentos
        nomes e códigos dos destinos
        __VIEWSTATEGENERATOR, __VIEWSTATE e __EVENTVALIDATION

consulta intermediaria (POST /WebMicroHorarioConsulta/MicroHorarioConsulta.aspx):
    envia:
        formulario pedindo uma consulta sem filtro
        cookies
        id da sessao
        __VIEWSTATEGENERATOR, __VIEWSTATE e __EVENTVALIDATION

    recebe:
        cookies
        id da sessao
        __VIEWSTATEGENERATOR, __VIEWSTATE e __EVENTVALIDATION

consulta final (POST /WebMicroHorarioConsulta/MicroHorarioConsulta.aspx):
    envia:
        formulario pedindo para baixar os resultados de uma consulta sem filtro
        cookies
        id da sessao
        __VIEWSTATEGENERATOR, __VIEWSTATE e __EVENTVALIDATION

    recebe:
        arquivo csv em utf-16
```

## Uso

Instale a biblioteca: 
```shell
pip install microhorario-dl
```

Importe e baixe os dados:

```pycon
>>> from microhorario_dl import Microhorario

>>> micro = Microhorario.download()
<Microhorario object at ...>

>>> micro.disciplinas
[<Disciplina [ACN1000]>, <Disciplina[ACN1002]>, ...]
```

Baixe as ementas:

```pycon
>>> micro.coletar_ementas(verbose=True)
[0/ 2000] Baixando ACN1000...  DONE (...)
[1/ 2000] Baixando ACN1002...  DONE (...)
[2/ 2000] Baixando ACN1004...
... 
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