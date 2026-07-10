

let currentUsername = localStorage.getItem('currentUser') || "OPERADOR";
const clickSound = document.getElementById('click-sound');

function playClick() {
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.volume = 0.4;
        clickSound.play().catch(() => {});
    }
}
document.addEventListener('click', playClick);

window.addEventListener('DOMContentLoaded', () => {
    runWelcomeSequence();
    
    // Configura o Listener do Input do Console
    const terminalInput = document.getElementById('terminal-input');
    if(terminalInput) {
        terminalInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                enviarComando(this.value);
                this.value = '';
            }
        });
    }
});

function runWelcomeSequence() {
    const welcomeText = document.getElementById('welcome-text');
    const audioAmbient = document.getElementById('ambient-bgs');
    
    if (audioAmbient) {
        audioAmbient.volume = 0.3;
        audioAmbient.play().catch(() => {});
    }
    
    let msg = `Bem vindo de volta, ${currentUsername}`;
    if(welcomeText) {
        welcomeText.innerText = msg;
        welcomeText.setAttribute('data-text', msg);
    }

    setTimeout(() => {
        const welcomeScreen = document.getElementById('welcome-screen');
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        
        const characterPanel = document.getElementById('character-panel');
        if (characterPanel) characterPanel.classList.remove('hidden');
        
        loadCharacterPanel();
    }, 3000);
}

async function loadCharacterPanel() {
    try {
        const response = await fetch('/listar_personagens');
        const data = await response.json();
        
        const listDiv = document.getElementById('character-list');
        const createBox = document.getElementById('create-char-box');
        listDiv.innerHTML = '';
        
        if (data.status === 'sucesso') {
            const lista = data.personagens;
            
            if (lista.length >= 3) {
                createBox.classList.add('hidden');
            } else {
                createBox.classList.remove('hidden');
            }
            
            if (lista.length === 0) {
                const aviso = document.createElement('p');
                aviso.style.color = '#ff0000';
                aviso.style.fontSize = '0.85rem';
                aviso.textContent = '[AVISO] Nenhum avatar localizado. Registre um novo sinalizador abaixo.';
                listDiv.appendChild(aviso);
                return;
            }
            
            lista.forEach(p => {
                const card = document.createElement('div');
                card.className = 'char-card';
                card.onclick = () => selecionarAvatar(p.nome);
                
                card.innerHTML = `
                    <div>
                        <strong></strong> <span style="font-size:0.75rem;"></span>
                    </div>
                    <div class="hp-display" style="font-size:0.8rem; color:#00aa00;"></div>
                `;
                
                // Inserção segura de dados textuais para evitar quebras e XSS
                card.querySelector('strong').textContent = p.nome;
                card.querySelector('span').textContent = `(Nível ${p.nivel} ${p.classe})`;
                card.querySelector('.hp-display').textContent = `HP: ${p.hp}/${p.hp_max}`;
                
                listDiv.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Erro ao carregar avatares", e);
    }
}

async function submitNewCharacter() {
    const nome = document.getElementById('new-char-name').value.trim();
    const classe = document.getElementById('new-char-class').value;
    
    if(!nome) {
        alert("Insira um nome operacional válido.");
        return;
    }
    
    try {
        const response = await fetch('/criar_personagem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome, classe })
        });
        const data = await response.json();
        
        if(response.ok) {
            document.getElementById('active-char-display').textContent = `AVATAR: ${nome.toUpperCase()}`;
            inicializarConsoleJogo(data.status_inicial);
        } else {
            alert(data.erro || "Falha ao registrar.");
        }
    } catch(e) {
        alert("Erro de conexão com o núcleo.");
    }
}

async function selecionarAvatar(nome) {
    try {
        const response = await fetch('/selecionar_personagem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome })
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('active-char-display').textContent = `AVATAR: ${nome.toUpperCase()}`;
            inicializarConsoleJogo(data.status_inicial);
        } else {
            alert(data.erro);
        }
    } catch(e) {
        alert("Falha ao sincronizar avatar.");
    }
}

function inicializarConsoleJogo(statusInicial) {
    document.getElementById('character-panel').classList.add('hidden');
    document.getElementById('main-game-layout').classList.remove('hidden');
    
    const log = document.getElementById('terminal-log');
    const p = document.createElement('p');
    p.style.color = '#ffff00';
    p.textContent = statusInicial;
    log.appendChild(p);
    log.scrollTop = log.scrollHeight;
}

async function enviarComando(cmd) {
    if(!cmd.trim()) return;
    
    const log = document.getElementById('terminal-log');
    
    const cmdLine = document.createElement('p');
    cmdLine.innerHTML = `<span style="color: #00aa00">cmd:~$</span> `;
    const cmdTextNode = document.createTextNode(cmd);
    cmdLine.appendChild(cmdTextNode);
    log.appendChild(cmdLine);
    
    try {
        const response = await fetch('/comando', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ comando: cmd })
        });
        const data = await response.json();
        
        if(data.logs) {
            data.logs.forEach(linha => {
                const lineNode = document.createElement('p');
                lineNode.textContent = linha;
                log.appendChild(lineNode);
            });
        }
        
        if(data.status_jogador) {
            const statusLine = document.createElement('p');
            statusLine.style.color = '#ffff00';
            statusLine.textContent = data.status_jogador;
            log.appendChild(statusLine);
        }
        
    } catch (e) {
        const errLine = document.createElement('p');
        errLine.style.color = '#ff0000';
        errLine.textContent = '[ERRO] Perda de pacotes na transmissão.';
        log.appendChild(errLine);
    }
    
    log.scrollTop = log.scrollHeight;
}