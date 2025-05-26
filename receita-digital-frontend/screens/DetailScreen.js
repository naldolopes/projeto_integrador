import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ScrollView,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_URL = 'http://192.168.26.103:5000/api';

export default function DetailScreen({ route, navigation }) {
  const { data, userData } = route.params;
  const [receitaDetalhes, setReceitaDetalhes] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReceitaDetalhes();
  }, []);

  const loadReceitaDetalhes = async () => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      
      const response = await fetch(`${API_URL}/receitas/${data.id_receita}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const detalhes = await response.json();
        setReceitaDetalhes(detalhes);
      } else {
        const errorData = await response.json();
        Alert.alert('Erro', errorData.message || 'Não foi possível carregar os detalhes da receita');
      }
    } catch (error) {
      console.error('Erro ao carregar detalhes da receita:', error);
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR') + ' - ' + 
           date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDateOnly = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const getImageForDoctor = (nome_medico) => {
    const doctorImages = {
      'Dr. Carlos José Marin': require('../assets/images/doc2.jpg'),
      'Dra. Marta Lopes da Silva': require('../assets/images/doc1.jpg'),
      'Dr. Mário Sérgio Calvancante': require('../assets/images/doc3.jpg'),
    };
    
    return doctorImages[nome_medico] || require('../assets/images/doc1.jpg');
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ativa':
        return '#4CAF50';
      case 'utilizada':
        return '#FF9800';
      case 'cancelada':
        return '#F44336';
      case 'expirada':
        return '#9E9E9E';
      default:
        return '#666';
    }
  };

  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#0F2707" />
        <Text style={styles.loadingText}>Carregando detalhes...</Text>
      </View>
    );
  }

  if (!receitaDetalhes) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Erro ao carregar receita</Text>
        <TouchableOpacity 
          style={styles.retryButton} 
          onPress={() => {
            setLoading(true);
            loadReceitaDetalhes();
          }}>
          <Text style={styles.retryButtonText}>Tentar Novamente</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const receita = receitaDetalhes;
  const hasMedicamentos = receita.medicamentos && receita.medicamentos.length > 0;
  const hasExames = receita.exames && receita.exames.length > 0;

  return (
    <ScrollView style={styles.scrollContainer}>
      <View style={styles.container}>
        <View style={styles.card}>
          <Image
            source={require('../assets/images/detail-top.png')}
            style={styles.image}
          />
          <Text style={styles.title}>RECEITA DIGITAL</Text>
          <Text style={styles.subtitle}>
            {receita.numero || `#${receita.id_receita.toString().padStart(8, '0')}`}
          </Text>

          {/* Status da receita */}
          <View style={styles.statusContainer}>
            <Text style={styles.statusLabel}>Status:</Text>
            <Text style={[
              styles.statusText, 
              { color: getStatusColor(receita.status) }
            ]}>
              {receita.status.toUpperCase()}
            </Text>
          </View>

          {/* Local da prescrição */}
          <View style={styles.placeContainer}>
            <Image
              source={require('../assets/images/place.png')}
              style={styles.placeIcon}
            />
            <Text style={styles.placeText}>
              {receita.local || 'Local não informado'}
            </Text>
          </View>

          {/* Informações do médico */}
          <View style={styles.doctorContainer}>
            <View style={styles.doctorNameContainer}>
              <Text style={styles.doctorText}>{receita.nome_medico}</Text>

              <View style={styles.inlineTextContainer}>
                <Text style={styles.doctorSpecText}>{receita.especialidade}</Text>
                <Text style={styles.doctorDocBullet}>{receita.crm}</Text>
              </View>
            </View>

            <Image 
              source={getImageForDoctor(receita.nome_medico)} 
              style={styles.doctorImage} 
            />
          </View>

          <View style={styles.separator} />

          {/* Informações do paciente */}
          <View style={styles.pacientContainer}>
            <Text style={styles.additionalInfoSubText}>Paciente</Text>
            <Text style={styles.pacientInfoText}>
              {userData ? userData.nome : receita.nome_paciente || 'Nome não disponível'}
            </Text>
          </View>

          <View style={styles.separator} />

          {/* Diagnóstico */}
          <View style={styles.pacientContainer}>
            <Text style={styles.additionalInfoSubText}>Diagnóstico</Text>
            <Text style={styles.pacientInfoText}>
              {receita.diagnostico || 'Não informado'}
            </Text>
          </View>

          <View style={styles.separator} />

          {/* Data de emissão e validade */}
          <View style={styles.pacientContainer}>
            <Text style={styles.additionalInfoSubText}>Data de Emissão</Text>
            <Text style={styles.pacientInfoText}>
              {formatDate(receita.data_emissao)}
            </Text>
            <Text style={styles.additionalInfoSubText}>Válida até</Text>
            <Text style={styles.pacientInfoText}>
              {formatDateOnly(receita.data_validade)}
            </Text>
          </View>

          <View style={styles.separator} />

          {/* Medicamentos */}
          {hasMedicamentos && (
            <View style={styles.section}>
              <View style={styles.pacientContainer}>
                <Text style={styles.innnerTitle}>Medicamentos</Text>

                {receita.medicamentos.map((medicamento, index) => (
                  <View key={index} style={styles.innerContainer}>
                    <Image
                      source={require('../assets/images/medicine_logo.png')}
                      style={styles.medicineIcon}
                    />
                    <View style={styles.textContainer}>
                      <Text style={styles.pacientInfoText}>
                        {medicamento.nome}
                      </Text>
                      <Text style={styles.pacientInfoTextDetail}>
                        {medicamento.dosagem} - {medicamento.posologia}
                      </Text>
                      <Text style={styles.pacientInfoTextDetail}>
                        Quantidade: {medicamento.quantidade}
                      </Text>
                      {medicamento.observacoes && (
                        <Text style={styles.pacientInfoTextDetail}>
                          Obs: {medicamento.observacoes}
                        </Text>
                      )}
                    </View>
                  </View>
                ))}

                <TouchableOpacity
                  style={[styles.button, styles.rowButton]}
                  onPress={() =>
                    navigation.navigate('Map', {
                      data: receita,
                    })
                  }>
                  <Text style={styles.buttonText}>Onde Comprar</Text>
                  <Image
                    source={require('../assets/images/map.png')}
                    style={styles.placeIcon}
                  />
                </TouchableOpacity>
              </View>

              <View style={styles.separator} />
            </View>
          )}

          {/* Exames */}
          {hasExames && (
            <View style={styles.section}>
              <View style={styles.pacientContainer}>
                <Text style={styles.innnerTitle}>Exames</Text>

                {receita.exames.map((exame, index) => (
                  <View key={index} style={styles.innerContainer}>
                    <Image
                      source={require('../assets/images/exam_logo.png')}
                      style={styles.medicineIcon}
                    />
                    <View style={styles.textContainer}>
                      <Text style={styles.pacientInfoText}>
                        {exame.nome}
                      </Text>
                      {exame.observacoes && (
                        <Text style={styles.pacientInfoTextDetail}>
                          {exame.observacoes}
                        </Text>
                      )}
                    </View>
                  </View>
                ))}
              </View>
              <View style={styles.separator} />
            </View>
          )}

          {/* Observações gerais */}
          {receita.observacoes && (
            <>
              <View style={styles.pacientContainer}>
                <Text style={styles.additionalInfoSubText}>Observações</Text>
                <Text style={styles.pacientInfoText}>
                  {receita.observacoes}
                </Text>
              </View>
              <View style={styles.separator} />
            </>
          )}

          {/* Footer */}
          <View style={styles.pacientContainer}>
            <Text style={styles.footerPlaceText}>
              {receita.cidade || 'Local'} - {formatDateOnly(receita.data_emissao)}
            </Text>
            <Image
              source={require('../assets/images/code.png')}
              style={styles.codeIcon}
            />
            <Text style={styles.footerSignText}>Assinatura Digital</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContainer: {
    flex: 1,
    backgroundColor: '#EDE8E8',
  },
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#EDE8E8',
    padding: 10,
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
  errorText: {
    fontSize: 18,
    color: '#F44336',
    marginBottom: 20,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#0F2707',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 15,
    width: '100%',
    maxWidth: '95%',
    minHeight: '90%',
    alignSelf: 'center',
    position: 'relative',
  },
  image: {
    width: 66,
    height: 65,
    position: 'absolute',
    top: 10,
    right: 20,
  },
  title: {
    fontSize: 24,
    color: '#222222',
    fontWeight: 'bold',
  },
  innnerTitle: {
    fontSize: 22,
    color: '#222222',
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: 'gray',
    marginBottom: 3,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
    marginBottom: 10,
  },
  statusLabel: {
    fontSize: 14,
    color: 'gray',
    marginRight: 5,
  },
  statusText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  placeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 10,
  },
  placeText: {
    fontSize: 16,
    color: '#222222',
    flex: 1,
  },
  doctorContainer: {
    marginTop: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  doctorNameContainer: {
    flex: 1,
    marginBottom: 5,
  },
  doctorText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#222222',
  },
  inlineTextContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
    flexWrap: 'wrap',
  },
  doctorImage: {
    width: 60,
    height: 60,
    borderRadius: 30,
    marginLeft: 10,
  },
  doctorSpecText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#0356F8',
    marginRight: 5,
  },
  doctorDocBullet: {
    backgroundColor: '#0F2707',
    padding: 5,
    fontSize: 10,
    fontWeight: 'bold',
    minWidth: 90,
    height: 26,
    textAlign: 'center',
    borderRadius: 30,
    color: 'white',
    marginLeft: 5,
  },
  pacientContainer: {
    marginTop: 2,
    padding: 4,
  },
  innerContainer: {
    margin: 10,
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 15,
  },
  medicineIcon: {
    width: 40,
    height: 40,
    marginRight: 15,
    marginTop: 5,
  },
  placeIcon: {
    width: 20,
    height: 20,
    marginRight: 10,
  },
  textContainer: {
    flex: 1,
    justifyContent: 'flex-start',
  },
  pacientInfoText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#222222',
    marginBottom: 5,
  },
  pacientInfoTextDetail: {
    fontSize: 14,
    color: 'gray',
    marginBottom: 3,
  },
  additionalInfoSubText: {
    fontSize: 14,
    color: 'gray',
    marginBottom: 5,
  },
  separator: {
    margin: 5,
    height: 1,
    backgroundColor: '#ddd',
  },
  rowButton: {
    margin: 10,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  button: {
    width: 200,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#0F2707',
    alignItems: 'center',
    alignSelf: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    fontSize: 16,
    color: '#fff',
    marginRight: 8,
    fontWeight: 'bold',
  },
  footerPlaceText: {
    fontSize: 13,
    color: '#222222',
    alignSelf: 'center',
    marginBottom: 5,
  },
  footerSignText: {
    fontSize: 11,
    color: 'gray',
    alignSelf: 'center',
  },
  codeIcon: {
    margin: 5,
    width: 110,
    height: 110,
    alignSelf: 'center',
  },
  section: {
    marginBottom: 10,
  },
});