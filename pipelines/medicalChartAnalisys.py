from typing import List, Union, Generator, Iterator
import os
import asyncio
import httpx
import pandas as pd
from sqlalchemy import create_engine, text
import re

class Pipeline:
    def __init__(self):
        self.name = "Analisar Prontuários Médicos"
        self.db_engine = None
        self.ollama_base_url = "http://ollama:11434"
        print(f"__init__: {self.name} inicializado.")

    async def on_startup(self):
        print(f"on_startup: {self.name} - Conectando ao PostgreSQL...")
        
        user = os.getenv("POSTGRES_USER", "default_user")
        password = os.getenv("POSTGRES_PASSWORD", "default_pass")
        db_name = os.getenv("POSTGRES_DB", "default_db")
        host = "postgres"
        conn_str = f"postgresql://{user}:{password}@{host}:5432/{db_name}"

        retries = 5
        while retries > 0:
            try:
                self.db_engine = create_engine(conn_str)
                connection = self.db_engine.connect()
                connection.close()
                print("✅ Conexão com o PostgreSQL estabelecida!")
                return
            except Exception as e:
                print(f"🔴 Erro ao conectar: {e}")
                retries -= 1
                self.db_engine = None
                print(f"Tentativas restantes: {retries}. Aguardando 5 segundos...")
                await asyncio.sleep(5)
        
        print("🔴 Falha na conexão com o banco após várias tentativas.")

    async def on_shutdown(self):
        if self.db_engine:
            self.db_engine.dispose()
            print("on_shutdown: Conexão fechada.")

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        
        if not self.db_engine:
            return "❌ Erro: Conexão com banco indisponível."

        nome_paciente = self._extrair_nome_paciente(user_message)
        
        if not nome_paciente:
            return """
 **Sistema de Análise de Prontuários**

Para consultar um paciente, use um dos formatos:
• "Analisar paciente João Silva"
• "Buscar Maria Santos"  
• "Prontuário de Pedro Costa"
• "Consultar Ana Oliveira"

 O sistema buscará o paciente no banco e gerará uma análise médica completa.
            """.strip()

        try:
            paciente_info = self._buscar_paciente(nome_paciente)
            
            if not paciente_info:
                return f"❌ Paciente '{nome_paciente}' não encontrado no sistema.\n\n💡 Verifique a grafia do nome e tente novamente."

            print(f"✅ Paciente encontrado: {paciente_info['nome']}. Gerando análise...")

            return self._gerar_analise_medica( paciente_info, model_id)
                
        except Exception as e:
            print(f"🔴 Erro no pipeline: {e}")
            return f"❌ Erro interno: {str(e)}"

    def _extrair_nome_paciente(self, mensagem: str) -> str:
        mensagem = mensagem.lower().strip()
        
        padroes = [
            r'analisar\s+paciente\s+(.+)',
            r'buscar\s+(.+)',
            r'prontuário\s+(?:de\s+|do\s+)?(.+)',
            r'consultar\s+(.+)',
            r'paciente\s+(.+)',
            r'análise\s+(?:de\s+|do\s+)?(.+)'
        ]
        
        for padrao in padroes:
            match = re.search(padrao, mensagem)
            if match:
                nome = match.group(1).strip()
                nome = re.sub(r'\b(por favor|pfv|obrigado|obrigada)\b', '', nome).strip()
                return nome.title()
            
        return ""

    def _buscar_paciente(self, nome: str) -> dict:
        try:
            query =  text("""
                            SELECT 
                                prontuario, nome, especialidade, data, comorbidade,
                                medicacao, mac, eco_endo, polipo, mioma,
                                gravidez, parto, aborto
                            FROM pacientes 
                            WHERE LOWER(nome) LIKE LOWER(:nome_busca)
                            ORDER BY 
                                CASE WHEN LOWER(nome) = LOWER(:nome_exato) THEN 1 ELSE 2 END,
                                nome
                            LIMIT 1
                        """)
                    
            with self.db_engine.connect() as conn:
                result = conn.execute(query, {
                    'nome_busca': f'%{nome}%',
                    'nome_exato': nome
                })
                row = result.fetchone()
                
                if row:
                    colunas = result.keys()
                    return dict(zip(colunas, row))
                    
        except Exception as e:
            print(f"🔴 Erro na busca: {e}")
            
        return None

    def _gerar_analise_medica(self, paciente: dict, model_id: str) -> str:
        prompt = f"""
Você é um assistente médico especializado em análise de prontuários. Analise as informações do paciente abaixo e forneça uma avaliação médica estruturada.

**INFORMAÇÕES DO PACIENTE:**
Nome: {paciente.get('nome', 'N/A')}
Especialidade: {paciente.get('especialidade', 'N/A')}
Data: {paciente.get('data', 'Não informado')}
Comorbidade: {paciente.get('comorbidade', 'Nenhum')}
Medicação: {paciente.get('medicacao', 'Nenhuma conhecida')}
MAC (Método Anticoncepcional): {paciente.get('mac', 'Não relatados')}
Exame Eco/Endo: {paciente.get('eco_endo', 'Nenhum')}
Pólipo: {paciente.get('polipo', 'Nenhuma')}
Mioma: {paciente.get('mioma', 'N/A')}
Gravidez: {paciente.get('gravidez', 'N/A')}
Parto: {paciente.get('parto', 'N/A')}
Aborto: {paciente.get('aborto', 'N/A')}


**SOLICITAÇÃO:**
Forneça uma análise médica estruturada seguindo este formato:

## RESUMO CLÍNICO
[Breve resumo da condição atual do paciente]

## PRINCIPAIS ACHADOS
[Pontos mais relevantes do histórico e sintomas]

## RECOMENDAÇÕES
[Sugestões de acompanhamento, exames ou cuidados]

## PONTOS DE ATENÇÃO
[Fatores que requerem monitoramento especial]

## CONSIDERAÇÕES FINAIS
[Determine se a pessoa precisa de um exame de histeroscopia ou outro procedimento baseado nas informações fornecidas]

**IMPORTANTE:** Esta é uma análise informativa baseada em IA. Sempre consulte um profissional de saúde qualificado para decisões médicas; HD SIGNIFICA HISTEROSCOPIA DIAGNOTICA, QUE É O TIPO DE EXAME QUE O PACIENTE SOLICITA.
        """
        
        return self._call_ollama(prompt, model_id)

    def _call_ollama(self, user_prompt: str, model_id: str) -> str:
            system_prompt = """Você é um assistente médico especializado em análise de prontuários. 
    Forneça análises médicas estruturadas, precisas e baseadas em evidências. 
    Sempre inclua avisos sobre a necessidade de consulta médica profissional.
    Mantenha um tom profissional e científico."""

            print("--- PIPE: Enviando payload de chat para o Ollama ---")
            
            ollama_payload = {
                "model": 'medgemma', 
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9
                }
            }

            try:
                print("--- PIPE: Aguardando resposta do Ollama (timeout de 5 minutos)... ---")
                response = httpx.post(
                    f"{self.ollama_base_url}/api/chat",
                    json=ollama_payload,
                    timeout=300.0
                )
                response.raise_for_status()
                response_data = response.json()
                
                if "message" in response_data and "content" in response_data["message"]:
                    print("✅ Resposta recebida do Ollama com sucesso!")
                    return response_data["message"]["content"].strip()
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