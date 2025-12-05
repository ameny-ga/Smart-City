/* ===== SYSTÈME D'AUTHENTIFICATION ===== */

// Stockage des credentials
let currentUser = null;
let authCredentials = null;

// Fonction pour encoder en Base64
function encodeCredentials(username, password) {
    return btoa(`${username}:${password}`);
}

// Fonction de login
async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    if (!username || !password) {
        alert('❌ Veuillez remplir tous les champs');
        return;
    }
    
    const credentials = encodeCredentials(username, password);
    
    try {
        const response = await fetch(`${GATEWAY_URL}/api/auth/me`, {
            headers: {
                'Authorization': `Basic ${credentials}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            currentUser = user;
            authCredentials = credentials;
            
            // Stocker dans localStorage
            localStorage.setItem('authCredentials', credentials);
            localStorage.setItem('currentUser', JSON.stringify(user));
            
            showUserInfo(user);
            hideLoginModal();
            
            alert(`✅ Bienvenue ${user.full_name} (${user.role})`);
            
            // Recharger la page actuelle si c'est transport
            const activeSection = document.querySelector('.service-section.active');
            if (activeSection && activeSection.id === 'transport') {
                loadTransports();
            }
        } else {
            alert('❌ Identifiants invalides');
        }
    } catch (error) {
        alert(`❌ Erreur de connexion: ${error.message}`);
    }
}

// Fonction de logout
function logout() {
    currentUser = null;
    authCredentials = null;
    localStorage.removeItem('authCredentials');
    localStorage.removeItem('currentUser');
    
    document.getElementById('user-info').style.display = 'none';
    document.getElementById('login-btn').style.display = 'block';
    
    alert('✅ Déconnecté avec succès');
    
    // Recharger si on est sur transport
    const activeSection = document.querySelector('.service-section.active');
    if (activeSection && activeSection.id === 'transport') {
        loadTransports();
    }
}

// Afficher les infos utilisateur
function showUserInfo(user) {
    document.getElementById('login-btn').style.display = 'none';
    const userInfo = document.getElementById('user-info');
    userInfo.style.display = 'flex';
    
    const roleIcon = user.role === 'admin' ? '👨‍💼' : '👤';
    const roleText = user.role === 'admin' ? 'Administrateur' : 'Citoyen';
    
    document.getElementById('user-name').textContent = user.full_name;
    document.getElementById('user-role').innerHTML = `${roleIcon} ${roleText}`;
}

// Afficher le modal de login
function showLoginModal() {
    document.getElementById('login-modal').style.display = 'flex';
}

// Cacher le modal de login
function hideLoginModal() {
    document.getElementById('login-modal').style.display = 'none';
    document.getElementById('login-username').value = '';
    document.getElementById('login-password').value = '';
}

// Vérifier si l'utilisateur est admin
function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// Wrapper pour les requêtes authentifiées
async function authenticatedFetch(url, options = {}) {
    if (authCredentials) {
        options.headers = options.headers || {};
        options.headers['Authorization'] = `Basic ${authCredentials}`;
    }
    return fetch(url, options);
}

// Restaurer la session au chargement
window.addEventListener('DOMContentLoaded', () => {
    const savedCredentials = localStorage.getItem('authCredentials');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedCredentials && savedUser) {
        authCredentials = savedCredentials;
        currentUser = JSON.parse(savedUser);
        showUserInfo(currentUser);
    }
});
