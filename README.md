# Exercice de Lettre de Motivation - Puzzle Hiérarchique

Application Flask pour un exercice pédagogique de reconstruction de lettres de motivation.

## Fonctionnalités

### Niveau 1 : Organisation des Blocs
- **Détection automatique** des blocs "Je", "Nous", "Vous" basée sur l'analyse des pronoms
- **Drag & Drop** des blocs dans les zones correspondantes de la lettre
- Interface avec 3 sections : Je (Introduction personnelle), Nous (Contexte partagé), Vous (Destinataire)

### Niveau 2 : Ordre des Phrases
- Chaque bloc peut être édité pour **réordonner les phrases**
- Modal d'édition avec drag & drop et boutons de déplacement
- Validation de l'ordre des phrases

### Mode Enseignant
- Zone de saisie pour coller le texte de la lettre
- Séparation automatique en blocs (par ligne vide)
- Génération du puzzle avec mélange aléatoire

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Lancer l'application :
```bash
python app.py
```

3. Ouvrir le navigateur à l'adresse :
```
http://localhost:5000
```

## Utilisation

### Pour l'Enseignant

1. **Préparer le texte** : 
   - Coller la lettre dans la zone "Zone Enseignant"
   - Séparer les différents paragraphes/sections par **une ligne vide** (`\n\n`)
   
2. **Exemple de format** :
```
[Vos coordonnées]

Je me permets de solliciter l'attribution d'une bourse. Ma situation financière nécessite un soutien.

Nous avons constaté que votre fondation soutient les étudiants. Nous serions honorés de bénéficier de votre aide.

Vous trouverez ci-joint mon dossier complet. Votre réponse sera précieuse pour mon avenir.
```

3. Cliquer sur **"Générer le Puzzle"**

### Pour l'Étudiant

1. **Étape 1 - Organiser les blocs** :
   - Glisser les blocs mélangés depuis la zone "Blocs à Organiser"
   - Les déposer dans les sections appropriées (Je, Nous, Vous)
   - Respecter l'ordre logique de la lettre

2. **Étape 2 - Ordonner les phrases** :
   - Cliquer sur "✏️ Ordonner les Phrases" pour chaque bloc
   - Réorganiser les phrases dans l'ordre correct
   - Valider l'ordre

3. **Vérification** :
   - Cliquer sur "✓ Vérifier l'Ordre" pour valider l'exercice
   - Le système indique le nombre de blocs correctement placés

## Architecture

### Backend (Flask)
- `app.py` : Application Flask principale
  - `/` : Page d'accueil
  - `/api/process` : Traitement du texte et génération du puzzle
  - `/api/verify` : Vérification de l'ordre des blocs

### Frontend
- `templates/index.html` : Interface utilisateur complète
  - Zone enseignant (saisie du texte)
  - Zone des blocs mélangés
  - Template de lettre avec sections Je/Nous/Vous
  - Modal d'édition des phrases
  - Drag & Drop interactif

## Détection des Types de Blocs

L'application détecte automatiquement le type de chaque bloc :
- **"Je"** : Présence de pronoms personnels (je, j', me, moi, mon, ma, mes)
- **"Nous"** : Présence de pronoms collectifs (nous, notre, nos)
- **"Vous"** : Présence de pronoms de politesse (vous, votre, vos)

Le type dominant détermine la catégorie du bloc.

## Technologies Utilisées

- **Backend** : Flask (Python)
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Features** : Drag & Drop API, Fetch API, Responsive Design

## Personnalisation

### Modifier les couleurs
Les couleurs sont définies dans les variables CSS (`:root` dans le `<style>`).

### Ajouter des types de blocs
Modifier la fonction `_detect_block_type()` dans `app.py` et ajouter les sections correspondantes dans le template HTML.

## Notes Pédagogiques

Cet exercice développe :
- La **cohérence textuelle** (ordre logique des idées)
- La **structure** d'une lettre formelle (Je → Nous → Vous)
- La **cohésion** interne des paragraphes

## Licence

Libre d'utilisation à des fins pédagogiques.

