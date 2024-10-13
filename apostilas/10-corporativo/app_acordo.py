# %%
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# %%
# Configurações do Streamlit
st.title('Simulação de Estratégia de Acordo')
st.sidebar.header('Configurações')

# Configurações ajustáveis pelo usuário
num_tentativas_por_mes = st.sidebar.slider('Número de tentativas por mês', min_value=1, max_value=50, value=30)
orcamento = st.sidebar.slider('Orçamento disponível para acordos', min_value=1e5, max_value = 6e6, value=2e6, step=1e5)
alcada = st.sidebar.slider('Alçada para a estratégia de acordo', min_value=0.0, max_value=1.0, value=0.5, step=0.01)
p_minima = st.sidebar.slider('Probabilidade mínima de derrota', min_value=0.1, max_value=0.9, value=0.5, step=0.1)
n_simulacoes = st.sidebar.slider('Número de simulações', min_value=100, max_value=1000, value=100, step=100)


# %%
#num_tentativas_por_mes, orcamento, alcada = 30, 800000, 0.5

# Simulação de processos
np.random.seed(42)
n_processos = 300
valores_causa = np.random.uniform(5000, 80000, n_processos)
prob_derrota = np.random.uniform(0.1, 0.9, n_processos)
tempos_esperados = np.random.uniform(1, 5, n_processos) * 12  # Convertendo anos para meses
max_meses = 60  # Definindo o número máximo de meses

# Função para calcular a probabilidade de sucesso do acordo
def probabilidade_acordo(alcada):
    return 1 / (1 + np.exp(10 - 15 * alcada))

# Função para simular uma estratégia mês a mês
def simular_estrategia(alcada, num_tentativas_por_mes, orcamento, max_meses):
    gastos_acumulados = np.zeros(max_meses)  # Inicializa array de gastos acumulados com tamanho fixo
    total_gastos = 0
    processos_por_tentar = np.argsort(-prob_derrota)  # Ordena por maior probabilidade de derrota
    tempos_restantes = tempos_esperados.copy()  # Copia os tempos esperados para atualizar
    finalizados = np.zeros(n_processos, dtype=bool)  # Para marcar processos finalizados
    perdido = np.random.rand(n_processos) < prob_derrota  # Processos perdidos

    for mes in range(1, max_meses + 1):
        tentativas = 0

        # Finalizar processos cujo tempo já passou
        for processo in range(n_processos):
            if tempos_restantes[processo] <= mes and not finalizados[processo]:
                # O processo é finalizado
                if perdido[processo]:  # Processo perdido
                    total_gastos += valores_causa[processo]
                finalizados[processo] = True

        # Tentativas de acordo em processos que ainda não foram finalizados
        for processo in processos_por_tentar:
            if tentativas >= num_tentativas_por_mes or total_gastos >= orcamento:
                break  # Limita o número de tentativas e o orçamento

            if prob_derrota[processo] > p_minima and tempos_restantes[processo] > mes and not finalizados[processo]:
                valor_acordo = valores_causa[processo] * alcada
                sucesso = np.random.rand() < probabilidade_acordo(alcada)
                tentativas += 1
                if sucesso and total_gastos + valor_acordo <= orcamento:
                    total_gastos += valor_acordo
                    finalizados[processo] = True  # O processo é encerrado

        gastos_acumulados[mes-1] = total_gastos

    return gastos_acumulados

# Simulação de cenários para 100 simulações mês a mês
def simular_varios_cenarios(num_simulacoes, alcada, num_tentativas_por_mes, orcamento, max_meses):
    resultados = []
    for _ in range(num_simulacoes):
        gastos_acumulados = simular_estrategia(alcada, num_tentativas_por_mes, orcamento, max_meses)
        resultados.append(gastos_acumulados)
    return np.mean(resultados, axis=0)


# Executando simulações
np.random.seed(42)
gastos_com_acordo = simular_varios_cenarios(n_simulacoes, alcada, num_tentativas_por_mes, orcamento, max_meses)
np.random.seed(42)
gastos_sem_acordo = simular_varios_cenarios(n_simulacoes, 0.0, num_tentativas_por_mes, orcamento, max_meses)


# %%

# Gráficos
st.subheader('Gastos acumulados ao longo do tempo')
plt.figure(figsize=(10, 6))
plt.plot(gastos_com_acordo, label='Com Acordo', color='blue')
plt.plot(gastos_sem_acordo, label='Sem Acordo', color='green')
plt.xlabel('Tempo (meses)')
plt.ylabel('Gastos Acumulados')
plt.legend()
st.pyplot(plt)

st.subheader('Lucro: Diferença (Sem Acordo - Com Acordo)')
plt.figure(figsize=(10, 6))
plt.plot(gastos_sem_acordo - gastos_com_acordo, label='Diferença de Gastos', color='blue')
plt.xlabel('Tempo (meses)')
plt.ylabel('Sem Acordo - Com Acordo')
plt.hlines(0, 0, max_meses, color='red', linestyle='--')
plt.legend()
st.pyplot(plt)
