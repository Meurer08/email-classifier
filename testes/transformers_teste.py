from transformers import pipeline
import torch

# === CLASSIFICAÇÃO ===
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0 if torch.cuda.is_available() else -1
)

# === SELEÇÃO DO MODELO DE GERAÇÃO ===
# Você pode alternar aqui 👇
model_name = "Qwen/Qwen2.5-1.5B-Instruct"
#model_name = "brazilian-devs/gpt-neo-pt-1.3B-instruct"

generator = pipeline(
    "text-generation",
    model=model_name,
    device=0 if torch.cuda.is_available() else -1
)

CANDIDATOS_CLASSIFICACAO = {
    "Produtivo": "Urgencia, Requer ação imediata, trabalho a ser feito ou solicitação",
    "Improdutivo": "Mensagem de cortesia, agradecimento ou felicitação"
}

texto_email = """Assunto: 🎉 Boas Festas e Agradecimento pela Parceria em 2025!

Prezada Equipe,

Em nome de toda a nossa divisão, gostaríamos de expressar nossa profunda gratidão pela parceria de sucesso que tivemos ao longo deste ano.

O trabalho em conjunto no projeto de otimização de custos foi fundamental, e agradecemos imensamente a dedicação de todos.

Desejamos a vocês e suas famílias um Natal muito feliz e um excelente começo de 2026!

Atenciosamente,

João Silva Gerente de Relacionamento
"""

candidatos = list(CANDIDATOS_CLASSIFICACAO.values())
resultado_classificacao = classifier(texto_email, candidatos, multi_label=False)
print(resultado_classificacao)

categoria = resultado_classificacao['labels'][0]
mapeamento_reverso = {v: k for k, v in CANDIDATOS_CLASSIFICACAO.items()}
categoria_final = mapeamento_reverso.get(categoria, 'ERRO')
print("Categoria:", categoria_final)


if categoria_final == "Produtivo":
    prompt = (
        "Você é um assistente corporativo responsável por responder e-mails profissionais.\n"
        "Responda de forma breve, formal e educada, informando que a solicitação está sendo analisada e que o retorno será enviado em breve.\n"
        "Evite se desculpar ou inventar informações novas.\n"
        "Não repita o conteúdo do e-mail original.\n"
        "Apenas escreva o corpo da resposta.\n" 
        "sem assinatura nem título.\n\n"
        "Apenas a resposta em texto simples.\n\n"
        f"E-mail recebido:\n{texto_email}\n\n"
        "Resposta:\nPrezado(a), "
    )
else:
    prompt = (
        "Você é um assistente cordial de e-mails corporativos.\n"
        "Escreva uma resposta curta e simpática de agradecimento à mensagem recebida.\n"
        "Apenas escreva o corpo da resposta.\n" 
        "sem assinatura nem título.\n\n"
        "Apenas a resposta.\n\n"
        "Não repita o e-mail, apenas agradeça de forma natural.\n\n"
        f"E-mail recebido:\n{texto_email}\n\n"
        "Resposta:\nPrezado(a), "
    )

print("\nGerando Resposta...\n")


resposta_gerada = generator(
    prompt,
    do_sample=True,
    temperature=0.3,
    top_p=0.5,
    top_k=40,
    max_new_tokens=120,
    repetition_penalty=1.2,
    pad_token_id=generator.tokenizer.eos_token_id
)[0]['generated_text']

resposta_final = resposta_gerada.split("Resposta:")[-1].strip()
print("Resposta final:\n")
print(resposta_final)
