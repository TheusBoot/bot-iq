import os
import math
from time import time,sleep
import sys
import numpy as np
from talib.abstract import *
#from threading import Timer
#from multiprocessing import Process
from datetime import datetime, timedelta
#from IPython.display import clear_output
from iqoptionapi.stable_api import IQ_Option
from multiprocessing import Process
from threading import Thread,Lock,get_ident


API = IQ_Option('xx','xx')
check_ = API.connect()
print(check_)
mode = "PRACTICE"
API.change_balance(mode)




def dir_log():
	try:
		dir_fpath = os.path.expanduser(r'~\AppData/Roaming\MetaQuotes\Terminal')
		dir_spath = [dir_fpath + '\\' + d for d in os.listdir( dir_fpath) if len(d) == 32][0]
		#dir_spath = [dir_fpath + '\\' + '98A82F92176B73A2100FCD1F8ABD7255']
		geral['dir'] = [dir_spath + '\\' + version + '\\files\\' for version in os.listdir(dir_spath) if 'MQL' in version][0]

	except Exception as e:
		print('erro',e)
		input('/ Aperte Enter para fechar')
		exit()


def retorno_ex():
	global geral
	try:
		if os.path.isfile(geral['dir'].replace('files','Indicators') + '/Retorno.ex4') == False:
			os.rename('Retorno.ex4',geral['dir'].replace('files','indicators') + '/Retorno.ex4')

	except:
		print('Não possivel veirifcar o arquivo')
		input('ERRO')
		exit()



def get_sinal():
	global geral

	sinais = []
	arq_sinais = geral['dir'] + datetime.now().strftime('%Y%m%d') + '_retorno.csv'
	try:
		file = open(arq_sinais, 'r').read()

	except Exception:
		file = open(arq_sinais, 'a').write('\n')
		file = ''

	par = 'EURUSD'
	timeframe = 1
	for index, sinal in enumerate(file.split('\n')):
		if len(sinal) > 0 and sinal != '':
			sinal_ = sinal.split(',')
			#print(sinal_)

			#TimeStamp, PARIDADE, CALL,1

			if sinal[0].isdigit():
				if int(int(sinal_[0]) - time()) <=2:
					sinais.append({'timestamp': sinal_[0],
									'par': sinal_[1],
									'dir':sinal_[2],
									'timeframe':sinal_[3]})

				velas = API.get_candles(par,(int(timeframe) * 60),20,time.time())
				ultimo = round(velas[0]['close'],4)
				primeiro = round(velas[-1]['close'],4)
				diferencia = abs(roubd((ultimo - primeiro / primeiro) *100,3))
				tendencia = "CALL" if ultimo < primeiro and diferencia > 0.01 else "PUT" if ultimo > primeiro and diferenca >0.01 else False
				if sinal_[2] == tendencia:
					open(arq_sinais,'w').write(file.replace(sinal,''))
					return sinais

	#return sinais



def entrada(data):
	global API
	global geral

	geral['lock'].acquire()
	geral['ops'].update({get_ident(): {'entrada': geral['valor'],'par': str(data['par']).upper(), 'timeframe': int(data['timeframe']),'dir':str(data['dir']).lower(),'timestamp':int(data['timestamp']),'resultado':'','lucro': 0,'status':'','id':0,'op_time':0}})

	geral['lock'].release()
	geral['lock'].acquire()
	try:
		geral['ops'][get_ident()]['status'],geral['ops'][get_ident()]['id'] = API.buy_digital_spot(geral['ops'][get_ident()]['par'],geral['ops'][get_ident()]['entrada'],geral['ops'][get_ident()]['dir'],geral['ops'][get_ident()]['timeframe'])
		geral['ops'][get_ident()]['op_time'] = int(time())
	except Exception as e:
		print('Error ao abrir operação',e)
		geral['ops'][get_ident()]['status'] = False
		pass

	geral['lock'].release()

	if geral['ops'][get_ident()]['status']:
		geral['ops'][get_ident()]['status'] = False

		while geral['ops'][get_ident()]['status'] == False:
			geral['lock'].acquire()
			geral['ops'][get_ident()]['status'],geral['ops'][get_ident()]['lucro'] = API.check_win_digital_v2(geral['ops'][get_ident()]['id'])
			geral['lock'].release()

		geral['lock'].acquire()
		print('\n Horarios do Sinal: ',datetime.fromtimestamp(int(geral['ops'][get_ident()]['timestamp'])).strftime("%H:%M:%S"))
		print('\n Horarios do da entrada: ',datetime.fromtimestamp(int(geral['ops'][get_ident()]['op_time'])).strftime("%H:%M:%S"))
		print('\n Horarios de diferencia: ',abs(int(geral['ops'][get_ident()]['op_time']) - int(geral['ops'][get_ident()]['timestamp'])),'segundos')
		print('PARIDADE',geral['ops'][get_ident()]['par'] )
		print('DIREÇÃO:',geral['ops'][get_ident()]['dir'])
		print('TIMEFRAME:',geral['ops'][get_ident()]['timeframe'])
		print('RESULTADO:', 'WIN' if geral['ops'][get_ident()]['lucro'] > 0 else 'LOSS' if geral['ops'][get_ident()]['lucro'] < 0 else 'Empate')
		print('LUCRO:', round(geral['ops'][get_ident()]['lucro'],2), '\n')

		geral['lock'].release()

	del geral['ops'][get_ident()]





geral = {'dir':'','valor':0.0,'lock': Lock(),'ops':{}}

dir_log()
retorno_ex()

geral['valor'] = 2


try:

	while True:
		sinais = get_sinal()
		if len(sinais) > 0:
			for data in sinais:
				Thread(target=entrada, args=(data,),daemon=True).start()

		print(len(geral['ops']),'Operações abertas',datetime.now().strftime('%H:%M:%S'), end='\r')
		sleep(0.5)
except Exception as e:
	print('ERRO AO RODAR OS SINAIS!',e)
	exit()

