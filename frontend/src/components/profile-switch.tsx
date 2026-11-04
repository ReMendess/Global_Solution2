import { StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/constants/theme';
import { useProfile } from '@/state/profile-context';

import { Badge } from './badge';

/**
 * Alterna entre os perfis demonstrativos (cidadão/administrador).
 *
 * O backend recebe o perfil pelo cabeçalho `X-User-Role`, portanto a troca é
 * imediata e não exige login (limitação documentada da FASE 2).
 */
export function ProfileSwitch() {
  const { role, toggleRole } = useProfile();

  return (
    <View style={styles.wrapper}>
      <Badge
        label={role === 'ADMIN' ? 'Administrador' : 'Cidadão'}
        background={role === 'ADMIN' ? colors.accentSoft : colors.primarySoft}
        textColor={role === 'ADMIN' ? colors.accent : colors.primary}
      />
      <Text accessibilityRole="button" onPress={toggleRole} style={styles.action}>
        {role === 'ADMIN' ? 'Usar como cidadão' : 'Entrar como admin'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  action: {
    fontSize: typography.caption,
    fontWeight: '700',
    color: colors.primary,
  },
});