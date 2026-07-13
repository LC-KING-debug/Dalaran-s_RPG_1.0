const clickSound = document.getElementById('click-sound');

function playClick() {
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.volume = 0.4;
        clickSound.play().catch(() => {});
    }
}

// Fade-Out controlável com delay
function triggerPageFadeOut(url) {
    const overlay = document.getElementById('page-transition');
    if (overlay) {
        overlay.classList.remove('fade-in');
        overlay.classList.add('fade-out');
        setTimeout(() => {
            window.location.href = url;
        }, 2500);
    } else {
        window.location.href = url;
    }
}

document.addEventListener('click', (event) => {
    const target = event.target;
    
    if (target.classList.contains('transition-trigger') || target.closest('.transition-trigger')) {
        event.preventDefault();
        const url = target.getAttribute('href') || target.closest('.transition-trigger').getAttribute('href');
        triggerPageFadeOut(url);
        return;
    }

    if (['BUTTON', 'INPUT', 'SELECT', 'A'].includes(target.tagName)) {
        playClick();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('page-transition');
    if (overlay) {
        overlay.classList.add('fade-in');
    }

    runGameLoadSequence();
    
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

function runGameLoadSequence() {
    const welcomeText = document.getElementById('welcome-text');
    const audioAmbient = document.getElementById('ambient-bgs');
    
    let activeChar = localStorage.getItem('activeCharName') || "AVATAR";
    
    if (audioAmbient) {
        audioAmbient.volume = 0.3;
        audioAmbient.play().catch(() => {});
    }
    
    let msg = `_CARREGANDO MUNDO DE:${activeChar.toUpperCase()}`;
    if(welcomeText) {
        welcomeText.innerText = msg;
        welcomeText.setAttribute('data-text', msg);
    }

    setTimeout(() => {
        const welcomeScreen = document.getElementById('welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
        
        const mainLayout = document.getElementById('main-game-layout');
        if (mainLayout) {
            mainLayout.classList.remove('hidden');
        }
        
        const charDisplay = document.getElementById('active-char-display');
        if (charDisplay) {
            charDisplay.textContent = `AVATAR: ${activeChar.toUpperCase()}`;
        }
        
        const terminalInput = document.getElementById('terminal-input');
        if(terminalInput) {
            terminalInput.focus();
        }
    }, 3000); 
}

// Novo: Função para colorir tags e processar negrito
function formatarLinhaLog(texto) {
    // 1. Processa marcadores de negrito ex: **texto**
    let html = texto.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #ffffff; text-shadow: 0 0 5px #fff;">$1</strong>');

    // 2. Dicionário de cores para cada Tag do game.py
    const tagCores = {
        '[SISTEMA]': '#00aaff',
        '[ERRO]': '#ff3333',
        '[AVISO]': '#ffaa00',
        '[COMBATE]': '#ff8800',
        '[FALHA]': '#ff5555',
        '[MOVIMENTO]': '#aaaaaa',
        '[ALERTA]': '#ffaa00',
        '[AÇÃO]': '#ff55ff',
        '[HABILIDADE]': '#bb55ff',
        '[PERIGO]': '#ff3300',
        '[VITORIA]': '#ffff00',
        '[DROP]': '#00ffaa',
        '[LEVEL UP]': '#ffffaa',
        '[GAME OVER]': '#ff0000',
        '[ITEM]': '#00ffaa',
        '[INVENTARIO]': '#00ffaa',
        '[STATUS]': '#aaffaa'
    };

    // 3. Aplica a cor apropriada à tag encontrada
    for (const [tag, color] of Object.entries(tagCores)) {
        if (html.includes(tag)) {
            html = html.replace(tag, `<span style="color: ${color}; font-weight: bold;">${tag}</span>`);
            // Se for erro ou game over, deixa a linha toda ligeiramente vermelha
            if (tag === '[ERRO]' || tag === '[GAME OVER]' || tag === '[FALHA]') {
                return `<span style="color: #ffcccc;">${html}</span>`;
            }
            break;
        }
    }
    
    return html;
}

async function enviarComando(cmd) {
    if(!cmd.trim()) return;
    
    const log = document.getElementById('terminal-log');
    if (!log) return;
    
    // Imprime o comando do usuário
    const cmdLine = document.createElement('p');
    cmdLine.innerHTML = `<span style="color: #00aa00">cmd:~$</span> <span>${cmd}</span>`;
    log.appendChild(cmdLine);
    
    try {
        const response = await fetch('/comando', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ comando: cmd })
        });
        const data = await response.json();
        
        // Renderiza as respostas do backend usando nosso formatador HTML
        if(data.logs) {
            data.logs.forEach(linha => {
                const lineNode = document.createElement('p');
                lineNode.innerHTML = formatarLinhaLog(linha);
                log.appendChild(lineNode);
            });
        }
        
        // Atualiza a linha de status (se vier separada na requisição)
        if(data.status_jogador) {
            const statusLine = document.createElement('p');
            statusLine.style.borderTop = '1px dashed #333';
            statusLine.style.paddingTop = '5px';
            statusLine.innerHTML = formatarLinhaLog(data.status_jogador);
            log.appendChild(statusLine);
        }
        
    } catch (e) {
        const errLine = document.createElement('p');
        errLine.innerHTML = `<span style="color: #ff3333; font-weight: bold;">[ERRO]</span> Perda de pacotes na transmissão.`;
        log.appendChild(errLine);
    }
    
    // Rola o terminal para o fundo
    log.scrollTop = log.scrollHeight;
}