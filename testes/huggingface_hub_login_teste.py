from huggingface_hub import login
import getpass
import os

print("--- Hugging Face Login Programático ---")
print("Este script salvará seu token de acesso no cache local.")

try:
    hf_token = getpass.getpass("Por favor, digite seu Token de Acesso do Hugging Face: ")

    login(token=hf_token)
    
    print("\n✅ Autenticação realizada com sucesso!")
    print("Seu token foi salvo. Você pode agora prosseguir com o teste de modelos restritos.")
    
except Exception as e:
    print(f"\n Erro durante a autenticação: {e}")
    print("Verifique se o token foi digitado corretamente e tente novamente.")