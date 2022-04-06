import requests
import warnings
from bs4 import BeautifulSoup

# typing
from typing import Optional
from bs4.element import Tag


URL_EMENTA = "https://www.puc-rio.br/ferramentas/ementas/ementa.aspx?cd={codigo}"


def encontra_ementa(html: str) -> Optional[str]:
    """
    Faz o parsing do html, procurando o texto da ementa.

    Retorna o texto da ementa se encontrar, ou None

    :param html: string contendo o html da página da ementa

    :return:
    """

    soup = BeautifulSoup(html, features='html.parser')

    tag_ementa: Tag = soup.find(id='pEmenta', recursive=True)

    return tag_ementa.text if tag_ementa is not None else None


def consulta_ementa(codigo: str) -> str:
    """
    Faz uma consulta para a página da ementa, e retorna a ementa.

    Há um sleep de 0.3 segundos para evitar muitas consultas em pouco tempo ao site.

    Se não encontrar ou houver algum erro, a ementa será "Disciplina sem ementa cadastrada."

    :param codigo: código da disciplina no formato XXX0000

    :return: o texto da ementa
    """

    ementa_erro = "Disciplina sem ementa cadastrada"

    r = requests.get(URL_EMENTA.format(codigo=codigo))
    if r.status_code != 200:
        warnings.warn(f"Consulta da ementa da disciplina {codigo} retornou codigo {r.status_code}")
        return ementa_erro

    ementa = encontra_ementa(r.text)
    return ementa.strip() if ementa is not None else ementa_erro
