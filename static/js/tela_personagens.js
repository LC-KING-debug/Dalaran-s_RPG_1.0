const clickSound = document.getElementById('click-sound');
const deleteSound = document.getElementById('delete-sound');

// Variável para armazenar o personagem selecionado
let avatarSelecionadoNome = null;

function playClick() {
    if (clickSound) {
        clickSound.currentTime = 0;
        clickSound.volume = 0.4;
        clickSound.play().catch(() => {});
    }
}

function playDeleteSound() {
    if (deleteSound) {
        deleteSound.currentTime = 0;
        deleteSound.volume = 0.5;
        deleteSound.play().catch(() => {});
    }
}

// Fade-Out controlável com delay estendido
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

    if (
        target.tagName === 'BUTTON' || 
        target.tagName === 'INPUT' || 
        target.tagName === 'SELECT' || 
        target.tagName === 'A' || 
        target.closest('.char-card-clickable')
    ) {
        playClick();
    }
});

window.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('page-transition');
    if (overlay) {
        overlay.classList.add('fade-in');
    }

    runWelcomeSequence();
    loadCharacterPanel();
});

function runWelcomeSequence() {
    const welcomeText = document.getElementById('welcome-text');
    let msg = `_AVATARES_`;
    if(welcomeText) {
        welcomeText.innerText = msg;
        welcomeText.setAttribute('data-text', msg);
    }

    setTimeout(() => {
        const welcomeScreen = document.getElementById('welcome-screen');
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        
        const characterPanel = document.getElementById('character-panel');
        if (characterPanel) characterPanel.classList.remove('hidden');
    }, 3000); 
}

// ================= FUNÇÕES DE ALERTAS =================

function showSystemAlert(message) {
    const alertOverlay = document.getElementById('system-alert');
    const alertMessage = document.getElementById('system-alert-message');
    
    if (alertOverlay && alertMessage) {
        alertMessage.textContent = message;
        alertOverlay.classList.remove('hidden');
        playClick(); 
    }
}

function closeSystemAlert() {
    const alertOverlay = document.getElementById('system-alert');
    if (alertOverlay) {
        alertOverlay.classList.add('hidden');
        playClick();
    }
}

// Funções para o Alerta de Confirmação
function showSystemConfirm(message, onConfirmCallback) {
    const confirmOverlay = document.getElementById('system-confirm');
    const confirmMessage = document.getElementById('system-confirm-message');
    const btnYes = document.getElementById('btn-confirm-yes');
    
    if (confirmOverlay && confirmMessage && btnYes) {
        confirmMessage.textContent = message;
        
        btnYes.onclick = () => {
            closeSystemConfirm();
            onConfirmCallback();
        };
        
        confirmOverlay.classList.remove('hidden');
        playClick(); 
    }
}

function closeSystemConfirm() {
    const confirmOverlay = document.getElementById('system-confirm');
    if (confirmOverlay) {
        confirmOverlay.classList.add('hidden');
        playClick();
    }
}

// ======================================================

async function loadCharacterPanel() {
    try {
        const response = await fetch('/listar_personagens');
        const data = await response.json();
        
        const listDiv = document.getElementById('character-list');
        const createBox = document.getElementById('create-char-box');
        const btnIniciar = document.getElementById('btn-iniciar-mundo');
        
        listDiv.innerHTML = '';
        
        // Esconde o botão e limpa a seleção ao recarregar a lista
        if(btnIniciar) btnIniciar.classList.add('hidden');
        avatarSelecionadoNome = null;
        
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
                card.id = `card-${p.nome}`;
                
                const cardClickable = document.createElement('div');
                cardClickable.className = 'char-card-clickable';
                cardClickable.style.flexGrow = '1';
                cardClickable.style.cursor = 'pointer';
                
                // O clique destaca o avatar
                cardClickable.onclick = () => destacarAvatar(p.nome, card);
                
                cardClickable.innerHTML = `
                    <div>
                        <strong></strong> <span style="font-size:0.75rem;"></span>
                    </div>
                    <div class="hp-display" style="font-size:0.8rem; color:#00aa00;"></div>
                `;
                
                cardClickable.querySelector('strong').textContent = p.nome;
                cardClickable.querySelector('span').textContent = `(Nível ${p.nivel} ${p.classe})`;
                cardClickable.querySelector('.hp-display').textContent = `HP: ${p.hp}/${p.hp_max}`;
                
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'delete-player-btn';
                deleteBtn.innerHTML = '&#128465;'; 
                deleteBtn.onclick = (e) => {
                    e.stopPropagation();
                    removerAvatarDoSistema(p.nome);
                };
                
                card.appendChild(cardClickable);
                card.appendChild(deleteBtn);
                listDiv.appendChild(card);
            });
        }
    } catch (e) {
        console.error("Erro ao carregar avatares", e);
    }
}

// Destaca o avatar selecionado e exibe o botão
function destacarAvatar(nome, cardElement) {
    document.querySelectorAll('.char-card').forEach(c => c.classList.remove('selected'));
    
    cardElement.classList.add('selected');
    avatarSelecionadoNome = nome;
    
    const btnIniciar = document.getElementById('btn-iniciar-mundo');
    if(btnIniciar) {
        btnIniciar.classList.remove('hidden');
    }
    
    playClick(); 
}

// MUDANÇA: Substituição do confirm() nativo pelo modal customizado
async function removerAvatarDoSistema(nome) {
    showSystemConfirm(`Deseja deletar o avatar [ ${nome.toUpperCase()} ] permanentemente?`, async () => {
        try {
            const response = await fetch('/deletar_personagem', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ nome })
            });
            
            if(response.ok) {
                playDeleteSound();
                loadCharacterPanel();
            } else {
                const data = await response.json();
                showSystemAlert(data.erro || "Falha ao excluir.");
            }
        } catch(e) {
            showSystemAlert("Erro de comunicação com o servidor.");
        }
    });
}

async function submitNewCharacter() {
    const nome = document.getElementById('new-char-name').value.trim();
    const classe = document.getElementById('new-char-class').value;
    
    if(!nome) {
        showSystemAlert("Insira um nome operacional válido.");
        return;
    }
    
    try {
        const response = await fetch('/criar_personagem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome, classe })
        });
        
        if(response.ok) {
            document.getElementById('new-char-name').value = '';
            showSystemAlert(`Sinalizador [ ${nome} ] registrado com sucesso. Selecione-o na lista para iniciar.`);
            loadCharacterPanel();
        } else {
            const data = await response.json();
            showSystemAlert(data.erro || "Falha ao registrar.");
        }
    } catch(e) {
        showSystemAlert("Erro de conexão com o núcleo.");
    }
}

async function entrarNoMundo() {
    if (!avatarSelecionadoNome) return;
    
    try {
        const response = await fetch('/selecionar_personagem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome: avatarSelecionadoNome })
        });
        
        if (response.ok) {
            localStorage.setItem('activeCharName', avatarSelecionadoNome);
            triggerPageFadeOut('/game');
        } else {
            const data = await response.json();
            showSystemAlert(data.erro);
        }
    } catch(e) {
        showSystemAlert("Falha ao sincronizar avatar.");
    }
}