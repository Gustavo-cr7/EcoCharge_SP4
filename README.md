# EcoCharge

## Sistema Inteligente de Gestão de Energia para Eletropostos (Desafio GoodWe)

Projeto desenvolvido para a sprint 4 das disciplinas de **Pensamento Computacional e Automação com Python** e **Soluções em Energias Renováveis e Sustentáveis**, com o objetivo de demonstrar uma solução integrada, funcional e sustentável de gestão energética para eletropostos utilizando tecnologias compatíveis com a **GoodWe**.

---

## Equipe Envolvida

- **Integrante:** 
 Gustavo Guedes Pereira — RM 569779
 Lucas Angelo — RM 569530
 Gustavo de Souza — RM 570746
 Arthur Tae — RM 570647
 Gabriel Rodrigues — RM 569322
 Murillo Boyadjian - RM 570774

- **Disciplinas:** Pensamento Computacional e Automação com Python / Soluções em Energias Renováveis e Sustentáveis



---

## Objetivo do Projeto e Alinhamento ao Desafio GoodWe

O **EcoCharge** é um sistema de gerenciamento inteligente de energia para eletropostos de veículos elétricos. Ele simula o consumo ao longo do dia (06h às 22h) e decide automaticamente qual fonte energética acionar a cada hora, integrando geração fotovoltaica, armazenamento em bateria e rede elétrica.

### Como a solução utiliza tecnologias compatíveis com a GoodWe:

1. **Inversor Híbrido GoodWe (Série ET):** atua como o núcleo inteligente do sistema, priorizando o abastecimento do eletroposto diretamente com a geração solar fotovoltaica e direcionando o excedente para o banco de baterias.
2. **Bateria de Alta Tensão GoodWe Lynx Home F:** armazena a energia solar excedente gerada entre 10h e 15h para descarregá-la nos momentos em que o consumo supera a geração solar.
3. **Carregador Veicular GoodWe HCA Series + Plataforma GoodWe SEMS:** nos horários de pico (18h às 21h), o sistema aplica uma automação de gerenciamento de demanda (*Peak Shaving*), reduzindo a potência exigida em 20% e registrando automaticamente os relatórios operacionais e ambientais.

---

## Arquitetura Final e Integração dos Sistemas

```text
┌────────────────────────────────────────────────────────┐
│           GERAÇÃO E EQUIPAMENTOS GOODWE                │
├────────────────────────────────────────────────────────┤
│ • Painéis Fotovoltaicos (Geração Solar 06h às 22h)     │
│ • Inversor Híbrido GoodWe ET Series                    │
│ • Bateria GoodWe Lynx Home F                           │
│ • Carregador Veicular GoodWe HCA Series                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│        VALIDAÇÃO E SERVIDOR LOCAL PYTHON               │
├────────────────────────────────────────────────────────┤
│ • HTTPServer / BaseHTTPRequestHandler (localhost:8000) │
│ • Tratamento de Erros (try/except) nos parâmetros      │
│ • Dicionário (equipamentos GoodWe) e Tupla (tarifas)   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│       GESTÃO INTELIGENTE DE ENERGIA (LÓGICA SEMS)      │
├────────────────────────────────────────────────────────┤
│ 1. Verifica a demanda por horário                      │
│ 2. Horário de pico (18h às 21h):                       │
│    └─> Redução automática de demanda em 20%            │
│ 3. Prioridade energética:                              │
│    SOLAR ──> BATERIA GOODWE ──> REDE ELÉTRICA          │
│ 4. Excedente solar armazenado na Bateria GoodWe        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│     PROCESSAMENTO, SUSTENTABILIDADE E VISUALIZAÇÃO     │
├────────────────────────────────────────────────────────┤
│ • Pandas DataFrame (Tabela horária detalhada)          │
│ • Cálculo de CO₂ evitado (kg) e Economia (R$)          │
│ • Exportação automática de arquivo (.txt)              │
│ • Gráfico Matplotlib integrado à Interface Web         │
└────────────────────────────────────────────────────────┘
```

---

## Resultados Quantitativos e Qualitativos Obtidos

Considerando o cenário padrão de simulação (**Nível Inicial da Bateria: 50 kWh** e **Capacidade da Bateria GoodWe: 100 kWh**), o sistema obteve os seguintes resultados em um ciclo diário (06h às 22h):

| Indicador | Resultado Obtido | Impacto / Benefício |
| :--- | :--- | :--- |
| **Consumo Original Total** | 1.150 kWh | Demanda bruta do eletroposto sem automação |
| **Demanda Reduzida no Pico (18h–21h)** | **82 kWh** | Alívio de 20% na sobrecarga do horário de ponta |
| **Energia Solar Utilizada Diretamente** | **605 kWh** | Aproveitamento direto pelos inversores GoodWe |
| **Energia Suprida pela Bateria GoodWe** | **150 kWh** | Uso da reserva acumulada com o excedente solar |
| **Energia Complementar da Rede** | **313 kWh** | Acionada apenas quando solar e bateria se esgotam |
| **Índice de Energia Renovável** | **70,7%** | Mais de dois terços da operação com energia limpa |
| **Pegada de Carbono Evitada** | **71,15 kg de CO₂** | Redução diária de emissões (base: 0,085 kg CO₂/kWh) |
| **Economia Financeira Estimada** | **R$ 671,65 / dia** | Economia combinando geração solar e descarga no pico |

### Avaliação Crítica de Sustentabilidade e Inovação
- **Viabilidade Técnica e Eficiência:** A combinação do corte de 20% na demanda de pico com a descarga da bateria GoodWe às 18h elimina completamente o uso da rede elétrica na primeira hora do horário de ponta e reduz drasticamente o custo nas horas seguintes.
- **Relevância Ambiental e Social:** Em um mês de operação (30 dias), um único eletroposto gerenciado pelo EcoCharge evita a emissão de aproximadamente **2,13 toneladas de CO₂** e gera uma economia superior a **R$ 20.000,00**, tornando a mobilidade elétrica realmente limpa e economicamente sustentável.

---

## Como Executar o Projeto

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute a aplicação:
   ```bash
   python app.py
   ```
3. Acesse no navegador:
   ```text
   http://localhost:8000
   ```
4. A cada simulação, o arquivo `relatorio_goodwe_sems.txt` é atualizado automaticamente na pasta do projeto.

---

## Vídeo Técnico de Apresentação

- **Link do vídeo:**https://youtu.be/Xyrr7oh2sd0
