# Projeto de Coleta e Refinamento de Dados Bovespa

Um pipeline ETL completo para coletar, refinar e disponibilizar dados diários da B3 (Bovespa) em um Data Lakehouse na AWS.

## 🎯 Objetivo

O principal objetivo deste projeto é automatizar a coleta diária dos dados do índice IBOV (Bovespa) da B3, persistir essas informações de forma estruturada e refinada em um Data Lakehouse na AWS, e disponibilizá-las para consumo analítico através do Amazon Athena. O pipeline segue uma arquitetura robusta para garantir a qualidade, rastreabilidade e acessibilidade dos dados.

## 🌟 Visão Geral

Este projeto é um pipeline ETL (Extract, Transform, Load) que abrange desde a extração dos dados brutos do site da B3 até a disponibilização dos dados refinados para consultas. Ele se baseia em serviços da AWS para garantir escalabilidade, resiliência e automação.

O fluxo principal é dividido em etapas, começando com a coleta de dados ate a disponibilização para análise.

## ✨ Principais Funcionalidades

* **Extração Diária:** Coleta automática dos dados dos componentes do índice Bovespa (IBOV) da B3.
* **Ingestão de Dados Brutos:** Armazenamento dos dados brutos no S3 em formato Parquet com particionamento diário, seguindo o padrão de uma camada `raw` do Data Lake.
* **Processamento ETL Gerenciado:** Utilização do AWS Glue para transformar e refinar os dados, seguindo um fluxo visual de desenvolvimento.
* **Armazenamento de Dados Refinados:** Persistência dos dados transformados em uma camada `refined` do Data Lake, também em formato Parquet e com particionamento inteligente por data e ação.
* **Catálogo de Dados Automático:** Integração com o AWS Glue Data Catalog para metadados e criação automática de tabelas.
* **Disponibilidade para Análise:** Dados prontos para serem consultados e analisados via Amazon Athena.

## 🏛️ Arquitetura e Fluxo do ETL

O pipeline ETL completo segue uma arquitetura serverless e gerenciada pela AWS, dividida nas seguintes etapas, cumprindo os requisitos do projeto:

1.  **Extração e Ingestão da Camada Raw (Lambda com Imagem de Contêiner no ECR) - Requisito 1 & 2:**
    * O script Python responsável pelo **scraping dos dados do site da B3** e pela ingestão dos dados brutos no S3 é empacotado em uma **imagem Docker**.
    * Esta imagem Docker é publicada no **Amazon Elastic Container Registry (ECR)**.
    * Uma **função AWS Lambda** é configurada para usar esta imagem de contêiner. Esta Lambda executa o script, que coleta os dados do pregão diário do IBOV e os converte para o formato **Parquet**.
    * Os dados são então **ingeridos no S3** em um bucket dedicado à camada `raw` (`bck-bovespa`), com uma estrutura de **particionamento diário** (`raw/dataproc=YYYYMMDD/`).
    

2.  **Orquestração do ETL (Lambda e Glue) - Requisito 3 & 4:**
    * O upload do arquivo Parquet para o bucket `raw` no S3 **aciona um evento S3**.
    * Este evento **invoca uma segunda função AWS Lambda** (construída em python, focada apenas em iniciar o job).
    * Esta segunda função Lambda, por sua vez, **chama um job de ETL no AWS Glue**.

3.  **Transformação e Refinamento (AWS Glue) - Requisito 5 & 6:**
    * O **Job Glue** é o coração da transformação dos dados. Ele é **desenvolvido no modo visual** (AWS Glue Studio) para facilitar a construção do pipeline de processamento.
    * O job lê os dados da camada `raw` no S3.
    * Realiza as transformações e validações necessárias nos dados do pregão.
    * Os **dados refinados são salvos em formato Parquet** em uma pasta na camada `refined` do S3, **particionados por data** (`dt_ref=YYYY-MM-DD/`) **e pelo código da ação do pregão** (ex: `codigo=ABEV3/`).
    

4.  **Catálogo de Dados (AWS Glue Data Catalog) - Requisito 7:**
    * Ao final da execução, o Job Glue **automaticamente cataloga os dados refinados no Glue Catalog**.
    * Ele **cria uma tabela no banco de dados `default`** (ou outro especificado) do Glue Catalog, inferindo o esquema dos dados Parquet.

5.  **Disponibilidade para Análise (Amazon Athena) - Requisito 8:**
    * Com a tabela catalogada no Glue Data Catalog, os **dados refinados tornam-se imediatamente disponíveis e legíveis para consultas SQL através do Amazon Athena**. Isso permite que analistas de dados e ferramentas de BI acessem os dados de forma fácil e performática.
    

Este pipeline garante que os dados da B3 sejam processados de forma eficiente, governada e prontos para consumo.

## 🛠️ Detalhes de Implementação

### Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **`requests`:** Para fazer requisições HTTP à API da B3.
* **`pandas`:** Para manipulação e tratamento de dados em DataFrame.
* **`pyarrow`:** Para conversão de DataFrame para o formato Parquet.
* **`boto3`:** SDK da AWS para interagir com serviços como o S3.
* **AWS S3:** Serviço de armazenamento de objetos para o Data Lake.
* **AWS Lambda:** Serviço de computação serverless, utilizado para a função de scraping/ingestão (baseada em imagem de contêiner) e para a orquestração do Glue Job.
* **AWS ECR (Elastic Container Registry):** Repositório para armazenar a imagem Docker do scraper.
* **AWS Glue:** Serviço ETL serverless para transformação e catalogação de dados.
* **Amazon Athena:** Serviço de consulta interativa para dados no S3.
* **Event notifications:** Para acionamento dos processos após arquivo pousado no S3 na camada raw.
* **AWS EventBridge:** Para agendamento da execução diária do contêiner do scraper.

### Representação do Fluxo

```text
[Agendador Diário: EventBridge]
        |
        | (Invoca) 
        v
[Lambda (Scraping B3 + Ingestão Raw no S3)]
        |
        | (extracao_bovespa_docker)
        v
[S3 - Camada Raw (Dados Brutos Parquet)]
        |
        | (Dispara Evento)
        v
[Lambda (Orquestrador Glue Job)]
        |
        | (start_job_glue)
        v
[AWS Glue Job (Refinamento ETL)]
        |
        | (etl_bovespa)
        v
[S3 - Camada Refined (Dados Refinados Parquet)]
        |
        | (Catálogo Automático)
        v
[AWS Glue Data Catalog]
        | 
        | (catalog)
        v
[Amazon Athena (Consulta Analítica)]
```