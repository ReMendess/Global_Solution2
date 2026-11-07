"""Portal administrativo fictício (servidor HTTP local).

Serve um formulário HTML simples. Ao submeter, gera um número de protocolo do
portal e devolve uma página de confirmação com `<span id="portal-protocol">`.

Execução:

    python -m rpa.portal.server --port 8100

Sem dependências externas (usa apenas a biblioteca padrão).
"""

from __future__ import annotations

import argparse
import html
import itertools
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

FORM_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Portal Administrativo — Smart Clean City (demonstrativo)</title>
  <style>
    body { font-family: sans-serif; max-width: 560px; margin: 40px auto; padding: 0 16px; }
    label { display: block; margin-top: 12px; font-weight: 600; }
    input, textarea { width: 100%%; padding: 8px; margin-top: 4px; box-sizing: border-box; }
    button { margin-top: 16px; padding: 10px 18px; }
    .note { color: #666; font-size: 14px; }
  </style>
</head>
<body>
  <h1>Portal Administrativo</h1>
  <p class="note">Sistema fictício de demonstração. Todos os dados são simulados.</p>
  <form method="POST" action="/submit">
    <label>Protocolo da ocorrência</label><input id="protocol" name="protocol">
    <label>Categoria</label><input id="category" name="category">
    <label>Prioridade</label><input id="priority" name="priority">
    <label>Bairro</label><input id="neighborhood" name="neighborhood">
    <label>Endereço</label><input id="address" name="address">
    <label>Descrição</label><textarea id="description" name="description" rows="4"></textarea>
    <button id="submit-button" type="submit">Enviar demanda</button>
  </form>
</body>
</html>"""

CONFIRMATION_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>Demanda registrada</title></head>
<body>
  <h1>Demanda registrada com sucesso</h1>
  <p>Protocolo gerado pelo portal:
     <span id="portal-protocol">{protocolo}</span></p>
  <p><a href="/">Registrar outra</a></p>
</body>
</html>"""


class PortalHandler(BaseHTTPRequestHandler):
    """Trata GET (formulário) e POST (submissão)."""

    server_version = "CidadeLimpaPortal/0.1"

    def _send_html(self, corpo: str, status: int = 200) -> None:
        dados = corpo.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            self._send_html(FORM_HTML)
        else:
            self._send_html("<h1>404</h1>", status=404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/submit":
            self._send_html("<h1>404</h1>", status=404)
            return

        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = self.rfile.read(tamanho).decode("utf-8", errors="replace")
        campos = {chave: valor[0] for chave, valor in parse_qs(corpo).items()}

        protocolo = self.server.next_protocol()
        self._send_html(CONFIRMATION_TEMPLATE.format(protocolo=html.escape(protocolo)))

        self.server.registrar(campos, protocolo)

    def log_message(self, formato: str, *args) -> None:  # noqa: N802
        # Silencia o log por requisição para não poluir a saída do robô.
        return


class PortalServer(ThreadingHTTPServer):
    """Servidor HTTP com contador de protocolos e histórico de submissões."""

    daemon_threads = True

    def __init__(self, address, handler_class=PortalHandler) -> None:
        super().__init__(address, handler_class)
        self._contador = itertools.count(1)
        self._historico: list[dict] = []
        self._lock = threading.Lock()

    def next_protocol(self) -> str:
        with self._lock:
            return f"PORTAL-{next(self._contador):04d}"

    def registrar(self, campos: dict, protocolo: str) -> None:
        with self._lock:
            self._historico.append({"fields": campos, "protocol": protocolo})

    @property
    def historico(self) -> list[dict]:
        with self._lock:
            return list(self._historico)


def run_server(host: str = "127.0.0.1", port: int = 8100) -> PortalServer:
    """Sobe o portal e devolve a instância (bloqueante até receber sinais)."""
    servidor = PortalServer((host, port))
    print(f"Portal administrativo fictício em http://{host}:{port}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.shutdown()
        servidor.server_close()
    return servidor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Portal administrativo fictício.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8100)
    args = parser.parse_args(argv)
    run_server(args.host, args.port)
    return 0


if __name__ == "__main__":
    main()
