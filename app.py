import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Balanço Energético - Carga", layout="wide")

@st.cache_data(show_spinner=False)
def load_data_from_path(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return _prepare_df(df)

@st.cache_data(show_spinner=False)
def load_data_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    import io
    df = pd.read_csv(io.BytesIO(file_bytes))
    return _prepare_df(df)

def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    # Remove coluna índice extra, se existir
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])

    # Tipos
    df['din_instante'] = pd.to_datetime(df['din_instante'], errors='coerce')
    df['val_carga'] = pd.to_numeric(df['val_carga'], errors='coerce')

    # Limpeza
    df = df.dropna(subset=['din_instante', 'val_carga'])
    df = df.sort_values('din_instante')

    return df

def aggregate(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    # df precisa ter din_instante como datetime
    dfx = df.set_index('din_instante')

    if freq == 'Hora':
        rule = 'h'
    elif freq == 'Dia':
        rule = 'D'
    elif freq == 'Mês':
        rule = 'MS'
    elif freq == 'Ano':
        rule = 'YS'
    else:
        rule = 'h'

    out = (
        dfx
        .groupby(['id_subsistema', 'nom_subsistema'])
        .resample(rule)
        .agg(carga_media=('val_carga', 'mean'), carga_maxima=('val_carga', 'max'))
        .reset_index()
    )
    return out

st.title("📈 Balanço Energético — Carga Média e Carga Máxima")
st.caption("Fonte de dados: arquivo CSV carregado no app. Os gráficos usam a coluna **val_carga**.")

with st.sidebar:
    st.header("Configurações")

    # Fonte do arquivo
    use_uploaded = st.toggle("Carregar CSV (upload)", value=False)
    if use_uploaded:
        up = st.file_uploader("Selecione o CSV", type=['csv'])
        if up is None:
            st.info("Faça upload do arquivo para começar.")
            st.stop()
        df = load_data_from_bytes(up.getvalue())
    else:
        default_path = st.text_input("Caminho do CSV no repositório/servidor", value="balanco_energetico.csv")
        try:
            df = load_data_from_path(default_path)
        except Exception as e:
            st.error(f"Não foi possível ler o arquivo em '{default_path}'. Erro: {e}")
            st.stop()

    # Filtros
    subs = df[['id_subsistema','nom_subsistema']].drop_duplicates().sort_values(['id_subsistema'])
    options = [f"{r.id_subsistema} — {r.nom_subsistema}" for r in subs.itertuples(index=False)]

    default_sel = [o for o in options if o.startswith('SIN')]
    if not default_sel:
        default_sel = options[:1]

    sel = st.multiselect("Subsistema(s)", options=options, default=default_sel)

    agg_level = st.selectbox("Agregação", options=['Hora','Dia','Mês','Ano'], index=0)

    min_dt = df['din_instante'].min().date()
    max_dt = df['din_instante'].max().date()
    start, end = st.date_input("Período", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)

# Aplica filtros
sel_ids = [s.split(' — ')[0].strip() for s in sel]
filtered = df[df['id_subsistema'].isin(sel_ids)].copy()

# Filtro de datas (inclui o dia final inteiro)
start_ts = pd.Timestamp(start)
end_ts = pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
filtered = filtered[(filtered['din_instante'] >= start_ts) & (filtered['din_instante'] <= end_ts)]

if filtered.empty:
    st.warning("Nenhum dado no recorte selecionado.")
    st.stop()

agg = aggregate(filtered, agg_level)

# Renomeia para exibição
agg = agg.rename(columns={'din_instante':'instante'})


st.write("Agregação atual:", agg_level)
st.write("Linhas agregadas:", len(agg))

# Gráfico: Carga média
fig_mean = px.line(
    agg,
    x='instante',
    y='carga_media',
    color='id_subsistema',
    hover_data={'nom_subsistema': True},
    labels={'instante':'Tempo', 'carga_media':'Carga média', 'id_subsistema':'Subsistema'},
    title='Carga média (val_carga)'
)
fig_mean.update_layout(legend_title_text='Subsistema')

# Gráfico: Carga máxima
fig_max = px.line(
    agg,
    x='instante',
    y='carga_maxima',
    color='id_subsistema',
    hover_data={'nom_subsistema': True},
    labels={'instante':'Tempo', 'carga_maxima':'Carga máxima', 'id_subsistema':'Subsistema'},
    title='Carga máxima (val_carga)'
)
fig_max.update_layout(legend_title_text='Subsistema')

# Layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_mean, use_container_width=True,key=f"fig_mean_{agg_level}")
with col2:
    st.plotly_chart(fig_max, use_container_width=True,key=f"fig_max_{agg_level}")

with st.expander("Ver tabela agregada"):
    st.dataframe(agg, use_container_width=True)

st.caption("Dica: use o zoom/seleção no gráfico para explorar períodos.")
