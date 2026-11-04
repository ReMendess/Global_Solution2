import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { colors, radius, spacing, typography } from '@/constants/theme';

export interface ChipOption<T extends string> {
  value: T;
  label: string;
}

interface ChoiceChipsProps<T extends string> {
  options: ChipOption<T>[];
  value: T | undefined;
  onChange: (value: T | undefined) => void;
  /** Permite limpar a seleção tocando no item já selecionado. */
  allowClear?: boolean;
  title?: string;
}

/** Grupo de opções em formato de chips, usado nos filtros e no formulário. */
export function ChoiceChips<T extends string>({
  options,
  value,
  onChange,
  allowClear = true,
  title,
}: ChoiceChipsProps<T>) {
  return (
    <View style={styles.wrapper}>
      {title ? <Text style={styles.title}>{title}</Text> : null}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.row}>
        {options.map((opcao) => {
          const selecionado = opcao.value === value;
          return (
            <Pressable
              key={opcao.value}
              accessibilityRole="button"
              accessibilityState={{ selected: selecionado }}
              onPress={() => {
                if (selecionado && allowClear) {
                  onChange(undefined);
                  return;
                }
                onChange(opcao.value);
              }}
              style={({ pressed }) => [
                styles.chip,
                selecionado ? styles.chipSelected : null,
                pressed ? styles.chipPressed : null,
              ]}
            >
              <Text style={[styles.chipLabel, selecionado ? styles.chipLabelSelected : null]}>
                {opcao.label}
              </Text>
            </Pressable>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    gap: spacing.sm,
  },
  title: {
    fontSize: typography.caption,
    fontWeight: '700',
    color: colors.textMuted,
  },
  row: {
    flexDirection: 'row',
    gap: spacing.sm,
    paddingRight: spacing.sm,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  chipSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  chipPressed: {
    opacity: 0.85,
  },
  chipLabel: {
    fontSize: typography.caption,
    fontWeight: '600',
    color: colors.textMuted,
  },
  chipLabelSelected: {
    color: colors.textInverse,
  },
});