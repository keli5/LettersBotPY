import markovify
import random


# class CharacterText(markovify.NewlineText):| this is what we used to use
#     def word_split(self, sentence):
#         return list(sentence)
#
#     def word_join(self, words):
#         return "".join(words)

class CharacterText(markovify.NewlineText):
    def word_split(self, sentence):
        n = random.choice([2, 3])
        return [sentence[i:i+n] for i in range(0, len(sentence), n)]

    def word_join(self, words):
        return "".join(words)
