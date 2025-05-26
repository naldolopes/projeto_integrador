import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Keyboard,
  TouchableWithoutFeedback,
  ActivityIndicator,
} from 'react-native';
import Svg, { Defs, LinearGradient, Stop, Rect } from 'react-native-svg';

const API_URL = 'http://10.0.0.2:5000/api';

export default function RegisterScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    email: '',
    senha: '',
    tipo: 'paciente',
    cpf: '',
    telefone: '',
    endereco: '',
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleRegister = async () => {
    // Validação básica
    if (!formData.nome || !formData.email || !formData.senha) {
      Alert.alert('Erro', 'Por favor, preencha todos os campos obrigatórios');
      return;
    }

    if (formData.tipo === 'paciente' && !formData.cpf) {
      Alert.alert('Erro', 'CPF é obrigatório para pacientes');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert(
          'Sucesso',
          'Cadastro realizado com sucesso! Faça login para continuar.',
          [
            {
              text: 'OK',
              onPress: () => navigation.navigate('Login'),
            },
          ]
        );
      } else {
        Alert.alert('Erro', data.message || 'Erro ao realizar cadastro');
      }
    } catch (error) {
      Alert.alert(
        'Erro de Conexão',
        'Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.background}>
        <Svg height="100%" width="100%">
          <Defs>
            <LinearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="0%" stopColor="#729466" stopOpacity="1" />
              <Stop offset="100%" stopColor="#788972" stopOpacity="1" />
            </LinearGradient>
          </Defs>
          <Rect x="0" y="0" width="100%" height="100%" fill="url(#grad)" />
        </Svg>
      </View>

      <KeyboardAvoidingView 
        behavior={Platform.OS === "ios" ? "padding" : "height"}
        style={styles.keyboardView}>
        <ScrollView 
          contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled">
          <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
            <View style={styles.contentContainer}>
              <Text style={styles.title}>Cadastro</Text>
              
              <View style={styles.formContainer}>
                <TextInput
                  style={styles.input}
                  placeholder="Nome Completo"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  value={formData.nome}
                  onChangeText={(value) => handleChange('nome', value)}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Email"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  keyboardType="email-address"
                  autoCapitalize="none"
                  value={formData.email}
                  onChangeText={(value) => handleChange('email', value)}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Senha"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  secureTextEntry
                  value={formData.senha}
                  onChangeText={(value) => handleChange('senha', value)}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="CPF"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  keyboardType="numeric"
                  value={formData.cpf}
                  onChangeText={(value) => handleChange('cpf', value)}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Telefone"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  keyboardType="phone-pad"
                  value={formData.telefone}
                  onChangeText={(value) => handleChange('telefone', value)}
                />
                
                <TextInput
                  style={styles.input}
                  placeholder="Endereço"
                  placeholderTextColor="rgba(0, 0, 0, 0.4)"
                  value={formData.endereco}
                  onChangeText={(value) => handleChange('endereco', value)}
                />

                <TouchableOpacity 
                  style={[styles.button, loading && styles.buttonDisabled]} 
                  onPress={handleRegister}
                  disabled={loading}>
                  {loading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.buttonText}>CADASTRAR</Text>
                  )}
                </TouchableOpacity>

                <TouchableOpacity 
                  style={styles.loginLink}
                  onPress={() => navigation.navigate('Login')}>
                  <Text style={styles.loginLinkText}>
                    Já tem uma conta? Faça login
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          </TouchableWithoutFeedback>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  background: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContainer: {
    flexGrow: 1,
  },
  contentContainer: {
    flex: 1,
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 30,
    marginTop: 20,
  },
  formContainer: {
    width: '100%',
    alignItems: 'center',
  },
  input: {
    width: '100%',
    height: 50,
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
    borderRadius: 25,
    paddingHorizontal: 20,
    fontSize: 16,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.1)',
    color: 'rgba(0, 0, 0, 0.6)',
  },
  button: {
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    borderRadius: 25,
    paddingVertical: 12,
    paddingHorizontal: 32,
    alignItems: 'center',
    marginTop: 20,
    width: '90%',
    height: 50,
    justifyContent: 'center',
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  loginLink: {
    marginTop: 20,
  },
  loginLinkText: {
    color: '#fff',
    fontSize: 16,
    textDecorationLine: 'underline',
  },
});
