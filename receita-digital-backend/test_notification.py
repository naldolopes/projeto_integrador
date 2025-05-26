from notifications import NotificationManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_notification():
    # Inicializa o gerenciador de notificações
    notification_manager = NotificationManager()
    
    # Token do dispositivo (você precisa substituir pelo token real)
    token = "SEU_TOKEN_AQUI"  # Substitua pelo token que você recebeu do frontend
    
    # Envia a notificação
    response = notification_manager.send_push_notification(
        token,
        "Nova Receita",
        "Você recebeu uma nova receita médica",
        {
            "tipo": "receita",
            "id_receita": 123
        }
    )
    
    print("Resposta:", response)

if __name__ == "__main__":
    test_notification() 