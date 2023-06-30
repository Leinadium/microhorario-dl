class BaseParsingError(Exception):
    """Exception base para as exceções no HTML

    Attributes:
        mensagem -- Mensagem da exceção
    """
    def __init__(self, mensagem: str):
        self.message = mensagem
        super().__init__(self.message)


class TagNotFoundError(BaseParsingError):
    """Exceção levantada quando o HTML não possui a tag solicitada

    Attributes:
        tag -- Nome da tag não encontrada
    """

    def __init__(self, tag: str):
        self.tag = tag
        super().__init__(f'Tag {tag} não encontrada')


class EmptyTagValueError(BaseParsingError):
    """Excecção levantada quando a tag HTML não tem `value` configurada

    Attributes:
        tag -- Nome da tag sem `value`
    """

    def __init__(self, tag):
        self.tag = tag
        super().__init__(f"Tag {tag} não possui value")


class PatternNotFoundError(BaseParsingError):
    """Exceção levantada quando o pattern não foi encontrado
    na resposta do servidor, impedindo de prosseguir a consulta

    Attributes:
        nome -- nome do pattern procurado
        regex -- regex usado para buscar o pattern
    """

    def __init__(self, nome: str, regex: str):
        self.nome = nome
        self.regex = regex
        super().__init__(
            f"{nome} não foi encontrado no HTML (regex: {regex})"
        )


class NotCSVError(BaseParsingError):
    """Exceção levantada quando a consulta final
    não retornou um CSV.

    Isso pode acontecer quando os
    headers ou o payload da consulta estão incorretos.
    """

    def __init__(self):
        super().__init__("Consulta final não retornou um CSV")


class WebExceptionError(BaseParsingError):
    """Exceção levantada quando a consulta inicial
    retorna uma página de erro.

    Isso pode acontecer quando os
    headers ou o payload da consulta estão incorretos.
    """

    def __init__(self, mensagem: str = ""):
        if not mensagem:
            mensagem = "Primeira consulta retornou uma página de erro"
        super().__init__(mensagem)
