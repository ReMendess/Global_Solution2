import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, useWindowDimensions } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { BottomNav, TopNav } from '@/components/app-nav';
import { colors } from '@/constants/theme';
import { ProfileProvider } from '@/state/profile-context';

/** A partir desta largura a navegação fica no topo (desktop/web). */
const TOP_NAV_BREAKPOINT = 768;

/**
 * Layout raiz: providers globais e a navegação (superior no desktop, inferior no
 * mobile, para que todas as abas fiquem acessíveis em telas estreitas).
 */
export default function RootLayout() {
  const { width } = useWindowDimensions();
  const wide = width >= TOP_NAV_BREAKPOINT;

  return (
    <SafeAreaProvider>
      <ProfileProvider>
        <StatusBar style="dark" />
        <View style={styles.root}>
          {wide ? <TopNav /> : null}
          <View style={styles.stack}>
            <Stack
              screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: colors.background },
              }}
            >
              <Stack.Screen name="index" options={{ title: 'Início' }} />
              <Stack.Screen name="registrar" options={{ title: 'Registrar ocorrência' }} />
              <Stack.Screen name="consultar" options={{ title: 'Consultar protocolo' }} />
              <Stack.Screen name="chat" options={{ title: 'Assistente' }} />
              <Stack.Screen name="admin" options={{ title: 'Administração' }} />
            </Stack>
          </View>
          {wide ? null : <BottomNav />}
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
  stack: {
    flex: 1,
  },
});