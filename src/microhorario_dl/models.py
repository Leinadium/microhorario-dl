import re
from dataclasses import dataclass, asdict

# typing stuff
from typing import Optional, Dict, Match, List


RE_HORARIO = re.compile(
    r'((?P<dia>SEG|TER|QUA|QUI|SEX|SAB|DOM)\s(?P<inicio>[0-9]{2})-(?P<fim>[0-9]{2})\s)?(?P<local>[a-zA-Z0-9]+)'
)


@dataclass
class Horario:
    # noinspection PyUnresolvedReferences
    """Horario da turma

    :param dia: SEG, TER, QUA, QUI, SEX, SAB ou DOM
    :type: str

    :param inicio: hora de inicio da aula (0 à 24)
    :type: int

    :param fim: hora de fim da aula (0 à 24)
    :type: int
    """
    dia: str
    inicio: int
    fim: int

    def __repr__(self):
        return f'<Horario [{self.dia} {self.inicio}-{self.fim}]>'


@dataclass
class Destino:
    # noinspection PyUnresolvedReferences
    """Destino da turma

    :param codigo: código do destino da turma (ex. QQC)
    :type: str

    :param nome: nome do destino da turma (ex. Qualquer curso)
    :type: str
    """
    codigo: str
    nome: str

    def __repr__(self):
        return f'<Destino [{self.codigo}]>'


@dataclass
class Alocacao:
    # noinspection PyUnresolvedReferences
    """Alocacao de uma turma

    :param destino: Destino da turma
    :type: Destino

    :param vagas: quantidade de vagas da turma
    :type: int
    """
    destino: Destino
    vagas: int

    def __repr__(self):
        return f'<Alocacao [{self.destino.codigo} - {self.vagas} vgs]>'


@dataclass
class RawDisciplina:
    # noinspection PyUnresolvedReferences
    """Dados de uma disciplina sem nenhum tratamento

    Esses dados estão quase exatamente como no CSV disponibilizado pelo microhorario

    Cada instancia representa na verdade uma turma, mas possui todas as informações da disciplina também.

    :arg codigo: codigo da discplina
    :type: str

    :arg nome: nome da disciplina
    :type: str

    :arg professor: nome do professor da disciplina
    :type: str

    :arg creditos: quantidade de créditos da disciplina
    :type: int

    :arg turma: código da turma
    :type: str

    :arg destino: destino da turma
    :type: str

    :arg vaga: quantidade de vagas na turma
    :type: int

    :arg turno: turno da turma
    :type: str

    :arg horario_local: string contendo horario e local da turma
    :type: str

    :arg horas_distancia: quantidade de horas à distância da turma
    :type: int

    :arg shf: quantidade de horas sem horário fixo da turma
    :type: int

    :arg pre_req: se a disciplina contém algum pré requisito
    :type: bool

    :arg depto: código do departamento da disciplina
    :type: str
    """
    codigo: str
    nome: str
    professor: str
    creditos: int
    turma: str
    destino: str
    vaga: int
    turno: str
    horario_local: str
    horas_distancia: int
    shf: int
    pre_req: bool
    depto: str

    def __repr__(self):
        return f'<RawDisciplina [{self.codigo}]>'


class Turma:
    """Representa uma turma de uma disciplina no Microhorario"""

    def __init__(self,
                 professor: str,
                 codigo: str,
                 turno: str,
                 horario_distancia: int,
                 shf: int,
                 horario_e_localizacao: str,
                 alocacao: Alocacao
                 ):

        self._professor = professor
        self._codigo = codigo
        self._turno = turno
        self._horario_distancia = horario_distancia
        self._shf = shf
        self._alocacao = alocacao

        # fazendo parsing do horario de local
        self._lista_horarios = []
        self._localizacao = None
        self._parse_horario_localizacao(horario_e_localizacao.strip())

    def __repr__(self):
        return f'<Turma [{self.codigo}]>'

    def as_dict(self):
        """Converte a turma para um dicionario"""

        horarios = [
            asdict(x) for x in self._lista_horarios if x is not None
        ]
        localizacao = self.localizacao if self.localizacao is not None else ''
        destino = self.alocacao.destino.codigo
        vagas = self.alocacao.vagas

        return {
            'professor': self.professor,
            'codigo': self.codigo,
            'turno': self.turno,
            'horario_distancia': self.horario_distancia,
            'shf': self.shf,
            'horarios': horarios,
            'localizacao': localizacao,
            'destino': destino,
            'vagas': vagas
        }

    def _parse_horario_localizacao(self, texto: str):
        """Faz o parsing da string contendo os horarios e a localização,
        transformando em uma lista de `Horario`, e guarda em `horarios`.

        Também salva a localização do último horário encontrado.
        """
        local = None
        for t in texto.split('  '):
            m: Match = RE_HORARIO.match(t)
            if m is None:
                return

            local = m.group('local')
            dia = m.group('dia')
            inicio = m.group('inicio')
            fim = m.group('fim')

            horario = Horario(dia, inicio, fim) if None not in (dia, inicio, fim) else None
            self._lista_horarios.append(horario)

        # so adiciona a ultima localizacao. pode ser um problema
        # se houver mais de uma localizaco dependendo da aula
        self._localizacao = local

    @property
    def professor(self) -> str:
        """Professor(a) que leciona a disciplina para essa turma"""
        return self._professor

    @property
    def codigo(self) -> str:
        """Código da turma"""
        return self._codigo

    @property
    def turno(self) -> str:
        """Turno da turma"""
        return self._turno

    @property
    def horarios(self) -> List[Horario]:
        """Lista de horários da turma"""
        return self._lista_horarios

    @property
    def horario_distancia(self):
        """Quantidade de horas à distância"""
        return self._horario_distancia

    @property
    def shf(self):
        """Quantidade de horas sem hora fixa."""
        return self._shf

    @property
    def localizacao(self):
        """Local onde é realizada a aula da turma"""
        return self._localizacao

    @property
    def alocacao(self):
        """Alocacao (vagas e destino) da turma"""
        return self._alocacao


@dataclass
class Departamento:
    # noinspection PyUnresolvedReferences
    """Um departamento no microhorario

    :arg codigo: codigo do departamento
    :type: str

    :arg nome: nome do departamento
    :type: str
    """

    codigo: str
    nome: str


class Disciplina:
    """Representa uma disciplina no Microhorário"""

    def __init__(self,
                 codigo: str,
                 nome: str,
                 creditos: int,
                 pre_req: bool,
                 departamento: Departamento,
                 ):

        self._codigo: str = codigo
        self._nome: str = nome
        self._creditos: int = creditos
        self._pre_req: bool = pre_req
        self._ementa: Optional[str] = None
        self._departamento = departamento
        self._turmas: Dict[str, Turma] = dict()

    def __repr__(self):
        return f'<Disciplina [{self.codigo}]>'

    @property
    def codigo(self) -> str:
        """Código da disciplina"""
        return self._codigo

    @property
    def nome(self) -> str:
        """Nome da disciplina"""
        return self._nome

    @property
    def creditos(self) -> int:
        """Quantidade de créditos da discplina"""
        return self._creditos

    @property
    def pre_req(self) -> bool:
        """Disciplina contém pré-requisitos"""
        return self._pre_req

    @property
    def ementa(self) -> Optional[str]:
        """
        Ementa da disciplina. Ela precisa ser baixada usando
        `microhorario.coletar_disciplinas()`
        """
        return self._ementa

    @ementa.setter
    def ementa(self, new_ementa: str):
        if self._ementa is None:
            self._ementa = new_ementa

    @property
    def departamento(self) -> Departamento:
        """Departamento da disciplina"""
        return self._departamento

    @property
    def turmas(self) -> List[Turma]:
        """Lista de turmas da disciplina"""
        return list(self._turmas.values())

    def add_turma(self, turma: Turma):
        """Adiciona uma turma na lista da disciplinas"""
        self._turmas[turma.codigo] = turma
