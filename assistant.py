import os
from pathlib import Path

import requests


API_URL = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
KNOWLEDGE_FILE = Path(__file__).with_name("managepro_knowledge.txt")


def load_system_prompt():
    knowledge = KNOWLEDGE_FILE.read_text(encoding="utf-8").strip()
    return (
        "Tu es l'assistant d'aide de ManagePro. Réponds dans la langue utilisée "
        "par la personne, quelle qu'elle soit, et peux changer de langue si elle "
        "le demande. Comprends et réponds aussi aux messages mêlant plusieurs "
        "langues. Sois clair et pratique. Appuie-toi sur la documentation ci-dessous. "
        "N'invente pas de fonctions ou de règles. La documentation distingue le "
        "fonctionnement décrit comme actuel du cahier des charges; lorsqu'ils se "
        "contredisent, signale la différence et demande une précision si nécessaire. "
        "Si tu ne comprends pas assez bien une langue ou une demande, dis-le "
        "honnêtement et demande une reformulation plutôt que de deviner.\n\n"
        f"Documentation ManagePro :\n{knowledge}"
    )


def request_answer(messages, api_key, model, system_prompt):
    response = requests.post(
        API_URL,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": model,
            "max_tokens": 1024,
            "system": system_prompt,
            "messages": messages,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    content = data.get("content")
    if not isinstance(content, list):
        raise RuntimeError("La réponse d'Anthropic ne contient pas de contenu exploitable.")

    text_blocks = [
        block["text"]
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text"), str)
    ]
    if not text_blocks:
        raise RuntimeError("Anthropic n'a renvoyé aucun texte.")
    return "\n".join(text_blocks)


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("Clé manquante : définis la variable d'environnement ANTHROPIC_API_KEY.")
        return 1

    model = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL).strip()
    if not model:
        print("La variable ANTHROPIC_MODEL ne peut pas être vide.")
        return 1

    try:
        system_prompt = load_system_prompt()
    except OSError as error:
        print(f"Impossible de lire la documentation ManagePro : {error}")
        return 1

    messages = []
    print("Assistant ManagePro prêt. Écris /quit pour quitter.")
    while True:
        try:
            question = input("Vous : ").strip()
        except EOFError:
            print()
            return 0

        if question.lower() in {"/quit", "/exit"}:
            return 0
        if not question:
            continue

        next_messages = messages + [{"role": "user", "content": question}]
        try:
            answer = request_answer(next_messages, api_key, model, system_prompt)
        except requests.RequestException as error:
            print(f"Erreur lors de l'appel à Anthropic : {error}")
            continue
        except RuntimeError as error:
            print(f"Réponse invalide de l'API : {error}")
            continue

        messages = next_messages + [{"role": "assistant", "content": answer}]
        print(f"Assistant : {answer}")


if __name__ == "__main__":
    raise SystemExit(main())
