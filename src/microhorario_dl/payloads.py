__all__ = ["PayloadMicrohorario"]

from enum import Enum, auto


class PayloadModo(Enum):
    """Modo de utilização dos Payloads"""
    MICROHORARIO = auto()       # utiliza a configuração padrão
    HORARIO = auto()            # utiliza a configuração alternativa


class PayloadMicrohorario:
    _INTERMEDIARIO = {
        "ScriptManager1": "pnlConteudo|btnBuscar",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "ddlNivel": "Sem Distinção",
        "txtCodigoDptDcp": "",
        "txtNomeDcp": "",
        "txtQtdCreditos": "",
        "txtNomeProfessor": "",
        "ddlBloqueio": "-1",
        "ddlDia": "Qualquer dia",
        "txtHoraInicio": "",
        "txtHoraFim": "",
        "ddlTurno": "-1",
        "ddlDeptoSolicitante": "-1",
        "hiddenInputToUpdateATBuffer_CommonToolkitScripts": "1",
        "__ASYNCPOST": "true",
        "btnBuscar": "Buscar",
    }

    _FINAL = {
        "ddlNivel": "Sem Distinção",
        "txtCodigoDptDcp": "",
        "txtNomeDcp": "",
        "txtQtdCreditos": "",
        "txtNomeProfessor": "",
        "ddlBloqueio": "-1",
        "ddlDia": "Qualquer dia",
        "txtHoraInicio": "",
        "txtHoraFim": "",
        "ddlTurno": "-1",
        "ddlDeptoSolicitante": "-1",
        "ddlNumResultados": "25",
        "ddlExtensao": "Texto",
        "btnDownload": "Baixar",
        "hiddenInputToUpdateATBuffer_CommonToolkitScripts": "1",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": ""
    }

    MODO = PayloadModo.MICROHORARIO

    @classmethod
    def altera_modo(cls):
        cls.MODO = PayloadModo.MICROHORARIO if cls.MODO == PayloadModo.HORARIO else PayloadModo.HORARIO

    @classmethod
    def intermediario(cls) -> dict:
        if cls.MODO == PayloadModo.MICROHORARIO:
            return cls._INTERMEDIARIO
        else:
            # removendo as opções que não existem no payload para o Horarios e Salas
            return cls._remove(cls._INTERMEDIARIO)

    @classmethod
    def final(cls) -> dict:
        if cls.MODO == PayloadModo.MICROHORARIO:
            return cls._FINAL
        else:
            # removendo as opções que não existem no payload para o Horarios e Salas
            return cls._remove(cls._FINAL)

    @classmethod
    def _remove(cls, payload: dict):
        ret = payload.copy()
        del ret["txtQtdCreditos"]
        del ret["ddlBloqueio"]
        del ret["ddlTurno"]
        return ret
