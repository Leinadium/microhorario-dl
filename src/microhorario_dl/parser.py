import re
import warnings

# typing stuff
from typing import List, Dict

# local imports
from .models import RawDisciplina


def get_informacoes_csv(info_str: str) -> Dict[str, str]:
    """
    Faz um parsing das informações do CSV gerado.

    Procura retirar as informações da primeira linha do CSV, no formato:
        Período: 20221;Emitido em: 05/04/2022 16:24 h; Data da última atualização: 05/04/2022 13:50h;

    :param info_str: linha contendo as informações do csv

    :return: um dicionario com as chaves "periodo", "emissao" e "atualizacao"
    """

    lista: List[str] = info_str.split(';')
    res = {
        'periodo': '',
        'emissao': '',
        'atualizacao': ''
    }

    for elemento in lista:
        # separando no ":", onde [0] tem um texto, e [1] o conteudo
        try:
            texto_e_conteudo = elemento.split(':')
            texto, conteudo = texto_e_conteudo[0], ':'.join(texto_e_conteudo[1:])
            if 'Período' in texto:
                res['periodo'] = conteudo.strip()
            elif 'Emitido' in texto:
                res['emissao'] = conteudo.strip()
            elif 'atualização' in texto:
                res['atualizacao'] = conteudo.strip()

        except ValueError:
            continue

    # verificando integridade
    for k, v in res.items():
        if not v:
            warnings.warn(f"A informacao '{k}' não foi encontrada no csv baixado")

    return res


def converte_para_json(texto_csv: str) -> dict:

    ret: dict = {}
    # le as linhas do csv
    linhas = texto_csv.splitlines()
    # salva as informacoes na linha inicial do arquivo
    ret.update(
        get_informacoes_csv(linhas[0])
    )

    # regex para o codigo, que é o primeiro texto na linha
    re_disciplina = re.compile('^[A-Z]{3}[0-9]{4}')

    lista_disciplinas: List[RawDisciplina] = list()

    for linha in linhas:
        if re_disciplina.match(linha) is None:
            continue     # pula a linha que nao tem informacao

        # splitando em brancos e retirando tambem o ';' final se tiver
        linha_split = linha.strip(' \n\r;').split(';')

        if len(linha_split) == 11:
            # caso especifico quando cai no Horarios e Salas (microhorario desligado)
            # nao existe a linha de 'créditos', 'destino' e 'vaga'
            linha_split.insert(3, '-1')     # creditos
            linha_split.insert(5, '--')     # destino
            linha_split.insert(6, '--')     # vaga

        if len(linha_split) == 14:
            # removendo horas de extensao (atualização nova do microhorario)
            linha_split.pop(11)

        if len(linha_split) != 13:
            warnings.warn(f"Linha iniciada em {linha_split[0]} está inválida: contém {len(linha_split)} elementos,"
                          f"esperado: 14, 13 ou 11")
            continue     # pula a linha que a informacao esta corrompida

        codigo = linha_split[0].strip()
        nome = linha_split[1].strip()
        professor = linha_split[2].strip()
        creditos = linha_split[3].strip()
        turma = linha_split[4].strip()
        destino = linha_split[5].strip()
        vaga = linha_split[6].strip()
        turno = linha_split[7].strip()
        horario_local = linha_split[8].strip()
        horas_distancia = linha_split[9].strip()
        shf = linha_split[10].strip()
        pre_req = linha_split[11].strip()
        depto = linha_split[12].strip()

        # fazendo parsing dos valores numericos
        creditos = int(creditos) if creditos.isnumeric() else -1
        vaga = int(vaga) if vaga.isnumeric() else -1
        horas_distancia = int(horas_distancia) if horas_distancia.isnumeric() else -1
        shf = int(shf) if shf.isnumeric() else -1

        # fazendo parsing dos valores booleanos
        pre_req = pre_req == "SIM"
        lista_disciplinas.append(RawDisciplina(
            nome=nome,
            codigo=codigo,
            professor=professor,
            creditos=creditos,
            turma=turma,
            destino=destino,
            vaga=vaga,
            turno=turno,
            horario_local=horario_local,
            horas_distancia=horas_distancia,
            shf=shf,
            pre_req=pre_req,
            depto=depto
        ))

    ret['disciplinas'] = lista_disciplinas

    return ret
