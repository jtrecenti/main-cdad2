from shiny import ui, render, App

from scipy import stats
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

app_ui = ui.page_fluid(
  ui.input_slider("n", "Tamanho da amostra", min=0, max=1000, value=50),
  ui.input_slider("sd", "Desvio padrão na população", min=1, max=10, value=4),
  ui.input_slider("draws", "Quantidade de amostras", min=100, max=5000, value=1000),
  ui.output_plot("hist"),
)

def server(input, output, session):

  @output
  @render.plot
  def hist():
    medias = []
    for i in range(input.draws()):
      amostra = stats.norm.rvs(loc=5, scale=input.sd(), size=input.n())
      medias.append({'amostra': i + 1, 'media': np.mean(amostra)})
    df_medias = pd.DataFrame(medias)
    sns.displot(df_medias, x = 'media', kde=True)
    plt.xlim(2, 8)

app = App(app_ui, server)
