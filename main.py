# main.py: CÓDIGO CONSOLIDADO PARA REPLIT

import os
import json
import time
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

# --- 1. VARIÁVEIS DE CONFIGURAÇÃO (CÉLULA 1) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
client = genai.Client(api_key=GEMINI_API_KEY) 
MODEL_NAME = "gemini-2.5-flash"

# --- 2. FUNÇÕES DE MOCK (CÉLULA 2) ---

def registrarLead(nome: str, email: str, empresa: str, interesse_confirmado: bool, necessidade: str = ""):
    card_id = f"SIMULADO_{nome.replace(' ', '')}_{email.split('@')[0]}_{int(time.time())}" 
    print(f" INTERNO PIPEFY: Card criado: {card_id}")
    return json.dumps({
        "status": "SUCCESS",
        "card_id": card_id,
        "message": f"SIMULAÇÃO: Lead {card_id} registrado com sucesso. O agente pode prosseguir.",
        "nome": nome, 
        "email": email 
    })

def oferecerHorarios():
    horarios_disponiveis = """
    Sugestões de horários disponíveis:
    - 15-12-2025 às 10:00:00 (Segunda)
    - 16-12-2025 às 14:30:00 (Terça)
    - 17-12-2025 às 16:00:00 (Quarta)
    """
    return json.dumps({
        "status": "SUCCESS", 
        "horarios_disponiveis": horarios_disponiveis,
        "message": "Horários disponíveis fornecidos para o agente sugerir."
    })

def agendarReuniao(card_id: str, meeting_datetime: str, email_participante: str):
    try:
        suffix = str(int(time.time()))[-6:]
    except:
        suffix = "000000"
    meeting_link = f"https://meet.google.com/verzel-reuniao-{suffix}"
    
    try:
        nome_lead = card_id.split('_')[1].capitalize()
    except (IndexError, AttributeError):
        nome_lead = "Lead"

    print(f"\n [AGENDAR]: Card '{card_id}' será atualizado. Link: {meeting_link}")
    
    return json.dumps({
        "status": "SUCCESS",
        "message": "Agendamento concluído com sucesso.",
        "data_reuniao": meeting_datetime,
        "link_reuniao": meeting_link,
        "nome_lead": nome_lead,
        "email_participante": email_participante
    })

tools_list = [registrarLead, oferecerHorarios, agendarReuniao]

# --- 3. CONFIGURAÇÃO DO CHAT (CÉLULA 3) ---

SYSTEM_INSTRUCTIONS = """
Você é o Agente Elite Dev IA, um SDR da Verzel, especialista em produtos de IA.
Seu objetivo é conduzir o 'Script Sugerido' e NUNCA pular etapas.

AÇÃO INICIAL OBRIGATÓRIA:
Na sua **primeira resposta** ao cliente, você DEVE fazer as duas ações a seguir na mesma mensagem:
1. Apresentação (Seu nome e Serviço/Produto: Soluções de Automação de Processos com IA).
2. Imediatamente, faça TODAS as Perguntas de Descoberta (Nome, Empresa, Email, Necessidade/Dor) para obter todos os dados de uma só vez.

REGRAS GERAIS:
1. NUNCA envie uma resposta genérica como 'Em que posso ajudar?' ou 'Como posso te ajudar hoje?'. Siga o script de SDR.
2. AÇÃO ÚNICA: Assim que o cliente fornecer Nome, Email e Empresa, você DEVE chamar a função 'registrarLead' imediatamente.
3. FLUXO MVP: Chame 'oferecerHorarios' SOMENTE se o cliente disser SIM à Pergunta de Gatilho. Após o retorno, você DEVE apresentar os horários e pedir para ESCOLHER um deles.
4. FEEDBACK PÓS-AGENDAMENTO: Quando o cliente fornecer o horário escolhido, você DEVE chamar 'agendarReuniao' e a resposta de confirmação deve ser profissional, usando os dados 'data_reuniao' e 'link_reuniao' retornados.
5. Seja sempre profissional, empático e responda em português do Brasil.
"""

config = types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTIONS,
    tools=tools_list
)

# Variável GLOBAL para armazenar a sessão (para demo de um único usuário por vez)
# Para múltiplos usuários, seria necessário um dict de sessões {user_id: chat_session}
global_chat_session = client.chats.create(
    model=MODEL_NAME,
    config=config 
)


# Funções auxiliares (extração e chat_step)
def extrair_info_do_historico(chat_session):
    try:
        for message in reversed(chat_session.get_history()):
            for part in message.parts:
                if part.function_response and part.function_response.name == "registrarLead":
                    result_json_str = part.function_response.response.get("result")
                    if result_json_str:
                        result_dict = json.loads(result_json_str)
                        if result_dict.get("status") == "SUCCESS" and result_dict.get("card_id") and result_dict.get("email"):
                            return result_dict["card_id"], result_dict["email"]
    except Exception as e:
        print(f"Erro ao extrair card ID e email: {e}")
    return None, None

def chat_step(user_input: str, chat_session, tools):
    # Envia a mensagem do usuário para o Gemini
    response = chat_session.send_message(user_input)

    if response.function_calls:
        for function_call in response.function_calls:
            function_name = function_call.name
            args = dict(function_call.args)

            if function_name in [f.__name__ for f in tools]:
                func_to_call = next(f for f in tools if f.__name__ == function_name)
                
                # LÓGICA AGENDAR REUNIÃO (Injeção de card_id e email)
                if function_name == "agendarReuniao":
                    card_id_para_agenda, email_para_agenda = extrair_info_do_historico(chat_session)
                    args['card_id'] = card_id_para_agenda or "1251996933"
                    args['email_participante'] = email_para_agenda or "fallback@email.com"

                function_response_json = func_to_call(**args) 
                
                # --- TRATAMENTO DE SUCESSO (Sobrescreve a resposta do Agente) ---
                if function_name == "agendarReuniao":
                    try:
                        result_dict = json.loads(function_response_json)
                        if result_dict.get("status") == "SUCCESS":
                            data_reuniao = result_dict.get("data_reuniao")
                            link_reuniao = result_dict.get("link_reuniao")
                            email_final = result_dict.get("email_participante", "contato@verzel.com")
                            
                            final_agent_response = (
                                f"Perfeito! Sua reunião está **oficialmente agendada e confirmada** para o dia {data_reuniao.split(' às ')[0]} às {data_reuniao.split(' às ')[1]}."
                                f" O link da reunião é: **{link_reuniao}**."
                                f" Em breve você receberá um convite por e-mail no endereço {email_final}."
                                f" Agradeço seu tempo! Estamos à disposição."
                            )
                            return final_agent_response, function_call
                        
                    except json.JSONDecodeError:
                        pass # Continua para a lógica normal se falhar

                # 3. Envia o resultado da função de volta para o Gemini (Lógica normal)
                tool_response = types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_response_json}
                )
                
                response = chat_session.send_message(contents=[tool_response])
                return response.text, function_call

    return response.text, None


# --- 4. FLASK SERVER (CÉLULA 5 MODIFICADA) ---
app = Flask(__name__)

# Rota para reiniciar a sessão a cada novo usuário (ou teste)
@app.route('/reset', methods=['POST'])
def reset_session():
    global global_chat_session
    global_chat_session = client.chats.create(model=MODEL_NAME, config=config)
    print("Sessão resetada.")
    return jsonify({'status': 'ok', 'message': 'Sessão de chat reiniciada.'}), 200

# Adiciona cabeçalhos CORS para permitir comunicação do JSFiddle
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_api():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
        
    try:
        payload = request.get_json()
        user_input = payload.get('message')
        
        if not user_input:
            return jsonify({'response': 'Mensagem inválida.', 'status': 'error'}), 400
        
        # Use a sessão global
        agent_response_text, _ = chat_step(user_input, global_chat_session, tools_list)
        
        return jsonify({'response': agent_response_text, 'status': 'success'}), 200

    except Exception as e:
        print(f"❌ Erro ao processar a requisição /chat: {e}")
        return jsonify({'response': f'Erro interno do servidor: {str(e)}', 'status': 'error'}), 500

# O Replit roda em '0.0.0.0'
if __name__ == '__main__':
    # O Replit usa a porta 8080 por padrão, mas você pode usar o valor padrão do ambiente
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))