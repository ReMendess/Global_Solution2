import type { ReactNode } from 'react';
import { ScrollView, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { CONTENT_MAX_WIDTH, colors, isWide, spacing, typography } from '@/constants/theme';

interface ScreenProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  /** Cabeçalho adicional (badges, ações). */
  headerRight?: ReactNode;
  /** Quando falso, o conteúdo não é rolável (telas curtas). */
  scrollable?: boolean;
}

/**
 * Contêiner padrão das telas: limita a largura no desktop, aplica padding e
 * centraliza o conteúdo — garantindo o mesmo layout no mobile e na web.
 */
export function Screen({ title, subtitle, children, headerRight, scrollable = true }: ScreenProps) {
  const { width } = useWindowDimensions();
  const wide = isWide(width);

  const corpo = (
    <View style={[styles.content, wide ? styles.contentWide : null]}>
      <View style={styles.header}>
        <View style={styles.headerTexts}>
          <Text style={[styles.title, wide ? styles.titleWide : null]}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        {headerRight ? <View style={styles.headerRight}>{headerRight}</View> : null}
      </View>
      {children}
    </View>
  );

  return (
    <SafeAreaView style={styles.safe} edges={['top', 'left', 'right']}>
      {scrollable ? (
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          {corpo}
        </ScrollView>
      ) : (
        corpo
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scrollContent: {
    flexGrow: 1,
    paddingBottom: spacing.xxl,
  },
  content: {
    flex: 1,
    width: '100%',
    alignSelf: 'center',
    paddingHorizontal: spacing.lg,
    paddingTop: spacing.lg,
    gap: spacing.lg,
  },
  contentWide: {
    maxWidth: CONTENT_MAX_WIDTH,
    paddingHorizontal: spacing.xl,
    paddingTop: spacing.xl,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: spacing.md,
  },
  headerTexts: {
    flex: 1,
    gap: spacing.xs,
  },
  headerRight: {
    alignItems: 'flex-end',
  },
  title: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.text,
  },
  titleWide: {
    fontSize: 26,
  },
  subtitle: {
    fontSize: typography.body,
    color: colors.textMuted,
    lineHeight: 22,
  },
});

/** Grades responsivas reutilizadas pelas telas. */
export function useResponsiveColumns(maxColumns = 3): { columns: number; gap: number } {
  const { width } = useWindowDimensions();
  if (width >= 1100) {
    return { columns: maxColumns, gap: spacing.lg };
  }
  if (width >= 700) {
    return { columns: Math.max(2, maxColumns - 1), gap: spacing.md };
  }
  return { columns: 1, gap: spacing.md };
}