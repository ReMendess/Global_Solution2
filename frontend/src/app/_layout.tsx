import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AppNav } from '@/components/app-nav';
import { colors } from '@/constants/theme';
import { ProfileProvider } from '@/state/profile-context';

/**
 * Layout raiz: providers globais, barra de navegação e pilha de telas.
 *
 * O Expo Router usa esta configuração tanto no nativo quanto no React Native Web.
 */
export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <ProfileProvider>
        <StatusBar style="dark" />
        <View style={styles.root}>
          <AppNav />
          <Stack
            screenOptions={{
              headerShown: false,
              contentStyle: { backgroundColor: colors.background },
            }}
          >
            <Stack.Screen name="index" options={{ title: 'Início' }} />
            <Stack.Screen name="registrar" options={{ title: 'Registrar ocorrência' }} />
            <Stack.Screen name="consultar" options={{ title: 'Consultar protocolo' }} />
            <Stack.Screen name="admin" options={{ title: 'Administração' }} />
          </Stack>
        </View>
      </ProfileProvider>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
});