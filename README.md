# Interface de IA para Saúde - Projeto COMPET-CISAM/UPE

> **Status:** 🚧 Em desenvolvimento 🚧

![Demonstração da Interface](https://raw.githubusercontent.com/compet-cisam/interface/main/static/upe.png)

Este repositório contém o código-fonte de uma interface web customizada, baseada no [Open WebUI](https://github.com/open-webui/open-webui), para um projeto de Inteligência Artificial na área da saúde. A iniciativa é uma colaboração do grupo de extensão e pesquisa **COMPET** com o **Centro Integrado de Saúde Amaury de Medeiros (CISAM)** da **Universidade de Pernambuco (UPE)**, em Recife.

A plataforma foi adaptada para servir como um ambiente seguro e intuitivo para interação com modelos de linguagem especializados, focados em apoiar profissionais, residentes e pesquisadores das áreas de Saúde da Mulher, Obstetrícia e Neonatologia.

## ✨ Principais Funcionalidades e Customizações

* **Interface Adaptada:** A interface foi modificada para refletir a identidade visual da UPE e otimizar o fluxo de trabalho dos profissionais de saúde do CISAM.
* **Segurança e Privacidade (On-Premises):** Projetado para rodar em servidores locais (on-premises), garantindo que nenhum dado sensível de paciente seja exposto externamente, em conformidade com a Lei Geral de Proteção de Dados (LGPD).
* **Assistente Especializado:** Conecta-se a modelos de IA que podem ser treinados para fornecer apoio à decisão clínica, sumarizar documentos, e acessar rapidamente protocolos e literatura médica relevante.
* **Foco no Usuário Clínico:** Componentes como o chat, entrada de texto e diálogos foram ajustados para as necessidades de um ambiente hospitalar.
* **Potencial para Ensino:** A ferramenta pode ser usada como um ambiente de simulação para o treinamento de residentes e estudantes, permitindo a exploração segura de casos clínicos.

## 🛠️ Tecnologias Utilizadas

* **Frontend:** SvelteKit
* **Backend:** Python (através do Open WebUI)
* **Containerização:** Docker e Docker Compose

## 🚀 Como Executar o Projeto Localmente

Siga os passos abaixo para ter a interface rodando em sua máquina.

### Pré-requisitos

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop/) e Docker Compose

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/compet-cisam/interface.git](https://github.com/compet-cisam/interface.git)
    cd interface
    ```

2.  **Configuração do Ambiente:**
    Este projeto utiliza o `docker-compose.yaml` para orquestrar os serviços. Certifique-se de que o Docker esteja em execução na sua máquina.

3.  **Inicie os containers:**
    Na pasta raiz do projeto, execute o comando:
    ```bash
    docker-compose up -d --build
    ```
    * O comando irá construir as imagens dos containers e iniciá-los em background (`-d`).

4.  **Acesse a interface:**
    Após a inicialização, a interface estará disponível no seu navegador. Acesse o endereço:
    ```
    http://localhost:8080
    ```
    *(A porta pode variar. Verifique o arquivo `docker-compose.yaml` se necessário).*

## 🎯 Missão do Projeto

O objetivo desta iniciativa é explorar o potencial da Inteligência Artificial generativa para criar ferramentas que aumentem a capacidade dos profissionais de saúde do CISAM, promovendo uma medicina mais ágil e baseada em dados, além de fomentar a inovação tecnológica no ambiente acadêmico da UPE.
