import re
import requests
from warnings import warn
from bs4 import BeautifulSoup

# typing modules
from typing import Dict, Any, Optional, Match, Union
from bs4.element import Tag
from requests import Response

# local modules
from .payloads import PayloadMicrohorario
from .utils import URL_CONSULTA, URL_INICIAL, USER_AGENT, pegar_sessao_da_url
from .exceptions import EmptyTagValueError, TagNotFoundError, NotCSVError, PatternNotFoundError, WebExceptionError


def de_opcoes_para_dicionario(t: Tag) -> Dict[str, str]:
    """Converte todas as opções dentro de uma tag de seleção em um dicionario.

    Em vez de pegar o `value` da opção como chave, é feito um regex na string.
    """
    ret: Dict[str, str] = {}
    for x in t.find_all('option'):       # type: Tag
        m: Match = re.search(r'(?P<ident>[A-Z]{3})\s-\s(?P<nome>[\w\s]+)', x.text)
        if m is not None:
            ident = m.group('ident')
            nome = m.group('nome')
            if (ident is not None) and (nome is not None):
                ret[ident] = nome
    return ret


def consulta_excecao(conteudo: str) -> Response:
    """
    Caso a primeira consulta foi redirecionada para a página de erro.
    Caso isso tenha acontecido, tenta ver se o "Horários e Salas" está disponível.
    Nesse caso, retorna a requisição para a página de consulta.
    """
    # faz o parsing do conteudo
    soup = BeautifulSoup(conteudo, features='html.parser')
    span_msg: Tag = soup.find(id='lblMensagem')     # pega a tag de span
    if span_msg is None:
        raise WebExceptionError("Exceção não possui mensagem de erro")

    # coleta a tag <a> dentro do conteudo
    tag_links_msg: list[Tag] = span_msg.find_all('a')
    if len(tag_links_msg) == 0:
        raise WebExceptionError("Exceção não possui link de redirecionamento")
    tag_link_msg: Tag = tag_links_msg[0]

    link_correto = tag_link_msg.get('href')

    # verifica se o link é o correto
    if link_correto is None or "WebMicroHorarioConsulta" not in link_correto:
        raise WebExceptionError("Link de redirecionamento não é o esperado")

    # altera o modo e avisa
    PayloadMicrohorario.altera_modo()
    warn("Microhorário indisponível, utilizando 'Horarios e Salas' como alternativa. "
         "A quantidade de créditos e as alocações (vagas por turma) estarão indisponíveis.")

    # faz a requisição para o link correto
    return requests.get(
        url=link_correto,
        headers={"User-Agent": USER_AGENT}
    )


def consulta_inicial() -> Dict[str, Any]:
    """
    Faz a primeira consulta no site do microhorario

    A primeira consulta é responsável por coletar os cookies necessários,
    as variáveis para o ASP.NET, a sessão do usuário,
    e também o nome dos departamentos e destinos.

    :return: dicionario contendo os cookies e os dados necessários
    """

    def valida_tag_ou_aborta(nome: str, t: Optional[Tag]) -> str:
        """
        Valida se a Tag foi coletada ou não.
        Se for None, aborta o programa com uma mensagem especifica

        :param nome: nome da tag
        :param t: tag ou None
        :return: a string `value` dentro da tag
        """
        if t is None:
            raise TagNotFoundError(nome)
        else:
            if isinstance(t, Tag):
                valor = t.get('value')
                if valor is None:
                    raise EmptyTagValueError(nome)
                else:
                    return valor

    r = requests.get(
        url=URL_INICIAL,
        headers={"User-Agent": USER_AGENT},
        allow_redirects=True
    )

    # pegando os cookies (juntando com os redirects)
    cookies: dict = r.cookies.get_dict()
    for r_history in r.history:
        cookies.update(r_history.cookies.get_dict())

    # se foi redirecionado para uma excecao, tenta acessar o link correto
    if "WebExcecao" in r.url:
        r = consulta_excecao(r.text)

    # pegando propriedades do ASP.NET
    soup = BeautifulSoup(r.text, features='html.parser')
    view_state_generator: Tag = soup.find(id='__VIEWSTATEGENERATOR')
    event_validation: Tag = soup.find(id='__EVENTVALIDATION')
    view_state: Tag = soup.find(id='__VIEWSTATE')

    # pegando destinos
    destinos_tag: Tag = soup.find(id='ddlBloqueio', recursive=True)
    destinos = de_opcoes_para_dicionario(destinos_tag) if destinos_tag is not None else {}

    # pegando departamentos
    departamentos_tag: Tag = soup.find(id='ddlDeptoSolicitante', recursive=True)
    departamentos = de_opcoes_para_dicionario(departamentos_tag) if departamentos_tag is not None else {}

    # pegando a sessao
    sessao = pegar_sessao_da_url(r.url)

    return {
        'cookies': cookies,
        'sessao': sessao,
        'departamentos': departamentos,
        'destinos': destinos,
        'dados': {
            '__VIEWSTATEGENERATOR': valida_tag_ou_aborta(
                nome='__VIEWSTATEGENERATOR',
                t=view_state_generator
            ),
            '__EVENTVALIDATION': valida_tag_ou_aborta(
                nome='__EVENTVALIDATION',
                t=event_validation
            ),
            '__VIEWSTATE': valida_tag_ou_aborta(
                nome='__VIEWSTATE',
                t=view_state
            )
        }
    }


def consulta_intermediaria(dados_iniciais: Dict[str, Any]):
    """
    Usando os dados iniciais da primeira consulta, é realiada um segunda consulta simulando
    uma pesquisa sem filtro, para atualizar as variáveis do ASP.NET necessárias para fazer
    a consulta final.

    Ao contrário da primeira consulta, essa retorna um texto que o javascript do framework do ASP.NET deveria
    utilizar. Por isso, para atualizar as variáveis, são utilizados regex

    :param dados_iniciais: dicionario retornada pela `consulta_inicial`
    :return: dicionario com os novos dados da consulta
    """
    def regex_ou_aborta(nome: str, pattern: str, string: str) -> str:
        m: Match = re.search(pattern, string)
        if m is None:
            raise PatternNotFoundError(nome=nome, regex=pattern)
        return m.group(1)

    payload: dict = PayloadMicrohorario.intermediario()
    payload.update(dados_iniciais['dados'])     # adiciona as variaveis coletadas no dados iniciais

    cookies = dados_iniciais.get('cookies')
    sessao = dados_iniciais.get('sessao')

    r = requests.post(
        url=URL_CONSULTA,
        cookies=cookies,
        params={'sessao': sessao},
        headers={
            'User-Agent': USER_AGENT,
            'Accept': 'text/plain',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Origin': "http://microhorario.rdc.puc-rio.br",     # noqa
        },
        data=payload
    )

    # pegando as novas informacoes
    return {
        'cookies': cookies,
        'sessao': sessao,
        'dados': {
            '__VIEWSTATEGENERATOR': regex_ou_aborta(
                nome='VIEWSTATEGENERATOR',
                pattern=r'__VIEWSTATEGENERATOR\|([0-9a-zA-Z+\/=]+)\|',
                string=r.text
            ),
            '__EVENTVALIDATION': regex_ou_aborta(
                nome='EVENTVALIDATION',
                pattern=r'__EVENTVALIDATION\|([0-9a-zA-Z+\/=]+)\|',
                string=r.text
            ),
            '__VIEWSTATE': regex_ou_aborta(
                nome='VIEWSTATE',
                pattern=r'__VIEWSTATE\|([0-9a-zA-Z+\/=]+)\|',
                string=r.text
            )
        }
    }


def consulta_final(dados_intermediarios: Dict[str, Union[Tag, str, dict]]) -> str:
    """
    Faz a consulta final, para obter o CSV com todas as disciplinas no microhorario.

    Usando as variáveis de ASP.NET fornecidas na consulta intermediaria, é feito um POST
    pedindo o CSV referente àquela consulta.

    :param dados_intermediarios: dados da consulta intermediaria

    :return: o texto do csv baixado
    """
    # preparando os dados
    payload: dict = PayloadMicrohorario.final()
    payload.update(dados_intermediarios.get('dados'))     # adiciona as variaveis coletadas no dados iniciais

    cookies = dados_intermediarios.get('cookies')
    sessao = dados_intermediarios.get('sessao')

    # preparando a consulta
    r = requests.post(
        url=URL_CONSULTA,
        cookies=cookies,
        headers={
            'Host': "microhorario.rdc.puc-rio.br",
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': "en-US,en;q=0.5",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': "http://microhorario.rdc.puc-rio.br",  # noqa
            'Connection': 'keep-alive',
            'Referer': f"{URL_CONSULTA}?sessao={sessao}",
            'Upgrade-Insecure-Requests': '1',
        },
        params={'sessao': sessao},
        data=payload
    )

    if 'text/csv' not in r.headers.get('Content-Type'):
        raise NotCSVError

    # pega o texto usando o encoding correto
    r.encoding = 'utf-16'
    return r.text
