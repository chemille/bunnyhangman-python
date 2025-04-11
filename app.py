from flask import Flask, render_template, request, session, redirect, url_for
import requests

app = Flask(__name__)
# setting up secret key for session mgmt
app.secret_key = 'MY_SECRET_KEY'  

API_URL = 'https://random-word-api.vercel.app/api?words=1&type=uppercase' 
# &length=9 optional
# &type default lowercase

def fetch_random_word():
    response = requests.get(API_URL)
    if response.status_code == 200:
        print(response)        
        return response.json()[0]
    return None

BUNNY_HANGMAN = {
    0: '⠀⢀⣀⠀⠀⠀⠀⠀⢀⣀⠀',
    1: '⢠⣯⢬⣷⡀⠀⠀⣴⡯⢌⣧',
    2: '⠸⣿⠀⠹⣷⠀⢸⡝⠀⢸⡿',
    3: '⠀⠻⣧⣀⣿⣦⣼⡁⣠⣿⠃',
    4: '⠀⢀⡾⠋⠀⠀⠀⠈⣙⣯⠀',
    5: '⠀⣾⠀⠀⠀⠀⠀⠀⠀⠸⡆',
    6: '⢰⡧⢄⢰⡆⠀⢰⡆⡠⢄⣧',
    7: '⠀⠳⣼⣤⣤⣤⣤⣤⣧⠾⠁',
}

@app.route('/')
def index():
    if 'word' not in session:
        session['word'] = fetch_random_word()
        session['guesses'] = []
        session['wrong_guesses'] = 0 
        session['message'] = ''
    # string_display = BUNNY_HANGMAN.get(session['wrong_guesses'], "") # THIS DISPLAYS ONE STRING AT A TIME

    # word_display = ""
    # for char in session['word']:
    #     if char in session['guesses']:
    #         word_display += char
    #     else:
    #         word_display += '_ '

    word_display = ''.join([char if char in session['guesses'] else '_ ' for char in session['word']])

    remaining_guesses = 7
    valid_guesses = []

    # picture_display = []
    
    # for key in BUNNY_HANGMAN:
    #     if key in range(1, session['wrong_guesses'] + 1):   
    #         picture_display.append(BUNNY_HANGMAN[key])

    picture_display = [BUNNY_HANGMAN[key] for key in BUNNY_HANGMAN if key in range(1, session['wrong_guesses'] + 1)]
    
    remaining_guesses -= len(picture_display)

    for letter in session['guesses']:
        if letter.isalpha() and letter not in session['word']:
            valid_guesses.append(letter)

    return render_template('index.html', valid_guesses=valid_guesses, remaining_guesses=remaining_guesses, picture_display=picture_display, word_display=word_display, guesses=session['guesses'], wrong_guesses=session['wrong_guesses'], message=session.get('message', ''))

## Need to reset after every session, so if user hits reset it will return to index.html
@app.route('/reset')
def reset():
    session.pop('word', None)
    session.pop('guesses', None)
    session.pop('wrong_guesses', None)
    session.pop('message', None)
    return redirect(url_for('index'))

@app.route('/guess', methods=['POST'])
def guess():
    guess = request.form['guess'].upper()
    
    if guess not in session['guesses']:
        session['guesses'].append(guess)
        if guess in session['word']:
            session['message'] = f'Great guess! "{guess}" is in the word!'
        elif not guess.isalpha():
            session['message'] = f'"{guess}" is not valid. Guess a letter.'
        else: 
            session['wrong_guesses'] += 1
            session['message'] = f'Sorry, "{guess}" is not in the word.'
    else: 
        session['message'] = f'You already guessed "{guess}".'
        if not guess.isalpha():
            session['message'] = f'"{guess}" is invalid. Must be a letter.'

    return redirect(url_for('index')) # This is keeping everything on the same page by doing it through links and redirects. So it won't be asynchronous, it'll be a one page web app.


if __name__ == '__main__':
    app.run(debug=True)
