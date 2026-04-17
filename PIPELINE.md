# Pipeline de Processamento e Geração de Cartas de Controle

## Estrutura do Fluxo

### 1️⃣ **Etapa 1: Data Processor** (`amostras/data_processor.py`)
- **Entrada**: Dados brutos em `amostras/banco_de_dados_amostras/dados_producao_total.json` (usado nos testes)
- **Processamento**:
  - Lê dados brutos
  - Processa cada tipo de chart (XR, P, U, IMR)
  - Calcula estatísticas
  - Gera dados tratados e normalizados
- **Saída**: Pasta `banco_de_dados_tratados/` com arquivos JSON processados
  - `dados_tratados_XR_0.json` - Dados da Carta XR
  - `dados_tratados_P_1.json` - Dados da Carta P
  - `dados_tratados_U_2.json` - Dados da Carta U
  - `dados_tratados_IMR_0.json` - Dados da Carta IMR (quando presente)
  - `indice_dados.json` - Índice com todos os dados

### 2️⃣ **Etapa 2: Cartas** (`cartas_controle/Cartas.py`)
- **Entrada**: Dados tratados em `banco_de_dados_tratados/indice_dados.json`
- **Processamento**:
  - `carta_xr()` - Gera Carta de Controle X-Bar e R
  - `carta_p()` - Gera Carta P (Proporção de Defeituosos)
  - `carta_u()` - Gera Carta U (Defeitos por Unidade)
  - `carta_imr()` - Gera Carta IMR (Individuais e Moving Range)
  - `gerar_todos_relatorios()` - Gera todos os PDFs
- **Saída**: Pasta `relatorios/` com PDFs
  - `relatorio_XR.pdf` - Gráfico duplo (X e R) + estatísticas
  - `relatorio_P.pdf` - Gráfico P + estatísticas
  - `relatorio_U.pdf` - Gráfico U + estatísticas
  - `relatorio_IMR.pdf` - Gráfico duplo (I e MR) + estatísticas

Nota: quando não houver dados tratados para `P` ou `U`, o sistema gera um PDF placeholder (`relatorio_P.pdf` / `relatorio_U.pdf`) contendo uma mensagem informativa; isso garante que as rotas sempre retornem um PDF mesmo sem entradas específicas.

### 3️⃣ **Etapa 3: Orquestração** (`cartas_controle/main.py`)
Classes e métodos principais:

```python
class Main:
    @staticmethod
    def processar_dados(arquivo)  # Executa apenas o Data Processor
    
    @staticmethod
    def gerar_relatorios()        # Executa apenas geração de PDFs
    
    @staticmethod
    def executar_completo()       # Pipeline completo
    
    @staticmethod
    def x()                       # Atalho para XR
    @staticmethod
    def p()                       # Atalho para P
    @staticmethod
    def u()                       # Atalho para U
```

---

## Como Usar

### Via Script Python
```bash
# Executar pipeline completo
python test_pipeline.py

# Ou importar e usar
from cartas_controle.main import Main
# Use o arquivo de exemplo gerado no repositório
Main.executar_completo('dados_producao_total.json')
```

### Via API Flask
```bash
# Iniciar servidor
python main.py

# Endpoints disponíveis:
GET /                      # Status e endpoints
GET /processar             # Processa dados + gera PDFs
GET /relatorio/xr          # Download PDF XR
GET /relatorio/p           # Gera (se necessário) e retorna PDF P (placeholder se não houver dados)
GET /relatorio/u           # Gera (se necessário) e retorna PDF U (placeholder se não houver dados)
GET /relatorio/imr         # Download PDF IMR
```

---

## Estrutura de Pastas (resumo)

```
backend_tpe_e/
├── amostras/
│   ├── data_processor.py
│   ├── banco_de_dados_amostras/
│   │   └── dados_producao_total.json    ← Dados brutos (exemplo)
│   └── __init__.py
│
├── cartas_controle/
│   ├── Cartas.py
│   ├── main.py
│   └── __init__.py
│
├── banco_de_dados_tratados/       ← Dados processados (criado)
│   ├── dados_tratados_XR_0.json
│   ├── dados_tratados_P_1.json
│   ├── dados_tratados_U_2.json
│   ├── dados_tratados_IMR_0.json
│   └── indice_dados.json
│
├── relatorios/                    ← PDFs gerados (criado)
│   ├── relatorio_XR.pdf
│   ├── relatorio_P.pdf
│   ├── relatorio_U.pdf
│   └── relatorio_IMR.pdf
│
├── main.py
├── test_pipeline.py
└── requirements.txt
```

---

## Tipos de Carta Suportados

### 1. **XR - Médias e Amplitudes**
- Usa quando há amostras com múltiplas medições
- Gera 2 gráficos: X-Bar (médias) e R (amplitudes)
- Calcula limites de controle para cada

### 2. **P - Proporção de Defeituosos**
- Usa quando há contagem de peças defeituosas por lote
- Formato aceito (exemplo preparado em `dados_producao_total.json`): cada amostra tem sua contagem

```json
{
  "Chart": "P",
  "n_amostra": 100,
  "measurements": {
    "1": [2],
    "2": [1],
    "3": [3]
  }
}
```

### 3. **U - Defeitos por Unidade**
- Usa quando há contagem de defeitos por unidade. Cada amostra contém a contagem de defeitos observada.

```json
{
  "Chart": "U",
  "n_amostra": 1,
  "measurements": {
    "1": [5],
    "2": [6],
    "3": [4]
  }
}
```

### 4. **IMR - Individuais e Moving Range**
- Usa para observações individuais (n=1)

```json
{
  "Chart": "IMR",
  "measurements": {
    "1": [100.5, 102.3, 101.8, 103.1]
  }
}
```

---

## Formato de Dados Tratados

Cada tipo gera um JSON com cálculos já prontos (exemplo simplificado):

```json
{
  "chart": "XR",
  "x_double_bar": 540.1234,
  "r_bar": 8.5432,
  "sigma": 2.1234,
  "lsc_x": 546.6234,
  "lic_x": 533.6234,
  "lsc_r": 25.4321,
  "lic_r": 0.0,
  "n_amostra": 10,
  "estatisticas_por_amostra": [ ... ]
}
```

---

## Requisitos

```
numpy
scipy
matplotlib
fpdf
flask
```

---

## Exemplo de Uso Completo

```python
from cartas_controle.main import Main

# Pipeline completo (arquivo de teste)
Main.executar_completo('dados_producao_total.json')

# Ou passo a passo
Main.processar_dados('dados_producao_total.json')
Main.gerar_relatorios()

# Gerar apenas XR
Main.x()
```

---

## Tratamento de Erros

- ✓ Valida se JSON existe e é válido
- ✓ Verifica tipos de chart suportados
- ✓ Trata dados nulos/vazios
- ✓ Cria pastas automaticamente se não existirem
- ✓ Retorna mensagens claras de erro
