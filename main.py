import pandas as pd
import streamlit as st

st.set_page_config(page_title=None,
                   page_icon=None, layout="wide",
                   )

st.title("Extrator emendas parlamentares (2023-2024)")

@st.cache_data
def load_data():
    emendas_orcamento = pd.read_excel("emendas_orcamento.xlsx")
    emendas_pagamentos = pd.read_excel("emendas_pagamentos.xlsx")
    emendas_transferegov = pd.read_excel("emendas_transferegov.xlsx")

    emendas_orcamento['Número'] = emendas_orcamento['Número'].astype(str)
    emendas_orcamento['Ano emenda'] = emendas_orcamento['Ano emenda'].astype(str)

    emendas_pagamentos['codigo_emenda_formatado'] = (
        emendas_pagamentos['Emenda (Número/Ano)']
        .astype(str)
        .apply(lambda x: f"{x[-4:]}{x[:-5].replace('-', '')}")
    )

    emendas_transferegov['Nº Emenda'] = emendas_transferegov['Nº Emenda'].astype(str)

    return emendas_orcamento, emendas_pagamentos, emendas_transferegov

@st.cache_data
def apply_filters(emendas_orcamento, emendas_pagamentos, emendas_transferegov,
                  numero, tipo_emenda, programa_governo, acao_governo,
                  plano_orcamentario, natureza_detalhada_despesa,
                  elemento_despesa, modalidade_aplicacao, ha_convenio, favorecido_pagamento,
                  favorecido_natureza_subgrupo, natureza_juridica):

    orcamento_filtrado = emendas_orcamento.copy()
    pagamentos_filtrado = emendas_pagamentos.copy()
    transferegov_filtrado = emendas_transferegov.copy()

    if numero:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Número'].astype(str).str.contains(str(numero))]
    if tipo_emenda:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Tipo emenda'] == tipo_emenda]
    if programa_governo:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Programa Governo Nome'] == programa_governo]
    if acao_governo:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Ação Governo Nome'] == acao_governo]
    if plano_orcamentario:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Plano Orç.'] == plano_orcamentario]
    if natureza_detalhada_despesa:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Natureza detalhada despesa'] == natureza_detalhada_despesa]
    if elemento_despesa:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Elemento despesa'] == elemento_despesa]
    if modalidade_aplicacao:
        orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Modalidade aplicação'] == modalidade_aplicacao]

    emendas_filtradas = set(orcamento_filtrado['Número'].astype(str))

    if favorecido_pagamento:
        pagamentos_filtrado = pagamentos_filtrado[
            pagamentos_filtrado['Favorecido do Pagamento - Município/UF'].str.contains(favorecido_pagamento, case=False, na=False)
        ]
    if favorecido_natureza_subgrupo:
        pagamentos_filtrado = pagamentos_filtrado[
            pagamentos_filtrado['Favorecido do Pagamento (Natureza Subgrupo)'] == favorecido_natureza_subgrupo
        ]

    emendas_filtradas_pagamentos = set(pagamentos_filtrado['codigo_emenda_formatado'])
    emendas_filtradas = emendas_filtradas & emendas_filtradas_pagamentos

    if natureza_juridica:
        transferegov_filtrado = transferegov_filtrado[
            transferegov_filtrado['Natureza Jurídica'] == natureza_juridica
        ]

    if ha_convenio == 'Sim':
        # Apenas emendas presentes em emendas_transferegov
        emendas_filtradas_transferegov = set(transferegov_filtrado['Nº Emenda'].astype(str))
        emendas_filtradas = emendas_filtradas & emendas_filtradas_transferegov
    elif ha_convenio == 'Não':

        emendas_com_convenio = set(emendas_transferegov['Nº Emenda'].astype(str))
        emendas_filtradas = emendas_filtradas - emendas_com_convenio

    orcamento_filtrado = orcamento_filtrado[orcamento_filtrado['Número'].astype(str).isin(emendas_filtradas)]
    pagamentos_filtrado = pagamentos_filtrado[pagamentos_filtrado['codigo_emenda_formatado'].isin(emendas_filtradas)]
    transferegov_filtrado = transferegov_filtrado[
        transferegov_filtrado['Nº Emenda'].astype(str).isin(emendas_filtradas)
    ]

    return orcamento_filtrado, pagamentos_filtrado, transferegov_filtrado

emendas_orcamento, emendas_pagamentos, emendas_transferegov = load_data()

col1, col2, col3 = st.columns(3)

with col1:
    numero = st.selectbox("Número emenda", [""] + emendas_orcamento['Número'].unique().tolist())
    tipo_emenda = st.selectbox("Tipo de Emenda", [""] + emendas_orcamento['Tipo emenda'].unique().tolist())
    ha_convenio = st.selectbox("Há Convênio?", [""] + ['Sim', 'Não'])

with col2:
    programa_governo = st.selectbox("Programa Governo",
                                    [""] + emendas_orcamento['Programa Governo Nome'].unique().tolist())
    acao_governo = st.selectbox("Ação Governo", [""] + emendas_orcamento['Ação Governo Nome'].unique().tolist())
    plano_orcamentario = st.selectbox("Plano Orçamentário", [""] + emendas_orcamento['Plano Orç.'].unique().tolist())
    natureza_detalhada_despesa = st.selectbox("Natureza Detalhada Despesa", [""] + emendas_orcamento['Natureza detalhada despesa'].unique().tolist())
    elemento_despesa = st.selectbox("Elemento Despesa", [""] + emendas_orcamento['Elemento despesa'].unique().tolist())
    modalidade_aplicacao = st.selectbox("Modalidade Aplicação", [""] + emendas_orcamento['Modalidade aplicação'].unique().tolist())

with col3:
    natureza_juridica = st.selectbox("Natureza Jurídica do Favorecido - Grupo",
                                     [""] + emendas_transferegov['Natureza Jurídica'].unique().tolist())
    favorecido_natureza_subgrupo = st.selectbox("Natureza Jurídica do Favorecido - Subgrupo",
                                                [""] + emendas_pagamentos[
                                                    'Favorecido do Pagamento (Natureza Subgrupo)'].unique().tolist())
    favorecido_pagamento = st.selectbox("Favorecido - Município/UF", [""] + emendas_pagamentos['Favorecido do Pagamento - Município/UF'].unique().tolist())

filtro_orcamento, filtro_pagamentos, filtro_transferegov = apply_filters(
    emendas_orcamento, emendas_pagamentos, emendas_transferegov,
    numero, tipo_emenda, programa_governo, acao_governo,
    plano_orcamentario, natureza_detalhada_despesa,
    elemento_despesa, modalidade_aplicacao, ha_convenio,
    favorecido_pagamento, favorecido_natureza_subgrupo, natureza_juridica
)

colunas_orcamento = [
    "Número",
    "Ano emenda",
    "Tipo emenda",
    "Programa",
    "Ação",
    "Plano Orç.",
    "Natureza detalhada despesa",
    "Elemento despesa",
    "Modalidade aplicação",
    "Empenhado (R$)",
    "Liquidado (R$)",
    "Pago (R$)",
    "Pagamentos totais (exercício + RAP)"
]

orcamento_visualizado = filtro_orcamento[colunas_orcamento]

st.subheader("Emendas filtradas - info. orçamentárias")
st.dataframe(orcamento_visualizado)
st.warning("Fonte: Siafi/Tesouro Gerencial")

st.subheader("Emendas filtradas - info. pagamentos")
st.dataframe(filtro_pagamentos)
st.warning("Fonte: Siga Brasil")

st.subheader("Emendas filtradas - info. instrumentos repasse")
st.dataframe(filtro_transferegov)
st.warning("Fonte: TransfereGov - Módulo emendas parlamentares")

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Baixar Emendas Orçamentárias Filtradas",
    data=convert_df(filtro_orcamento),
    file_name="emendas_orcamento_filtradas.csv",
    mime="text/csv",
)

st.download_button(
    label="Baixar Pagamentos Filtrados",
    data=convert_df(filtro_pagamentos),
    file_name="emendas_pagamentos_filtrados.csv",
    mime="text/csv",
)

st.download_button(
    label="Baixar Emendas TransfereGov Filtradas",
    data=convert_df(filtro_transferegov),
    file_name="emendas_transferegov_filtradas.csv",
    mime="text/csv",
)
