import os
import sys
import django
from django.conf import settings
from django.core.mail import EmailMessage

# Configurar o ambiente Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def testar_envio():
    print("--- Diagnóstico Simples de Email ---")
    destinatario = input("Digite o email EXTERNO (Gmail/Hotmail) para testar: ")
    
    if not destinatario:
        return

    try:
        # Pega exatamente o usuário logado para evitar bloqueio do Google
        remetente_real = settings.EMAIL_HOST_USER
        print(f"\nTentando enviar DE: {remetente_real}")
        print(f"Tentando enviar PARA: {destinatario}")
        
        email = EmailMessage(
            subject='Teste de Entrega Imobidon - Google SMTP',
            body='Este é um teste de entrega forçando o remetente correto.\nSe chegou, ajuste seu DEFAULT_FROM_EMAIL no .env',
            from_email=remetente_real,  # Forçando ser igual ao user logado
            to=[destinatario],
        )
        
        # Força o backend retornar a resposta do servidor
        retorno = email.send(fail_silently=False)
        
        print(f"\n[Status do Envio: {retorno}]")
        if retorno == 1:
            print("✅ SUCESSO! O Google aceitou o email.")
            print("👉 Agora vá na caixa de SPAM do email de destino e verifique.")
        else:
            print("⚠️ O envio retornou 0. Algo estranho aconteceu.")
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: O Google rejeitou conexao.")
        print(e)

if __name__ == "__main__":
    testar_envio()
