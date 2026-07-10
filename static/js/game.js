const clickSound = document.getElementById('click-sound');

function playClick() {
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.volume = 0.4;
        clickSound.play().catch(() => {});
    }
}

// Fade-Out controlável com delay estendido para 2.5 segundos (2500ms)
function triggerPageFadeOut(url) {
    const overlay = document.getElementById('page-transition');
    if (overlay) {
        overlay.classList.remove('fade-in');
        overlay.classList.add('fade-out');
        setTimeout(() => {
            window.location.href = url;
        }, 2500); // Sincronizado com o CSS
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

    if (
        target.tagName === 'BUTTON' || 
        target.tagName === 'INPUT' || 
        target.tagName === 'SELECT' || 
        target.tagName === 'A'
    ) {
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
    
    let msg = `_CARREGANDO PROGRESSO DE ${activeChar.toUpperCase()}`;
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

async function enviarComando(cmd) {
    if(!cmd.trim()) return;
    
    const log = document.getElementById('terminal-log');
    if (!log) return;
    
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