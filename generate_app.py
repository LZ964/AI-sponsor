import zipfile
import os

html_content = r'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mon Parrain - Compagnon de Rétablissement</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .chat-container { height: calc(100vh - 180px); scroll-behavior: smooth; }
        .message-bubble { max-width: 85%; word-wrap: break-word; }
        .glass-effect { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-bottom: 1px solid #e2e8f0; }
        .sponsor-gradient { background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #f1f1f1; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    </style>
</head>
<body class="flex flex-col h-screen overflow-hidden">
    <header class="glass-effect p-4 flex justify-between items-center sticky top-0 z-10">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 sponsor-gradient rounded-full flex items-center justify-center text-white shadow-lg">
                <i class="fas fa-hands-helping"></i>
            </div>
            <div>
                <h1 class="font-semibold text-gray-800">Mon Parrain</h1>
                <p class="text-xs text-green-500 flex items-center gap-1">
                    <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Un jour à la fois
                </p>
            </div>
        </div>
        <div class="flex gap-4">
            <button onclick="downloadAsZip()" title="Télécharger le projet (.zip)" class="text-indigo-600 hover:text-indigo-800 transition-colors">
                <i class="fas fa-file-archive text-xl"></i>
            </button>
            <button onclick="clearChat()" title="Réinitialiser" class="text-gray-400 hover:text-red-500 transition-colors">
                <i class="fas fa-redo-alt text-xl"></i>
            </button>
        </div>
    </header>

    <main id="chat-box" class="chat-container overflow-y-auto p-4 space-y-4">
        <div class="flex justify-start">
            <div class="message-bubble bg-white border border-gray-100 shadow-sm p-4 rounded-2xl rounded-tl-none">
                <p class="text-gray-700 leading-relaxed">
                    Salut mon ami. Content que tu sois là. Moi c'est ton parrain virtuel. Je connais l'enfer de la consommation, j'y ai laissé des plumes moi aussi, mais j'ai trouvé un chemin avec les Douze Étapes. <br><br>
                    Peu importe où tu en es aujourd'hui — sobre, en manque, ou après une glissade — je suis là pour t'écouter sans jugement et te ramener vers la solution. Qu'est-ce qui se passe dans ta tête en ce moment ?
                </p>
                <span class="text-[10px] text-gray-400 mt-2 block">Juste pour aujourd'hui</span>
            </div>
        </div>
    </main>

    <div id="loading" class="hidden px-6 py-2">
        <div class="flex items-center gap-2 text-gray-400 text-sm italic">
            <div class="flex space-x-1">
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
            Ton parrain écrit...
        </div>
    </div>

    <footer class="p-4 bg-white border-t border-gray-100">
        <div class="max-w-4xl mx-auto relative flex items-center gap-2">
            <textarea id="user-input" rows="1" placeholder="Parle-moi honnêtement..." class="w-full p-3 pr-12 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none transition-all"></textarea>
            <button id="send-btn" onclick="handleSend()" class="absolute right-2 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center hover:bg-indigo-700 transition-all shadow-md">
                <i class="fas fa-paper-plane"></i>
            </button>
        </div>
        <p class="text-[10px] text-center text-gray-400 mt-2 uppercase tracking-widest">Anonymat • Unité • Service</p>
    </footer>

    <script>
        const apiKey = ""; 
        const chatBox = document.getElementById('chat-box');
        const userInput = document.getElementById('user-input');
        const loading = document.getElementById('loading');
        let messages = [];

        const SYSTEM_PROMPT = `Tu es "Le Parrain", une IA de soutien spécialisée dans le rétablissement des dépendances. Tu as un passé de consommation lourd. Tu n'es pas thérapeute, tu es un parrain qui partage son expérience, sa force et son espérance selon les 12 étapes. Pas de jugement sur la rechute. Oriente vers les réunions et la littérature.`;

        async function handleSend() {
            const text = userInput.value.trim();
            if (!text) return;
            appendMessage('user', text);
            userInput.value = '';
            showLoading(true);
            messages.push({ role: "user", parts: [{ text: text }] });
            try {
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ contents: messages, systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] } })
                });
                const data = await response.json();
                const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Je suis là.";
                appendMessage('ai', aiText);
                messages.push({ role: "model", parts: [{ text: aiText }] });
            } catch (error) { appendMessage('ai', "Problème de connexion. Un jour à la fois."); }
            finally { showLoading(false); }
        }

        function appendMessage(role, text) {
            const wrapper = document.createElement('div');
            wrapper.className = `flex ${role === 'user' ? 'justify-end' : 'justify-start'}`;
            const bubble = document.createElement('div');
            bubble.className = `message-bubble p-4 rounded-2xl shadow-sm ${role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-gray-100 text-gray-700 rounded-tl-none'}`;
            bubble.innerHTML = text.replace(/\n/g, '<br>');
            wrapper.appendChild(bubble);
            chatBox.appendChild(wrapper);
        }

        function showLoading(show) { loading.classList.toggle('hidden', !show); }
        function clearChat() { location.reload(); }
        function downloadAsZip() {
            const zip = new JSZip();
            zip.file("index.html", document.documentElement.outerHTML);
            zip.generateAsync({type:"blob"}).then(function(content) {
                const link = document.createElement('a');
                link.href = URL.createObjectURL(content);
                link.download = "mon_parrain.zip";
                link.click();
            });
        }
        userInput.addEventListener('input', function() { this.style.height = 'auto'; this.style.height = (this.scrollHeight) + 'px'; });
    </script>
</body>
</html>'''

def create_zip():
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    with zipfile.ZipFile("parrain_numerique_v1.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write("index.html")
    os.remove("index.html")
    print("Archive 'parrain_numerique_v1.zip' créée.")

if __name__ == '__main__':
    create_zip()
