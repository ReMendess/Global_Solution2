import { Text } from 'react-native';

import type { ReactNode } from 'react';

import { Card } from '@/components/card';
import { ProfileSwitch } from '@/components/profile-switch';
import { colors } from '@/constants/theme';
import { useProfile } from '@/state/profile-context';

/** Bloqueia o conteúdo administrativo quando o perfil ativo é o do cidadão. */
export function AdminGate({ children }: { children: ReactNode }) {
  const { isAdmin } = useProfile();

  if (!isAdmin) {
    return (
      <Card
        title="Área administrativa"
        subtitle="Estas informações são restritas ao perfil administrador (a API responderia 403)."
      >
        <Text style={{ color: colors.textMuted }}>
          Troque para o perfil administrador para consultar indicadores, ocorrências e contêineres.
        </Text>
        <ProfileSwitch />
      </Card>
    );
  }

  return <>{children}</>;
}