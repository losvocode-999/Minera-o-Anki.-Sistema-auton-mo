import sys
import os
import genanki
from gtts import gTTS
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QLineEdit, QLabel

class AnkiCardGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.deckNameLabel = QLabel('Nome do baralho existente:')
        layout.addWidget(self.deckNameLabel)

        self.deckNameInput = QLineEdit()
        self.deckNameInput.setPlaceholderText('Deixe em branco para criar um novo baralho')
        layout.addWidget(self.deckNameInput)

        self.textEdit = QTextEdit()
        self.textEdit.setPlaceholderText("Insira suas frases aqui, uma por linha, no formato:\n\nPalavra: Tradução1, Tradução2, Tradução3\nFrase em inglês com a palavra.")
        layout.addWidget(self.textEdit)

        self.generateButton = QPushButton('Gerar Arquivo Anki')
        self.generateButton.clicked.connect(self.generate_anki_file)
        layout.addWidget(self.generateButton)

        self.setLayout(layout)
        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('Gerador de Cards Anki')
        self.show()

    def generate_anki_file(self):
        text = self.textEdit.toPlainText()
        phrases = text.split('\n\n')
        if not phrases:
            QMessageBox.warning(self, "Erro", "Por favor, insira algumas frases.")
            return

        deck_name = self.deckNameInput.text().strip() or "Frases em Inglês com Áudio"

        try:
            self.create_anki_deck(phrases, deck_name)
            QMessageBox.information(self, "Sucesso", f"Arquivo 'frases_ingles.apkg' gerado com sucesso para o baralho '{deck_name}'!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def create_anki_deck(self, phrases, deck_name):
        model = genanki.Model(
            1607392319,
            'Frases com Áudio',
            fields=[
                {'name': 'Frase'},
                {'name': 'Áudio'},
                {'name': 'Tradução'}
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '<div style="text-align: center; font-size: 20px;">{{Frase}}</div><br>{{Áudio}}',
                    'afmt': '{{FrontSide}}<hr id="answer"><div style="text-align: center; font-size: 20px;">{{Tradução}}</div>',
                },
            ])

        deck = genanki.Deck(2059400110, deck_name)
        media_files = []

        for i, phrase in enumerate(phrases, 1):
            lines = phrase.split('\n')
            if len(lines) != 2:
                raise ValueError(f"Formato inválido na frase {i}")

            word_def, sentence = lines
            word, translations = word_def.split(': ')
            translations = translations.split(', ')

            # Destacar a palavra em negrito na frase
            highlighted_sentence = sentence.replace(word, f'<b>{word}</b>')

            # Gerar áudio
            tts = gTTS(sentence, lang='en')
            audio_file = f'audio_{i}.mp3'
            tts.save(audio_file)
            media_files.append(audio_file)

            # Criar nota
            note = genanki.Note(
                model=model,
                fields=[highlighted_sentence, f'[sound:{audio_file}]', f'{word}: {", ".join(translations)}']
            )

            deck.add_note(note)

        # Gerar pacote Anki
        package = genanki.Package(deck)
        package.media_files = media_files
        package.write_to_file('frases_ingles.apkg')

        # Limpar arquivos de áudio
        for file in media_files:
            os.remove(file)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnkiCardGenerator()
    sys.exit(app.exec_())