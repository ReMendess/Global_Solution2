import { Link, usePathname } from 'expo-router';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, radius, spacing, typography } from '@/constants/theme';

interface NavItem {
  href: '/' | '/registrar' | '/consultar' | '/chat' | '/admin/dashboard';
  label: string;
  short: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: '/', label: 'Início', short: 'Início' },
  { href: '/registrar', label: 'Registrar', short: 'Registrar' },
  { href: '/consultar', label: 'Consultar', short: 'Consultar' },
  { href: '/chat', label: 'Assistente', short: 'Assistente' },
  { href: '/admin/dashboard', label: 'Administração', short: 'Admin' },
];

function isActive(href: string, pathname: string): boolean {
  return href === '/'
    ? pathname === '/'
    : pathname.startsWith(href.split('/').slice(0, 2).join('/'));
}

/** Navegação superior (telas largas / web). */
export function TopNav() {
  const pathname = usePathname();

  return (
    <View style={styles.topBar}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.topRow}>
        <Text style={styles.brand}>Smart Clean City</Text>
        {NAV_ITEMS.map((item) => {
          const ativo = isActive(item.href, pathname);
          return (
            <Link key={item.href} href={item.href} style={[styles.topLink, ativo ? styles.topLinkActive : null]}>
              <Text style={[styles.topLabel, ativo ? styles.topLabelActive : null]}>{item.label}</Text>
            </Link>
          );
        })}
      </ScrollView>
    </View>
  );
}

/** Navegação inferior em abas (telas estreitas / mobile): todas as abas visíveis. */
export function BottomNav() {
  const pathname = usePathname();
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.bottomBar, { paddingBottom: insets.bottom }]}>
      {NAV_ITEMS.map((item) => {
        const ativo = isActive(item.href, pathname);
        return (
          <Link key={item.href} href={item.href} style={[styles.bottomItem, ativo ? styles.bottomItemActive : null]}>
            <Text style={[styles.bottomLabel, ativo ? styles.bottomLabelActive : null]}>{item.short}</Text>
          </Link>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  topBar: {
    backgroundColor: colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    paddingVertical: spacing.xs,
  },
  topRow: {
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
  topLink: {
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.md,
    borderRadius: radius.pill,
  },
  topLinkActive: {
    backgroundColor: colors.primarySoft,
  },
  topLabel: {
    fontSize: typography.caption,
    fontWeight: '600',
    color: colors.textMuted,
  },
  topLabelActive: {
    color: colors.primary,
    fontWeight: '700',
  },
  bottomBar: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  bottomItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: spacing.sm,
    paddingBottom: spacing.sm,
    minHeight: 52,
    borderTopWidth: 2,
    borderTopColor: 'transparent',
  },
  bottomItemActive: {
    borderTopColor: colors.primary,
  },
  bottomLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: colors.textMuted,
    textAlign: 'center',
  },
  bottomLabelActive: {
    color: colors.primary,
    fontWeight: '700',
  },
});