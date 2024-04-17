# T2Extractor: Python Data Extraction Toolkit

## O que é?
**T2Extractor** é uma biblioteca Python que oferece funcionalidades para extração de texto de documentos usando AWS Textract e interação com o OpenAI GPT.

## Principais recursos
**Extração de Texto de Documentos:** Extrai texto de documentos em formatos PDF e imagens.

**Integração com AWS Textract:** Utiliza o serviço AWS Textract para extração de texto de documentos.

**Interação com OpenAI GPT:** Interage com o OpenAI GPT para capturar dados específicos do texto do documento conforme configurações do prompt do OpenAI GPT

**Conversão de Documentos em Base64:** Converte documentos em formato PDF e imagens em strings base64.

**Envio de Dados para T2 Verification:** Envia os dados extraídos para o portal T2 Verification para verificação do usuário.

## Instalação
- `pip install "git+https://github.com/T2C-Consultoria/prj_QUAL_T2Extractor_Lib"`

## Dependências
- boto3
- openpyxl
- pdf2image
- pyodbc
- PyPDF2
- requests
