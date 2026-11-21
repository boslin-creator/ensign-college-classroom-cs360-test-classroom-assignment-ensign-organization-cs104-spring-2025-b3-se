import json
import os
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import requests

from assistant import DEFAULT_MODEL, load_system_prompt, request_answer


HOST = "127.0.0.1"
PORT = 8000
MAX_REQUEST_BYTES = 1_000_000
MAX_MESSAGES = 40
MAX_MESSAGE_LENGTH = 8_000
STATIC_DIR = Path(__file__).with_name("static")


def valid_messages(messages):
    if not isinstance(messages, list) or not 1 <= len(messages) <= MAX_MESSAGES:
        return False

    expected_role = "user"
    for message in messages:
        if not isinstance(message, dict):
            return False
        content = message.get("content")
        if (
            message.get("role") != expected_role
            or not isinstance(content, str)
            or not content.strip()
            or len(content) > MAX_MESSAGE_LENGTH
        ):
            return False
        expected_role = "assistant" if expected_role == "user" else "user"

    return messages[-1]["role"] == "user"


class AssistantRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'; connect-src 'self'; "
            "base-uri 'self'; frame-ancestors 'none'",
        )
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_json(404, {"error": "Adresse introuvable."})
            return

        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self.send_json(400, {"error": "Taille de requête invalide."})
            return
        if length <= 0 or length > MAX_REQUEST_BYTES:
            self.send_json(413, {"error": "Requête vide ou trop volumineuse."})
            return

        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_json(400, {"error": "Le corps de la requête doit être un JSON valide."})
            return

        messages = payload.get("messages") if isinstance(payload, dict) else None
        if not valid_messages(messages):
            self.send_json(400, {"error": "Historique de conversation invalide."})
            return

        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            self.send_json(
                503,
                {"error": "Configure la variable ANTHROPIC_API_KEY puis relance l'application."},
            )
            return

        model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL).strip()
        if not model:
            self.send_json(503, {"error": "La variable ANTHROPIC_MODEL ne peut pas être vide."})
            return

        try:
            answer = request_answer(messages, api_key, model, load_system_prompt())
        except requests.RequestException as error:
            self.send_json(502, {"error": f"Erreur lors de l'appel à Anthropic : {error}"})
            return
        except (OSError, RuntimeError) as error:
            self.send_json(500, {"error": f"Impossible de préparer la réponse : {error}"})
            return

        self.send_json(200, {"answer": answer})


def main():
    handler = partial(AssistantRequestHandler, directory=str(STATIC_DIR))
    server = ThreadingHTTPServer((HOST, PORT), handler)
    address = f"http://{HOST}:{PORT}"
    print(f"Assistant ManagePro disponible à {address}")
    print("Garde cette fenêtre ouverte. Appuie sur Ctrl+C pour arrêter.")
    webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt de l'application.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
