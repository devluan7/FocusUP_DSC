    import requests
    import json
    from datetime import date
    from dataclasses import dataclass, asdict
    from typing import List, Optional, Literal, Dict, Any
    import sys
    import subprocess

    # --- Importação e inicialização do Colorama ---
    try: # <-- CORRIGIDO AQUI (removido o '')
        from colorama import Fore, Style, init
        init(autoreset=True)
    except ImportError:
        print("Biblioteca 'colorama' não encontrada. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            from colorama import Fore, Style, init
            init(autoreset=True)
        except Exception as e:
            print(f"Não foi possível instalar 'colorama': {e}. Continuando sem cores.")
            class DummyColor:
                def __getattr__(self, name): return ""
            Fore = DummyColor()
            Style = DummyColor()


    # --- 1. Estrutura de Dados (Para um código limpo) ---

    @dataclass
    class TarefaSugerida:
        """Representa uma tarefa (ou jornada) gerada pela IA."""
        id: Optional[int]
        titulo: str
        descricao_motivacional: str
        dificuldade: Literal["facil", "medio", "dificil"]
        xp_sugerido: int

    # --- 2. O Motor Principal da IA (Versão Simplificada) ---

    class FocusAIEngine:
        """Motor de IA de 2 estágios (Análise e Geração)."""
        def __init__(self, model="llama3", timeout=120):
            self.api_url = "http://localhost:11434/api/generate"
            self.model = model
            self.timeout = timeout
            print(Fore.GREEN + f"[FocusAIEngine] Motor de IA inicializado com o modelo {self.model}.")

        def _chamar_ollama(self, prompt: str) -> Dict[str, Any]:
            """Função interna para lidar com a chamada da API e erros."""
            payload = {"model": self.model, "prompt": prompt, "format": "json", "stream": False}
            try:
                response = requests.post(self.api_url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                return json.loads(response.json()['response'])
            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Não foi possível conectar ao Ollama em {self.api_url}.")
            except json.JSONDecodeError:
                raise ValueError("A IA retornou dados mal formatados.")

        def _analisar_contexto(self, perfil_usuario: dict, historico_tarefas: List[dict]) -> str:
            """ESTÁGIO 1: A "Análise Interna" da IA."""
            prompt = f"""
            Você é um coach de produtividade e psicologia. Faça uma ANÁLISE INTERNA (JSON) do usuário.
            PERFIL: {json.dumps(perfil_usuario)}
            HISTÓRICO: {json.dumps(historico_tarefas)}

            Sua análise JSON deve ter as chaves: "objetivo_real", "maior_bloqueio", "estrategia".
            (Ex: "objetivo_real": "Ele quer se sentir no controle, não sobrecarregado pela bagunça.")
            (Ex: "maior_bloqueio": "Cansaço no fim do dia e não saber por onde começar.")
            (Ex: "estrategia": "Sugerir uma 'micro-tarefa' de 10 minutos para criar um sentimento de vitória rápida.")

            Retorne APENAS o objeto JSON da sua análise.
            """
            try:
                print(Fore.BLUE + "[FocusAIEngine] Estágio 1: Analisando perfil do usuário...")
                analise_json = self._chamar_ollama(prompt)
                print(Fore.BLUE + "[FocusAIEngine] Estágio 1: Análise concluída.")
                return json.dumps(analise_json)
            except Exception as e:
                return json.dumps({"erro": f"Falha na análise: {e}"})

        # ALTERAÇÃO CRÍTICA: Esta função agora entende "jornada"
        def gerar_tarefas(self,
                        perfil_usuario: dict,
                        tipo_tarefa: Literal["diaria", "semanal", "jornada"],
                        historico_tarefas: List[dict] = [],
                        titulos_excluidos: List[str] = []) -> List[TarefaSugerida]:
            """ESTÁGIO 2: Geração de Tarefas para o Usuário."""

            analise_interna = self._analisar_contexto(perfil_usuario, historico_tarefas)

            if tipo_tarefa == 'diaria':
                instrucao_tipo = "Sugira 3 MISSÕES DIÁRIAS (curtas, objetivas)."
                num_sugestoes = 3
            elif tipo_tarefa == 'semanal':
                instrucao_tipo = "Sugira 3 MISSÕES SEMANAIS (projetos médios)."
                num_sugestoes = 3
            else: # jornada
                instrucao_tipo = "Sugira UMA (1) 'JORNADA' ÉPICA de longa duração (ex: 15 dias). Ela deve ter de 3 a 5 etapas claras que se conectam."
                num_sugestoes = 1 # Gera apenas UMA jornada

            prompt_geracao = f"""
            Você é o "FocusBuddy", um "Mestre de Jogo" (Game Master) amigável e criativo. Sua tarefa é criar {num_sugestoes} "Missões" (tarefas) para o jogador.

            REGRA PRINCIPAL: ESTRUTURA DA MISSÃO
            1. "titulo" (O NOME DA MISSÃO):
            - DEVE ser um nome de missão curto, criativo e "legal" (Ex: "O Arquiteto de Dados", "Operação Tempestade no Quarto").
            2. "descricao_motivacional" (A DESCRIÇÃO DA MISSÃO):
            - DEVE ser a tarefa acionável e clara.
            - DEVE incluir o "porquê" que liga a tarefa ao objetivo do perfil.
            - Se for uma JORNADA, a descrição DEVE conter as 3-5 etapas (Ex: "Etapa 1: ...\\nEtapa 2: ...").

            ANÁLISE INTERNA (Seu guia estratégico, não mostre ao usuário):
            {analise_interna}

            INSTRUÇÕES DE GERAÇÃO:
            1. Baseie-se 100% na "ANÁLISE INTERNA" para definir as tarefas.
            2. {instrucao_tipo}
            3. O foco do usuário é "{perfil_usuario.get('foco_nome', 'geral')}".
            4. NÃO sugira nenhuma missão da lista de "Títulos a Excluir".
            5. LINGUAGEM: Use português simples, amigável e acessível.
            6. REVISÃO: Verifique a ortografia (Ex: 'séries', não 'sereias').

            Títulos a Excluir: {json.dumps(titulos_excluidos)}

            Retorne APENAS um objeto JSON com a chave "sugestoes", contendo
            uma lista de {num_sugestoes} missões. Cada missão deve ter as chaves:
            - "id": null (para tarefas novas)
            - "titulo": O NOME CRIATIVO DA MISSÃO.
            - "descricao_motivacional": A DESCRIÇÃO ACIONÁVEL + O "PORQUÊ". (Para Jornadas, inclua as etapas aqui).
            - "dificuldade": "facil", "medio", ou "dificil". (Para Jornadas, é a dificuldade TOTAL).
            - "xp_sugerido": Um número (Diárias: 10-25; Semanais: 50-100; Jornadas: 200-500).
            """

            try:
                print(Fore.BLUE + f"[FocusAIEngine] Estágio 2: Gerando {tipo_tarefa}...")
                resposta_json = self._chamar_ollama(prompt_geracao)

                tarefas_sugeridas = []
                for tarefa_data in resposta_json.get("sugestoes", []):
                    tarefas_sugeridas.append(
                        TarefaSugerida(
                            id=tarefa_data.get("id"),
                            titulo=tarefa_data.get("titulo", "Missão Inválida"),
                            descricao_motivacional=tarefa_data.get("descricao_motivacional", "Descrição indisponível."),
                            dificuldade=tarefa_data.get("dificuldade", "facil"),
                            xp_sugerido=tarefa_data.get("xp_sugerido", 10)
                        )
                    )
                print(Fore.GREEN + f"[FocusAIEngine] Estágio 2: {tipo_tarefa.capitalize()} gerada(s) com sucesso.")
                return tarefas_sugeridas
            except Exception as e:
                print(Fore.RED + f"Erro no Estágio 2 (Geração): {e}")
                return []

    # --- 3. NOSSA SIMULAÇÃO DE TERMINAL (O Fluxo Interativo) ---

    FOCOS_DISPONIVEIS = {
        "1": "academia", "2": "estudos", "3": "trabalho",
        "4": "saude", "5": "casa", "6": "lazer"
    }

    PERFIS_DE_FOCO = {
        "academia": {
            "foco_nome": "academia",
            "descricao_curta": "Treino focado em hipertrofia e definição.",
            "detalhes": "Idade: 21, Peso: 63kg, Nível: Iniciante/Intermediário, Objetivo: definição muscular, Frequência: 3x/semana."
        },
        "estudos": {
            "foco_nome": "estudos",
            "descricao_curta": "Estudante de Ciência da Computação.",
            "detalhes": "3º semestre. Dificuldades: Cálculo e Estrutura de Dados. Objetivo: Passar e montar portfólio no GitHub."
        },
        "trabalho": {
            "foco_nome": "trabalho",
            "descricao_curta": "Desenvolvedor Jr. em uma startup.",
            "detalhes": "Dev Python Jr. remoto. Desafio: organização e procrastinação. Objetivo: entregar no prazo."
        },
        "saude": {
            "foco_nome": "saude",
            "descricao_curta": "Melhorar o bem-estar geral e o sono.",
            "detalhes": "Objetivo: reduzir estresse, melhorar sono. Problemas: ansiedade, dorme tarde. Interesses: meditação, menos tela."
        },
        "casa": {
            "foco_nome": "casa",
            "descricao_curta": "Manter o apartamento organizado.",
            "detalhes": "Mora sozinho, home office. Problema: louça acumula, mesa bagunçada. Objetivo: criar rotina de limpeza leve."
        },
        "lazer": {
            "foco_nome": "lazer",
            "descricao_curta": "Encontrar tempo para hobbies e relaxar.",
            "detalhes": "Interesses: RPGs, violão, ficção científica. Problema: 'só trabalha e estuda'. Objetivo: reservar tempo para hobbies."
        }
    }

    MINHAS_TAREFAS = [
        {"id": 10, "titulo": "Operação Hidratação", "tipo": "diaria", "data_criacao": date(2025, 10, 14)},
    ]

    def ver_minhas_tarefas():
        print(Style.BRIGHT + Fore.CYAN + "\n--- MINHAS MISSÕES ATIVAS ---")
        if not MINHAS_TAREFAS:
            print(Fore.YELLOW + "Você ainda não tem missões ativas.")
            return

        hoje = date.today()
        for tarefa in MINHAS_TAREFAS:
            info_extra = f"({tarefa.get('tipo', 'desconhecido')})"
            data_tarefa = tarefa.get('data_criacao')

            if tarefa.get('tipo') == 'jornada':
                info_extra = Fore.YELLOW + Style.BRIGHT + "(JORNADA ÉPICA)"
            elif isinstance(data_tarefa, date) and tarefa.get('tipo') == 'diaria' and data_tarefa < hoje:
                info_extra += Fore.GREEN + " (Missão diária reiniciada para hoje!)"

            print(f"- {tarefa.get('titulo', 'Missão sem nome')} {Style.NORMAL}{Fore.CYAN}{info_extra}")
        print(Style.BRIGHT + Fore.CYAN + "----------------------------\n")

    # ALTERAÇÃO CRÍTICA: Fluxo principal dividido para lidar com Jornadas vs. Missões
    def iniciar_geracao_tarefa(engine: FocusAIEngine):
        print(Style.BRIGHT + Fore.CYAN + "\n--- GERAR NOVA MISSÃO ---")

        # 1. Escolher Foco
        print(Fore.YELLOW + "1. Por favor, selecione seu foco:")
        for key, focus_name in FOCOS_DISPONIVEIS.items():
            descricao = PERFIS_DE_FOCO[focus_name].get('descricao_curta', '')
            print(f"  {key}. {focus_name.capitalize()} " + Style.NORMAL + Fore.WHITE + f"({descricao})")

        foco_escolhido_nome = ""
        perfil_ativo = {}
        while not foco_escolhido_nome:
            escolha = input(Fore.YELLOW + "Digite o número do foco: ")
            if escolha in FOCOS_DISPONIVEIS:
                foco_escolhido_nome = FOCOS_DISPONIVEIS[escolha]
                perfil_ativo = PERFIS_DE_FOCO[foco_escolhido_nome]
            else:
                print(Fore.RED + "Opção inválida.")

        # 2. Escolher Tipo (com a nova opção de Jornada)
        tipo_texto = ""
        while not tipo_texto:
            tipo_escolha = input(Fore.YELLOW + "2. Gerar missão [1] Diária, [2] Semanal ou [3] Jornada (Épica)? ")
            if tipo_escolha == "1": tipo_texto = "diaria"
            elif tipo_escolha == "2": tipo_texto = "semanal"
            elif tipo_escolha == "3": tipo_texto = "jornada"
            else: print(Fore.RED + "Opção inválida.")

        historico_serializavel = []
        for tarefa in MINHAS_TAREFAS:
            tarefa_copia = tarefa.copy()
            if 'data_criacao' in tarefa_copia and isinstance(tarefa_copia['data_criacao'], date):
                tarefa_copia['data_criacao'] = tarefa_copia['data_criacao'].isoformat()
            historico_serializavel.append(tarefa_copia)

        # --- NOVO FLUXO PARA JORNADA ---
        if tipo_texto == "jornada":
            # Verifica se já existe uma jornada ativa
            if any(t.get('tipo') == 'jornada' for t in MINHAS_TAREFAS):
                print(Fore.RED + Style.BRIGHT + "\nVocê já tem uma Jornada Épica ativa! Conclua-a primeiro antes de gerar uma nova.")
                return

            print(Fore.BLUE + f"\nBuscando uma Jornada Épica para o perfil '{foco_escolhido_nome}'...")
            sugestoes: List[TarefaSugerida] = engine.gerar_tarefas(
                perfil_usuario=perfil_ativo,
                tipo_tarefa=tipo_texto,
                historico_tarefas=historico_serializavel,
                titulos_excluidos=[]
            )

            if not sugestoes:
                print(Fore.RED + "A IA não conseguiu gerar uma Jornada desta vez. Tente novamente.")
                return

            jornada = sugestoes[0] # Pega a única jornada sugerida

            print(Fore.YELLOW + Style.BRIGHT + "\nA IA SUGERIU A SEGUINTE JORNADA ÉPICA:")
            print(Fore.MAGENTA + f"\n  Título: " + Style.BRIGHT + f"{jornada.titulo}")
            print(Fore.WHITE + f"\n  Descrição e Etapas:\n    {jornada.descricao_motivacional.replace('\n', '\n    ')}")
            print(Fore.YELLOW + f"\n  (Dificuldade: {jornada.dificuldade} | Recompensa Total: {jornada.xp_sugerido} XP)")

            while True:
                escolha_user = input(Fore.YELLOW + "\nAceitar esta Jornada? [s]im ou [n]ão: ").lower()
                if escolha_user == 's':
                    nova_tarefa = asdict(jornada)
                    nova_tarefa["tipo"] = tipo_texto
                    nova_tarefa["data_criacao"] = date.today()
                    MINHAS_TAREFAS.append(nova_tarefa)
                    print(Fore.GREEN + f"\nJornada '{nova_tarefa.get('titulo')}' aceita! Boa sorte!")
                    return
                elif escolha_user == 'n':
                    print(Fore.WHITE + "Jornada recusada. Voltando ao menu principal.")
                    return
                else:
                    print(Fore.RED + "Entrada inválida.")

        # --- FLUXO ANTIGO (Diária/Semanal) ---
        else:
            titulos_ja_vistos_nesta_sessao = []
            while True:
                titulos_em_minhas_tarefas = [t.get('titulo') for t in MINHAS_TAREFAS if t.get('titulo')]
                titulos_para_excluir = list(set(titulos_em_minhas_tarefas + titulos_ja_vistos_nesta_sessao))

                print(Fore.BLUE + f"\nBuscando {tipo_texto} para o perfil '{foco_escolhido_nome}'...")
                sugestoes: List[TarefaSugerida] = engine.gerar_tarefas(
                    perfil_usuario=perfil_ativo,
                    tipo_tarefa=tipo_texto,
                    historico_tarefas=historico_serializavel,
                    titulos_excluidos=titulos_para_excluir
                )

                if not sugestoes:
                    print(Fore.RED + "A IA não conseguiu gerar sugestões desta vez. Tente novamente.")
                    return

                for s in sugestoes:
                    if s.titulo:
                        titulos_ja_vistos_nesta_sessao.append(s.titulo)

                while sugestoes:
                    print(Fore.YELLOW + "\nA IA sugeriu as seguintes missões:")
                    for i, tarefa in enumerate(sugestoes):
                        print(Fore.MAGENTA + f"\n  {i + 1}: " + Style.BRIGHT + f"{tarefa.titulo}")
                        print(Fore.WHITE + f"    {tarefa.descricao_motivacional}")
                        print(Fore.YELLOW + f"    (Dificuldade: {tarefa.dificuldade} | XP: {tarefa.xp_sugerido})")

                    print(Style.BRIGHT + Fore.CYAN + "\nOpções:")
                    print("  - Digite o número de uma missão para adicioná-la.")
                    print("  - Digite [g] para gerar novas missões.")
                    print("  - Digite [s] para sair e voltar ao menu.")

                    escolha_user = input(Fore.YELLOW + "O que deseja fazer? ").lower()

                    if escolha_user == 's': return
                    if escolha_user == 'g': break

                    try:
                        escolha_num = int(escolha_user)
                        if 1 <= escolha_num <= len(sugestoes):
                            tarefa_escolhida = sugestoes.pop(escolha_num - 1)

                            nova_tarefa = asdict(tarefa_escolhida)
                            nova_tarefa["tipo"] = tipo_texto
                            nova_tarefa["data_criacao"] = date.today()

                            MINHAS_TAREFAS.append(nova_tarefa)
                            print(Fore.GREEN + f"\nMissão '{nova_tarefa.get('titulo')}' adicionada com sucesso!")
                        else: print(Fore.RED + "Número fora do intervalo.")
                    except ValueError: print(Fore.RED + "Entrada inválida.")

                if not sugestoes:
                    print(Fore.GREEN + "\nTodas as sugestões foram adicionadas!")
                    break

    # --- PONTO DE ENTRADA DA SIMULAÇÃO ---
    if __name__ == "__main__":

        # Inicializa o motor de IA uma única vez
        try:
            engine = FocusAIEngine()
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"ERRO CRÍTICO: Não foi possível inicializar o motor de IA.")
            print(Fore.RED + f"Detalhe: {e}")
            print(Fore.YELLOW + "Por favor, verifique se o Ollama está em execução e tente novamente.")
            exit()

        print(Style.BRIGHT + Fore.GREEN + "\nBem-vindo ao FocusUP (Simulação de Terminal v2.5 - Modo Jornada!)")

        while True:
            print(Style.BRIGHT + Fore.CYAN + "\n--- MENU PRINCIPAL ---")
            print("1. Ver Minhas Missões")
            print("2. Gerar Nova Missão com IA")
            print("3. Sair")
            escolha_menu = input(Fore.YELLOW + "O que você deseja fazer? ")

            if escolha_menu == "1":
                ver_minhas_tarefas()
            elif escolha_menu == "2":
                try:
                    iniciar_geracao_tarefa(engine)
                except Exception as e:
                    print(Fore.RED + Style.BRIGHT + f"\nOcorreu um erro inesperado durante a geração:")
                    print(Fore.RED + f"{e}")
                    print(Fore.YELLOW + "Retornando ao menu principal.")
            elif escolha_menu == "3":
                print(Fore.GREEN + "Até a próxima!"); break
            else:
                print(Fore.RED + "Opção inválida.")