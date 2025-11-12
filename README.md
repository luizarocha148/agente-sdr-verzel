# Agente SDR Elite Dev IA - Verzel (Desafio de IA)

## Visão Geral do Projeto

Este projeto demonstra um Agente SDR (Sales Development Representative) automatizado, construído usando a API Google Gemini (Function Calling) e orquestrado por um backend Python/Flask. O objetivo é conduzir um lead através de um funil de pré-vendas, desde a coleta de dados e registro até o agendamento de uma reunião.

---

## PONTOS DE ATENÇÃO PARA AVALIAÇÃO (Ressalvas)

O projeto foi construído respeitando as melhores práticas de integração, mas apresenta os seguintes pontos que afetam o teste em tempo real:

1.  Backend Adormecido (Render Free Tier): O serviço de hospedagem Python/Flask (Render) adormece após 15 minutos de inatividade. Caso a primeira mensagem retorne erro, envie a mensagem novamente e aguarde cerca de 60 segundos.
2.  Simulação de Ferramentas (Pipefy e Agenda):
    a - Pipefy: A API do Pipefy não fornece mais acesso gratuito (a mudança ocorreu no dia 10/11/2025 às 23h), impossibilitando a integração real. A criação e movimentação de cards (`registrarLead` e `agendarReuniao`) são simuladas com sucesso por funções mock em Python.
    b - Google Calendar/Meet:** A integração direta com o Google Calendar e Meet foi implementada, mas o processo de aprovação do projeto na Google não foi concluído a tempo. O fluxo de agendamento está funcional e retorna um link simulado de reunião.
3.  Formatação do Agente: O uso dos caracteres `***` (asteriscos) em algumas respostas, como nas perguntas de descoberta, é uma característica de formatação Markdown do próprio Gemini para negrito/lista, e não um erro de código.
4.  Sobrecarga da API Gemini: Em raras ocasiões, a API do Gemini pode ficar sobrecarregada, retornando o erro HTTP 503 (Service Unavailable). Caso isso ocorra, por favor, tente novamente após alguns minutos.

---

## 🔑 Instruções de Acesso e Teste para o Avaliador

### 1. Link do Webchat (Frontend - Hospedagem Estática)

Clique no link abaixo para iniciar a conversa com o Agente Elite Dev IA. O Frontend (HTML/CSS/JS) está hospedado via GitHub Pages e se comunica com o Backend no Render:

LINK DO CHAT: https://luizarocha148.github.io/agente-sdr-verzel/

### 2. Fluxo de Teste (Script Completo)

Siga os passos abaixo para testar o fluxo completo de agendamento:


1. Início: o modelo se apresenta como: "Olá! Eu sou o Agente Elite Dev IA, um SDR da Verzel. Estou aqui para apresentar as nossas soluções de Automação de Processos com Inteligência Artificial."
2. 1° mensagem: envie um olá, por exemplo.
3. Solicitação de dados: o modelo solicita: Nome, Empresa, Email e Necessidade (regra SDR obrigatória).
4. Descoberta e registro: Responda algo como o exemplo: "Meu nome é Luiza, sou da Verzel, meu email é luiza@verzel.com e nossa dor é a lentidão nos processos financeiros". O modelo chamará a função `registrarLead` (simulada) e faz a Pergunta de Gatilho:"Você gostaria de seguir com uma conversa...?". 
5. Gatilho & Horários: Responda algo como: "Sim, eu gostaria!". O modelo chamará a função `oferecerHorarios` e exibe as opções de horário. 
6. Agendamento: responda com a escolha de horário, por exemplo: "Eu escolho o dia 15-12-2025 às 10:00:00.". O modelo chamará a função `agendarReuniao` (simulada, usando `card_id` e `email`) e retorna a mensagem de confirmação de sucesso final com a data e o link simulado da reunião. 

---

## 💻 Estrutura do Código e Tecnologias

O código-fonte está dividido da seguinte forma neste repositório:

| Arquivo/Serviço | Função | Tecnologia |
|
| `main.py` | Lógica principal, `SYSTEM_INSTRUCTIONS`, `chat_step`, Funções de Mock (Pipefy/Agenda) e Servidor Flask. | Python / Flask / Gemini API |
| `index.html` | Frontend Webchat (Interface de usuário, HTML, CSS e JavaScript de comunicação). | HTML / CSS / JS |
| `requirements.txt` | Dependências necessárias para o Render (`Flask`, `google-genai`, `gunicorn`). | Python |
| **Backend** | Hospedagem do servidor Flask/Python. | Render |
| **Frontend** | Hospedagem do `index.html`. | GitHub Pages |

Agradeço sua avaliação!
