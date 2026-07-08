function switchTab(type) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');
    const tabLogin = document.getElementById('tab-login');
    const tabReg = document.getElementById('tab-register');
    document.getElementById('auth-message').innerText = '';

    if (type === 'login') {
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
        tabLogin.classList.add('active');
        tabReg.classList.remove('active');
    } else {
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
        tabLogin.classList.remove('active');
        tabReg.classList.add('active');
    }
}

async function handleAuth(event, type) {
    event.preventDefault();
    const msg = document.getElementById('auth-message');
    msg.style.color = '#00ff00';
    msg.innerText = "ENVIANDO PACOTES...";

    const username = type === 'login' ? document.getElementById('login-user').value : document.getElementById('reg-user').value;
    const password = type === 'login' ? document.getElementById('login-pass').value : document.getElementById('reg-pass').value;

    const endpoint = type === 'login' ? '/login' : '/register';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();

        if (response.ok) {
            msg.innerText = "SESSÃO VALIDADA.";
            // Guarda temporariamente no localStorage para sabermos quem logou antes de ir pro index
            localStorage.setItem('currentUser', username);
            setTimeout(() => { window.location.href = '/game'; }, 800);
        } else {
            msg.style.color = '#ff0000';
            msg.innerText = `ERR: ${data.message || 'Dados inválidos.'}`;
        }
    } catch (e) {
        msg.style.color = '#ff0000';
        msg.innerText = "ERRO NA CENTRAL DO PROTOCOLO.";

        
    }
}

// Gerenciador de som para elementos de fato clicáveis
document.addEventListener('DOMContentLoaded', () => {
    const audioClick = document.getElementById('global-click-sound');

    const playClickSound = (event) => {
        // Seleciona o elemento real que foi clicado
        const target = event.target;

        // Lista de tags e atributos que consideramos como "clicáveis" no sistema
        const isClickable = 
            target.tagName === 'BUTTON' || 
            target.tagName === 'INPUT' || 
            target.tagName === 'LABEL' || 
            target.tagName === 'A' ||
            target.hasAttribute('onclick') || 
            target.classList.contains('tab-btn') ||
            target.closest('button') || // Garante clique em ícones/textos dentro de botões
            target.closest('.tab-btn');

        // Só toca o áudio se passou no teste acima
        if (isClickable && audioClick) {
            audioClick.currentTime = 0; // Reseta para o início caso clique rápido
            audioClick.volume = 0.5;
            audioClick.play().catch(() => {});
        }
    };

    // Escuta cliques do mouse e toques na tela nos elementos específicos
    document.addEventListener('click', playClickSound);
    document.addEventListener('touchstart', playClickSound, { passive: true });
});