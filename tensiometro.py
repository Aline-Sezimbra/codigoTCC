from machine import Pin, ADC, RTC
from time import sleep_ms, ticks_ms, ticks_add, ticks_diff
from umqtt.simple import MQTTClient
from network import STA_IF, WLAN
from ujson import dumps,load
import ntptime
import ina219

arquivo = open("config.json", "r")
config = load(arquivo)
arquivo.close()

pressao = ADC(Pin(34))

ina = ina219.INA219()

rtc = RTC()
relogio = rtc.datetime()

#conexao e envio dos dados
def ativaWifi (rede, senha):
  wifi = WLAN(STA_IF)
  wifi.active(True)
  if not wifi.isconnected():
    wifi.connect(rede, senha)
    tentativas = 0
    while not wifi.isconnected() and tentativas < 10:
      sleep_ms(1000)
      tentativas += 1
  return wifi if wifi.isconnected() else None

def conectaTB(client):
  cliente.connect()
  if cliente.connect() >= 0:
    tentativas = 0
    while cliente.connect() < 0 and tentativas < 10:
      cliente.connect()
      sleep_ms(1000)
      tentativas += 1
  return cliente if cliente.connect() else None

#dados do cliente 
client_id = 'tensiometro'
broker = 'demo.thingsboard.io'
port = 1883
password = ''
user = 'ErURKNlxf8smWIHdvGh6'
cliente = MQTTClient(client_id, broker, 1883, user, password)

network = config["ssid"]
password = config["pass"]

rede = ativaWifi (network, password)
thingsboard = conectaTB (cliente)

topicoEnvio = b'v1/devices/me/telemetry'

horarios = config["horas"]

futuro = ticks_ms()

#config. de sincronização
while True:
    if relogio[4] == 0 and relogio[5] == 0 and relogio[6] == 0:
        ntptime.settime()
        relogio = rtc.datetime()
        
    for hora in horarios:
        if relogio[4] == hora and relogio[5] == 0 and relogio[6] == 0:
            x = ina.read() #controle do nível de bateria
            calc = (x[1])/config["bateria"]
            data = {'TENSAO': calc}
            data_s = dumps(data)
            cliente.publish(topicoEnvio, data_s)
            print(data_s)
        
        for i in range(30):
            if ticks_diff(ticks_ms(),futuro) > 0:
                x = pressao.read()
                valor = -0.0391*x + 20.241 #ajuste da eq
                dado = {'PRESSAO': valor} 
                dado_s = dumps(dado)
                cliente.publish(topicoEnvio, dado_s)
                futuro = ticks_add (ticks_ms(), 2000)
