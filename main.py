import pandas as pd
import streamlit as st

# Carregar os dados
@st.cache_data
def load_data():
    url_orcamento = 'emendas_orcamento.xlsx'
    url_pagamentos = 'emendas_pagamentos.xlsx'
    emendas_orcamento = pd.read_excel(url_orcamento)
    emendas_pagamentos = pd.read_excel(url_pagamentos)

    # Ajustar o formato do número da emenda em emendas_orcamento
    emendas_orcamento['codigo_emenda_formatado'] = (
        emendas_orcamento['Autor Emendas Orçamento Código']
        .astype(str)
        .apply(lambda x: f"{x[4:]}-{x[:4]}")
    )

    return emendas_orcamento, emendas_pagamentos

# Carregar as planilhas
emendas_orcamento, emendas_pagamentos = load_data()

# Título do app
st.title("Filtrar Emendas Orçamentárias e Pagamentos")

# Mostrar os tipos de emenda disponíveis
tipo_emendas = emendas_orcamento['Autor Emendas Orçamento Código'].unique()
tipo_selecionado = st.selectbox("Selecione a Emenda", tipo_emendas)

# Filtrar os dados
emendas_filtradas = emendas_orcamento[emendas_orcamento['Autor Emendas Orçamento Código'] == tipo_selecionado]
pagamentos_filtrados = emendas_pagamentos[
    emendas_pagamentos['Emenda (Número/Ano)'].isin(emendas_filtradas['codigo_emenda_formatado'])
]

# Exibir os resultados
st.subheader("Planilha de Emendas Orçamentárias Filtradas")
st.dataframe(emendas_filtradas)

st.subheader("Planilha de Pagamentos Filtrados")
st.dataframe(pagamentos_filtrados)

# Opção para baixar os resultados
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_orcamento = convert_df(emendas_filtradas)
csv_pagamentos = convert_df(pagamentos_filtrados)

st.download_button(
    label="Baixar Emendas Orçamentárias Filtradas",
    data=csv_orcamento,
    file_name="emendas_orcamento_filtradas.csv",
    mime="text/csv",
)

st.download_button(
    label="Baixar Pagamentos Filtrados",
    data=csv_pagamentos,
    file_name="emendas_pagamentos_filtrados.csv",
    mime="text/csv",
)
