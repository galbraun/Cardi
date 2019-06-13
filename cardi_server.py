from telegram.ext import Updater
import logging
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import json
import ibm_watson
import soundfile as sf
from ibm_watson import SpeechToTextV1
from os.path import join

def parse_ogg_to_flac(ogg_path):
    data, samplerate = sf.read(ogg_path)
    sf.write('new_file.flac', data, samplerate)

################ TELEGRAM STUFF #################################
TELEGRAM_TOKEN_PATH = 'telegram_bot_token'
TELEGRAM_TOKEN = open(TELEGRAM_TOKEN_PATH).read()

updater = Updater(token=TELEGRAM_TOKEN)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#####################################################

################# WATSON STUFF ####################################
ASSISTANT_ID = '9bf907c5-b91d-47f1-bb1a-b58803b4d01e'
IAM_APIKEY_PATH = 'watson_iam_apikey'
IAM_APIKEY = open(IAM_APIKEY_PATH).read()
S2T_APIKEY_PATH = 'speech_to_text_watson_apikey'
S2T_APIKEY = open(S2T_APIKEY_PATH).read()

# speech to text
speech_to_text = SpeechToTextV1(
    iam_apikey=S2T_APIKEY,
    url='https://gateway-lon.watsonplatform.net/speech-to-text/api'
)

# assistant
service = ibm_watson.AssistantV2(
    iam_apikey=IAM_APIKEY,
    version='2019-02-28',
    url='https://gateway-lon.watsonplatform.net/assistant/api'
)

response = service.create_session(
    assistant_id=ASSISTANT_ID
).get_result()

print(response)

SESSION_ID = response['session_id']
print('Session ID: {}'.format(SESSION_ID))
###############################################################

#def start(bot, update):
#    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
#start_handler = CommandHandler('start', start)
#dispatcher.add_handler(start_handler)


def assisant_voice_communication(bot, update):
    print('lalalalalalal')
    telegram_file = update.message.voice.get_file()
    custom_path = join(r'C:\users\galb', 'Cardi_voice.ogg')
    telegram_file.download(custom_path=custom_path)
    with open(custom_path, 'rb') as audio_file:
        speech_recognition_results = speech_to_text.recognize(
            audio=audio_file,
            content_type='audio/ogg',
            word_alternatives_threshold=0.9,
            keywords=['colorado', 'tornado', 'tornadoes'],
            keywords_threshold=0.5
        ).get_result()
    audio_transcript = speech_recognition_results['results'][0]['alternatives'][0]['transcript']
    print(speech_recognition_results)
    print(audio_transcript)
    response = service.message(
        assistant_id=ASSISTANT_ID,
        session_id=SESSION_ID,
        input={
            'message_type': 'text',
            'text': audio_transcript
        }
    ).get_result()
    bot.send_message(chat_id=update.message.chat_id, text=response['output']['generic'][0]['text'])

def assisant_text_communication(bot, update):
    response = service.message(
        assistant_id=ASSISTANT_ID,
        session_id=SESSION_ID,
        input={
            'message_type': 'text',
            'text': update.message.text.lower()
        }
    ).get_result()
    bot.send_message(chat_id=update.message.chat_id, text=response['output']['generic'][0]['text'])


bot_text_handler = MessageHandler(Filters.text, assisant_text_communication)
bot_audio_handler = MessageHandler(Filters.voice, assisant_voice_communication)
dispatcher.add_handler(bot_text_handler)
dispatcher.add_handler(bot_audio_handler)


updater.start_polling()

