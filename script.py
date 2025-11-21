import random
import time
import csv
import os
from datetime import datetime

# ================================================================
# ======================== CONFIGURAÇÕES ==========================
# ================================================================

DIRETORIO_ARQUIVO = r"Resultados"     # Diretório onde o .csv será salvo
NOME_ARQUIVO = "dados_estufa.csv"             # Nome do arquivo CSV de saída

INTERVALO_LEITURA = 15                        # Tempo entre leituras dos sensores (segundos)
INTERVALO_SALVAMENTO = 60                     # Tempo entre salvamentos no arquivo CSV (segundos)

ALVO_TEMPERATURA = (22, 28)                   # Faixa ideal de temperatura (min, max)
ALVO_UMIDADE_AR = (50, 70)                    # Faixa ideal de umidade (%)
# ================================================================


# SIMULADOR DE SENSORES
class Simulador:
    def ler_dados(self):
        """Simula a leitura dos sensores."""
        dados = {
            "temp": round(random.uniform(18, 35), 1),
            "humid": round(random.uniform(40, 90), 1),
            "soil": round(random.uniform(20, 80), 1),
            "lux": round(random.uniform(1000, 25000), 0)
        }
        return dados


# CONTROLADOR DA ESTUFA
class ControladorEstufa:
    def __init__(self):
        self.temp_min, self.temp_max = ALVO_TEMPERATURA
        self.umid_min, self.umid_max = ALVO_UMIDADE_AR

        self.ventilador = False
        self.umidificador = False

    def controlar(self, dados):
        temp = dados["temp"]
        umid = dados["humid"]

        print("\n===== Dados do Ambiente =====")
        print(f"Temperatura: {temp}°C")
        print(f"Umidade do ar: {umid}%")
        print("==============================")

        # Controle de temperatura
        if temp > self.temp_max:
            self.ventilador = True
            print("Temperatura ALTA → Ligando ventiladores!")
        elif temp < self.temp_min:
            self.ventilador = False
            print("Temperatura BAIXA → Desligando ventiladores.")
        else:
            self.ventilador = False
            print("Temperatura ideal. Nenhuma ação necessária.")

        # Controle de umidade
        if umid < self.umid_min:
            self.umidificador = True
            print("Umidade BAIXA → Ligando umidificador!")
        elif umid > self.umid_max:
            self.umidificador = False
            print("Umidade ALTA → Desligando umidificador.")
        else:
            self.umidificador = False
            print("Umidade adequada. Nenhuma ação necessária.")

        print("\n----- Estado dos Atuadores -----")
        print(f"Ventiladores:   {'LIGADOS' if self.ventilador else 'DESLIGADOS'}")
        print(f"Umidificador:   {'LIGADO' if self.umidificador else 'DESLIGADO'}")
        print("--------------------------------\n")

        return self.ventilador, self.umidificador


# Função para salvar o CSV
def salvar_csv(caminho_completo, registros):
    cabecalho = ["timestamp", "temperatura", "umidade_ar", "umidade_solo", "luminosidade",
                 "ventilador", "umidificador"]

    arquivo_novo = not os.path.exists(caminho_completo)

    with open(caminho_completo, "a", newline="") as f:
        writer = csv.writer(f)
        if arquivo_novo:
            writer.writerow(cabecalho)
        writer.writerows(registros)


# ====================== PROGRAMA PRINCIPAL =======================
if __name__ == "__main__":
    sensor = Simulador()
    controlador = ControladorEstufa()

    buffer_dados = []
    ultima_gravacao = time.time()

    # Garante que o diretório exista
    os.makedirs(DIRETORIO_ARQUIVO, exist_ok=True)
    caminho_completo = os.path.join(DIRETORIO_ARQUIVO, NOME_ARQUIVO)

    print("\nSistema de Estufa Automática Iniciado!")
    print(f"Leitura a cada {INTERVALO_LEITURA} segundos.")
    print(f"Salvando no CSV a cada {INTERVALO_SALVAMENTO} segundos.\n")

    try:
        while True:
            dados = sensor.ler_dados()
            vent, umidif = controlador.controlar(dados)

            buffer_dados.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                dados["temp"],
                dados["humid"],
                dados["soil"],
                dados["lux"],
                "LIGADO" if vent else "DESLIGADO",
                "LIGADO" if umidif else "DESLIGADO"
            ])

            # Salvamento periódico
            if time.time() - ultima_gravacao >= INTERVALO_SALVAMENTO or not os.path.exists(caminho_completo):
                salvar_csv(caminho_completo, buffer_dados)
                print(f"Dados salvos em: {caminho_completo}\n")
                buffer_dados.clear()
                ultima_gravacao = time.time()


            time.sleep(INTERVALO_LEITURA)

    except KeyboardInterrupt:
        print("\n\nEncerrado pelo usuário. Sistema desligado.")
        if buffer_dados:
            salvar_csv(caminho_completo, buffer_dados)
            print("Dados restantes foram salvos.")

