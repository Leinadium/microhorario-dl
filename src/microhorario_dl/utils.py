import re
import warnings

URL_INICIAL = 'https://www.puc-rio.br/microhorario'
URL_CONSULTA = 'http://microhorario.rdc.puc-rio.br/WebMicroHorarioConsulta/MicroHorarioConsulta.aspx'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'


def pegar_sessao_da_url(url: str) -> str:
    """
    Retorna a sessao, que é um parametro na url.
    :param url:
    :return:
    """

    m: re.Match = re.search(r'\?sessao=(.*)$', url)
    if m is not None:
        return m.group(1)
    else:
        warnings.warn(message="Não foi encontrada a sessão na url. ")
        return ''
