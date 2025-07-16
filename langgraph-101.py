from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from dotenv import load_dotenv
import streamlit as st
from openai import RateLimitError
import sys
import random

# Configuração da página
st.set_page_config(page_title="Dr.Inhamuns - Oncologia e Relatórios Inteligentes", page_icon="🧠")

# Configuração do tema
st.markdown("""
    <style>
        :root {
            /* Base colors */
            --primary: #2563eb;       /* Blue-600 */
            --primary-hover: #1d4ed8;  /* Blue-700 */
            --bg-color: #ffffff;
            --text-color: #1f2937;
            --border-color: #e5e7eb;
            --sidebar-bg: #f9fafb;
            --card-bg: #ffffff;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #3b82f6;
        }
        
        /* Dark mode */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #111827;
                --text-color: #f9fafb;
                --sidebar-bg: #1f2937;
                --card-bg: #1f2937;
                --border-color: #374151;
            }
            
            .stTextArea > div > div > textarea {
                background-color: #1f2937 !important;
                color: #f9fafb !important;
                border-color: #374151 !important;
            }
        }
        
        /* Base styles */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Text area */
        .stTextArea > div > div > textarea {
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.75rem;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
        
        .stTextArea > div > div > textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }
        
        /* Navigation buttons */
        .stButton > button[title*="Sobre"],
        .stButton > button[title*="Aviso Legal"] {
            background-color: transparent;
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
            margin: 0.25rem 0;
            width: 100%;
            text-align: left;
        }
        
        /* Example query buttons */
        .stButton > button:not([title*="Sobre"]):not([title*="Aviso Legal"]) {
            background-color: rgba(37, 99, 235, 0.05);
            color: var(--primary);
            border: 1px solid rgba(37, 99, 235, 0.2);
            padding: 0.6rem 1rem;
            border-radius: 6px;
            font-weight: 500;
            transition: all 0.2s ease;
            margin: 0.35rem 0;
            width: 100%;
            text-align: left;
        }
        
        /* Button hover states */
        .stButton > button[title*="Sobre"]:hover,
        .stButton > button[title*="Aviso Legal"]:hover {
            background-color: rgba(0, 0, 0, 0.03);
            border-color: var(--primary);
        }
        
        .stButton > button:not([title*="Sobre"]):not([title*="Aviso Legal"]):hover {
            background-color: rgba(37, 99, 235, 0.1);
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        /* Main send button */
        div[data-testid="stHorizontalBlock"] > div > button {
            background-color: var(--primary) !important;
            color: white !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 0.5rem 1.25rem !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease !important;
            margin: 0.5rem 0 !important;
            width: auto !important;
            min-width: 100px !important;
        }
        
        div[data-testid="stHorizontalBlock"] > div > button:hover {
            background-color: var(--primary-hover) !important;
            transform: none !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }
        
        /* Tooltips */
        [data-testid="stTooltipContent"] {
            background-color: var(--card-bg) !important;
            color: var(--text-color) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 0.85rem !important;
            opacity: 1 !important;
            visibility: visible !important;
        }
        
        /* Status messages */
        .stAlert {
            border-radius: 6px !important;
            padding: 1rem !important;
        }
        
        /* Cards and containers */
        .st-bd, .st-bc, .st-bb, .st-ba {
            border-color: var(--border-color) !important;
        }
        
        /* Links */
        a {
            color: var(--primary) !important;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .stButton > button {
                padding: 0.5rem 0.75rem !important;
                font-size: 0.85rem !important;
            }
        }
        
        .stAlert {
            border-radius: 4px;
        }
        
        .stAlert > div {
            color: var(--primary-text);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--primary-accent);
        }
        
        .stSpinner > div > div {
            border-color: var(--primary-accent) transparent transparent transparent;
        }
    </style>
""", unsafe_allow_html=True)

# Carrega as variáveis do .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Define o modelo
try:
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=API_KEY
    )
    model_loaded = True
except Exception as e:
    st.error("⚠️ Erro ao carregar o modelo. Verifique sua chave da API.")
    st.stop()

# Ferramenta de busca web
@tool
def search_web(query: str = "") -> str:
    """Searches the web using Tavily and returns results for the given query."""
    try:
        tavily_tool = TavilySearchResults()
        return tavily_tool.invoke({"query": query})
    except Exception as e:
        print(f"Erro na busca web: {e}", file=sys.stderr)
        return "Não foi possível realizar a busca no momento."

# Template de prompt
system_prompt = """
Você é o Dr. Inhamuns, um assistente especializado em oncologia e relatórios médicos. Sua missão é fornecer informações precisas e baseadas em evidências para auxiliar profissionais de saúde, sem substituir o julgamento clínico.

DIRETRIZES PRINCIPAIS:
1. Forneça informações baseadas em diretrizes clínicas atualizadas (SBOC, NCCN, ESMO, ASCO, Ministério da Saúde)
2. Seja claro, objetivo e use linguagem técnica apropriada
3. Em caso de incerteza, responda: "Não sei com segurança e não posso afirmar."
4. Inclua referências a diretrizes e estudos quando relevante
5. Mantenha um tom profissional e empático

FONTES DE CONSULTA PREFERENCIAIS:
- Diretrizes SBOC, NCCN, ESMO, ASCO
- Periódicos: NEJM, JCO, The Lancet Oncology, JAMA Oncology
- Bases: UpToDate, Micromedex, PubMed
- Legislação e protocolos do Ministério da Saúde/ANVISA

Ao responder, siga esta estrutura:
1. Resposta objetiva e direta
2. Base científica/regulatória
3. Contexto adicional (quando aplicável)
4. Sugestão de próximos passos (quando relevante)

Bases de Dados Farmacológicas e Regulatórias
1. UpToDate, Micromedex, DrugBank, PubMed
2. Bulas e registros da ANVISA
3. Interações medicamentosas, toxicidades e farmacocinética

Economia da Saúde e Acesso
1. CONITEC, NICE (UK), CADTH (Canadá)
2. ISPOR Princípios de farmacoeconomia para saúde suplementar

Capacidades Técnicas Adicionais
1. Geração de relatórios com estrutura padronizada e adaptável a modelos exigidos pelas operadoras de saúde.
2. Inserção, quando aplicável, de indicadores de custo-efetividade e alternativas terapêuticas.
3. Respeito ao formato aceito por sistemas de auditoria, operadoras, convênios e instâncias regulatórias.

Diretrizes de Atualização e Busca
1. Monitoramento e ingestão ativa de publicações nos próximos 5 anos nas seguintes bases:
2. PubMed, SciELO, ClinicalTrials.gov, base da CONITEC, Google Scholar (filtrado), entre outras.
3. Zero tolerância à especulação clínica.
4. Quando em dúvida sobre validade de estudo ou indicação, o GPT consulta ou orienta o usuário a consultar diretamente a fonte referencial.

Exemplo de Resposta do Dr. Inhamuns (Postura Clínica Segura)
Baseando-me nas diretrizes da NCCN 2024 e nos dados do estudo publicado em The Lancet Oncology (ID: 10.1016/S1470-2045(23)...), o uso de Pembrolizumabe como terapia adjuvante em carcinoma de pulmão estágio IIIA é considerado apropriado. Caso deseje, posso incluir dados de custo-efetividade para justificar junto à operadora de saúde.

| Pilar                 | Descrição                                                           |
| --------------------- | ------------------------------------------------------------------- |
|     Alvo              | Médicos oncologistas, clínicas, operadoras de saúde                 |
|   Foco                | Relatórios, justificativas e pareceres com base em evidências       |
|   Diferencial         | Linguagem técnica, humanizada e adaptada ao cenário brasileiro      |
|   Região de impacto   | Prioriza cenários de baixa oferta médica, como os Inhamuns          |
|   Valor central       | Suporte sem substituir. Clareza sem simplismo. Ciência com empatia. |

"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

# Pipeline de execução
chain: Runnable = prompt | model | StrOutputParser()

# Interface Streamlit
st.title("🧠 Dr. Inhamuns – Oncologia e Relatórios")
st.write("Assistente especializado em oncologia baseado em evidências científicas")

# Exemplos de consultas rápidas
examples = [
    "Gerar um parecer técnico para operadora de saúde",
    "Padronizar laudo para auditoria médica",
    "Sintomas Comuns em Câncer de Próstata Metastático",
    "Sintomas Comuns em Câncer de Mama"
]

def set_example(example):
    st.session_state.user_input = example

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Sobre")
    st.markdown("""
    **Missão**: Democratizar o acesso à inteligência clínica de ponta em oncologia, fortalecendo a tomada de decisão médica com precisão e empatia.
    """)
    
    st.markdown("### 💡 Exemplos de Consultas")
    for example in examples:
        st.button(example, on_click=set_example, args=(example,), use_container_width=True, key=f"btn_{example}")
    
    st.markdown("---")
    st.markdown("""
    **Aviso Legal**: Este assistente não substitui o julgamento clínico. Consulte sempre as fontes primárias e um médico especialista.
    """)

# Inicializa a variável de sessão se não existir
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Área de texto principal
user_input = st.text_area(
    "Descreva sua dúvida ou caso clínico:",
    value=st.session_state.user_input,
    height=150,
    help="Digite sua pergunta ou selecione um exemplo ao lado"
)

if st.button("Enviar Consulta", use_container_width=False) and user_input:
    try:
        with st.spinner("Analisando sua consulta..."):
            resposta = chain.invoke({"input": user_input})
            
        st.subheader("Resposta do Dr. Inhamuns:")
        st.markdown(resposta)
        
        # Opcional: Adicionar busca web para informações adicionais
        if any(termo in user_input.lower() for termo in ["atualização", "estudo", "pesquisa"]):
            with st.spinner("Consultando fontes atualizadas..."):
                web_result = search_web(f"{user_input} site:nccn.org OR site:esmo.org OR site:asco.org OR site:pubmed.ncbi.nlm.nih.gov")
            if web_result and len(web_result) > 0:
                st.subheader("Fontes Adicionais:")
                st.write(web_result)
    
    except RateLimitError:
        st.error("⚠️ **Limite de requisições excedido**")
        st.warning("""
        Parece que você atingiu o limite de requisições disponíveis em sua conta.
        
        **O que fazer agora?**
        - Verifique o saldo da sua conta OpenAI
        - Atualize seu plano ou adicione mais créditos
        - Entre em contato com o suporte se precisar de ajuda
        """)
    
    except Exception as e:
        st.error("❌ Ocorreu um erro inesperado")
        st.warning("Por favor, tente novamente mais tarde ou entre em contato com o suporte.")
        print(f"Erro inesperado: {e}", file=sys.stderr)