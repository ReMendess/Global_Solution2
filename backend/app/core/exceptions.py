"""Exceções de domínio traduzidas para respostas HTTP pelo handler global."""

from __future__ import annotations


class AppError(Exception):
    """Erro de regra de negócio com status HTTP associado."""

    status_code: int = 400
    default_detail: str = "Não foi possível processar a solicitação."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Recurso inexistente."""

    status_code = 404
    default_detail = "Recurso não encontrado."


class ConflictError(AppError):
    """Violação de regra de negócio que conflita com o estado atual."""

    status_code = 409
    default_detail = "A operação conflita com o estado atual do recurso."


class UnprocessableError(AppError):
    """Entrada válida em formato, mas inválida para a regra de negócio."""

    status_code = 422
    default_detail = "Dados inválidos para esta operação."


class PayloadTooLargeError(AppError):
    """Arquivo enviado acima do limite configurado."""

    status_code = 413
    default_detail = "Arquivo enviado excede o limite permitido."


class ForbiddenError(AppError):
    """Perfil de acesso sem permissão para a rota."""

    status_code = 403
    default_detail = "Perfil sem permissão para executar esta operação."


class ModelUnavailableError(AppError):
    """Modelo de visão computacional ainda não treinado/carregado."""

    status_code = 503
    default_detail = (
        "Modelo de classificação indisponível. Treine o modelo (FASE 3) e publique os pesos "
        "em ml/models/ antes de usar a inferência."
    )
