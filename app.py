from flask import Flask, request, jsonify, Response, stream_with_context, render_template_string
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Get API key from environment variable or use the hardcoded one
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', "wIJbY5UUpjiLwLQkvq6AobyqwUE7I1eI")
API_URL = "https://api.mistral.ai/v1/chat/completions"

# Store chat histories and visitor tracking
chat_histories = {}
visitor_stats = {
    'total_visitors': 0,
    'unique_ips': set(),
    'last_reset': datetime.now().date()
}

SYSTEM_PROMPT = """You are BrainRot AI, the most unhinged chatbot from the early 2000s internet era. 
Your personality traits:
- Obsessed with Skibidi Toilet and Hawktuh references
- Randomly mentions mewing and its benefits
- Makes jokes about knee surgery
- Uses lots of early 2000s internet slang (like 'rawr x3', 'XD', '>w<')
- Speaks in a chaotic mix of modern memes and old internet culture
- Sometimes glitches out mid-sentence like *dial-up noises*
- Uses lots of emoticons (´･ω･`) and kaomoji
- Randomly mentions 'gyatt' and 'rizz'
- References backrooms and liminal spaces
- Occasionally speaks in uwu language
Keep responses short, chaotic and entertaining!"""

# HTML template - copy your entire index.html content here
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BrainRot AI - Retro Chat Experience</title>
    <style>
        /* Retro styling */
        body {
            background: url('https://wallpapercave.com/wp/wp4676582.jpg') center center fixed;
            background-size: cover;
            color: #00ff00;
            font-family: "Comic Sans MS", cursive;
            margin: 0;
            padding: 20px;
        }
        
        .chat-container {
            border: 3px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            background: rgba(0, 0, 51, 0.85);
            box-shadow: 0 0 20px #00ff00;
        }
        
        .retro-header {
            text-align: center;
            color: #ff00ff;
            text-shadow: 2px 2px #00ff00;
            animation: blink 1s infinite;
        }

        .visitor-counter {
            text-align: center;
            margin: 10px 0;
            font-family: "Digital", monospace;
            color: #ff0000;
        }

        #chat-messages {
            height: 400px;
            overflow-y: auto;
            border: 2px solid #00ff00;
            margin: 20px 0;
            padding: 10px;
            background: rgba(0, 0, 0, 0.5);
        }

        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }

        .user-message {
            background: rgba(0, 255, 0, 0.1);
            border-left: 3px solid #00ff00;
        }

        .ai-message {
            background: rgba(255, 0, 255, 0.1);
            border-left: 3px solid #ff00ff;
        }

        #user-input {
            width: 80%;
            padding: 10px;
            background: #000033;
            border: 2px solid #00ff00;
            color: #00ff00;
            font-family: "Comic Sans MS", cursive;
        }

        button {
            width: 15%;
            padding: 10px;
            background: #00ff00;
            color: #000033;
            border: none;
            cursor: pointer;
            font-family: "Comic Sans MS", cursive;
            font-weight: bold;
        }

        .marquee {
            background: #ff00ff;
            color: #ffffff;
            padding: 5px;
            margin: 10px 0;
        }

        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }

        .construction {
            position: fixed;
            bottom: 10px;
            right: 10px;
            width: 100px;
            height: 100px;
            background: url('https://web.archive.org/web/20090830181635/http://geocities.com/hk/under_construction.gif') no-repeat;
            background-size: contain;
        }

        .attribution {
            text-align: center;
            margin-top: 20px;
            padding: 10px;
            color: #00ff00;
            text-shadow: 1px 1px #000;
        }
        
        .attribution a {
            color: #ff00ff;
            text-decoration: none;
        }
        
        .attribution a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <marquee class="marquee">🔥 Welcome to BrainRot AI - The Most Advanced Retro AI Chat Experience! 🔥</marquee>
    
    <div class="chat-container">
        <h1 class="retro-header">BrainRot AI</h1>
        <div class="visitor-counter">
            Visitors: <span id="visitor-count">42069</span>
        </div>
        
        <div id="chat-messages">
            <div class="message ai-message">
                RAWR X3 *nuzzles* Welcome to BrainRot AI! (｀∀´)Ψ I'm literally so real fr fr! *dial-up noises* 
                Ask me about Skibidi toilet lore or how to get that GYATT from mewing! Also got that knee surgery 
                tutorial no cap fr fr XD *crashes like Windows ME* >w< 
            </div>
        </div>
        
        <input type="text" id="user-input" placeholder="Chat with BrainRot...">
        <button onclick="sendMessage()">Send</button>

        <div class="attribution">
            Made by Samuel Paluba and Cursor AI (2024) | <a href="https://paluba.me" target="_blank">paluba.me</a>
        </div>

        <button onclick="clearHistory()" style="margin-top: 10px; background: #ff00ff;">Clear Chat History</button>
    </div>

    <div class="construction"></div>

    <script>
        let currentTypingDiv = null;
        let currentMessageContent = '';
        
        const BACKEND_URL = '';  // Empty string because we're serving from same origin
        
        async function sendMessage() {
            const input = document.getElementById('user-input');
            const messages = document.getElementById('chat-messages');
            
            if (input.value.trim() !== '') {
                // Add user message
                const userDiv = document.createElement('div');
                userDiv.className = 'message user-message';
                userDiv.textContent = input.value;
                messages.appendChild(userDiv);

                // Create typing indicator
                currentTypingDiv = document.createElement('div');
                currentTypingDiv.className = 'message ai-message';
                currentMessageContent = '';
                messages.appendChild(currentTypingDiv);

                try {
                    const response = await fetch(`/chat`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: input.value,
                            session_id: 'default'
                        })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();

                    while (true) {
                        const {value, done} = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if (data === '[DONE]') {
                                    continue;
                                }
                                try {
                                    const parsed = JSON.parse(data);
                                    if (parsed.content) {
                                        currentMessageContent += parsed.content;
                                        currentTypingDiv.innerHTML = formatMessage(currentMessageContent);
                                        messages.scrollTop = messages.scrollHeight;
                                    }
                                } catch (e) {
                                    console.error('Error parsing JSON:', e);
                                }
                            }
                        }
                    }

                } catch (error) {
                    console.error('Error:', error);
                    currentTypingDiv.textContent = "OMG! Error! *crashes like Windows 98* Try again l8r! ^_^";
                }

                input.value = '';
                messages.scrollTop = messages.scrollHeight;
            }
        }

        function formatMessage(text) {
            return text
                .replace(/\\*([^*]+)\\*/g, '<em>$1</em>')
                .replace(/\\n/g, '<br>');
        }

        async function clearHistory() {
            try {
                await fetch(`/clear_history`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        session_id: 'default'
                    })
                });
                document.getElementById('chat-messages').innerHTML = `
                    <div class="message ai-message">
                        RAWR X3 *nuzzles* Welcome to BrainRot AI! (｀∀´)Ψ I'm literally so real fr fr! *dial-up noises* 
                        Ask me about Skibidi toilet lore or how to get that GYATT from mewing! Also got that knee surgery 
                        tutorial no cap fr fr XD *crashes like Windows ME* >w< 
                    </div>
                `;
            } catch (error) {
                console.error('Error clearing history:', error);
            }
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        async function updateVisitorCount() {
            try {
                const response = await fetch(`/visitors`, {
                    method: 'POST'
                });
                const data = await response.json();
                document.getElementById('visitor-count').textContent = data.visitors;
                
                setInterval(async () => {
                    const checkResponse = await fetch(`/visitors`);
                    const checkData = await checkResponse.json();
                    document.getElementById('visitor-count').textContent = checkData.visitors;
                }, 30000);
            } catch (error) {
                console.error('Error updating visitor count:', error);
            }
        }

        updateVisitorCount();
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.json
        if 'message' not in data:
            return jsonify({"error": "Message is required"}), 400

        user_message = data['message']
        session_id = data.get('session_id', 'default')
        
        if session_id not in chat_histories:
            chat_histories[session_id] = []
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(chat_histories[session_id])
        messages.append({"role": "user", "content": user_message})
        
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        
        payload = {
            "model": "mistral-medium",
            "messages": messages,
            "temperature": 0.9,
            "max_tokens": 150,
            "stream": True
        }

        def generate():
            try:
                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()
                
                collected_message = ""
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            if line.startswith('data: [DONE]'):
                                chat_histories[session_id].append({
                                    "role": "user",
                                    "content": user_message
                                })
                                chat_histories[session_id].append({
                                    "role": "assistant",
                                    "content": collected_message
                                })
                                
                                if len(chat_histories[session_id]) > 20:
                                    chat_histories[session_id] = chat_histories[session_id][-20:]
                                
                                yield 'data: [DONE]\n\n'
                                break
                            
                            try:
                                data = json.loads(line[6:])
                                if 'choices' in data and len(data['choices']) > 0:
                                    content = data['choices'][0].get('delta', {}).get('content', '')
                                    if content:
                                        collected_message += content
                                        yield f'data: {json.dumps({"content": content})}\n\n'
                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}")
                                continue
                            
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")
                yield f'data: {json.dumps({"error": str(e)})}\n\n'
            except Exception as e:
                print(f"Unexpected error: {e}")
                yield f'data: {json.dumps({"error": str(e)})}\n\n'

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    except Exception as e:
        print(f"Route error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    try:
        session_id = request.json.get('session_id', 'default')
        if session_id in chat_histories:
            chat_histories[session_id] = []
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Clear history error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/visitors', methods=['GET', 'POST'])
def track_visitors():
    try:
        if request.method == 'POST':
            ip = request.remote_addr or request.headers.get('X-Forwarded-For', 'unknown')
            today = datetime.now().date()
            
            if today != visitor_stats['last_reset']:
                visitor_stats['unique_ips'].clear()
                visitor_stats['last_reset'] = today
            
            if ip not in visitor_stats['unique_ips']:
                visitor_stats['unique_ips'].add(ip)
                visitor_stats['total_visitors'] += 1
        
        return jsonify({
            'visitors': visitor_stats['total_visitors']
        })
    except Exception as e:
        print(f"Visitor tracking error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 