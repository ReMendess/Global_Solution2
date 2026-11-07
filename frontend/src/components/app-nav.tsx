import { Link, usePathname } from 'expo-router';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/constants/theme';

interface NavItem {
  href: '/' | '/registrar' | '/consultar' | '/chat' | '/admin/dashboard';
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: '/', label: 'Início' },
  { href: '/registrar', label: 'Registrar' },
  { href: '/consultar', label: 'Consultar' },
  { href: '/chat', label: 'Assistente' },
  { href: '/admin/dashboard', label: 'Administração' },
];

/** Barra de navegação superior, comum a todas as telas (web e mobile). */
export function AppNav() {
  const pathname = usePathname();

  return (
    <View style={styles.bar}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.row}>
        <Text style={styles.brand}>Smart Clean City</Text>
        {NAV_ITEMS.map((item) => {
          const ativo =
            item.href === '/' ? pathname === '/' : pathname.startsWith(item.href.split('/').slice(0, 2).join('/'));
          return (
            <Link key={item.href} href={item.href} style={styles.link}>
              <Text style={[styles.linkLabel, ativo ? styles.linkActive : null]}>{item.label}</Text>
            </Link>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  bar: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.lg,
    paddingHorizontal: spacing.lg,
    minHeight: 44,
  },
  brand: {
    fontSize: typography.subheading,
    fontWeight: '800',
    color: colors.primary,
    marginRight: spacing.sm,
  },
  link: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    borderRadius: radius.sm,
  },
  linkLabel: {
    fontSize: typography.body,
    fontWeight: '600',
    color: colors.textMuted,
  },
  linkActive: {
    color: colors.primary,
  },
});