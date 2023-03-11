from mtranslate import translate
import openai
import requests
from playsound import playsound
import wave, struct
from pydub import AudioSegment
from pydub.playback import play
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import cv2
import numpy as np
from datetime import datetime
from multiprocessing import Process
import speech_recognition as sr

# firebase
cred = credentials.Certificate("D:\tomodachi-prototype in cmd\\ai-chan-3074e-firebase-adminsdk-8sgnr-2a8bbe6e28.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://ai-chan-3074e-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference('/')

#Open ai
openai.api_key = "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"
model_engine = "text-davinci-003"

#tem
tem_api_key = "0bddcc3609d450dc7d5264d45b10ab09"
city = "ubon ratchathani"
url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={tem_api_key}'
respon = requests.get(url).json()
des = respon['weather'][0]['description']
tem = respon['main']['temp'] - 273.15
dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
tem_result = f'%.2f / {des} | {dt_string}' %(tem)

while True :
  #spech to text
  r = sr.Recognizer()
  while True:
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.record(source, duration=3)

    try:
        user_input = r.recognize_google(audio, language='th')
        break
    except sr.UnknownValueError:
        print("Could not understand audio")
        continue

  prompt = translate(user_input, 'en')

  if user_input == 'เปิดไฟที่1' :
    response_output = "เปิดไฟที่1"
    ref.set({'iot_1': '1'}) 

  elif user_input == 'ปิดไฟที่1' :
    response_output = "ปิดไฟที่1"
    ref.set({'iot_1': '0'})

  completion = openai.Completion.create(
      engine=model_engine,
      prompt=prompt,
      max_tokens=1024,
      n=1,
      stop=None,
      temperature=0.5,
  )

  response = completion.choices[0].text
  response_output = translate(response , 'th')

  #vaja 
  url_vaja = 'https://api.aiforthai.in.th/vaja'
  
  headers_vaja = {'Apikey':'If66yNxYjCF1T5XtBgQ3k9VczUbHJn51','Content-Type' : 'application/x-www-form-urlencoded'}

  params_vaja = {'text':response_output,'mode':'st'}
  
  response_vaja = requests.get(url_vaja, params=params_vaja, headers=headers_vaja).json()

  result = response_vaja["output"]["audio"]["result"]
  numChanels = response_vaja["output"]["audio"]["numChannels"]
  validBits = response_vaja["output"]["audio"]["validBits"]
  sizeSample = response_vaja["output"]["audio"]["sizeSample"]
  sampleRate = response_vaja["output"]["audio"]["sampleRate"]
  
  obj = wave.open('sound.wav','wb') 
  obj.setparams((1, int(validBits/8), sampleRate, 0, 'NONE', 'not compressed'))
  for i in range(sizeSample):
    value = int(result[i])
    data = struct.pack('<h', value)  
    obj.writeframesraw(data)
  obj.close()

  sound = AudioSegment.from_wav('sound.wav')

  #sen
  url_sen = "https://api.aiforthai.in.th/ssense" 
  params_sen = {'text':response_output}
  
  headers_sen = {
      'Apikey': "If66yNxYjCF1T5XtBgQ3k9VczUbHJn51"
  }
  response_sen = requests.get(url_sen, headers=headers_sen, params=params_sen).json()
  polarity_score = response_sen['sentiment']['polarity']
  if polarity_score == '' :
      polarity_score = 'neutral'

  #out_put
  print(tem_result)
  print(f'{response_output} [{polarity_score}]')
  play(sound)