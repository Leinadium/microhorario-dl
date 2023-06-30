"""MicroHorario Downloader

Essa ferramenta permite um download rápido de todas as disciplinas
da PUC-Rio, sem utilizar webscraping manual ou simuladores de browser
como Selenium.

A ferramenta utiliza chamadas HTTP (GET e POST) para interagir
com o microhorário e baixar todas as disciplinas
"""

__author__ = "Daniel Guimarães (github.com/Leinadium)"
__version__ = "1.4.1"
__copyright__ = "Copyright (c) 2022 Daniel Guimarães"
__license__ = "MIT"

from time import sleep

from .consultas import consulta_inicial, consulta_intermediaria, consulta_final
from .parser import converte_para_json
from .models import RawDisciplina, Disciplina, Turma, Alocacao, Departamento, Destino
from .ementa import consulta_ementa

from typing import Dict, List, Optional

__all__ = [
    "Microhorario",
    "models",
    "exceptions"
]


class Microhorario:
    """Representa a tabela completa do Microhorario.
    """

    @staticmethod
    def download():
        """Faz o download do microhorario, criando o objeto

        :rtype: Microhorario
        """
        inicio = consulta_inicial()
        inter = consulta_intermediaria(inicio)
        fim = consulta_final(inter)

        dados_crus: dict = converte_para_json(fim)

        instance: Microhorario = Microhorario(
            periodo=dados_crus['periodo'],
            emissao=dados_crus['emissao'],
            atualizacao=dados_crus['atualizacao'],
            dados_crus=dados_crus,
            departamentos=inicio.get('departamentos'),
            destinos=inicio.get('destinos')
        )

        for rd in dados_crus['disciplinas']:    # type: RawDisciplina
            instance._add_raw_disciplina(rd)

        return instance

    def __init__(self,
                 periodo: str,
                 emissao: str,
                 atualizacao: str,
                 dados_crus: dict,
                 departamentos: Optional[dict] = None,
                 destinos: Optional[dict] = None):
        """
        Cria uma instancia do Microhorario

        Ao criar uma instancia, as disciplinas não estão preenchidas. As disciplinas só podem
        ser adicionadas através do método privado `_add_raw_disciplina`, por isso instanciar
        manualmente um microhorario não é recomendado.

        :param periodo: string representando o período atual do microhorario (20XX-X)

        :param emissao: string representando a data de emissão do microhorario atual

        :param atualizacao: string represetando a data da ultima atualização do microhorario

        :param dados_crus: o dicionario contendo as `RawDisciplina`s e as informações originais.

        :param departamentos: Caso seja um dicionario, cada chave e valor serão respectivamentes
        o código e o nome do departamento, para ser pré-adicionado.

        :param destinos: Caso seja um dicionario, cada chave e valor serão respectivamentes
        o código e o nome do destino, para ser pré adicionado.
        """

        self._periodo: str = periodo
        self._emissao: str = emissao
        self._atualizacao: str = atualizacao
        self._dados_crus: dict = dados_crus
        self._disciplinas: Dict[str, Disciplina] = dict()
        self._departamentos: Dict[str, Departamento] = dict()

        # adicionando departamentos
        if isinstance(departamentos, dict):
            self._departamentos = {
                k: Departamento(codigo=k, nome=v) for k, v in departamentos.items()
            }

        # adicionando destinos
        if isinstance(destinos, dict):
            self._destinos: Optional[dict] = destinos
        else:
            self._destinos: Optional[dict] = None

    @property
    def periodo(self):
        """O perído atual do microhorario"""
        return self._periodo

    @property
    def emissao(self):
        """A data de emissão do download do microhorario"""
        return self._emissao

    @property
    def atualizacao(self):
        """A última atualização do microhorario"""
        return self._atualizacao

    @property
    def disciplinas(self) -> List[Disciplina]:
        """Lista das disciplinas baixados"""
        return list(self._disciplinas.values())

    @property
    def departamentos(self) -> List[Departamento]:
        """Lista dos departamentos encontrados."""
        return list(self._departamentos.values())

    @property
    def raw(self):
        """Dicionario dos dados baixados, sem processamento"""
        return self._dados_crus

    def _add_raw_disciplina(self, raw: RawDisciplina):
        """Adiciona uma disciplina utilizando uma `RawDisciplina`
        """
        # criando destino
        nome_destino = raw.destino      # nome padrão é o proprio código
        if self._destinos is not None and raw.destino in self._destinos:
            nome_destino = self._destinos.get(raw.destino)
        destino = Destino(codigo=raw.destino, nome=nome_destino)

        # criando alocacao
        alocacao = Alocacao(destino=destino, vagas=raw.vaga)

        # criando turma
        turma = Turma(
            professor=raw.professor,
            codigo=raw.turma,
            turno=raw.turno,
            horario_distancia=raw.horas_distancia,
            shf=raw.shf,
            horario_e_localizacao=raw.horario_local,
            alocacao=alocacao
        )

        # se ja existir a turma, só adiciona na disciplina
        if raw.codigo in self._disciplinas:
            self._disciplinas[raw.codigo].add_turma(turma)

        # se nao existir, tem que criar a disciplina tambem
        else:
            # se existir o departamento, coleta.
            if raw.depto in self._departamentos:
                departamento = self._departamentos[raw.depto]
            # se nao existir, cria do zero
            else:
                # pegando nome do departamento antes
                departamento = Departamento(
                    codigo=raw.depto,
                    nome=raw.depto      # nao tem como saber o nome se ele já não havia sido adicionado
                )
                self._departamentos[raw.depto] = departamento

            # cria a disciplina
            disciplina = Disciplina(
                codigo=raw.codigo,
                nome=raw.nome,
                pre_req=raw.pre_req,
                creditos=raw.creditos,
                departamento=departamento
            )
            # adiciona a turma na propria disciplinia
            disciplina.add_turma(turma)

            self._disciplinas[raw.codigo] = disciplina

        return

    def as_json(self) -> dict:
        """
        Transforma o objeto em um dicionário, que é um json válido.

        :return: um dicionario contendo todas as informações do json
        """

        return {
            'periodo': self.periodo,
            'emissao': self.emissao,
            'atualizacao': self.atualizacao,
            'departamentos': [
                {
                    'nome': x.nome,
                    'codigo': x.codigo
                }
                for x in self.departamentos
            ],
            'disciplinas': [
                {
                    'nome': d.nome,
                    'codigo': d.codigo,
                    'pre_req': d.pre_req,
                    'creditos': d.creditos,
                    'departamento': d.departamento.codigo,
                    'turmas': [t.as_dict() for t in d.turmas]
                }
                for d in self.disciplinas
            ]
        }

    def coletar_ementas(self, verbose=True):
        """
        Coleta as ementas de todas as disciplinas cadastradas.

        Essa função irá fazer uma chamada ao site da PUC para cada ementa, por isso
        o tempo de execução é longo.

        :param verbose: imprime o status atual no stdout
        """

        total = len(self._disciplinas)
        for i, (cod, disc) in enumerate(self._disciplinas.items()):       # type: int, str, Disciplina
            if verbose:
                print(f"\r[{i}/{total}] Coletando ementa de [{cod}]", end='')

            disc.ementa = consulta_ementa(cod)
            sleep(0.2)

