from typing import List, Union, Generator, Iterator
import base64
import json
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import ollama
import httpx
import os
import numpy as np

print("🔧 Usando apenas PIL para processamento de imagens")

class Pipeline:

    def __init__(self):
        self.name = "Analisar Imagens"
        self.ollama_base_url = "http://ollama:11434"
        print(f"__init__: {self.name} inicializado (PIL apenas)")
        
    async def on_startup(self):
        print(f"on_startup: {self.name}")

    async def on_shutdown(self):
        print('on_shutdown')

    def _extract_base64_from_url(self, base64_url: str) -> str:
        try:
            if ',' in base64_url:
                return base64_url.split(',', 1)[1]
            else:
                return base64_url
        except Exception as e:
            print(f"🔴 Erro ao extrair base64 da URL: {e}")
            return base64_url

    def _validate_base64_image(self, base64_string: str) -> bool:
        try:
            base64_clean = base64_string.strip().replace('\n', '').replace(' ', '')
            image_data = base64.b64decode(base64_clean)
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            
            image = Image.open(io.BytesIO(image_data))
            print(f"✅ Imagem válida encontrada - Formato: {image.format}, Tamanho: {image.size}")
            return True
            
        except Exception as e:
            print(f"🔴 Base64 inválido ou imagem corrompida: {e}")
            return False

    def _normalize_image(self, base64_string: str) -> str:
        try:
            print("🔄 Iniciando normalização com qualidade melhorada...")
            
            img_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(img_bytes))
            print(f"🔄 Imagem carregada: {image.size}, modo={image.mode}")
            

            if image.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')


            width, height = image.size
            max_size = 800 
            min_size = 400  
            

            if width > max_size or height > max_size:
                scale_factor = min(max_size/width, max_size/height)
                new_size = (int(width * scale_factor), int(height * scale_factor))

                image = image.resize(new_size, Image.Resampling.BICUBIC)
                print(f"🔄 Redimensionada para: {image.size}")
            elif width < min_size or height < min_size:
               
                scale_factor = min(2.0, max(min_size/width, min_size/height))  # Máximo 2.0x
                new_size = (int(width * scale_factor), int(height * scale_factor))
                image = image.resize(new_size, Image.Resampling.BICUBIC)
                print(f"🔄 Upscale para: {image.size}")


            original_mode = image.mode
            convert_to_grayscale = False
            

            img_array = np.array(image)
            estimated_size = len(base64_string) * 0.75 
            
            if estimated_size > 2000000: 
                if image.mode != 'L':
                    image = image.convert('L')
                    convert_to_grayscale = True
                    print("🔄 Convertida para escala de cinza (otimização de tamanho)")
            

            if image.mode == 'L':
                img_array = np.array(image)
                std_dev = np.std(img_array)
                mean_brightness = np.mean(img_array)
                
                if std_dev < 45:  
                    
                    if mean_brightness < 100:  
                        enhancer = ImageEnhance.Brightness(image)
                        image = enhancer.enhance(1.1)
                        print("🔄 Brilho aumentado levemente")
                    
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(1.3) 
                    print("🔄 Contraste melhorado")
            else:

                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.1)
                print("🔄 Contraste RGB ajustado")

            if convert_to_grayscale or np.std(np.array(image)) < 30:

                image = image.filter(ImageFilter.MedianFilter(size=3))
                print("🔄 Ruído reduzido")
            else:

                image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=2))
                print("🔄 Nitidez melhorada")


            buffer = io.BytesIO()
            

            if image.mode == 'L':
                
                image_rgb = Image.new('RGB', image.size)
                image_rgb.paste(image)
                image = image_rgb
                initial_quality = 85  
            else:
                initial_quality = 90  
            

            image.save(buffer, format='JPEG', quality=initial_quality, optimize=True, progressive=True)
            base64_processed = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            print(f"✅ Primeira tentativa: {len(base64_processed)} chars (JPEG {initial_quality}%)")
            

            if len(base64_processed) > 1800000:  
                print("🔄 Aplicando compressão adaptativa...")
                

                qualities = [80, 75, 70]
                for quality in qualities:
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG', quality=quality, optimize=True, progressive=True)
                    base64_processed = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    print(f"🔄 Testando qualidade {quality}%: {len(base64_processed)} chars")
                    
                    if len(base64_processed) <= 1600000:  
                        break
                
                print(f"🔄 Compressão final: {len(base64_processed)} chars (JPEG {quality}%)")
            
            return base64_processed

        except Exception as e:
            print(f"❌ Erro na normalização: {str(e)}")

            return base64_string

    async def inlet(self, body: dict, user: dict) -> dict:
        print("--- DEBUG: BODY RECEBIDO ---")
        print(json.dumps(body, indent=2, ensure_ascii=False))
        
        print("--- INLET: Processando arquivos para passar ao pipe ---")

        files_to_pass = []

        messages = body.get("messages", [])
        if messages:
            last_message = messages[-1] 
            content_list = last_message.get("content", [])

            for content_item in content_list:
                if content_item.get("type") == "image_url":
                    image_url_dict = content_item.get("image_url", {})
                    base64_url = image_url_dict.get("url")
                    
                    if base64_url:
                        try:
                            base64_clean = self._extract_base64_from_url(base64_url)
                            base64_normalized = self._normalize_image(base64_clean)
                            
                            if self._validate_base64_image(base64_normalized):
                                files_to_pass.append({
                                    "data": base64_url,
                                    "base64_clean": base64_normalized
                                })
                                print(f"✅ Imagem adicionada com sucesso (tamanho: {len(base64_normalized)} chars)")
                            else:
                                print("🔴 Imagem inválida descartada")
                        except Exception as e:
                            print(f"🔴 Erro ao processar imagem: {e}")

        if not files_to_pass:
            print("--- INLET: Nenhum arquivo encontrado em 'messages'. Tentando 'metadata.files'... ---")
            files_metadata = body.get("metadata", {}).get("files", [])
            if files_metadata:
                for file_meta in files_metadata:
                    file_data = file_meta.get("file", {})
                    if file_data:
                        data = file_data.get("data", "")
                        if data:
                            try:
                                base64_clean = self._extract_base64_from_url(data)
                                base64_normalized = self._normalize_image(base64_clean)
                                
                                if self._validate_base64_image(base64_normalized):
                                    files_to_pass.append({
                                        "data": data,
                                        "base64_clean": base64_normalized
                                    })
                            except Exception as e:
                                print(f"🔴 Erro ao processar arquivo de metadata: {e}")

        body['processed_files'] = files_to_pass
        print(f"--- INLET: {len(files_to_pass)} arquivos preparados no body. ---")
        return body

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:

        processed_files = body.get('processed_files', [])
        
        if processed_files:
            first_file = processed_files[0]
            base64_clean = first_file.get('base64_clean', '')
            
            if base64_clean:
                print(f"--- PIPE: Usando imagem do inlet (tamanho: {len(base64_clean)} chars) ---")
                return self._call_ollama(base64_clean, user_message)
        
        print("--- PIPE: Processando imagens diretamente das mensagens ---")
        
        messages = body.get("messages", [])
        if messages:
            last_message = messages[-1] 
            content_list = last_message.get("content", [])

            for content_item in content_list:
                if content_item.get("type") == "image_url":
                    image_url_dict = content_item.get("image_url", {})
                    base64_url = image_url_dict.get("url")
                    
                    if base64_url:
                        try:
                            base64_clean = self._extract_base64_from_url(base64_url)
                            base64_normalized = self._normalize_image(base64_clean)
                            
                            if self._validate_base64_image(base64_normalized):
                                print(f"--- PIPE: Imagem encontrada e validada (tamanho: {len(base64_normalized)} chars) ---")
                                return self._call_ollama(base64_normalized, user_message)
                            else:
                                print("🔴 PIPE: Imagem inválida encontrada")
                        except Exception as e:
                            print(f"🔴 PIPE: Erro ao processar imagem: {e}")

        print("--- PIPE: Nenhuma imagem válida encontrada para processar. ---")
        return "Nenhuma imagem foi encontrada ou todas as imagens estão corrompidas. Por favor, envie uma imagem válida."

    def _call_ollama(self, base64_string: str, user_message: str = "") -> str:
        print("--- PIPE: Chamando Ollama para análise de imagem ---")
        print(f"--- Base64 size: {len(base64_string)} characters ---")

        base_prompt = """Você é um assistente médico especializado em análise de imagens diagnósticas. Se baseia nas imagens para fornecer diagnósticos e recomendações médicas."""

        if user_message.strip():
            base_prompt += f"\n\nPERGUNTA ESPECÍFICA DO USUÁRIO: {user_message}"

        ollama_payload = {
            "model": 'gemma3:12b',
            "messages": [
                {
                    "role": "user",
                    "content": base_prompt,
                    "images": [base64_string]
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }

        try:
            print("--- PIPE: Aguardando resposta do Ollama (timeout de 5 minutos)... ---")
            response = httpx.post(
                f"{self.ollama_base_url}/api/chat",
                json=ollama_payload,
                timeout=400.0
            )
            response.raise_for_status()
            response_data = response.json()
            
            if "message" in response_data and "content" in response_data["message"]:
                content = response_data["message"]["content"].strip()
                print(f"✅ Resposta recebida do Ollama com sucesso! (tamanho: {len(content)} chars)")
                return content
            else:
                print(f"🔴 Resposta inesperada do Ollama: {response_data}")
                return "Ollama não retornou uma mensagem com conteúdo válido."
                    
        except httpx.RequestError as e:
            print(f"🔴 Erro de rede ao chamar Ollama: {e}")
            return "Erro de conexão com o serviço de análise."
        except httpx.HTTPStatusError as e:
            print(f"🔴 Erro HTTP do Ollama: {e.response.status_code} - {e.response.text}")
            return "Erro no serviço de análise (status HTTP)."
        except Exception as e:
            print(f"🔴 Erro inesperado ao chamar Ollama: {e}")
            return "Erro interno no serviço de análise."