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
            item.href === '/'
              ? pathname === '/'
              : pathname.startsWith(item.href.split('/').slice(0, 2).join('/'));
          return (
            <Link key={item.href} href={item.href} style={[styles.link, ativo ? styles.linkActive : null]}>
              <Text style={[styles.linkLabel, ativo ? styles.linkLabelActive : null]}>{item.label}</Text>
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
    paddingVertical: spacing.xs,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingHorizontal: spacing.md,
    minHeight: 40,
  },
  brand: {
    fontSize: typography.body,
    fontWeight: '800',
    color: colors.primary,
    marginRight: spacing.md,
  },
  link: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
  },
  linkActive: {
    backgroundColor: colors.primarySoft,
  },
  linkLabel: {
    fontSize: typography.caption,
    fontWeight: '600',
    color: colors.textMuted,
  },
  linkLabelActive: {
    color: colors.primary,
    fontWeight: '700',
  },
});