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
        self.aws_access_key_id = arg_strAwsAccessKeyId
        self.aws_secret_access_key = arg_strAwsSecretAccessKey
        self.aws_region_name = arg_strAwsRegionName
        self.aws_service_name = arg_strAwsServiceName
        self.gpt_api_key = arg_strGptApiKey
        self.version_chatgpt = arg_strVersionChatGPT

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
            var_ImgPdf = convert_from_path(arg_strDocumento, dpi=300)

            for img in var_ImgPdf:
                byte_array = BytesIO()
                img.save(byte_array, format='PNG')
                imagem_base64 = base64.b64encode(byte_array.getvalue()).decode('utf-8')
            return imagem_base64
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
            with open(arg_strDocumento, 'rb') as file:
                img = Image.open(file)
                byte_array = BytesIO()
                img.save(byte_array, format='PNG')
                imagem_base64 = base64.b64encode(byte_array.getvalue()).decode('utf-8')
            return imagem_base64
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
            client = boto3.client(service_name=self.aws_service_name, region_name=self.aws_region_name, 
                                aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_secret_access_key)
            # Abre o arquivo PDF
            with open(arg_strDocumento, "rb") as file:
                var_pdfReader = PyPDF2.PdfFileReader(file)
                var_intTotalPages = var_pdfReader.numPages
                print(f"Número de páginas PDF: {var_intTotalPages}")
                var_strTextoExtraido = ""
                
                # Percorre sobre cada página do PDF
                for page_number in range(var_intTotalPages):
                    print(f"Extraindo texto da página: {page_number+1}")
                    # Extrai uma página especifica
                    var_pdfPage = var_pdfReader.getPage(page_number)
                    
                    # Cria um novo arquivo PDF temporário contendo apenas esta página
                    var_strCaminhoTempPDF = f"page_{page_number}.pdf"
                    var_pdfTempPDFWriter = PyPDF2.PdfFileWriter()
                    var_pdfTempPDFWriter.addPage(var_pdfPage)
                    
                    with open(var_strCaminhoTempPDF, "wb") as temp_pdf_file:
                        var_pdfTempPDFWriter.write(temp_pdf_file)
                    
                    # Extrai texto da página atual usando Textract
                    var_bytesDocumento = open(var_strCaminhoTempPDF, "rb").read()
                    var_dictResponse = client.detect_document_text(Document={'Bytes': var_bytesDocumento})
                    
                    # Concatena o texto extraido da página atual
                    for block in var_dictResponse['Blocks']:
                        if block['BlockType'] == 'LINE':
                            var_strTextoExtraido += block['Text'] + "\n"
                    
                    # Exclui o arquivo PDF temporário
                    os.remove(var_strCaminhoTempPDF)
            output_txt = "teste_txt.txt"
            with open(output_txt, "w", encoding="utf-8") as file:
                file.write(var_strTextoExtraido)
            return var_strTextoExtraido
        except Exception as exception:
                print(arg_strMensagemLog="Erro ao extrair texto do documento: " + exception.__str__())
                raise

    def reading_text(self, arg_strPromptChatGPT:str, arg_strTexto_documento:str, arg_intMaxTokens:int=350):
        """
        Realiza a leitura de texto usando o ChatGPT.

        Parâmetros:
        arg_strPromptChatGPT (str): Prompt para o modelo de chat.
        arg_strTexto_documento (str): Texto do documento.
        arg_intMaxTokens (int): Número máximo de tokens a serem gerados (padrão: 350).

        Retorna:
        tuple: Tupla contendo a resposta do modelo de ChatGPT, o número de tokens de prompt e o número de tokens de conclusão.
        """
        try:
            print("Realizando leitura do texto do documento")
            var_dictBody = {
                "model": self.version_chatgpt,
                "messages": [{"role": "user", "content": f"{arg_strPromptChatGPT}: {arg_strTexto_documento}"}],
                "max_tokens": arg_intMaxTokens,
                "temperature": 0.8,
            }
            var_dictHeaders = {"Authorization": f"Bearer {self.gpt_api_key}", "Content-Type": "application/json"}
            var_response = requests.post("https://api.openai.com/v1/chat/completions", headers=var_dictHeaders, data=json.dumps(var_dictBody))
            var_jsonResponse = var_response.json()
            
            var_strRespostaChatGPT = var_jsonResponse["choices"][0]["message"]["content"]
            var_intTokenPrompt = var_jsonResponse['usage']['prompt_tokens']
            var_intTokenCompletion = var_jsonResponse['usage']['completion_tokens']
            
            print("Resposta ChatGPT: ", var_strRespostaChatGPT)
            print("Token Prompt: ", var_intTokenPrompt)
            print("Token de Conclusão: ", var_intTokenCompletion)

            return var_strRespostaChatGPT, var_intTokenPrompt, var_intTokenCompletion
        
        except Exception as exception:
            print("Erro ao realizar leitura do texto do documento: " + exception.__str__())
            raise

    def verification(self, arg_strDocumento:str, arg_strRespostaChatGPT:str, arg_strLayout:str, arg_strTokenVerification:str, 
                     arg_strProject:str, arg_strStatus:str="unassigned", arg_strPriority:str="high"):
        """
        Realiza a verificação de um documento.

        Parâmetros:
        arg_strDocumento (str): Caminho para o documento.
        arg_strRespostaChatGPT (str): Resposta do ChatGPT.
        arg_strLayout (str): Layout do documento.
        arg_strTokenVerification (str): Token de autenticação da API T2Verification.
        arg_strProject (str): ID do projeto na API T2Verification.
        arg_strStatus (str): Status do documento (padrão: "unassigned").
        arg_strPriority (str): Prioridade do documento (padrão: "high") - Todas Opções: ('low', 'Baixa'), ('medium', 'Média'), ('high', 'Alta').

        Raises:
        Exception: Se houver um erro ao enviar informações para a API.
        """
        try:
            print("Iniciando Verification..")

            if ".PDF" in arg_strDocumento.upper():
                var_strBytesDocumento = self.pdf_para_base64(arg_strDocumento=arg_strDocumento)
            else:
                var_strBytesDocumento = self.imagem_para_base64(arg_strDocumento=arg_strDocumento)
            
            var_jsonRespostaChatGPT = json.loads(arg_strRespostaChatGPT)

            try: 
                var_dictRespostaTratada = {key: tuple(value.values())[0] for key, value in var_jsonRespostaChatGPT.items()}
                var_strResposta = json.dumps(var_dictRespostaTratada, ensure_ascii=False, indent=4)
            except: 
                var_strResposta = json.dumps(var_jsonRespostaChatGPT, ensure_ascii=False, indent=4)

            var_strUrl = "https://api.t2verification.com.br/api/tasks/"
            var_dictBody = {
                "project": arg_strProject, # ID do Projeto no Verification
                "t2layout": arg_strLayout, # Nome do Layout do Documento no Verification
                "t2priority": arg_strPriority, # Prioridade do Documento
                "t2document": f"{var_strBytesDocumento}", # Documento em Bytes que será renderizado no Portal
                "t2status": arg_strStatus, # Status do Documento
                "t2verification": f"{var_strResposta}" # Informações do Documento
            }

            var_dictHeaders = {
                "Authorization": f"Bearer {arg_strTokenVerification}",
                "Content-Type": "application/json"
            }

            var_response = requests.post(var_strUrl, json=var_dictBody, headers=var_dictHeaders)

            if var_response.status_code == 200 or var_response.status_code == 201:
                print(var_response.text)
            else:
                print(var_response.text)
                raise
        except Exception as exception:
            print("Erro ao subir informações para a API: " + exception.__str__())
            raise
