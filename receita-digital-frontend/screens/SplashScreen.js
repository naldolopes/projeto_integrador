import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Image, Animated } from 'react-native';
import Svg, { Defs, LinearGradient, Stop, Rect } from 'react-native-svg';

export default function SplashScreen({ navigation }) {
  const [progress, setProgress] = useState(new Animated.Value(0));

  useEffect(() => {
    // Animação de progresso
    Animated.timing(progress, {
      toValue: 1,
      duration: 2000,
      useNativeDriver: false,
    }).start(() => {
      navigation.replace('Login');
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigation]);

  return (
    <View style={styles.container}>
      {/* Gradiente de fundo */}
      <View style={StyleSheet.absoluteFill}>
        <Svg height="100%" width="100%">
          <Defs>
            <LinearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
              <Stop offset="100%" stopColor="#485E41" stopOpacity="1" />
              <Stop offset="50%" stopColor="#729466" stopOpacity="1" />
              <Stop offset="100%" stopColor="#485E41" stopOpacity="1" />
            </LinearGradient>
          </Defs>
          <Rect x="0" y="0" width="100%" height="100%" fill="url(#grad)" />
        </Svg>
      </View>

      {/* Logo */}
      <Image
        source={require('../assets/images/logo.png')}
        style={styles.logo}
        resizeMode="contain"
      />
      {/* Barra de carregamento */}
      <View style={styles.progressBar}>
        <Animated.View
          style={[
            styles.progress,
            {
              width: progress.interpolate({
                inputRange: [0, 1],
                outputRange: ['0%', '100%'],
              }),
            },
          ]}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 320,
    height: 320,
    marginBottom: 20,
    opacity: 0.8,
  },
  progressBar: {
    height: 10,
    width: '80%',
    backgroundColor: '#ddd',
    borderRadius: 5,
    overflow: 'hidden',
  },
  progress: {
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderRadius: 5,
  },
});
