import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

import type { UserRole } from '@/types/domain';

interface ProfileContextValue {
  role: UserRole;
  isAdmin: boolean;
  setRole: (role: UserRole) => void;
  toggleRole: () => void;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

/**
 * Perfil de acesso da sessão demonstrativa.
 *
 * O backend identifica o perfil pelo cabeçalho `X-User-Role` (docs/DECISIONS.md ADR-014),
 * então basta alternar o valor no cliente. Não há autenticação real nesta fase.
 */
export function ProfileProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole>('CITIZEN');

  const toggleRole = useCallback(() => {
    setRole((atual) => (atual === 'ADMIN' ? 'CITIZEN' : 'ADMIN'));
  }, []);

  const valor = useMemo<ProfileContextValue>(
    () => ({ role, isAdmin: role === 'ADMIN', setRole, toggleRole }),
    [role, toggleRole],
  );

  return <ProfileContext.Provider value={valor}>{children}</ProfileContext.Provider>;
}

/** Acessa o perfil atual da sessão. */
export function useProfile(): ProfileContextValue {
  const contexto = useContext(ProfileContext);
  if (!contexto) {
    throw new Error('useProfile precisa estar dentro de <ProfileProvider>.');
  }
  return contexto;
}