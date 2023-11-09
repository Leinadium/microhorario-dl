import requests
import warnings
from bs4 import BeautifulSoup

# typing
from typing import Optional, List, Tuple
from bs4.element import Tag


URL_EMENTA = "https://www.puc-rio.br/ferramentas/ementas/ementa.aspx?cd={codigo}"


def encontra_ementa(soup: BeautifulSoup) -> Optional[str]:
    """
    Faz o parsing do html, procurando o texto da ementa.

    Retorna o texto da ementa se encontrar, ou None

    :param soup: objeto BeautifulSoup contendo a página da ementa

    :return:
    """

    tag_ementa: Tag = soup.find(id='pEmenta', recursive=True)

    return tag_ementa.text if tag_ementa is not None else None


def encontra_prerequisitos(soup: BeautifulSoup) -> List[List[str]]:
    """
    Faz o parsing do html, procurando os grupos de prerequisitos.

    Retorna uma lista de grupos de ementas

    :param soup: objeto BeautifulSoup contendo a página da ementa
    """
    ret = []

    tag_prerequisito: Tag = soup.find(id='prerequisito', recursive=True)
    if tag_prerequisito is None:
        return ret

    for tag_grupo in tag_prerequisito.find_all('span'):
        grupo = set()
        for tag_disc in tag_grupo.find_all('a'):
            disc = tag_disc.text.strip().upper()
            if disc:
                grupo.add(disc)
        if grupo:
            ret.append(list(grupo))

    return ret


def encontra_credito(soup: BeautifulSoup) -> Optional[int]:
    """
    Faz o parsing do html, procurando a quantidade de creditos.

    Retorna um inteiro contendo a quantidade

    :param soup: objeto BeautifulSoup contendo a página da ementa
    """
    tag_creditos: Tag = soup.find(id='hCreditos', recursive=True)
    if tag_creditos is None:
        return None

    try:
        c: int = int(tag_creditos.text.strip().split()[0])
        return c if c > 0 else None
    except ValueError:
        return None


def consulta_extra(codigo: str) -> Tuple[str, List[List[str]], Optional[int]]:
    """
    Faz uma consulta para a página da ementa, e retorna a ementa e prerequisitos.

    Há um sleep de 0.3 segundos para evitar muitas consultas em pouco tempo ao site.

    Se não encontrar ou houver algum erro, a ementa será "Disciplina sem ementa cadastrada."

    :param codigo: código da disciplina no formato XXX0000

    :return: o texto da ementa
    """

    ementa_erro = "Disciplina sem ementa cadastrada"
    prereq_erro = []
    creditos_erro = None

    r = requests.get(URL_EMENTA.format(codigo=codigo))
    if r.status_code != 200:
        warnings.warn(f"Consulta da ementa da disciplina {codigo} retornou codigo {r.status_code}")
        return ementa_erro, prereq_erro, creditos_erro

    soup = BeautifulSoup(r.text, features='html.parser')

    ementa = encontra_ementa(soup)
    prereqs = encontra_prerequisitos(soup)
    creditos = encontra_credito(soup)

    return (
        ementa.strip() if ementa is not None else ementa_erro,
        prereqs,
        creditos
    )
