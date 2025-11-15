from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import torch

app = Flask(__name__)


# Modelos de IA
# Classificador Zero-Shot (Produtivo / Improdutivo)
print("Carregando modelos...")
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0 if torch.cuda.is_available() else -1
)

# Modelo de geração de texto
MODEL_GENERATION = "Qwen/Qwen2.5-1.5B-Instruct"
generator = pipeline(
    "text-generation",
    model=MODEL_GENERATION,
    device=0 if torch.cuda.is_available() else -1
)

print("Modelos carregados com sucesso!")

# Chave-> nome classificação, valor -> frase para categorizar
CANDIDATOS_CLASSIFICACAO = {
    "Produtivo": (
        "Urgencia, Requer ação imediata, trabalho a ser feito ou solicitação, status de chamado"
    ),
    "Improdutivo": (
        "Mensagem de cortesia, agradecimento ou felicitação, engraçado"
    ),
}


# Rota para classificar e gerar resposta
@app.route("/generate", methods=["POST"])
def generate():
    """
    Espera JSON contendo:
    {
        "corpo": "conteúdo do e-mail"
    }
    Retorna JSON:
    {
        "categoria": "Produtivo" | "Improdutivo",
        "resposta": "texto gerado"
    }
    """
    data = request.json or {}
    email_text = data.get("corpo")

    if not email_text:
        return jsonify({"error": "Campo 'corpo' é obrigatório."}), 400

    # Executa classificação
    candidatos = list(CANDIDATOS_CLASSIFICACAO.values())
    resultado = classifier(email_text, candidatos, multi_label=False)
    categoria_texto = resultado["labels"][0]

    # Converte texto da categoria para a chave do dicionário
    reverse_map = {v: k for k, v in CANDIDATOS_CLASSIFICACAO.items()}
    categoria_final = reverse_map.get(categoria_texto, "Produtivo")

    print("Resultado classificação:", resultado)

    # Seleciona prompt conforme categoria
    if categoria_final == "Produtivo":
        prompt = (
            "Você é um assistente corporativo responsável por responder e-mails profissionais.\n"
            "Responda de forma breve, formal e educada, informando que a solicitação está sendo analisada e que o retorno será enviado em breve.\n"
            "Evite se desculpar ou inventar informações novas.\n"
            "Não repita o conteúdo do e-mail original.\n"
            "Apenas escreva o corpo da resposta. Sem assinatura nem título.\n\n"
            f"E-mail recebido:\n{email_text}\n\n"
            "Resposta:\nPrezado(a), "
        )
    else:
        prompt = (
            "Escreva uma resposta curta e simpática de agradecimento à mensagem recebida.\n"
            "Apenas escreva o corpo da resposta.\n"
            "Sem assinatura nem título.\n"
            "Não repita o e-mail original.\n\n"
            f"E-mail recebido:\n{email_text}\n\n"
            "Resposta:\nPrezado(a), "
        )

    # Gera resposta 
    gerado = generator(
        prompt,
        do_sample=True,
        temperature=0.3,
        top_p=0.5,
        top_k=40,
        max_new_tokens=120,
        repetition_penalty=1.2,
        pad_token_id=generator.tokenizer.eos_token_id
    )[0]["generated_text"]

    # Limpa possíveis repetições
    resposta_final = gerado.split("Resposta:")[-1].strip()

    return jsonify({
        "categoria": categoria_final,
        "resposta": resposta_final
    })


# Rota para página
@app.route("/", methods=["GET"])
def home():
    """Renderiza a página principal."""
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
