from flask import Flask, render_template, request, jsonify
import random
import re
import time
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre-cle-secrete-super-securisee'

# Télécharger les données NLTK nécessaires (silencieux)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class LetterProcessor:
    """Traite le texte de la lettre et gère le découpage en blocs et phrases."""

    @staticmethod
    def split_into_sentences(text):
        text = text.strip()
        if not text:
            return []

        try:
            sentences = sent_tokenize(text, language='french')
            return [s.strip() for s in sentences if s.strip()]
        except Exception:
            parts = re.split(r'([.?!:;])\s*', text)
            sentences = []
            for i in range(0, len(parts), 2):
                sentence = parts[i].strip()
                if sentence:
                    if i + 1 < len(parts):
                        sentence += parts[i + 1]
                    sentences.append(sentence.strip())
            return [s for s in sentences if s]

    @staticmethod
    def process_letter(raw_text):
        if not raw_text or not raw_text.strip():
            return {'blocks': []}

        major_blocks = [block.strip() for block in raw_text.split('\n\n') if block.strip()]

        if len(major_blocks) < 2:
            return {'blocks': [], 'error': 'Séparez les blocs par une ligne vide'}

        blocks = []
        for block_index, block_text in enumerate(major_blocks):
            block_type = LetterProcessor._detect_block_type(block_text)
            sentences = LetterProcessor.split_into_sentences(block_text)

            sentence_objects = [
                {'id': f"{block_index + 1}-{s_id + 1}", 'text': sentence}
                for s_id, sentence in enumerate(sentences)
            ]

            blocks.append({
                'id': block_index + 1,
                'type': block_type,
                'full_text': block_text,
                'sentences': sentence_objects
            })

        return {'blocks': blocks}

    @staticmethod
    def _detect_block_type(text):
        text_lower = text.lower()

        try:
            tokens = word_tokenize(text_lower, language='french')
            je_pronouns = {'je', 'j', 'me', 'moi', 'mon', 'ma', 'mes', 'm'}
            nous_pronouns = {'nous', 'notre', 'nos'}
            vous_pronouns = {'vous', 'votre', 'vos'}

            je_count = sum(1 for token in tokens if token in je_pronouns)
            nous_count = sum(1 for token in tokens if token in nous_pronouns)
            vous_count = sum(1 for token in tokens if token in vous_pronouns)

        except Exception:
            je_count = len(re.findall(r"\b(je|j'|me|moi|mon|ma|mes)\b", text_lower))
            nous_count = len(re.findall(r'\b(nous|notre|nos)\b', text_lower))
            vous_count = len(re.findall(r'\b(vous|votre|vos)\b', text_lower))

        if je_count >= nous_count and je_count >= vous_count:
            return 'je'
        elif nous_count >= vous_count:
            return 'nous'
        else:
            return 'vous'


# In-memory storage for current exercise
current_exercise = {
    'blocks': [],
    'shuffled_blocks': []
}

# In-memory storage for student scores and timer
student_scores = {}  # {nickname: {'score': int, 'time_taken': float, 'completed_at': timestamp}}
timer_config = {
    'duration': 300,  # Default 5 minutes in seconds
    'started_at': None,
    'is_active': False
}


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/professor')
def professor():
    return render_template('professor.html')


@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Validate admin password"""
    data = request.get_json()
    password = data.get('password', '')
    
    # Admin password validation
    if password == 'admin123':
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Mot de passe incorrect'}), 401


@app.route('/student')
def student():
    return render_template('student.html')


@app.route('/api/process', methods=['POST'])
def process_letter():
    global current_exercise
    data = request.get_json()
    raw_text = data.get('text', '')

    result = LetterProcessor.process_letter(raw_text)

    if 'error' in result:
        return jsonify({'error': result['error']}), 400

    shuffled_blocks = result['blocks'][:]
    random.shuffle(shuffled_blocks)

    for block in shuffled_blocks:
        block['sentences'] = block['sentences'][:]
        random.shuffle(block['sentences'])

    # Store globally for student access
    current_exercise = {
        'blocks': result['blocks'],
        'shuffled_blocks': shuffled_blocks
    }

    return jsonify({
        'blocks': result['blocks'],
        'shuffled_blocks': shuffled_blocks,
        'success': True
    })


@app.route('/api/get-exercise', methods=['GET'])
def get_exercise():
    """Endpoint for students to get the current exercise"""
    if not current_exercise['blocks']:
        return jsonify({'error': 'Aucun exercice disponible'}), 404

    return jsonify({
        'shuffled_blocks': current_exercise['shuffled_blocks'],
        'available': True
    })


@app.route('/api/verify', methods=['POST'])
def verify_letter():
    global current_exercise
    data = request.get_json()
    submitted_blocks = data.get('blocks', [])
    original_blocks = current_exercise.get('blocks', [])

    if not original_blocks:
        return jsonify({'error': 'Aucun exercice actif'}), 400

    correct_block_order = 0
    correct_sentence_orders = 0

    original_block_map = {block['id']: block for block in original_blocks}

    # Check if all blocks are placed
    if len(submitted_blocks) != len(original_blocks):
        return jsonify({
            'error': 'Placez tous les blocs avant de vérifier',
            'correct_blocks': 0,
            'total_blocks': len(original_blocks),
            'correct_sentence_orders': 0
        }), 400

    for i, submitted_block in enumerate(submitted_blocks):
        # Check block order
        if i < len(original_blocks) and submitted_block['id'] == original_blocks[i]['id']:
            correct_block_order += 1

        # Check sentence order within block
        if submitted_block['id'] in original_block_map:
            original_sentences = [s['id'] for s in original_block_map[submitted_block['id']]['sentences']]
            submitted_sentence_ids = [s['id'] for s in submitted_block['sentences']]

            if original_sentences == submitted_sentence_ids:
                correct_sentence_orders += 1

    return jsonify({
        'correct_blocks': correct_block_order,
        'total_blocks': len(original_blocks),
        'correct_sentence_orders': correct_sentence_orders,
        'all_correct': correct_block_order == len(original_blocks) and correct_sentence_orders == len(original_blocks)
    })


@app.route('/api/timer/set', methods=['POST'])
def set_timer():
    """Set the timer duration (admin only)"""
    global timer_config
    data = request.get_json()
    duration = data.get('duration', 300)  # Default 5 minutes
    
    if not isinstance(duration, int) or duration < 10:
        return jsonify({'error': 'Durée invalide (minimum 10 secondes)'}), 400
    
    timer_config['duration'] = duration
    timer_config['started_at'] = None
    timer_config['is_active'] = False
    
    return jsonify({
        'success': True,
        'duration': duration
    })


@app.route('/api/timer/start', methods=['POST'])
def start_timer():
    """Start the timer (admin only)"""
    global timer_config, student_scores
    
    # Reset student scores when starting a new timer
    student_scores = {}
    
    timer_config['started_at'] = time.time()
    timer_config['is_active'] = True
    
    return jsonify({
        'success': True,
        'started_at': timer_config['started_at'],
        'duration': timer_config['duration']
    })


@app.route('/api/timer/stop', methods=['POST'])
def stop_timer():
    """Stop the timer (admin only)"""
    global timer_config
    
    timer_config['is_active'] = False
    
    return jsonify({
        'success': True
    })


@app.route('/api/timer/status', methods=['GET'])
def get_timer_status():
    """Get current timer status"""
    global timer_config
    
    remaining = 0
    if timer_config['is_active'] and timer_config['started_at']:
        elapsed = time.time() - timer_config['started_at']
        remaining = max(0, timer_config['duration'] - elapsed)
        
        # Auto-stop timer if expired
        if remaining <= 0:
            timer_config['is_active'] = False
    
    return jsonify({
        'is_active': timer_config['is_active'],
        'duration': timer_config['duration'],
        'remaining': int(remaining),
        'started_at': timer_config['started_at']
    })


@app.route('/api/score/submit', methods=['POST'])
def submit_score():
    """Submit a student's score"""
    global student_scores, timer_config
    
    data = request.get_json()
    nickname = data.get('nickname', '').strip()
    score = data.get('score', 0)
    
    if not nickname:
        return jsonify({'error': 'Surnom requis'}), 400
    
    # Calculate time taken
    time_taken = 0
    if timer_config['started_at']:
        time_taken = time.time() - timer_config['started_at']
    
    # Store or update score (keep best score)
    if nickname not in student_scores or score > student_scores[nickname]['score']:
        student_scores[nickname] = {
            'score': score,
            'time_taken': time_taken,
            'completed_at': time.time()
        }
    
    return jsonify({
        'success': True,
        'score': score,
        'time_taken': time_taken
    })


@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the leaderboard with student scores"""
    global student_scores
    
    # Sort by score (descending), then by time_taken (ascending)
    sorted_scores = sorted(
        student_scores.items(),
        key=lambda x: (-x[1]['score'], x[1]['time_taken'])
    )
    
    leaderboard = [
        {
            'rank': i + 1,
            'nickname': nickname,
            'score': data['score'],
            'time_taken': round(data['time_taken'], 1)
        }
        for i, (nickname, data) in enumerate(sorted_scores)
    ]
    
    return jsonify({
        'leaderboard': leaderboard,
        'total_students': len(student_scores)
    })


@app.route('/api/leaderboard/reset', methods=['POST'])
def reset_leaderboard():
    """Reset the leaderboard (admin only)"""
    global student_scores
    student_scores = {}
    
    return jsonify({
        'success': True
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
