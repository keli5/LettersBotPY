import markovify


class CharacterText(markovify.NewlineText):
    def word_split(self, sentence):
        return list(sentence)

    def word_join(self, words):
        return "".join(words)
