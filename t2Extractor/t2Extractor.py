import base64
import boto3
import json
import os
import PyPDF2
import requests
from io import BytesIO
from pdf2image import convert_from_path
from PIL import Image

class Extractor:
    """
    Classe para extrair texto de documentos usando AWS Textract e interagir com o OpenAI GPT para processamento.
    """
    def __init__(self, arg_strGptApiKey:str, arg_strVersionChatGPT:str, arg_strAwsAccessKeyId:str, 
                 arg_strAwsSecretAccessKey:str, arg_strAwsRegionName:str="us-east-1", arg_strAwsServiceName:str="textract"):
        """
        Inicializa o T2Extractor com as credenciais da AWS e a chave de API do OpenAI GPT.

        Parâmetros:
        arg_strGptApiKey (str): Chave de API do OpenAI GPT.
        arg_strVersionChatGPT (str): Versão do ChatGPT.
        arg_strAwsAccessKeyId (str): ID da chave de acesso da AWS.
        arg_strAwsSecretAccessKey (str): Chave de acesso secreta da AWS.
        arg_strAwsRegionName (str): Nome da região da AWS (padrão: "us-east-1").
        arg_strAwsServiceName (str): Nome do serviço da AWS (padrão: "textract").
        """
        #FIXME Colocar atributos da classe no padrao (Variaveis com tipo etc)              
        self.var_strAwsAccessKeyId = arg_strAwsAccessKeyId
        self.var_strAwsSecretAccessKey = arg_strAwsSecretAccessKey
        self.var_strAwsRegionName = arg_strAwsRegionName
        self.var_strAwsServiceName = arg_strAwsServiceName
        self.var_strGptApiKey = arg_strGptApiKey
        self.var_strVersionChatGpt = arg_strVersionChatGPT

    def pdf_para_base64(self, arg_strDocumento:str):
        """
        Converte um arquivo PDF em uma string base64.

        Parâmetros:
        arg_strDocumento (str): Caminho para o arquivo PDF.

        Retorna:
        str: String base64 do arquivo PDF.
        """
        try:
            # Convertendo o arquivo PDF em imagens
            #FIXME colocar no padrao de variaveis 
            var_listImage = convert_from_path(arg_strDocumento, dpi=300)

            for img in var_listImage:
                var_bytesArray = BytesIO()
                img.save(var_bytesArray, format='PNG')
                var_strImgBase64 = base64.b64encode(var_bytesArray.getvalue()).decode('utf-8')
            return var_strImgBase64
        except Exception as exception:
            print(f"Erro ao converter o PDF para base64: {exception.__str__()}")
            return None

    def imagem_para_base64(self, arg_strDocumento:str):
        """
        Converte uma imagem em uma string base64.

        Parâmetros:
        arg_strDocumento (str): Caminho para a imagem.

        Retorna:
        str: String base64 da imagem.
        """
        try:
            #FIXME padrao de variaveis 
            with open(arg_strDocumento, 'rb') as file:
                var_imgDocumento = Image.open(file)
                var_bytesArray = BytesIO()
                var_imgDocumento.save(var_bytesArray, format='PNG')
                var_strImgBase64 = base64.b64encode(var_bytesArray.getvalue()).decode('utf-8')
            return var_strImgBase64
        except Exception as exception:
            print(f"Erro ao converter a imagem para base64: {exception.__str__()}")
            return None

    def extract_text_document(self, arg_strDocumento:str):
        """
        Extrai texto de um documento usando AWS Textract.

        Parâmetros:
        arg_strDocumento (str): Caminho para o documento.

        Retorna:
        str: Texto extraído do documento.
        """
        try:
            #FIXME padrao de variaveis 
            var_bcClientTextract = boto3.client(service_name=self.var_strAwsServiceName, region_name=self.var_strAwsRegionName,
                                            aws_access_key_id=self.var_strAwsAccessKeyId, aws_secret_access_key=self.var_strAwsSecretAccessKey)

            if arg_strDocumento.lower().endswith('.pdf'):
                # Abre o arquivo PDF
                with open(arg_strDocumento, "rb") as file:
                    var_pdfReader = PyPDF2.PdfReader(file)
                    var_intTotalPages = len(var_pdfReader.pages)
                    print(f"Número de páginas PDF: {var_intTotalPages}")
                    var_strTextoExtraido = ""
                    
                    # Percorre sobre cada página do PDF
                    for page_number in range(var_intTotalPages):
                        print(f"Extraindo texto da página: {page_number+1}")
                        # Extrai uma página especifica
                        var_pdfPage = var_pdfReader.pages[page_number]
                        
                        # Cria um novo arquivo PDF temporário contendo apenas esta página
                        var_strCaminhoTempPDF = f"page_{page_number}.pdf"
                        var_pdfTempPDFWriter = PyPDF2.PdfWriter()
                        var_pdfTempPDFWriter.add_page(var_pdfPage)
                        
                        with open(var_strCaminhoTempPDF, "wb") as temp_pdf_file:
                            var_pdfTempPDFWriter.write(temp_pdf_file)
                        
                        # Extrai texto da página atual usando Textract
                        var_bytesDocumento = open(var_strCaminhoTempPDF, "rb").read()
                        var_dictResponse = var_bcClientTextract.detect_document_text(Document={'Bytes': var_bytesDocumento})
                        
                        # Concatena o texto extraido da página atual
                        for block in var_dictResponse['Blocks']:
                            if block['BlockType'] == 'LINE':
                                var_strTextoExtraido += block['Text'] + "\n"
                        # Exclui o arquivo PDF temporário
                        os.remove(var_strCaminhoTempPDF)
            elif arg_strDocumento.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                var_bytesDocumento = open(arg_strDocumento, "rb").read()
                var_dictResponse = var_bcClientTextract.detect_document_text(Document={'Bytes': var_bytesDocumento})
                var_strTextoExtraido = ""
                
                # Concatena o texto extraido da página atual
                for block in var_dictResponse['Blocks']:
                    if block['BlockType'] == 'LINE':
                        var_strTextoExtraido += block['Text'] + "\n"
            else: 
                print("Formato do documento não suportado")
            return var_strTextoExtraido
        except Exception as exception:
                #FIXME corrigir texto do print 
                print("Erro ao extrair texto do documento: " + exception.__str__())
                raise

    def reading_text(self, arg_strPromptChatGPT:str, arg_strTexto_documento:str, arg_intMaxTokens:int=350):
        """
        #FIXME aqui não é leitura, aqui seria extracao dos dados solicitados 
        Realiza a extração dos dados solicitados ao ChatGPT.

        Parâmetros:
        #FIXME melhorar a explicacao do argumento do prompt 
        arg_strPromptChatGPT (str): Parâmetro que solicita ao ChatGPT quais dados serão extraídos do documento.
        arg_strTexto_documento (str): Texto do documento.
        arg_intMaxTokens (int): Número máximo de tokens a serem gerados (padrão: 350).

        Retorna:
        #FIXME tentar evitar ao maximo a utilização de tupla, tentar utilizar dicionario quando não há adição de multiplas linhas, em caso de multiplas
        #FIXME linhas, utilizar json 
        var_dictRespostaChatGPT (dict): Dicionário contendo a resposta do ChatGPT, o número de tokens de prompt e o número de tokens de conclusão.
        - "resposta_gpt" (str): Resposta gerada pelo ChatGPT.
        - "token_prompt" (int): Número de tokens no prompt enviado.
        - "token_conclusao" (int): Número de tokens na resposta gerada.
        """
        try:
            print("Iniciando extração dos dados no texto do documento")

            # Dicionário contendo os dados a serem enviados na requisição POST
            var_dictBody = {
                "model": self.var_strVersionChatGpt,
                "messages": [{"role": "user", "content": f"{arg_strPromptChatGPT}: {arg_strTexto_documento}"}],
                "max_tokens": arg_intMaxTokens,
                "temperature": 0.8,
            }

            # Cabeçalhos da requisição
            var_dictHeaders = {"Authorization": f"Bearer {self.var_strGptApiKey}", "Content-Type": "application/json"}
            
            # Realiza a requisição POST para a API da openAI
            var_response = requests.post("https://api.openai.com/v1/chat/completions", headers=var_dictHeaders, data=json.dumps(var_dictBody))
            var_jsonResponse = var_response.json()
            
            # Resposta do Chatgpt, Token da solicitação e Token da Resposta
            var_strRespostaChatGPT = var_jsonResponse["choices"][0]["message"]["content"]
            var_intTokenPrompt = var_jsonResponse['usage']['prompt_tokens']
            var_intTokenCompletion = var_jsonResponse['usage']['completion_tokens']
            
            print("Resposta ChatGPT: ", var_strRespostaChatGPT)
            print("Token Prompt: ", var_intTokenPrompt)
            print("Token de Conclusão: ", var_intTokenCompletion)

            # Dicionário contendo a resposta do ChatGPT, o número de tokens de prompt e o número de tokens de conclusão.
            var_dictRespostaChatGPT = {
                "resposta_gpt": var_strRespostaChatGPT,
                "token_prompt": var_intTokenPrompt,
                "token_conclusao": var_intTokenCompletion
            }

            return var_dictRespostaChatGPT
        
        except Exception as exception:
            print("Erro ao realizar leitura do texto do documento: " + exception.__str__())
            raise

    def verification(self, arg_strDocumento:str, arg_strRespostaChatGPT:str, arg_strLayout:str, arg_strTokenVerification:str, 
                     arg_strProject:str, arg_strPriority:str="high"):
        """
        Realiza a verificação de um documento.

        Parâmetros:
        arg_strDocumento (str): Caminho para o documento.
        arg_strRespostaChatGPT (str): Resposta do ChatGPT.
        arg_strLayout (str): Layout do documento.
        arg_strTokenVerification (str): Token de autenticação da API T2Verification.
        arg_strProject (str): ID do projeto na API T2Verification.
        #FIXME status nao deve ser uma escolha do desenvolvedor 
        arg_strPriority (str): Prioridade do documento (padrão: "high") - Todas Opções: ('low', 'Baixa'), ('medium', 'Média'), ('high', 'Alta').

        Raises:
        Exception: Se houver um erro ao enviar informações para a API.
        """
        try:
            print("Iniciando Verification")

            if arg_strDocumento.lower().endswith('.pdf'):
                var_strBytesDocumento = self.pdf_para_base64(arg_strDocumento=arg_strDocumento)
            elif arg_strDocumento.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                var_strBytesDocumento = self.imagem_para_base64(arg_strDocumento=arg_strDocumento)
            else: 
                print("Formato do documento não suportado")
            
            #FIXME nao basta ser só json? 

            # Dicionário contendo os dados a serem enviados na requisição POST
            var_strUrl = "https://api.t2verification.com.br/api/tasks/"
            var_dictBody = {
                "project": arg_strProject, # ID do Projeto no Verification
                "t2layout": arg_strLayout, # Nome do Layout do Documento no Verification
                "t2priority": arg_strPriority, # Prioridade do Documento
                "t2document": var_strBytesDocumento, # Documento em Bytes que será renderizado no Portal
                "t2status": "unassigned", # Status do Documento
                "t2verification": arg_strRespostaChatGPT # Informações do Documento
            }

            # Cabeçalhos da requisição
            var_dictHeaders = {
                "Authorization": f"Bearer {arg_strTokenVerification}",
                "Content-Type": "application/json"
            }

            # Realiza a requisição POST para o Portal T2 Verification
            var_response = requests.post(var_strUrl, json=var_dictBody, headers=var_dictHeaders)

            if var_response.status_code == 200 or var_response.status_code == 201:
                print(var_response.text)
            else:
                print(var_response.text)
                raise
        except Exception as exception:
            print("Erro ao subir informações para a API: " + exception.__str__())
            raise
