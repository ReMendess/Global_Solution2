import { Link } from 'expo-router';
import { StyleSheet, Text, View } from 'react-native';

import { colors, spacing, typography } from '@/constants/theme';

/** Tela exibida quando a rota não existe. */
export default function NotFoundScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Página não encontrada</Text>
      <Text style={styles.text}>O endereço acessado não existe nesta aplicação.</Text>
      <Link href="/" style={styles.link}>
        <Text style={styles.linkLabel}>Voltar para o início</Text>
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.md,
    padding: spacing.xl,
    backgroundColor: colors.background,
  },
  title: {
    fontSize: typography.heading,
    fontWeight: '700',
    color: colors.text,
  },
  text: {
    fontSize: typography.body,
    color: colors.textMuted,
    textAlign: 'center',
  },
  link: {
    paddingVertical: spacing.sm,
  },
  linkLabel: {
    fontSize: typography.body,
    fontWeight: '700',
    color: colors.primary,
  },
});