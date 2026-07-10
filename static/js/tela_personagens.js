const clickSound = document.getElementById('click-sound');
const deleteSound = document.getElementById('delete-sound');

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
    let msg = `_PERSONAGENS_`;
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
                
                const cardClickable = document.createElement('div');
                cardClickable.className = 'char-card-clickable';
                cardClickable.style.flexGrow = '1';
                cardClickable.style.cursor = 'pointer';
                cardClickable.onclick = () => selecionarAvatar(p.nome);
                
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

async function removerAvatarDoSistema(nome) {
    if(!confirm(`Deseja deletar o avatar [ ${nome.toUpperCase()} ] permanentemente?`)) return;
    
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
            alert(data.erro || "Falha ao excluir.");
        }
    } catch(e) {
        alert("Erro de comunicação com o servidor.");
    }
}

async function submitNewCharacter() {
    const nome = document.getElementById('new-char-name').value.trim();
    const classe = document.getElementById('new-char-class').value;
    
    if(!nome) {
        alert("Insira um nome operational válido.");
        return;
    }
    
    try {
        const response = await fetch('/criar_personagem', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nome, classe })
        });
        
        if(response.ok) {
            localStorage.setItem('activeCharName', nome);
            triggerPageFadeOut('/game');
        } else {
            const data = await response.json();
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
        
        if (response.ok) {
            localStorage.setItem('activeCharName', nome);
            triggerPageFadeOut('/game');
        } else {
            const data = await response.json();
            alert(data.erro);
        }
    } catch(e) {
        alert("Falha ao sincronizar avatar.");
    }
}