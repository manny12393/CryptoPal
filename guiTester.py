import PySimpleGUI as sg
import main as m
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import urllib
import json
import datetime
import smtplib
import matplotlib.dates as mdates


figure_agg = None
crypto_list = None
crypto_obj_list = None #contains list of crypto objects

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    plt.close('all')
    
def makeCryptoList():
    global crypto_obj_list
    raw_list = m.makeCryptoList()
    crypto_obj_list = m.makeCryptoList()
    
    retLst = []
    
    for i in raw_list:
        retLst.append(str(i.symbol + " " + i.slug))
    
    return retLst

def makeGraph(slug):
    return m.makeGraph(slug, 2017, 5, 7, 2019, 3, 4, 1)

matplotlib.use("TkAgg")

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.get_tk_widget().forget()
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


fig = matplotlib.figure.Figure((5, 4), dpi=100)
settingOptions = ["open", "high", "low", "close"]

#num_of_days settings
num_of_days = [ "1 month", "3 months", "6 months", "9 months", "1 year", "2 years", "5 years"]

def computeGraph(slug_name, numOfMonths, settingIndex):
    x,y = m.makeGraph(slug_name, numOfMonths, settingIndex)
        
    if x == None or y == None:
        sg.Popup('Opps!', 'Cannot get data for this crypto!')
        return
    
    fig.add_subplot(1,1,1).plot(x, y)
    fig.subplots_adjust(bottom=.25, left=.25)
    axes = fig.axes
    axes[0].set_xticklabels(x, rotation='90')
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    axes[0].set_xlabel('Time (date)')
    axes[0].set_ylabel('Price ($)')
    axes[0].set_title(slug_name)

sg.theme('DarkAmber')

crypto_list = makeCryptoList()

layout = [ [sg.Text('Crypto Price Tracker', font = ("Arial", 13))],
[sg.Text('Cryptocuurency: '), sg.Combo(crypto_list, enable_events=True, key='combo'),sg.Text('Data Type: '), sg.Combo(settingOptions, default_value="open", enable_events=True, key="settingType"), \
  sg.Text('Duration: '), sg.Combo(num_of_days, default_value="1 month", enable_events=True, key="numOfDays"), sg.Button("Update")],
[sg.Canvas(key="-CANVAS-")],
[sg.Text('Notifcation Email:'), sg.InputText(key='textbox'), sg.Button("Set Email")]]

window = sg.Window('CryptoPal', layout)

while True:
    event, values = window.read()
    if event == 'BTC' or event == 'ETH':
        pass  #does nothing for the time being (fix later)
    elif event == "Update":
        if figure_agg:
            delete_figure_agg(figure_agg)
            fig.clear()
        
        combo = values['combo']
        if(combo == ""):
            continue
        slug_name = combo.split(' ')[1].strip()
        
        settingType = values['settingType']
        settingIndex = 1 #open at default
        if(settingType == settingOptions[0]):
            settingIndex = 1
        elif(settingType == settingOptions[1]):
            settingIndex = 2
        elif(settingType == settingOptions[2]):
            settingIndex = 3
        elif(settingType == settingOptions[3]):
            settingIndex = 4
        
        duration = values['numOfDays']
        
        numOfMonths = 1
        if(duration == num_of_days[0]):
            numOfMonths = 1
        elif(duration == num_of_days[1]):
            numOfMonths = 3
        elif(duration == num_of_days[2]):
            numOfMonths = 6
        elif(duration == num_of_days[3]):
            numOfMonths = 9
        elif(duration == num_of_days[4]):
            numOfMonths = 12
        elif(duration == num_of_days[5]):
            numOfMonths = 24
        elif(duration == num_of_days[6]):
            numOfMonths = 60
            
        print(slug_name)
        computeGraph(slug_name, numOfMonths, settingIndex)
        figure_agg = draw_figure(window["-CANVAS-"].TKCanvas, fig)
    elif event == "Set Email":
        combo = values['combo']
        if(combo == ""):
            continue
        slug_name = combo.split(' ')[1].strip()
        x,y = m.makeGraph(slug_name, 1, 1) 
        currentprice = y[-1]
        email = values['textbox']
        print(email)
        
        priceInUSD = 0
        
        for i in range(len(crypto_obj_list)):
            if combo == crypto_list[i]:
                priceInUSD = crypto_obj_list[i].currentValue
                break
        
        print(priceInUSD)

        msg = "Price Update= {name} is worth {pricecad} USD".format(name = slug_name, pricecad = priceInUSD)
        print(msg)
        with smtplib.SMTP('smtp.gmail.com',587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login('noreplycryptotrackerhtn@gmail.com' ,'HackTheNorth123!')
            smtp.sendmail('noreplycryptotrackerhtn@gmail.com', email , msg)
    elif event == sg.WIN_CLOSED:
        break

window.close()