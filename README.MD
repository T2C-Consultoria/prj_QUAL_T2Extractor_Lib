# T2Extractor: Python Data Extraction Toolkit

<div>
  <a href="https://www.python.org/" target="_blank"><img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" target="_blank"></a>
  <a href ="https://aws.amazon.com/pt/textract/" target="_blank"><img src="https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white" target="_blank"></a>
  <a href="https://chat.openai.com/" target="_blank"><img src="https://img.shields.io/badge/chatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white" target="_blank"></a>  
</div>

## O que é?
**T2Extractor** é uma biblioteca Python que oferece funcionalidades para extração de texto de documentos usando AWS Textract e interação com o OpenAI GPT.

## Principais recursos
**Extração de Texto de Documentos:** Extrai texto de documentos em formatos PDF e imagens.

**Integração com AWS Textract:** Utiliza o serviço AWS Textract para extração de texto de documentos.

**Interação com OpenAI GPT:** Interage com o OpenAI GPT para processamento adicional do texto extraído.

**Conversão de Documentos em Base64:** Converte documentos em formato PDF e imagens em strings base64.

**Captura de Dados Específicos:** Captura dados específicos do texto do documento conforme configurações do prompt do OpenAI GPT.

**Envio de Dados para T2 Verification:** Envia os dados extraídos para o portal T2 Verification para verificação do usuário.

## Instalação
- `pip install "git+https://github.com/T2C-Consultoria/prj_QUAL_T2Extractor_Lib"`

## Tecnologias Utilizadas
- boto3
- openpyxl
- pdf2image
- pyodbc
- PyPDF2
- requests
