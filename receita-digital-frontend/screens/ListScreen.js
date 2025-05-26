import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  Text,
  TouchableOpacity,
  StyleSheet,
  Dimensions,
  Image,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import Svg, { Rect, Defs, LinearGradient, Stop } from 'react-native-svg';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://192.168.26.103:5000/api';

const { height, width } = Dimensions.get('window');

export default function ListScreen({ route, navigation }) {
  const [userData, setUserData] = useState(null);
  const [receitas, setReceitas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadUserData();
    loadReceitas();
  }, []);

  const loadUserData = async () => {
    try {
      const storedUserData = await AsyncStorage.getItem('userData');
      if (storedUserData) {
        const user = JSON.parse(storedUserData);
        setUserData(user);
        
        // Se for paciente, buscar dados específicos do perfil
        if (user.tipo === 'paciente') {
          await loadProfileData();
        }
      }
    } catch (error) {
      console.error('Erro ao carregar dados do usuário:', error);
    }
  };

  const loadProfileData = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      const response = await fetch(`${API_URL}/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const profileData = await response.json();
        setUserData(prevData => ({
          ...prevData,
          ...profileData
        }));
      }
    } catch (error) {
      console.error('Erro ao carregar perfil:', error);
    }
  };

  const loadReceitas = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      
      const response = await fetch(`${API_URL}/receitas`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const receitasData = await response.json();
        setReceitas(receitasData);
      } else {
        const errorData = await response.json();
        Alert.alert('Erro', errorData.message || 'Não foi possível carregar as receitas');
      }
      
    } catch (error) {
      console.error('Erro ao carregar receitas:', error);
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };



  const onRefresh = () => {
    setRefreshing(true);
    loadReceitas();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' - ' + 
           date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const getItensPrescritos = (receita) => {
    const tipos = [];
    if (receita.medicamentos && receita.medicamentos.length > 0) {
      tipos.push('MEDICAMENTOS');
    }
    if (receita.exames && receita.exames.length > 0) {
      tipos.push('EXAMES');
    }
    return tipos;
  };

  const getImageForDoctor = (nome_medico) => {
    // Mapear médicos para imagens (você pode expandir isso baseado nos seus dados)
    const doctorImages = {
      'Dr. Carlos José Marin': require('../assets/images/doc2.jpg'),
      'Dra. Marta Lopes da Silva': require('../assets/images/doc1.jpg'),
      'Dr. Mário Sérgio Calvancante': require('../assets/images/doc3.jpg'),
    };
    
    return doctorImages[nome_medico] || require('../assets/images/doc1.jpg'); // imagem padrão
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Deseja realmente sair do aplicativo?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Sair',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem('userToken');
              await AsyncStorage.removeItem('userData');
              navigation.replace('Login');
            } catch (error) {
              console.error('Erro ao fazer logout:', error);
            }
          },
        },
      ]
    );
  };

  const renderItem = ({ item }) => {
    const itensPrescritos = getItensPrescritos(item);
    
    return (
      <View style={styles.item}>
        <View style={styles.row}>
          <View style={styles.textLeft}>
            <Text style={styles.title}>{item.nome_medico}</Text>
            <Text style={styles.subtitle}>{item.especialidade}</Text>
            <Text style={styles.subtitle}>{item.crm}</Text>
          </View>
          <Image source={getImageForDoctor(item.nome_medico)} style={styles.imageCard} />
        </View>

        <View style={styles.separator} />
        <View style={styles.section}>
          <Text style={styles.subtitle}>Paciente</Text>
          <Text style={styles.textLeftAligned}>
            {userData ? userData.nome : 'Carregando...'}
          </Text>
        </View>

        <View style={styles.separator} />
        <View style={styles.section}>
          <Text style={styles.subtitle}>Data da Receita</Text>
          <Text style={styles.textLeftAligned}>
            {formatDate(item.data_emissao)}
          </Text>
        </View>

        <View style={styles.separator} />
        <View style={styles.section}>
          <Text style={styles.subtitle}>Número da Receita</Text>
          <Text style={styles.textLeftAligned}>
            {item.numero || `#${item.id_receita.toString().padStart(8, '0')}`}
          </Text>
        </View>

        <View style={styles.separator} />
        <View style={styles.section}>
          <Text style={styles.subtitle}>Status</Text>
          <Text style={[
            styles.textLeftAligned,
            { color: item.status === 'ativa' ? '#4CAF50' : '#FF9800' }
          ]}>
            {item.status.toUpperCase()}
          </Text>
        </View>

        <View style={styles.separator} />
        <View style={styles.section}>
          <Text style={styles.subtitle}>Itens Prescritos</Text>
          {itensPrescritos.map((tipo, index) => (
            <View key={index} style={styles.textContainer}>
              <Image
                source={require('../assets/images/check.png')}
                style={styles.icon}
              />
              <Text style={styles.checkText}>{tipo}</Text>
            </View>
          ))}
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={() =>
            navigation.navigate('Details', {
              data: item,
              userData: userData,
            })
          }>
          <Text style={styles.buttonText}>VISUALIZAR</Text>
        </TouchableOpacity>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#729466" />
        <Text style={styles.loadingText}>Carregando receitas...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.topView}>
        <Svg height={height * 0.4} width={width}>
          <Defs>
            <LinearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="100%" stopColor="#485E41" stopOpacity="1" />
              <Stop offset="50%" stopColor="#729466" stopOpacity="1" />
              <Stop offset="100%" stopColor="#485E41" stopOpacity="1" />
            </LinearGradient>
          </Defs>
          <Rect x="0" y="0" width="100%" height="100%" fill="url(#grad)" />
        </Svg>

        <View style={styles.profileContainer}>
          <Image 
            source={require('../assets/images/user_photo.jpg')} 
            style={styles.picture} 
          />
          <Text style={styles.userText}>
            {userData ? userData.nome : 'Carregando...'}
          </Text>

          <View style={styles.textContainer}>
            <Image
              source={require('../assets/images/card.png')}
              style={styles.icon}
            />
            <Text style={styles.docText}>
              {userData && userData.cpf ? userData.cpf : userData && userData.email ? userData.email : 'Carregando...'}
            </Text>
          </View>

          <View style={styles.textContainer}>
            <Image
              source={require('../assets/images/phone.png')}
              style={styles.icon}
            />
            <Text style={styles.phoneText}>
              {userData && userData.telefone ? userData.telefone : 'Não informado'}
            </Text>
          </View>

          <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
            <Text style={styles.logoutText}>Sair</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={styles.fixedView}>
        <View style={styles.textContainer}>
          <Image
            source={require('../assets/images/case.png')}
            style={styles.header_icon}
          />
          <Text style={styles.fixedText}>RECEITAS DIGITAIS</Text>
        </View>
      </View>

      <FlatList
        data={receitas}
        renderItem={renderItem}
        keyExtractor={(item) => item.id_receita.toString()}
        contentContainerStyle={styles.listContainer}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            colors={['#729466']}
          />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Nenhuma receita encontrada</Text>
            <TouchableOpacity style={styles.refreshButton} onPress={onRefresh}>
              <Text style={styles.refreshButtonText}>Atualizar</Text>
            </TouchableOpacity>
          </View>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#EDE8E8',
  },
  centered: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  topView: {
    width: width,
    height: height * 0.4,
    justifyContent: 'center',
    alignItems: 'center',
    position: 'absolute',
    zIndex: 1,
    top: 0,
  },
  profileContainer: {
    position: 'absolute',
    bottom: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  picture: {
    marginTop: 20,
    width: 130,
    height: 130,
    borderRadius: 130 / 2,
  },
  userText: {
    marginTop: 10,
    color: '#0F2707',
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  docText: {
    color: '#0F2707',
    fontSize: 16,
  },
  phoneText: {
    color: '#0F2707',
    fontSize: 16,
  },
  checkText: {
    color: 'rgba(0, 0, 0, 0.8)',
    fontWeight: 'bold',
    fontSize: 16,
  },
  logoutButton: {
    marginTop: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    paddingHorizontal: 15,
    paddingVertical: 5,
    borderRadius: 15,
  },
  logoutText: {
    color: '#0F2707',
    fontSize: 14,
    fontWeight: 'bold',
  },
  listContainer: {
    paddingTop: height * 0.4 + 45,
    paddingHorizontal: 16,
    paddingBottom: 5,
  },
  item: {
    backgroundColor: '#fff',
    padding: 20,
    marginVertical: 8,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: 'gray',
    marginBottom: 3,
  },
  textContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
  },
  icon: {
    width: 20,
    height: 20,
    tintColor: '#0F2707',
    marginRight: 10,
  },
  header_icon: {
    width: 22,
    height: 20,
    marginRight: 10,
  },
  fixedView: {
    position: 'absolute',
    paddingLeft: 20,
    top: height * 0.4,
    width: width,
    backgroundColor: '#EDE8E8',
    padding: 5,
    zIndex: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  fixedText: {
    fontSize: 20,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  separator: {
    height: 1,
    backgroundColor: '#ddd',
    marginVertical: 10,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textLeft: {
    flex: 1,
    marginRight: 10,
  },
  section: {
    marginBottom: 5,
  },
  textLeftAligned: {
    fontSize: 16,
    color: '#333',
    marginBottom: 5,
  },
  button: {
    backgroundColor: '#0F2707',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  imageCard: {
    width: 60,
    height: 60,
    borderRadius: 30,
    aspectRatio: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingTop: 50,
  },
  emptyText: {
    fontSize: 18,
    color: '#666',
    marginBottom: 20,
  },
  refreshButton: {
    backgroundColor: '#729466',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  refreshButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});