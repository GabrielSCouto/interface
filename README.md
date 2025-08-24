# Interface de IA para Saúde - Projeto COMPET-CISAM/UPE

![Demonstração da Interface](https://raw.githubusercontent.com/compet-cisam/interface/main/static/upe.png)

Este repositório contém o código-fonte de uma interface web customizada, baseada no [Open WebUI](https://github.com/open-webui/open-webui), para um projeto de Inteligência Artificial na área da saúde. A iniciativa é uma colaboração do grupo de extensão e pesquisa **COMPET** com o **Centro Integrado de Saúde Amaury de Medeiros (CISAM)** da **Universidade de Pernambuco (UPE)**, em Recife.

A plataforma foi adaptada para servir como um ambiente seguro e intuitivo para interação com modelos de linguagem especializados, focados em apoiar profissionais, residentes e pesquisadores das áreas de Saúde da Mulher, Obstetrícia e Neonatologia.

## ✨ Principais Funcionalidades e Customizações

* **Interface Adaptada:** A interface foi modificada para refletir a identidade visual da UPE e otimizar o fluxo de trabalho dos profissionais de saúde do CISAM.
* **Segurança e Privacidade (On-Premises):** Projetado para rodar em servidores locais (on-premises), garantindo que nenhum dado sensível de paciente seja exposto externamente, em conformidade com a Lei Geral de Proteção de Dados (LGPD).
* **Assistente Especializado:** Conecta-se a modelos de IA que podem ser treinados para fornecer apoio à decisão clínica, sumarizar documentos, e acessar rapidamente protocolos e literatura médica relevante.
* **Foco no Usuário Clínico:** Componentes como o chat, entrada de texto e diálogos foram ajustados para as necessidades de um ambiente hospitalar.
* **Potencial para Ensino:** A ferramenta pode ser usada como um ambiente de simulação para o treinamento de residentes e estudantes, permitindo a exploração segura de casos clínicos.
* **Análise de prontuários médicos:** Analisa prontuários médicos de forma simplificada na interface e retorna uma avaliação do paciente.

## 🛠️ Tecnologias Utilizadas

* **Frontend:** SvelteKit
* **Backend:** Python e Ollama (através do Open WebUI)
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

2.  **Crie o arquivo de ambiente:**
    O projeto usa um arquivo `.env` para configurar variáveis de ambiente. Renomeie o arquivo de exemplo:
    ```bash
    mv .example.env .env
    ```
    *(\*Nota: Você pode editar o arquivo `.env` se precisar alterar alguma configuração, como as portas dos serviços).*

3.  **Baixar o modelo Medgemma `medgemma-4b-it-Q8_0.gguf` do Hugging Face:**
    ```bash
    cd modelfiles/medgemma-4b-it-Q8_0
    wget [https://huggingface.co/kelkalot/medgemma-4b-it-GGUF/resolve/main/medgemma-4b-it-Q8_0.gguf](https://huggingface.co/kelkalot/medgemma-4b-it-GGUF/resolve/main/medgemma-4b-it-Q8_0.gguf)
    ```

4.  **Adicionar o modelo dentro do container do Ollama:**
    ```bash
    docker exec -it <nome_do_container_ollama> ollama create nome_do_modelo_novo -f /modelfiles/nome_do_modelo_novo/Modelfile
    ```

    <details>
    <summary>Como adicionar outros modelos:</summary>

    1. Criar pasta para o modelo novo dentro da pasta **modelfiles**: `/modelfiles/nome_do_modelo_novo` (substituir `nome_do_modelo_novo` pelo nome desejado).
    2. Dentro da pasta nova, criar um arquivo `Modelfile` contendo as instruções para a execução do modelo pelo Ollama — checar a [documentação do Ollama](https://ollama.readthedocs.io/en/modelfile/) ou o `Modelfile` já existente em `/modelfiles/medgemma-4b-it-Q8_0`.
    3. Na pasta raiz, alterar o arquivo `entrypoint.sh` para incluir o modelo desejado (antes de `wait`):
       ```bash
       [...]

       ollama create nome_do_modelo_novo -f /modelfiles/nome_do_modelo_novo/Modelfile
       
       wait
       ```
    4. Rebuildar o ambiente e acessar a interface atualizada:
       ```bash
       docker-compose down
       docker-compose up -d --build
       ```
       Acesse: `http://localhost:8080`

    </details>

5.  **Inicie os containers:**
    Na pasta raiz do projeto, execute o comando:
    ```bash
    docker-compose up -d
    ```
    *O comando irá construir as imagens dos containers e iniciá-los em background (`-d`).*

    <details>
    <summary>Caso não queira usar todos os containers</summary>

    - Para deixar o ambiente de desenvolvimento mais leve, você pode inicializar apenas os containers necessários. Na pasta raiz do projeto, execute o comando:
      
    ```bash
    docker compose up -d ollama open-webui
    ```
    </details>

6.  **Acesse a interface:**
    Após a inicialização, a interface estará disponível no seu navegador. Acesse o endereço:
    ```
    http://localhost:8080
    ```
    *(\*A porta pode variar. Verifique o arquivo `docker-compose.yaml` ou seu `.env` se necessário).*

**ATENÇÃO:**
- O servidor Ollama não deve estar rodando na sua máquina; esse processo deve ser feito através do Docker Compose.
- Não commitar diretamente na branch `main`.
- Qualquer problema ao tentar configurar o projeto na sua máquina, entre em contato.
