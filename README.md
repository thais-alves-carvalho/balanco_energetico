# Plataforma online (Streamlit) — Balanço Energético

Este projeto cria um app web **online e compartilhável** para visualizar o arquivo `balanco_energetico.csv`.

## O que o app faz
- Lê o CSV do repositório (padrão) **ou** permite upload.
- Permite selecionar **subsistema(s)**.
- Permite trocar a granularidade para **Hora / Dia / Mês / Ano**.
- Mostra dois gráficos dinâmicos (baseados em `val_carga`):
  - **Carga média** (média do período)
  - **Carga máxima** (máximo do período)

## Como rodar localmente
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Como colocar online e compartilhar (Streamlit Community Cloud)
1. Crie um repositório no GitHub com estes arquivos:
   - `app.py`
   - `requirements.txt`
   - `balanco_energetico.csv` (ou hospede o dado e use upload)
2. Acesse https://streamlit.io/cloud e conecte ao seu GitHub.
3. Selecione o repositório e defina o arquivo principal como `app.py`.
4. Clique em **Deploy**.
5. Você receberá um link público do tipo `https://<app>.streamlit.app/` para compartilhar.

## Observações
- Se o CSV ficar grande, recomenda-se não versionar o arquivo no GitHub e usar **upload** ou uma fonte de dados (Blob/SharePoint) com autenticação.
