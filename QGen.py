import numpy as np
from pprint import pprint
from unidecode import unidecode
from keras.preprocessing.text import text_to_word_sequence
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.models import Sequential, Model
from keras.layers import Dense, Dropout, TimeDistributed, Bidirectional, Input, LSTM, RepeatVector, Activation, Flatten
from keras.optimizers import SGD
import json, os
from keras.layers import Embedding

#load the dataset
filepath = "../QueryDataSet/data_v4.json"
GLOVE_DIR = "/home/gaurav/Downloads/dataset/embeddings/glove.6B"
MAX_SEQUENCE_LENGTH = 1000
MAX_NB_WORDS = 20000
EMBEDDING_DIM = 200
num_layers = 2
hidden_size = 2

file = json.load(open(filepath))

#corrected_answer, verbalized_question

input_text = []
output_text = []

for quant in file:
	output_text.append(unidecode(quant["corrected_question"]))
	input_text.append(unidecode(quant["verbalized_question"]).replace(">","").replace("<",""))

#entire text.
text = " ".join(output_text+input_text)
# [['who is the pressdent ?'],['Who is the president ?']]

''' 
    Vocabulary building
'''

tokenizer = Tokenizer()
text_array = output_text+input_text
tokenizer.fit_on_texts(text_array)
word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))
MAX_SEQUENCE_LENGTH = max([ len(x.split()) for x in text_array ])
print MAX_SEQUENCE_LENGTH


x_seq = tokenizer.texts_to_sequences(input_text)
y_seq = tokenizer.texts_to_sequences(output_text)
x = pad_sequences(x_seq, maxlen=MAX_SEQUENCE_LENGTH)
y = pad_sequences(y_seq, maxlen=MAX_SEQUENCE_LENGTH)
x_train,x_test = x[:int(x.shape[0]*.80)],x[int(x.shape[0]*.80):]
print len(x_train)
y_train,y_test = y[:int(y.shape[0]*.80)],y[int(y.shape[0]*.80):]

print('Indexing word vectors.')
inverse_token_lookup = {}

for word in word_index:
    inverse_token_lookup[word_index[word]] = word

'''Word embedding'''
embeddings_index = {}
f = open(os.path.join(GLOVE_DIR, 'glove.6B.200d.txt'))
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

num_words = min(MAX_NB_WORDS, len(word_index))
embedding_matrix = np.zeros((num_words, EMBEDDING_DIM))
for word, i in word_index.items():
    if i >= MAX_NB_WORDS:
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # words not found in embedding index will be all-zeros.
		embedding_matrix[i] = embedding_vector
print embedding_matrix.shape

model = Sequential()
print len(word_index)
embedding_layer = Embedding(len(word_index),
                            EMBEDDING_DIM,
                            weights=[embedding_matrix],
                            input_length=MAX_SEQUENCE_LENGTH,
                            trainable=False,mask_zero=True)


model.add(embedding_layer)
model.add(LSTM(hidden_size))

#decoder

model.add(RepeatVector(MAX_SEQUENCE_LENGTH)) #repeate vector -: Repeats the input MAX_SEQUENCE_LENGTHtimes.
for _ in range(num_layers):
    model.add(LSTM(MAX_SEQUENCE_LENGTH, return_sequences=True))
model.add(TimeDistributed(Dense(MAX_SEQUENCE_LENGTH)))
model.add(Flatten())
model.add(Dense(MAX_SEQUENCE_LENGTH))
model.add(Activation('tanh'))
model.compile(loss='cosine_proximity',
            optimizer='sgd',
            metrics=['accuracy'])
model.summary()
model.fit(x_train, y_train, epochs=20, batch_size=400)

loss_and_metrics = model.evaluate(x_test, y_test, batch_size=998)
print loss_and_metrics

a = ['Where is the PM of America when?']
a = tokenizer.texts_to_sequences(a)
a = pad_sequences(a, maxlen=MAX_SEQUENCE_LENGTH)
print a
y = model.predict(a)
print y