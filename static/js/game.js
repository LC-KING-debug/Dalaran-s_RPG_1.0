let currentUsername = localStorage.getItem('currentUser') || "OPERADOR";
let userCharacters = [];

// Elemento de áudio global para o clique
const clickSound = document.getElementById('click-sound');

// Desbloqueia e gerencia o som de clique universal de forma otimizada para Mobile/Desktop
function playClick() {
    if (clickSound) {
        // Truque para navegadores mobile: se o áudio estiver pausado/suspenso, força o reset
        clickSound.currentTime = 0;
        clickSound.volume = 0.6;
        
        // O play() retorna uma promessa, tratamos o erro caso o navegador bloqueie antes da primeira interação
        const playPromise = clickSound.play();
        if (playPromise !== undefined) {
            playPromise.catch(error => {
                console.log("Áudio aguardando interação inicial.");
            });
        }
    }
}

// Escuta cliques normais (Desktop) e toques touch (Mobile)
document.addEventListener('click', playClick);
document.addEventListener('touchstart', playClick, { passive: true });


// --- SEU PROCESSO DO WELCOME SEQUENCE DA RESPOSTA ANTERIOR CONTINUA ABAIXO ---
window.addEventListener('DOMContentLoaded', () => {
    runWelcomeSequence();
});

function runWelcomeSequence() {
    const welcomeText = document.getElementById('welcome-text');
    const audioAmbient = document.getElementById('ambient-bgs');
    
    if (audioAmbient) {
        audioAmbient.volume = 0.5;
        audioAmbient.play().catch(() => {
            // Se o autoplay da música falhar, ela pega carona no clique universal configurado acima
            const startAmbient = () => { audioAmbient.play().catch(() => {}); };
            document.addEventListener('click', startAmbient, { once: true });
            document.addEventListener('touchstart', startAmbient, { once: true });
        });
    }
    
    const hasVisited = localStorage.getItem(`visited_${currentUsername}`);
    let msg = `Bem vindo a Dalaran's, ${currentUsername}`;
    
    if (hasVisited) {
        msg = `Bem vindo de volta a Dalaran's, ${currentUsername}`;
    } else {
        localStorage.setItem(`visited_${currentUsername}`, 'true');
    }

    welcomeText.innerText = msg;
    welcomeText.setAttribute('data-text', msg);

    setTimeout(() => {
        const welcomeScreen = document.getElementById('welcome-screen');
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        loadCharacterPanel();
    }, 4500);
}