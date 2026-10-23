from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import base64
from io import BytesIO


horarios = list(range(6, 23))

consumo_eletroposto = [
    20, 25, 30, 35, 45, 55, 60, 70, 75,
    80, 85, 90, 100, 110, 105, 95, 70
]

geracao_solar = [
    0, 5, 15, 30, 50, 70, 85, 95, 100,
    90, 75, 55, 30, 10, 0, 0, 0
]

sistema_goodwe = {
    "inversor": "GoodWe ET Series (Híbrido)",
    "bateria": "GoodWe Lynx Home F",
    "monitoramento": "GoodWe SEMS Portal",
    "carregador_ev": "GoodWe HCA Series (EV Charger)",
    "fator_co2_kg_kwh": 0.085
}

tarifas_energia = (0.65, 1.20)


def validar_parametros(bateria_str, capacidade_str):

    alerta_erro = ""

    try:
        bateria_inicial = float(bateria_str)
        capacidade_bateria = float(capacidade_str)

        if capacidade_bateria <= 0 or bateria_inicial < 0:
            raise ValueError("Valores menores ou iguais a zero.")

        if bateria_inicial > capacidade_bateria:
            bateria_inicial = capacidade_bateria
            alerta_erro = (
                "Aviso: O nível inicial era maior que a capacidade. "
                "Ajustado automaticamente para a capacidade máxima."
            )

    except ValueError:
        bateria_inicial = 50.0
        capacidade_bateria = 100.0
        alerta_erro = (
            "Aviso: Valor inválido digitado. "
            "Foram aplicados os valores padrão (50 kWh e 100 kWh)."
        )

    return bateria_inicial, capacidade_bateria, alerta_erro


def simular(bateria_inicial, capacidade_bateria):

    bateria = bateria_inicial

    energia_rede = []
    energia_solar_usada = []
    energia_bateria_usada = []
    energia_reduzida = []
    consumo_efetivo = []
    acoes_sistema = []
    nivel_bateria = []

    for i in range(len(horarios)):

        horario = horarios[i]
        consumo = consumo_eletroposto[i]
        solar = geracao_solar[i]

        solar_usada = 0
        bateria_usada = 0
        rede = 0
        reducao = 0

        demanda = consumo

        if 18 <= horario <= 21:
            reducao = consumo * 0.20
            demanda = consumo - reducao

        if solar >= demanda:

            solar_usada = demanda
            excedente = solar - demanda

            bateria = min(
                capacidade_bateria,
                bateria + excedente
            )

            acao = (
                "Usar energia solar e armazenar "
                "o excedente na bateria GoodWe"
            )

        else:

            solar_usada = solar
            restante = demanda - solar

            if bateria >= restante:

                bateria_usada = restante
                bateria -= restante

                acao = (
                    "Usar energia solar + bateria GoodWe"
                )

            else:

                bateria_usada = bateria
                restante -= bateria
                bateria = 0

                rede = restante

                if 18 <= horario <= 21:

                    acao = (
                        "Horário de pico: demanda reduzida "
                        "em 20% e energia complementar "
                        "fornecida pela rede"
                    )

                else:

                    acao = (
                        "Usar energia solar + bateria "
                        "+ rede elétrica"
                    )

        energia_solar_usada.append(solar_usada)
        energia_bateria_usada.append(bateria_usada)
        energia_rede.append(rede)
        energia_reduzida.append(reducao)
        consumo_efetivo.append(demanda)
        acoes_sistema.append(acao)
        nivel_bateria.append(bateria)

    return (
        energia_rede,
        energia_solar_usada,
        energia_bateria_usada,
        energia_reduzida,
        consumo_efetivo,
        acoes_sistema,
        nivel_bateria
    )


def calcular_impacto_sustentavel(
    energia_solar_usada,
    energia_bateria_usada,
    energia_rede,
    energia_reduzida
):

    total_solar = sum(energia_solar_usada)
    total_bateria = sum(energia_bateria_usada)
    total_rede = sum(energia_rede)
    total_reduzido = sum(energia_reduzida)

    energia_limpa = total_solar + total_bateria
    consumo_total_atendido = energia_limpa + total_rede

    if consumo_total_atendido > 0:
        percentual_renovavel = (energia_limpa / consumo_total_atendido) * 100
    else:
        percentual_renovavel = 0

    co2_evitado = (energia_limpa + total_reduzido) * sistema_goodwe["fator_co2_kg_kwh"]

    economia_solar = total_solar * tarifas_energia[0]
    economia_bateria_e_pico = (total_bateria + total_reduzido) * tarifas_energia[1]
    economia_total = economia_solar + economia_bateria_e_pico

    resumo = {
        "total_solar": round(total_solar, 2),
        "total_bateria": round(total_bateria, 2),
        "total_rede": round(total_rede, 2),
        "total_reduzido": round(total_reduzido, 2),
        "energia_limpa": round(energia_limpa, 2),
        "percentual_renovavel": round(percentual_renovavel, 1),
        "co2_evitado_kg": round(co2_evitado, 2),
        "economia_reais": round(economia_total, 2)
    }

    return resumo


def salvar_relatorio_txt(resumo, bateria_inicial, capacidade_bateria):

    nome_arquivo = "relatorio_goodwe_sems.txt"

    try:
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("RELATÓRIO DE MONITORAMENTO - ECOCHARGE GOODWE\n\n")
            arquivo.write(f"Inversor Utilizado: {sistema_goodwe['inversor']}\n")
            arquivo.write(f"Sistema de Bateria: {sistema_goodwe['bateria']}\n")
            arquivo.write(f"Carregador Veicular: {sistema_goodwe['carregador_ev']}\n")
            arquivo.write(f"Plataforma: {sistema_goodwe['monitoramento']}\n\n")
            arquivo.write("PARÂMETROS DA SIMULAÇÃO\n")
            arquivo.write(f"Nível Inicial da Bateria: {bateria_inicial} kWh\n")
            arquivo.write(f"Capacidade Total da Bateria: {capacidade_bateria} kWh\n\n")
            arquivo.write("RESULTADOS QUANTITATIVOS E SUSTENTABILIDADE\n")
            arquivo.write(f"Energia Solar Utilizada: {resumo['total_solar']} kWh\n")
            arquivo.write(f"Energia da Bateria Utilizada: {resumo['total_bateria']} kWh\n")
            arquivo.write(f"Energia da Rede Elétrica: {resumo['total_rede']} kWh\n")
            arquivo.write(f"Demanda Reduzida no Pico (18h-21h): {resumo['total_reduzido']} kWh\n")
            arquivo.write(f"Índice de Energia Renovável: {resumo['percentual_renovavel']}%\n")
            arquivo.write(f"Emissão de CO2 Evitada: {resumo['co2_evitado_kg']} kg\n")
            arquivo.write(f"Economia Financeira Estimada: R$ {resumo['economia_reais']}\n")

        return f"Relatório salvo com sucesso em '{nome_arquivo}'."

    except IOError:
        return "Erro ao tentar salvar o arquivo de relatório."


def criar_dataframe(
    energia_rede,
    energia_solar_usada,
    energia_bateria_usada,
    energia_reduzida,
    consumo_efetivo,
    acoes_sistema,
    nivel_bateria
):

    dados = pd.DataFrame({
        "Horário (h)": [f"{h}:00" for h in horarios],
        "Consumo Original (kWh)": consumo_eletroposto,
        "Geração Solar (kWh)": geracao_solar,
        "Demanda Reduzida (kWh)": energia_reduzida,
        "Consumo Efetivo (kWh)": consumo_efetivo,
        "Solar Usada (kWh)": energia_solar_usada,
        "Bateria Usada (kWh)": energia_bateria_usada,
        "Rede Usada (kWh)": energia_rede,
        "Nível Bateria (kWh)": nivel_bateria,
        "Ação do Sistema GoodWe": acoes_sistema
    })

    return dados


def gerar_grafico(
    energia_solar_usada,
    energia_bateria_usada,
    energia_rede,
    nivel_bateria
):

    plt.figure(figsize=(10, 5))

    plt.plot(horarios, consumo_eletroposto, label="Consumo Original", linestyle="--", color="#555555")
    plt.plot(horarios, energia_solar_usada, label="Energia Solar Usada", marker="o", color="#f39c12")
    plt.plot(horarios, energia_bateria_usada, label="Bateria GoodWe Usada", marker="s", color="#27ae60")
    plt.plot(horarios, energia_rede, label="Rede Elétrica", marker="^", color="#c0392b")
    plt.plot(horarios, nivel_bateria, label="Nível da Bateria", linestyle=":", color="#2980b9")

    plt.title("Desempenho Energético do Eletroposto - EcoCharge & GoodWe")
    plt.xlabel("Horário do Dia (h)")
    plt.ylabel("Energia (kWh)")
    plt.xticks(horarios)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)

    imagem_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    return imagem_base64


class EcoChargeHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        url_analisada = urlparse(self.path)

        if url_analisada.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        parametros = parse_qs(url_analisada.query)

        bateria_str = parametros.get("bateria_inicial", ["50"])[0]
        capacidade_str = parametros.get("capacidade_bateria", ["100"])[0]

        bateria_inicial, capacidade_bateria, alerta_erro = validar_parametros(
            bateria_str,
            capacidade_str
        )

        (
            energia_rede,
            energia_solar_usada,
            energia_bateria_usada,
            energia_reduzida,
            consumo_efetivo,
            acoes_sistema,
            nivel_bateria
        ) = simular(bateria_inicial, capacidade_bateria)

        resumo = calcular_impacto_sustentavel(
            energia_solar_usada,
            energia_bateria_usada,
            energia_rede,
            energia_reduzida
        )

        status_arquivo = salvar_relatorio_txt(
            resumo,
            bateria_inicial,
            capacidade_bateria
        )

        df = criar_dataframe(
            energia_rede,
            energia_solar_usada,
            energia_bateria_usada,
            energia_reduzida,
            consumo_efetivo,
            acoes_sistema,
            nivel_bateria
        )

        tabela_html = df.to_html(index=False, classes="tabela-dados")

        grafico_base64 = gerar_grafico(
            energia_solar_usada,
            energia_bateria_usada,
            energia_rede,
            nivel_bateria
        )

        bloco_alerta = ""
        if alerta_erro != "":
            bloco_alerta = f"<div class='alerta'>{alerta_erro}</div>"

        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <title>EcoCharge - Gestão Inteligente GoodWe</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f7f6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    max-width: 1100px;
                    margin: auto;
                    background: #fff;
                    padding: 25px;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #1e8449;
                }}
                .goodwe-box {{
                    background-color: #eafaf1;
                    border-left: 5px solid #27ae60;
                    padding: 12px 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                .alerta {{
                    background-color: #fcf3cf;
                    border-left: 5px solid #f1c40f;
                    padding: 10px;
                    margin-bottom: 15px;
                }}
                .formulario {{
                    background: #f8f9f9;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }}
                .formulario input {{
                    padding: 6px;
                    margin-right: 15px;
                    width: 100px;
                }}
                .formulario button {{
                    padding: 7px 15px;
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }}
                .cards {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    margin-bottom: 20px;
                }}
                .card {{
                    flex: 1 1 200px;
                    background: #f8f9f9;
                    border: 1px solid #dce1e0;
                    border-radius: 6px;
                    padding: 12px;
                    text-align: center;
                }}
                .card h3 {{
                    margin: 0 0 8px 0;
                    font-size: 14px;
                    color: #555;
                }}
                .card p {{
                    margin: 0;
                    font-size: 20px;
                    font-weight: bold;
                    color: #1e8449;
                }}
                .grafico {{
                    text-align: center;
                    margin: 25px 0;
                }}
                .grafico img {{
                    max-width: 100%;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                }}
                .tabela-dados {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 13px;
                }}
                .tabela-dados th, .tabela-dados td {{
                    border: 1px solid #ccc;
                    padding: 8px;
                    text-align: center;
                }}
                .tabela-dados th {{
                    background-color: #27ae60;
                    color: white;
                }}
                .tabela-dados tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .rodape-log {{
                    margin-top: 15px;
                    font-size: 13px;
                    color: #555;
                    background: #eef2f1;
                    padding: 10px;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>EcoCharge – Sistema Inteligente de Gestão de Energia para Eletropostos</h1>

                <div class="goodwe-box">
                    <strong>Integração Tecnológica GoodWe:</strong><br>
                    • <strong>Inversor:</strong> {sistema_goodwe["inversor"]} |
                    <strong>Armazenamento:</strong> {sistema_goodwe["bateria"]} |
                    <strong>Carregador EV:</strong> {sistema_goodwe["carregador_ev"]} |
                    <strong>Monitoramento:</strong> {sistema_goodwe["monitoramento"]}
                </div>

                {bloco_alerta}

                <form class="formulario" method="GET" action="/">
                    <label>Nível Inicial da Bateria (kWh):</label>
                    <input type="text" name="bateria_inicial" value="{bateria_inicial}">
                    <label>Capacidade da Bateria GoodWe (kWh):</label>
                    <input type="text" name="capacidade_bateria" value="{capacidade_bateria}">
                    <button type="submit">Simular</button>
                </form>

                <h2>Indicadores Energéticos e de Sustentabilidade</h2>
                <div class="cards">
                    <div class="card">
                        <h3>Energia Solar Usada</h3>
                        <p>{resumo["total_solar"]} kWh</p>
                    </div>
                    <div class="card">
                        <h3>Bateria GoodWe Usada</h3>
                        <p>{resumo["total_bateria"]} kWh</p>
                    </div>
                    <div class="card">
                        <h3>Energia da Rede</h3>
                        <p>{resumo["total_rede"]} kWh</p>
                    </div>
                    <div class="card">
                        <h3>Redução no Pico (20%)</h3>
                        <p>{resumo["total_reduzido"]} kWh</p>
                    </div>
                    <div class="card">
                        <h3>Uso Renovável</h3>
                        <p>{resumo["percentual_renovavel"]}%</p>
                    </div>
                    <div class="card">
                        <h3>CO₂ Evitado</h3>
                        <p>{resumo["co2_evitado_kg"]} kg</p>
                    </div>
                    <div class="card">
                        <h3>Economia Estimada</h3>
                        <p>R$ {resumo["economia_reais"]}</p>
                    </div>
                </div>

                <div class="grafico">
                    <h2>Gráfico de Operação por Horário</h2>
                    <img src="data:image/png;base64,{grafico_base64}" alt="Gráfico EcoCharge">
                </div>

                <h2>Tabela Detalhada por Horário</h2>
                {tabela_html}

                <div class="rodape-log">
                    <strong>Status de Automação (Arquivo Local):</strong> {status_arquivo}
                </div>
            </div>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


if __name__ == "__main__":
    servidor = HTTPServer(("localhost", 8000), EcoChargeHandler)
    print("Servidor EcoCharge rodando em http://localhost:8000")
    servidor.serve_forever()
