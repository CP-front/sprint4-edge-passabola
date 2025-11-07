# Projeto IoT: Sistema de Check-in por Presença "Passa a Bola Encontros"
## Sprint 4: Aplicação Prática da Arquitetura IoT

Repositório final para a disciplina de Edge Computing and Computer Systems, demonstrando uma Prova de Conceito (PoC) funcional de uma arquitetura IoT completa, desde a coleta de dados no dispositivo de borda (edge) até a visualização em um dashboard dinâmico.

🔗 **Vídeo explicativo no YouTube:** [Clique aqui para abrir](https://youtu.be/iLlr0hzQKF8?si=qaeBIQXRiDaR5Aba)

🔗 **Projeto no Wokwi:** [Clique aqui para abrir](https://wokwi.com/projects/445024602202020865)

---

### Arquitetura da Solução
![Arquitetura](./img/FiwareDeploy_new_v5%20(1).drawio%20(1).png)

---

### 1. Integrantes (Grupo: Visionary Solutions)
* 1ESPG
* Arthur Araújo Tenório - 562272
* Breno Gonçalves Báo - 564037
* Rodrigo Cardoso Tadeo - 562010
* Vinicius Cavalcanti dos Reis - 562063

---

### 2. Contexto e Descrição do Projeto

#### 2.1. O Problema
No contexto do projeto "Passa a Bola Encontros", um dos maiores desafios operacionais da plataforma é o gerenciamento de presença nos jogos de futebol feminino amador. O processo de check-in manual é lento, suscetível a erros e impede que as organizadoras saibam em tempo real quem está presente, causando atrasos e frustração.

#### 2.2. A Solução Proposta
Este projeto implementa uma solução de **Internet das Coisas (IoT)** para automatizar o processo de check-in. A solução consiste em um dispositivo de hardware (ESP32) posicionado na entrada da quadra, que detecta automaticamente as jogadoras por proximidade e atualiza um dashboard de controle em tempo real.

O fluxo completo é:
1.  A jogadora, com seu smartphone, utiliza um aplicativo (simulado pelo **nRF Connect**) que emite um sinal **Bluetooth Low Energy (BLE)**.
2.  Um **ESP32** na quadra escaneia o ambiente, detecta esse sinal, extrai o ID único da jogadora e **publica** esse ID via **MQTT** para um broker na nuvem.
3.  Uma plataforma **FIWARE** (rodando em uma VM na Azure) recebe essa mensagem.
4.  O **Orion Context Broker** (o "cérebro" do FIWARE) armazena o ID da última jogadora detectada.
5.  Um **Dashboard dinâmico em Python (Dash)** consulta a API do Orion a cada 5 segundos, detecta novas jogadoras e atualiza um contador e uma lista de presença com os horários do primeiro check-in de cada uma.

---

### 3. Funcionalidades Implementadas
O sistema implementa as seguintes funcionalidades:

* **Detecção Automática de Presença:** O ESP32 escaneia e identifica dispositivos BLE (jogadoras) em proximidade.
* **Comunicação MQTT:** Envio eficiente dos dados de check-in do dispositivo (ESP32) para a plataforma em nuvem (FIWARE).
* **Armazenamento de Estado:** O FIWARE Orion armazena o **último** check-in detectado, servindo como fonte de dados em tempo real.
* **Dashboard em Tempo Real:** Uma interface web (Dash) que exibe:
    * Um **contador** com a quantidade de jogadoras únicas que fizeram check-in.
    * Uma **lista de presença** com o ID de cada jogadora e o horário (local, UTC-3) do seu **primeiro** check-in.
* **Lógica de Check-in Único:** O dashboard possui uma lógica interna (em memória) que ignora check-ins de jogadoras que já estão na lista, garantindo que o contador e a lista mostrem apenas IDs únicos.
* **Reset de Contagem:** Um botão "Zerar Contagem de Check-ins" no dashboard que limpa tanto o histórico local do dashboard quanto a entidade de check-in no servidor FIWARE, permitindo o início de um novo jogo.
* **Serviço Automatizado:** O dashboard em Python é implementado como um serviço `systemd` no Linux, garantindo que ele inicie automaticamente com o servidor e se recupere de falhas.

---

### 4. Arquitetura em Camadas

A solução foi estruturada em três camadas distintas:

#### 4.1. Camada de Aplicação (Visualização)
É a interface com o usuário final (a organizadora do jogo).
* **Componentes:** Dashboard Web (Dash/Plotly) rodando em Python.
* **Função:** Consome a API do back-end (via HTTP) a cada 5 segundos para buscar o último check-in. Aplica a lógica de negócio (filtro de IDs únicos, conversão de fuso horário) e exibe os dados (contador e lista) em tempo real. Também envia comandos (como o `DELETE` do "Reset") de volta para o back-end.

#### 4.2. Camada de Back-end (Plataforma IoT)
O cérebro do sistema, rodando em uma VM na Azure.
* **Componentes:** Stack FIWARE (Orion, IoT Agent, STH-Comet), Broker Mosquitto, Docker, Python (para o servidor do dashboard).
* **Função:** Recebe dados via MQTT (do Mosquitto), traduz (com o IoT Agent), armazena o estado atual (no Orion), armazena o histórico (no STH-Comet, via Subscrição) e expõe os dados através de uma API HTTP/REST.

#### 4.3. Camada IoT (Dispositivos de Borda)
Os dispositivos físicos que coletam os dados do mundo real.
* **Componentes:** ESP32, Smartphone (simulando beacon BLE).
* **Função:** O ESP32 detecta o sinal BLE, extrai o ID e publica os dados na Camada de Back-end usando MQTT.

---

### 5. Componentes e Materiais Utilizados

* **Recursos de Hardware:**
    * 1x Placa de desenvolvimento ESP32 (ex: DevKit v1).
    * 1x Cabo Micro-USB (de dados).
    * 1x Smartphone com app **nRF Connect for Mobile** (para simular o beacon da jogadora).
* **Recursos de Software (Plataforma e Cloud):**
    * **Microsoft Azure:** 1x VM Ubuntu 20.04.
    * **Docker & Docker Compose:** Para orquestração dos contêineres do back-end.
    * **FIWARE Descomplicado:** Stack FIWARE pré-configurado, contendo:
        * **Mosquitto:** Broker MQTT para ingestão de dados.
        * **FIWARE IoT Agent (UltraLight):** Tradutor de MQTT para o formato NGSI.
        * **FIWARE Orion Context Broker:** Banco de dados de estado atual (API na porta 1026).
        * **FIWARE STH-Comet:** Banco de dados de histórico (API na porta 8666).
    * **Python 3.12:** Linguagem do servidor do dashboard.
    * **Bibliotecas Python:** `dash`, `plotly`, `requests`, `pandas`, `dash-bootstrap-components`, `pytz`.
    * **Linux Systemd:** Para gerenciamento do serviço do dashboard.
* **Ferramentas de Desenvolvimento:**
    * **Arduino IDE:** Para programar o ESP32.
    * **Postman:** Para configurar, provisionar e testar a API do FIWARE.

---

### 6. Lógica de Sistema e Operação

#### 6.1. Lógica do Dispositivo (ESP32)
O código no ESP32 (`esp32_checkin_scanner.ino`) executa um loop simples:
1.  Escaneia o ambiente por 5 segundos procurando por beacons BLE com o UUID `4fafc201-1fb5-459e-8fcc-c5c9c331914b`.
2.  Se encontrar, extrai o MAC Address do dispositivo (ex: `6aaff4b5292f`).
3.  Publica este ID no tópico MQTT `/TEF/scanner01/attrs` no formato UltraLight 2.0: `p|6aaff4b5292f`.
4.  Pausa por 2 segundos e repete.

#### 6.2. Lógica do Back-end (Dashboard Python)
Esta é a parte crucial da nossa solução, pois o componente `STH-Comet` (histórico) se mostrou instável. Para contornar isso, criamos a lógica de histórico e de IDs únicos na própria aplicação:

1.  **Armazenamento em Memória:** O script `dashboard.py` mantém uma variável global, um dicionário Python chamado `unique_players_history = {}`.
2.  **Consulta (a cada 5s):** O dashboard **consulta o Orion (porta 1026)** para pegar o *último* check-in (ex: `lastPlayerId: "6aaff..."`).
3.  **Filtro de IDs Únicos:** Ao receber o ID, o script verifica: `if player_id and player_id not in unique_players_history:`.
4.  **Adição ao Histórico:** Se o ID for novo, ele é adicionado ao dicionário `unique_players_history`, usando a hora do check-in (convertida de UTC para `America/Sao_Paulo`) como valor.
5.  **Atualização da UI:** O dashboard é redesenhado com base no conteúdo atualizado do `unique_players_history`, mostrando a contagem (`len()`) e a lista.
6.  **Lógica de Reset:** Quando o botão "Zerar" é clicado:
    a. O histórico em memória (`unique_players_history = {}`) é limpo.
    b. Uma requisição **`DELETE`** é enviada ao Orion (`http://127.0.0.1:1026/v2/entities/...`) para apagar a entidade do servidor.
    c. O dashboard é retornado zerado e permanece assim até que um novo check-in seja enviado pelo ESP32.

---

### 7. Estrutura do Repositório (Projeto)
O repositório está organizado nas seguintes pastas para garantir a separação de responsabilidades:
```
/ 
├── backend-fiware/ 
│ └── docker-compose.yml                        # Arquivo de orquestração dos serviços FIWARE. 
│ 
├── backend-dashboard/ 
│ ├── dashboard.py                              # Script principal do dashboard em Dash/Python. 
│ ├── requirements.txt                          # Lista de dependências Python. 
│ └── passabola.service                         # Arquivo de serviço Systemd para deploy. 
│ 
├── dispositivo-iot/ 
│ └── esp32_checkin_scanner.ino                 # Código-fonte do ESP32 para Arduino IDE. 
│ 
├── configuracao-postman/ 
│ └── PassaBola_FIWARE.postman_collection.json  # Collection do Postman para configurar a API. 
│ 
├── prints-resultado/ 
│ ├── contador pessoas.png                      # Print do dashboard funcional. 
│ ├── contador esp32.png                        # Print do ESP32 enviando dados. 
│ ├── contador postman.png                      # Print da API do Orion (estado atual). 
│ 
└── README.md                                   # Esta documentação.
```
---

### 8. Manual de Instalação e Replicabilidade

Este guia garante que o projeto possa ser replicado.

#### Pré-requisitos
* Uma conta na Microsoft Azure (ou outra provedora de cloud).
* Um ESP32 e um cabo de dados USB.
* Software local: Arduino IDE, Postman, um terminal SSH.

#### A. Configuração da VM (Azure)
1.  **Criar VM:** Inicie uma VM **Ubuntu 20.04** ou 22.04.
2.  **Abrir Portas (Firewall):** No "Network Security Group" (NSG) da VM, crie regras de entrada para **Permitir (Allow)** tráfego **TCP** de **Qualquer (Any)** origem para as seguintes portas:
    * `22` (SSH)
    * `1883` (MQTT)
    * `4041` (FIWARE IoT Agent)
    * `1026` (FIWARE Orion Broker)
    * `8666` (FIWARE STH-Comet)
    * `5000` (Dashboard Python)
3.  **Instalar Docker:** Conecte-se à VM via SSH e instale o Docker e o Docker Compose:
    ```bash
    sudo apt update
    sudo apt install docker.io
    sudo apt install docker-compose
    ```

#### B. Configuração do Back-end FIWARE (VM)
1.  **Clonar FIWARE:** Na VM, clone o repositório "FIWARE Descomplicado":
    ```bash
    git clone https://github.com/fabiocabrini/fiware.git
    cd fiware
    ```
2.  **Editar `docker-compose.yml` (Opcional, mas Recomendado):**
    * Para garantir estabilidade, edite o `docker-compose.yml` (`nano docker-compose.yml`).
    * Encontre o serviço `sth-comet:` e adicione a linha `restart: always` (com a indentação correta).
3.  **Iniciar FIWARE:**
    ```bash
    docker-compose up -d
    ```
4.  **Verificar:** Aguarde 1-2 minutos e execute `docker ps`. Confirme que todos os serviços estão com o status `(healthy)`.

#### C. Configuração do Back-end Dashboard (VM)
1.  **Dependências Python:**
    ```bash
    sudo apt-get install -y python3-venv
    ```
2.  **Criar Venv:** Na mesma pasta `~/fiware`, crie o ambiente virtual:
    ```bash
    python3 -m venv dash-env
    ```
3.  **Ativar Venv:**
    ```bash
    source dash-env/bin/activate
    ```
4.  **Instalar Dependências:**
    * Crie o `requirements.txt`: `nano requirements.txt`
    * Cole o conteúdo do arquivo `backend-dashboard/requirements.txt` do repositório.
    * Instale: `pip install -r requirements.txt`
5.  **Criar Script do Dashboard:**
    * Crie o `dashboard.py`: `nano dashboard.py`
    * Cole o conteúdo do arquivo `backend-dashboard/dashboard.py` do repositório.
    * **IMPORTANTE:** Verifique se a variável `VM_IP` no script está definida como `"127.0.0.1"`.
6.  **Criar e Iniciar o Serviço (Deploy):**
    * Copie o arquivo de serviço de `backend-dashboard/passabola.service` do repositório, e crie o serviço: `sudo nano /etc/systemd/system/passabola.service`
    * Recarregue o systemd: `sudo systemctl daemon-reload`
    * Habilite o serviço (para iniciar com o boot): `sudo systemctl enable passabola.service`
    * Inicie o serviço: `sudo systemctl start passabola.service`
7.  **Verificar Serviço:** `sudo systemctl status passabola.service` (deve mostrar `active (running)`).

#### D. Provisionamento da Plataforma (Postman Local)
1.  **Importar:** Abra o Postman na sua máquina local e importe o arquivo `FIWARE Descomplicado Passa a Bola.postman_collection.json` (da pasta `configuracao-postman/`).
2.  **Configurar IP:** Crie uma variável de ambiente no Postman chamada `{{url}}` e coloque o **IP público** da sua VM (ex: `20.81.162.205`).
3.  **Executar (na ordem):** Envie as requisições da collection para configurar o FIWARE:
    1.  `IOT Agent MQTT [POST] 2. Provisioning a Service Group...` (Deve retornar `201 Created`)
    2.  `IOT Agent MQTT [POST] 3. Provisionar Scanner de Check-in` (Deve retornar `201 Created`)
    3.  `STH-Comet [POST] 2. Criar Assinatura para Histórico (STH-Comet)` (Deve retornar `201 Created`)

#### E. Configuração do Dispositivo (Arduino IDE Local)
1.  **Abrir Código:** Abra o `esp32_checkin_scanner.ino` (da pasta `dispositivo-iot/`) na sua Arduino IDE.
2.  **Configurar:** Altere as 3 variáveis no topo:
    * `ssid`: Nome da sua rede Wi-Fi local.
    * `password`: Senha da sua rede Wi-Fi local.
    * `mqtt_server`: O **IP público** da sua VM Azure.
3.  **Upload:** Conecte seu ESP32, selecione a Placa (`ESP32 Dev Module`) e a Porta COM correta. Clique em **Upload**.
    * *Nota:* Talvez seja necessário segurar o botão `BOOT` na placa durante o upload.

---

### 9. Execução do Sistema (Operação)

Com todas as fases de instalação concluídas, o sistema está operacional:

1.  **ESP32:** Abra o Monitor Serial (115200 baud) na Arduino IDE.
2.  **Smartphone:** Abra o nRF Connect e ative o "Advertiser" com o UUID correto.
3.  **Dashboard:** Acesse `http://<IP_PUBLICO_DA_VM>:5000` no seu navegador. O dashboard deve carregar e mostrar "0".
4.  **Teste:** Aproxime o celular do ESP32.
    * O Monitor Serial deve mostrar "Beacon detectado!" e "Payload (dados enviados): p|...".
    * O Dashboard deve atualizar automaticamente (em até 5s), mostrando "1" no contador e o ID da jogadora na lista com o horário local correto.
    * Envie a requisição `IOT Agent MQTT [GET] 8. Verificar Entidade do Ponto de Check-in` para ver o ponto de check-in.
    * Se você clicar em "Zerar Contagem de Check-ins", o dashboard e o servidor FIWARE serão limpos.

---

### 10. Resultados da PoC (Prints de Integração IoT com "Site")

A Prova de Conceito foi validada. O "site" é representado pelo nosso Dashboard dinâmico em Python, que consome a API HTTP do FIWARE exatamente como o front-end final do "Passa a Bola" faria.

**Print 1: Dashboard Final em Funcionamento (com Múltiplos Check-ins)**
![Dashboard Final](./img/contador%20pessoas.png)

**Print 2: Monitor Serial (ESP32 Enviando Dados)**
![Monitor Serial](./img/contador%20esp32.png)

**Print 3: Postman (Orion - Estado Atual OK)**
![Postman Orion](./img/contador%20postman.png)

---

### 11. Notas de Segurança (Importante)

Esta implementação é uma Prova de Conceito e **não está pronta para produção**. Por razões de simplicidade, todas as portas (MQTT, HTTP, API) estão abertas publicamente (`0.0.0.0`).

Em um ambiente de produção real, as seguintes medidas seriam necessárias:
* Configurar o firewall da VM para aceitar conexões apenas de IPs confiáveis.
* Implementar autenticação (usuário/senha ou certificados) no broker MQTT (Mosquitto).
* Colocar as APIs do FIWARE e do Dashboard por trás de um proxy reverso (como Nginx) com autenticação e HTTPS (SSL).
* Idealmente, o ESP32 se conectaria à nuvem através de uma VPN.

---

### 12. Dependências do Projeto (Python)

Todas as dependências de software do lado do servidor estão listadas no arquivo `backend-dashboard/requirements.txt`. Elas podem ser instaladas em um ambiente virtual Python usando:

```bash
pip install -r requirements.txt
```

---

### 13. Recursos e Materiais
[Repositório FIWARE Descomplicado](https://github.com/fabiocabrini/fiware)

[Documentação Oficial do Dash Plotly](https://dash.plotly.com)

[Documentação do FIWARE Orion](https://fiware-orion.readthedocs.io/en/master)

---

### 14. Licença

Este projeto é livre para uso educacional. Para uso comercial, consulte os autores.

