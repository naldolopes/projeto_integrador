import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';

// Configuração do comportamento das notificações
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Função para registrar o dispositivo para receber notificações push
export async function registerForPushNotificationsAsync() {
  let token;

  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'default',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  if (Device.isDevice) {
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      alert('Falha ao obter o token de notificação!');
      return;
    }
    
    // Obter o token Expo Push
    token = (await Notifications.getExpoPushTokenAsync({
      projectId: 'reginaldo.oliveira/receita-digital'
    })).data;

    console.log('Token de notificação:', token);

    // Enviar o token para o backend
    try {
      await fetch('http://localhost:5000/api/notifications/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          platform: Platform.OS,
        }),
      });
    } catch (error) {
      console.error('Erro ao registrar token no backend:', error);
    }
  } else {
    alert('É necessário um dispositivo físico para receber notificações');
  }

  return token;
}

// Função para enviar uma notificação local
export async function sendLocalNotification(title, body, data = {}) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data,
    },
    trigger: null, // null significa que a notificação será enviada imediatamente
  });
}

// Função para agendar uma notificação
export async function scheduleNotification(title, body, trigger, data = {}) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data,
    },
    trigger,
  });
} 