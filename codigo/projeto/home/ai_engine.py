# home/ai_engine.py

import requests
import json
from dataclasses import dataclass
from typing import List, Optional, Literal, Dict, Any
import logging
import time

logger = logging.getLogger(__name__)

# --- NOSSO SISTEMA DE XP ---
XP_POR_DIFICULDADE = {
    "facil": 10,
    "medio": 25,
    "dificil": 50,
    "hiperdificil": 100
}
DIFICULDADES_VALIDAS = ["facil", "medio", "dificil"] 
# ------------------------------------

@dataclass
class TarefaSugerida:
    titulo: str
    descricao_motivacional: str
    dificuldade: Literal["facil", "medio", "dificil", "hiperdificil"]
    xp_calculado: int 

class FocusAIEngine:
    def __init__(self, model="llama3", timeout=180, max_retries=2):
        self.api_url = "http://localhost:11434/api/generate"
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        logger.info(f"[FocusAIEngine] Motor de IA: modelo={self.model}, timeout={self.timeout}s, retries={self.max_retries}.")

    def _chamar_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        # (Função _chamar_ollama com retentativas - SEM MUDANÇAS)
        payload = {"model": self.model, "prompt": prompt, "format": "json", "stream": False}
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    wait_time = 1.5 ** attempt
                    logger.warning(f"[FocusAIEngine] Tentativa {attempt + 1}/{self.max_retries + 1}...")
                    time.sleep(wait_time)
                logger.debug(f"[FocusAIEngine] Chamando Ollama (tentativa {attempt + 1})...")
                response = requests.post(self.api_url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                response_data = response.json()
                if 'response' in response_data:
                     try:
                         json_interno = json.loads(response_data['response'])
                         logger.debug(f"[FocusAIEngine] Ollama retornou JSON válido.")
                         return json_interno
                     except json.JSONDecodeError as json_err:
                         logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Erro JSON: {json_err}")
                         logger.error(f"[FocusAIEngine] Resposta (string): {response_data['response']}")
                         last_exception = json_err
                else:
                    logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Chave 'response' não encontrada.")
                    last_exception = ValueError("Chave 'response' não encontrada")
            except Exception as e:
                logger.error(f"[FocusAIEngine] Tentativa {attempt + 1}: Erro Inesperado: {e}")
                last_exception = e
        logger.error(f"[FocusAIEngine] Todas as {self.max_retries + 1} tentativas falharam.")
        if last_exception: logger.error(f"[FocusAIEngine] Último erro: {type(last_exception).__name__}: {last_exception}")
        return None

    # --- FUNÇÃO ATUALIZADA ---
    def gerar_sugestao_tarefa_diaria(self, perfil_usuario: dict) -> Optional[TarefaSugerida]:
        
        instrucao_tipo = "Sugira UMA (1) MISSÃO DIÁRIA."
        num_sugestoes = 1
        
        # Pega o dia da semana (ex: "terça-feira")
        dia_da_semana = perfil_usuario.get("dia_da_semana", "hoje")
        
        # === PROMPT ATUALIZADO (FOCO EM GAMIFICAÇÃO E VARIEDADE) ===
        prompt_geracao = f"""
        Você é o "FocusBuddy", um Mestre de Jogo (Game Master) criativo e encorajador. Sua missão é criar {num_sugestoes} "Missão Diária" (tarefa) para o jogador.

        **REGRA DE OURO: VARIEDADE TOTAL E AÇÕES CONCRETAS!**
        * **NÃO** se prenda a exemplos. Seja criativo.
        * **NÃO** use sempre as mesmas frases de início (Ex: "Que tal começar por..."). Varie!
        * **NÃO** sugira tarefas vagas (Ex: "Organize-se").
        * **SUGIRA AÇÕES** claras, com começo, meio e fim (Ex: "Escreva o rascunho do email X", "Complete a Lição Y", "Faça 3 séries de agachamento").
        * **CONTEXTO SUTIL:** Hoje é **{dia_da_semana.capitalize()}**. Use isso *apenas se* fizer sentido (Ex: "Comece a semana (segunda-feira)..." ou "Relaxe nesta sexta..."), mas NÃO mencione o dia da semana em todas as tarefas.

        **PERFIL DO USUÁRIO (Sua fonte de ideias):**
        {json.dumps(perfil_usuario, ensure_ascii=False, indent=2)}

        **INSTRUÇÕES DE GERAÇÃO:**
        1.  Baseie-se 100% no Perfil do Usuário. Use o `foco_nome` e os `dados_especificos` para criar uma tarefa RELEVANTE.
            * **Ex (Academia):** Se o `objetivo_academia` é 'Me definir', sugira uma ação: "Complete sua sessão de cardio de hoje (20 min na esteira)".
            * **Ex (Estudos):** Se `area_estudo` é 'Programação', sugira: "Resolva um desafio de algoritmo hoje."
            * **Ex (Casa):** Se `tarefa_principal_casa` é 'Organização', sugira: "Organize a gaveta de talheres da cozinha."
        2.  **"titulo"**: Crie um nome de "Missão" curto e gamificado (Ex: "O Código do Mestre", "Fortalecendo o Core", "Hidratação Nível 1", "Checkmate de Emails").
        3.  **"descricao_motivacional"**: Dê a ação concreta e uma frase motivacional curta. (Ex: "Hora de focar no seu código. Complete o módulo de 'loops' do seu curso de Python.").
        4.  **"dificuldade"**: Classifique a ação como "facil" (< 10min), "medio" (15-30min), ou "dificil" (> 30min).

        **Retorne APENAS um objeto JSON com a chave "sugestoes"**, contendo uma lista com {num_sugestoes} missão(ões).
        Cada missão DEVE ter as chaves **"titulo"** (em português), **"descricao_motivacional"** (em português), e **"dificuldade"**.
        """
        # === FIM DO NOVO PROMPT ===

        try:
            logger.info(f"[FocusAIEngine] Gerando sugestão diária para foco '{perfil_usuario.get('foco_nome', 'N/A')}' (Dia: {dia_da_semana})...")
            resposta_json = self._chamar_ollama(prompt_geracao)

            if not resposta_json or "sugestoes" not in resposta_json or not isinstance(resposta_json["sugestoes"], list) or not resposta_json["sugestoes"]:
                logger.warning("[FocusAIEngine] IA não retornou sugestões válidas.")
                return None

            tarefa_data = resposta_json["sugestoes"][0]
            
            # === CORREÇÃO "title" vs "titulo" (Robusta) ===
            # Tenta várias chaves comuns, priorizando português
            titulo = (tarefa_data.get("titulo") or 
                      tarefa_data.get("title") or 
                      tarefa_data.get("Título") or 
                      tarefa_data.get("Titulo"))
            
            desc = (tarefa_data.get("descricao_motivacional") or 
                    tarefa_data.get("description_motivacional") or 
                    tarefa_data.get("descrição_motivacional") or 
                    tarefa_data.get("descricao"))
            # ============================================

            diff = tarefa_data.get("dificuldade", "facil").lower() # Pega e normaliza

            if not titulo or not isinstance(titulo, str) or not desc or not isinstance(desc, str):
                 logger.error(f"[FocusAIEngine] IA retornou dados incompletos (após fallback): {tarefa_data}")
                 return None
            
            # Garante que dificuldade seja uma das válidas
            if diff not in DIFICULDADES_VALIDAS:
                logger.warning(f"[FocusAIEngine] Dificuldade inválida '{diff}', usando 'facil'.")
                diff = "facil" 

            # Calcula o XP usando o mapeamento (10, 25, 50)
            xp_calculado = XP_POR_DIFICULDADE.get(diff, 10) # Usa 10 como fallback

            sugestao = TarefaSugerida(titulo=titulo, descricao_motivacional=desc, dificuldade=diff, xp_calculado=xp_calculado)
            logger.info(f"[FocusAIEngine] Sugestão gerada: '{sugestao.titulo}' (Dificuldade: {diff}, XP: {xp_calculado})")
            return sugestao

        except Exception as e:
            logger.exception(f"[FocusAIEngine] Erro na geração:")
            return None