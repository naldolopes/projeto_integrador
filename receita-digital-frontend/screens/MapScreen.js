import React, { useState, useCallback, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import MapView, { Marker } from 'react-native-maps';
import { useFocusEffect } from '@react-navigation/native';
import * as Location from 'expo-location'; // Importa o expo-location

const MapScreen = () => {
  const [region, setRegion] = useState(null);
  const [coordinates, setCoordinates] = useState([]);
  const [userLocation, setUserLocation] = useState(null);
  const [hasPermission, setHasPermission] = useState(false); // Estado para verificar permissões

  // Função para obter a localização do usuário
  useEffect(() => {
    const getUserLocation = async () => {
      // Solicitar permissões de localização
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        setHasPermission(true);
        const location = await Location.getCurrentPositionAsync({
          accuracy: Location.Accuracy.High,
        });
        setUserLocation({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
          latitudeDelta: 0.04,
          longitudeDelta: 0.03,
        });
      } else {
        console.log('Permissão de localização não concedida');
      }
    };

    getUserLocation();
  }, []);

  useFocusEffect(
    useCallback(() => {
      setCoordinates([
        {
          id: 1,
          latitude: -23.10603847339874,
          longitude: -45.70746983956266,
          title: 'Farmácia Unimed',
          bestplace: false,
        },
        {
          id: 2,
          latitude: -23.10520168508735,
          longitude: -45.707924723087515,
          title: 'Droga Raia',
          bestplace: true, // Melhor lugar
        },
        {
          id: 3,
          latitude: -23.1035449763157,
          longitude: -45.70921317793684,
          title: 'Carrefour Drogaria',
          bestplace: false,
        },
        {
          id: 4,
          latitude: -23.105696260127,
          longitude: -45.71028606147458,
          title: 'Drogaria São Paulo',
          bestplace: false,
        },
      ]);
    }, [])
  );

  return (
    <View style={styles.container}>
      {userLocation ? (
        <MapView
          style={styles.map}
          region={userLocation}
          onRegionChangeComplete={(newRegion) => setRegion(newRegion)}>
          {/* Exibindo marcador da localização atual */}
          <Marker
            coordinate={{
              latitude: userLocation.latitude,
              longitude: userLocation.longitude,
            }}
            title="Sua Localização"
            description={`Latitude: ${userLocation.latitude.toFixed(
              6
            )}, Longitude: ${userLocation.longitude.toFixed(6)}`}
            pinColor="#0356F8" // Cor do marcador da localização
          />
          {coordinates.map((coord) => (
            <Marker
              key={coord.id}
              coordinate={{
                latitude: coord.latitude,
                longitude: coord.longitude,
              }}
              title={coord.title}
              description={
                coord.bestplace
                  ? 'Melhor Preço da região!'
                  : `Coordenadas: ${coord.latitude.toFixed(
                      6
                    )}, ${coord.longitude.toFixed(6)}`
              }
              pinColor={coord.bestplace ? 'gold' : 'red'} // Alterado para 'yellow' se for o melhor lugar
            />
          ))}
        </MapView>
      ) : (
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>
            {hasPermission
              ? 'Carregando mapa...'
              : 'Permissão de localização necessária!'}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
});

export default MapScreen;
