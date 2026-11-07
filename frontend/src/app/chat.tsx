import { useRef, useState } from 'react';
import { ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { Button } from '@/components/button';
import { Screen } from '@/components/screen';
import { colors, radius, spacing, typography } from '@/constants/theme';
import { describeError } from '@/hooks/use-async';
import { api } from '@/services/api';

interface Bubble {
  id: number;
  role: 'user' | 'assistant';
  text: string;
}

const SUGESTOES = [
  'registrar ocorrência de transbordamento em Pinheiros',
  'nível do contêiner CONT-001',
  'quantas ocorrências existem?',
];

function gerarSessionId(): string {
  return `sess-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

/** Tela de conversa com o agente (FASE 6). */
export default function ChatScreen() {
  const [sessionId] = useState(gerarSessionId);
  const [mensagens, setMensagens] = useState<Bubble[]>([]);
  const [entrada, setEntrada] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const contador = useRef(0);
  const scrollRef = useRef<ScrollView>(null);

  async function enviar(texto?: string) {
    const mensagem = (texto ?? entrada).trim();
    if (!mensagem || enviando) {
      return;
    }
    setEntrada('');
    setErro(null);
    setMensagens((atual) => [...atual, { id: contador.current++, role: 'user', text: mensagem }]);
    setEnviando(true);

    try {
      const resposta = await api.agentMessage(sessionId, mensagem);
      setMensagens((atual) => [
        ...atual,
        { id: contador.current++, role: 'assistant', text: resposta.response },
      ]);
    } catch (causa) {
      setErro(describeError(causa));
    } finally {
      setEnviando(false);
    }
  }

  return (
    <Screen
      title="Assistente"
      subtitle="Converse com o assistente virtual do Smart Clean City e tire dúvidas sobre ocorrências, contêineres e indicadores."
    >
      <View style={styles.chatBox}>
        <ScrollView
          ref={scrollRef}
          contentContainerStyle={styles.mensagens}
          onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
        >
          {mensagens.length === 0 ? (
            <View style={styles.vazio}>
              <Text style={styles.vazioTitulo}>Como posso ajudar?</Text>
              <Text style={styles.vazioTexto}>
                Digite sua pergunta ou toque em uma das sugestões abaixo.
              </Text>
            </View>
          ) : (
            mensagens.map((bolha) => (
              <View
                key={bolha.id}
                style={[styles.linha, bolha.role === 'user' ? styles.linhaUsuario : styles.linhaAssistente]}
              >
                <View
                  style={[styles.bolha, bolha.role === 'user' ? styles.bolhaUsuario : styles.bolhaAssistente]}
                >
                  <Text
                    style={[
                      styles.textoBolha,
                      bolha.role === 'user' ? styles.textoUsuario : styles.textoAssistente,
                    ]}
                  >
                    {bolha.text}
                  </Text>
                </View>
              </View>
            ))
          )}
        </ScrollView>

        {mensagens.length === 0 ? (
          <View style={styles.sugestoes}>
            {SUGESTOES.map((sugestao) => (
              <Text key={sugestao} style={styles.sugestao} onPress={() => enviar(sugestao)}>
                {sugestao}
              </Text>
            ))}
          </View>
        ) : null}

        {erro ? <Text style={styles.erro}>{erro}</Text> : null}

        <View style={styles.linhaEntrada}>
          <TextInput
            value={entrada}
            onChangeText={setEntrada}
            placeholder="Digite sua mensagem..."
            placeholderTextColor={colors.textMuted}
            style={styles.entrada}
            onSubmitEditing={() => enviar()}
            returnKeyType="send"
            editable={!enviando}
          />
          <Button label="Enviar" onPress={() => enviar()} loading={enviando} />
        </View>
      </View>
    </Screen>
  );
}
const styles = StyleSheet.create({
  chatBox: {
    flex: 1,
    gap: spacing.md,
  },
  mensagens: {
    gap: spacing.sm,
    paddingVertical: spacing.sm,
  },
  vazio: {
    alignItems: 'center',
    gap: spacing.xs,
    paddingVertical: spacing.xl,
  },
  vazioTitulo: {
    fontSize: typography.subheading,
    fontWeight: '700',
    color: colors.text,
  },
  vazioTexto: {
    fontSize: typography.caption,
    color: colors.textMuted,
    textAlign: 'center',
  },
  linha: {
    flexDirection: 'row',
  },
  linhaUsuario: {
    justifyContent: 'flex-end',
  },
  linhaAssistente: {
    justifyContent: 'flex-start',
  },
  bolha: {
    maxWidth: '82%',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm + 2,
    borderRadius: radius.lg,
  },
  bolhaUsuario: {
    backgroundColor: colors.primary,
    borderBottomRightRadius: radius.sm,
  },
  bolhaAssistente: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderBottomLeftRadius: radius.sm,
  },
  textoBolha: {
    fontSize: typography.body,
    lineHeight: 21,
  },
  textoUsuario: {
    color: colors.textInverse,
  },
  textoAssistente: {
    color: colors.text,
  },
  sugestoes: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  sugestao: {
    fontSize: typography.caption,
    color: colors.primary,
    backgroundColor: colors.primarySoft,
    borderRadius: radius.pill,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  erro: {
    fontSize: typography.caption,
    color: colors.danger,
  },
  linhaEntrada: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  entrada: {
    flex: 1,
    minHeight: 46,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: spacing.md,
    backgroundColor: colors.surface,
    color: colors.text,
    fontSize: typography.body,
  },
});