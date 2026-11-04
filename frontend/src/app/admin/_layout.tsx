import { Stack } from 'expo-router';

import { colors } from '@/constants/theme';

/** Pilha de telas da área administrativa. */
export default function AdminLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: colors.background },
      }}
    >
      <Stack.Screen name="dashboard" options={{ title: 'Dashboard' }} />
      <Stack.Screen name="ocorrencias" options={{ title: 'Ocorrências' }} />
      <Stack.Screen name="ocorrencias/[id]" options={{ title: 'Detalhe da ocorrência' }} />
      <Stack.Screen name="conteineres" options={{ title: 'Contêineres' }} />
    </Stack>
  );
}