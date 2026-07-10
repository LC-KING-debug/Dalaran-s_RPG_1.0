

const globalClickSound = document.getElementById('global-click-sound');

function playLoginClick() {
    if (globalClickSound) {
        globalClickSound.currentTime = 0;
        globalClickSound.volume = 0.4;
        globalClickSound.play().catch(() => {});
    }
}

// Vincula o som a interações na página
document.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON' || e.target.classList.contains('tab-btn')) {
        playLoginClick();
    }
});

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
            msg.innerText = type === 'login' ? "SESSÃO VALIDADA. REDIRECIONANDO..." : "CADASTRO REALIZADO! FAÇA LOGIN.";
            if(type === 'login') {
                localStorage.setItem('currentUser', username);
                setTimeout(() => { window.location.href = '/game'; }, 800);
            } else {
                switchTab('login');
            }
        } else {
            msg.style.color = '#ff0000';
            msg.innerText = `ERR: ${data.message || data.erro || 'Falha operacional.'}`;
        }
    } catch (e) {
        msg.style.color = '#ff0000';
        msg.innerText = "ERRO NA CENTRAL DO PROTOCOLO.";
    }
}