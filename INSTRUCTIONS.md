# 🎓 Système Multi-Utilisateurs - Exercice Lettre

## ✅ Ce qui a été implémenté

### Backend (app.py)
- ✅ Système d'authentification : "admin" pour le professeur, nom libre pour les étudiants
- ✅ Gestion des sessions avec Flask sessions
- ✅ WebSocket avec Flask-SocketIO pour communication temps réel
- ✅ Endpoints pour login, admin, student
- ✅ Système de timer synchronisé
- ✅ Classement en temps réel des étudiants

### Pages créées
1. **login.html** - Page de connexion pour tout le monde
2. **admin.html** - Interface professeur (copie de index.html à modifier)
3. **student.html** - Interface étudiant (copie de index.html à modifier)

## 📋 Ce qu'il reste à faire

### 1. Modifier admin.html
Ajouter après le `<header>` :

```html
<!-- Panneau de contrôle Admin -->
<div class="admin-controls" style="background: white; padding: 25px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08);">
    <h2>🎮 Panneau de Contrôle</h2>
    
    <!-- Timer Controls -->
    <div style="display: flex; gap: 15px; margin-bottom: 20px; align-items: center;">
        <label>Durée (minutes) :</label>
        <input type="number" id="timer-duration" value="5" min="1" max="60" 
               style="padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; width: 100px;">
        <button onclick="startTimer()" class="btn">⏱️ Démarrer le Timer</button>
        <button onclick="stopTimer()" class="btn btn-secondary">⏹️ Arrêter</button>
        <span id="timer-display" style="font-size: 1.5rem; font-weight: bold; margin-left: 20px;">--:--</span>
    </div>
    
    <!-- Students List -->
    <div>
        <h3>👥 Étudiants Connectés: <span id="student-count">0</span></h3>
        <div id="students-list" style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;"></div>
    </div>
    
    <!-- Leaderboard -->
    <div style="margin-top: 20px;">
        <h3>🏆 Classement</h3>
        <div id="leaderboard"></div>
    </div>
</div>
```

Ajouter avant `</body>` :

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
    const socket = io();
    let timerInterval = null;
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('user_joined', (data) => {
        if (data.role === 'student') {
            updateStudentsList();
        }
    });
    
    socket.on('leaderboard_update', (data) => {
        displayLeaderboard(data);
    });
    
    function startTimer() {
        const duration = parseInt(document.getElementById('timer-duration').value) * 60;
        socket.emit('start_timer', { duration });
        
        let remaining = duration;
        timerInterval = setInterval(() => {
            remaining--;
            const minutes = Math.floor(remaining / 60);
            const seconds = remaining % 60;
            document.getElementById('timer-display').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            if (remaining <= 0) {
                clearInterval(timerInterval);
                stopTimer();
            }
        }, 1000);
    }
    
    function stopTimer() {
        socket.emit('stop_timer');
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        document.getElementById('timer-display').textContent = 'TERMINÉ';
    }
    
    function displayLeaderboard(leaderboard) {
        const container = document.getElementById('leaderboard');
        if (!leaderboard || leaderboard.length === 0) {
            container.innerHTML = '<p style="color: #999;">Aucun étudiant n\'a terminé</p>';
            return;
        }
        
        let html = '<table style="width: 100%; border-collapse: collapse;">';
        html += '<tr style="background: #f0f2f5;"><th style="padding: 10px;">Rang</th><th>Nom</th><th>Temps</th></tr>';
        
        leaderboard.forEach((student, index) => {
            html += `<tr style="border-bottom: 1px solid #e0e0e0;">
                <td style="padding: 10px; text-align: center;">${index + 1}</td>
                <td style="padding: 10px;">${student.username}</td>
                <td style="padding: 10px;">${student.time}</td>
            </tr>`;
        });
        
        html += '</table>';
        container.innerHTML = html;
    }
    
    // Modifier generatePuzzle pour envoyer aux étudiants
    async function generatePuzzle() {
        const rawText = document.getElementById('raw-text-input').value;
        
        if (!rawText.trim()) {
            alert('Veuillez saisir un texte !');
            return;
        }
        
        try {
            const response = await fetch('/api/process', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: rawText })
            });
            
            if (!response.ok) {
                const error = await response.json();
                alert(error.error || 'Erreur lors du traitement');
                return;
            }
            
            const result = await response.json();
            alert('✅ Lettre envoyée à tous les étudiants !');
            
            // Masquer la zone enseignant
            document.getElementById('teacher-workspace').style.display = 'none';
        } catch (error) {
            console.error('Erreur:', error);
            alert('Erreur de connexion au serveur');
        }
    }
</script>
```

### 2. Modifier student.html

Remplacer le header par :

```html
<header>
    <h1>📝 Exercice : Reconstruire la Lettre</h1>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
        <p class="instruction">
            <strong>Objectif :</strong>
            Organisez les blocs dans le bon ordre avant la fin du temps !
        </p>
        <div id="timer-student" style="font-size: 2rem; font-weight: bold; color: #f44336;">--:--</div>
    </div>
</header>
```

Supprimer la section "teacher-zone" complètement.

Ajouter avant `</body>` :

```html
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
    const socket = io();
    let timerInterval = null;
    
    socket.on('connect', () => {
        console.log('Connected to server');
    });
    
    socket.on('letter_received', (data) => {
        puzzleData = data;
        correctBlockOrder = data.original_order;
        
        // Afficher la zone puzzle
        document.getElementById('puzzle-workspace').style.display = 'grid';
        
        // Mélanger les phrases dans chaque bloc
        for (let i = 0; i < puzzleData.blocks.length; i++) {
            puzzleData.blocks[i] = LetterProcessor.shuffle_sentences_in_block(puzzleData.blocks[i]);
        }
        
        displayBlocks(puzzleData.blocks);
        
        document.getElementById('verify-btn').disabled = false;
        document.getElementById('reset-btn').disabled = false;
        
        updateStatus('🎯 Puzzle reçu ! Commencez à organiser les blocs.');
    });
    
    socket.on('timer_started', (data) => {
        let remaining = data.duration;
        
        timerInterval = setInterval(() => {
            remaining--;
            const minutes = Math.floor(remaining / 60);
            const seconds = remaining % 60;
            document.getElementById('timer-student').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Changer la couleur quand il reste moins d'1 minute
            if (remaining < 60) {
                document.getElementById('timer-student').style.color = '#f44336';
            }
            
            if (remaining <= 0) {
                clearInterval(timerInterval);
                document.getElementById('timer-student').textContent = 'TEMPS ÉCOULÉ';
                alert('⏰ Le temps est écoulé !');
            }
        }, 1000);
    });
    
    socket.on('timer_stopped', () => {
        if (timerInterval) {
            clearInterval(timerInterval);
        }
        alert('⏹️ Le professeur a arrêté le chronom\u00e8tre');
    });
    
    socket.on('leaderboard_update', (data) => {
        // Optionnel : afficher le classement aux étudiants
        console.log('Classement mis à jour:', data);
    });
    
    // Supprimer la fonction generatePuzzle (les étudiants ne peuvent pas générer)
</script>
```

## 🚀 Comment utiliser

### Étape 1 : Démarrer le serveur
```bash
python app.py
```

### Étape 2 : Le professeur se connecte
1. Aller sur http://localhost:5000
2. Entrer "admin" comme nom
3. Arriver sur la page admin

### Étape 3 : Les étudiants se connectent
1. Aller sur http://localhost:5000
2. Entrer un nom d'utilisateur (ex: "Marie", "Ahmed", etc.)
3. Arriver sur la page étudiant

### Étape 4 : Déroulement de la session
1. Le professeur colle le texte de la lettre et clique "Générer le Puzzle"
2. Tous les étudiants reçoivent la lettre mélangée automatiquement
3. Le professeur lance le chronomètre (ex: 5 minutes)
4. Les étudiants travaillent sur leur lettre
5. Le premier à finir correctement est en tête du classement
6. Le professeur voit le classement en temps réel

## 📦 Déploiement sur PythonAnywhere

1. Uploader tous les fichiers
2. Dans le fichier WSGI, utiliser :
```python
from app import app, socketio

application = app
```

3. Activer Always On pour les WebSockets
4. Configurer les variables d'environnement si nécessaire

## ⚠️ Notes importantes

- Les sessions sont stockées en mémoire (perdu au redémarrage)
- Pour production : utiliser Redis pour stocker les sessions
- Le système supporte UNE session active à la fois
- Pour multi-sessions : modifier la logique de `current_session_id`
