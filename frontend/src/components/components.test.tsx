import { fireEvent, render, screen } from '@testing-library/react-native';

import { Badge, ProgressBar } from '@/components/badge';
import { Button } from '@/components/button';
import { PriorityBadge, StatusBadge } from '@/components/occurrence-list-item';

describe('Badge', () => {
  it('renderiza o rótulo informado', async () => {
    await render(<Badge label="Crítico" />);

    expect(screen.getByText('Crítico')).toBeTruthy();
  });

  it('usa o rótulo como descrição de acessibilidade', async () => {
    await render(<Badge label="Revisão humana" />);

    expect(screen.getByLabelText('Revisão humana')).toBeTruthy();
  });
});

describe('StatusBadge e PriorityBadge', () => {
  it('traduz o status para português', async () => {
    await render(<StatusBadge status="PENDING_DISPATCH" />);

    expect(screen.getByText('Aguardando envio')).toBeTruthy();
  });

  it('traduz a prioridade para português', async () => {
    await render(<PriorityBadge priority="CRITICAL" />);

    expect(screen.getByText('Crítica')).toBeTruthy();
  });
});

describe('Button', () => {
  it('dispara onPress quando habilitado', async () => {
    const onPress = jest.fn();
    await render(<Button label="Enviar" onPress={onPress} />);

    await fireEvent.press(screen.getByRole('button', { name: 'Enviar' }));

    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it('não dispara onPress quando desabilitado', async () => {
    const onPress = jest.fn();
    await render(<Button label="Enviar" onPress={onPress} disabled />);

    await fireEvent.press(screen.getByRole('button', { name: 'Enviar' }));

    expect(onPress).not.toHaveBeenCalled();
  });

  it('exibe indicador em vez do rótulo durante o carregamento', async () => {
    const { toJSON } = await render(<Button label="Enviar" onPress={jest.fn()} loading />);

    expect(screen.queryByText('Enviar')).toBeNull();
    expect(toJSON()).toBeTruthy();
  });
});

describe('ProgressBar', () => {
  it('renderiza sem erros para valores fora do intervalo', async () => {
    const { toJSON } = await render(<ProgressBar value={150} />);

    expect(toJSON()).toBeTruthy();
  });
});