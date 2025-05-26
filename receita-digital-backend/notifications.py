import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NotificationManager:
    def __init__(self):
        self.expo_api_url = "https://exp.host/--/api/v2/push/send"
        self.project_id = os.getenv('EXPO_PROJECT_ID')

    def send_push_notification(self, push_token, title, body, data=None):
        """
        Envia uma notificação push para um dispositivo específico
        """
        try:
            message = {
                "to": push_token,
                "title": title,
                "body": body,
                "data": data or {},
                "sound": "default",
                "priority": "high",
            }

            response = requests.post(
                self.expo_api_url,
                json=message,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao enviar notificação: {response.text}")
                return None

        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return None

    def send_multiple_push_notifications(self, push_tokens, title, body, data=None):
        """
        Envia notificações push para múltiplos dispositivos
        """
        try:
            messages = [
                {
                    "to": token,
                    "title": title,
                    "body": body,
                    "data": data or {},
                    "sound": "default",
                    "priority": "high",
                }
                for token in push_tokens
            ]

            response = requests.post(
                self.expo_api_url,
                json=messages,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erro ao enviar notificações: {response.text}")
                return None

        except Exception as e:
            print(f"Erro ao enviar notificações: {e}")
            return None 