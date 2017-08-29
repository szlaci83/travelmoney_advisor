'''
Linear regression forecaster for currency exchange rates using Quandl tickers.
Author : Laszlo Szoboszlai
2017
'''
import pandas as pd
import quandl, math, datetime, os, platform, time
import numpy as np
from sklearn import preprocessing, cross_validation, svm
from sklearn.linear_model import LinearRegression
from datetime import datetime
from datetime import timedelta
import pickle

'''Quandl tickers'''
currencies = {
            'USD' :{
                        'HUF' : 'BOE/XUDLBK35',
                        'PLN' : 'BOE/XUDLBK49',
                        'GBP' : 'BOE/XUDLGBD'
                    },
            'GBP' :{
                        'HUF' : 'BOE/XUDLBK33',
                        'PLN' : 'BOE/XUDLBK47'
                    },
            'EUR' :{
                        'HUF' : 'BOE/XUDLBK34',
                        'BGN' : 'ECB/EURBGN',
                        'PLN' : 'BOE/XUDLBK48',
                        'GBP' : 'BOE/XUDLSER'
                    }

            }

def create_plottable(dates, values):
    '''Creates plottable timestamps(dates) for the frontend
    :param dates: the dates predicted for
    :param values: the predicted values
    :return: arr : points to plot, min_day : date of the minimum value, max_day : date of the maximum value
    '''
    values = values.tolist()
    min_day = str(dates[values.index(min(values))])[:10]
    max_day = str(dates[values.index(max(values))])[:10]
    points = []

    for date,value in zip(dates, values):
        temp = {}
        temp['x'] = (date.timestamp() * 1000)
        temp['y'] = round(value, 3)
        points.append(temp)
    return points, min_day, max_day

def get_next_days(lastknownrate, no_of_days):
    '''
    Selects and returns the weekdays only for given number of days.
    :param lastknownrate: last known exchange rate
    :param no_of_days: number of days to do the selection
    :return: list of dates which are weekdays
    '''
    SATURDAY = 5
    SUNDAY = 6
    dates = []
    pos = lastknownrate.find('Name:') + 6
    date_str = lastknownrate[pos:pos + 10]
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    date_obj = date_obj + timedelta(days= no_of_days+2)
    i = 0
    while i<no_of_days:
        date_obj= date_obj + timedelta(days=1)
        if ((date_obj.weekday() != SATURDAY) & (date_obj.weekday() != SUNDAY)):
            dates.append(date_obj)
            i=i+1
    return dates

def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime

def download_data(currencyfrom, currencyto, save = False, silent = True ):
    '''Function to download currency exchange rate data from Quandl site.
    :param currencyfrom: the currency to change from
    :param currencyto: the currency to change to
    :param save: if True saves the data in 'CURRENCYNAME'.csv file, default = False
    :param silent: if False, prints logs on stdout, default = True
    :return: dataframe with exchange rate data form Quandl.
    '''
    df = quandl.get(currencies[currencyfrom][currencyto])
    df.columns= [currencyto]

    if save:
        filename = currencyfrom + '_to_' + currencyto + '.csv'
        df.to_csv(filename , sep='\t', encoding='utf-8')
        if not silent:
            print('Currency info saved to:' + filename)
    return df

def load_data(currencyfrom, currencyto, save = False, silent = True, refresh_interval = 1):
    '''Function to download new data if the saved data is "too old" .
       NOTE: Use this instead of download_data for cacheing.
    :param currencyfrom: the currency to change from
    :param currencyto: the currency to change to
    :param save: passes it to download_data if its called.
    :param silent: if False, prints logs on stdout, default = True
    :param refresh_interval: sets the interval in days
    :return: dataframe with exchange rate data form Quandl.
    '''
    #turn days into seconds
    refresh_interval = refresh_interval * 86400
    filename = currencyfrom + '_to_' + currencyto + '.csv'
    print(bool(math.floor(((time.time() - creation_date(filename)) / refresh_interval ))))
    if bool(math.floor(((time.time() - creation_date(filename)) / refresh_interval ))):
        if not silent:
            print('Download of ' + filename + ' triggered.')
        download_data(currencyfrom, currencyto, save, silent)
    return pd.read_csv(filename, sep='\t')

def lin_reg_predict(currencyfrom, currencyto, forecast_out, save_ds = False,savemodel = False, silent = True, cache = True,
                    train_a_lot = 1, retrain = False, refresh_interval = 1,):
    '''
    Function to predict out future currency rates.
    :param currencyfrom: the currency to change from
    :param currencyto: the currency to change to
    :param forecast_out: the number of days we want the prediction for.
    :param save_ds: triggers cacheing of newly downloaded dataset.
    :param savemodel: triggers saving the classifier.
    :param silent: turns logging to stdout on.
    :param cache: use load instead of download
    :param retrain: forces the retrain of the model
    :param train_a_lot: number of times it trains the model to get best performing one
    :param refresh_interval: refresh interval in days of the dataset if cacheing is on
    :return:predicted currency rates for "forecast_out" number of days
    '''
    df = load_data(currencyfrom, currencyto, save_ds, silent, refresh_interval) if cache else download_data(currencyfrom, currencyto, save_ds, silent)
    df = df[[currencyto]]

    # currency to forecast
    forecast_col = currencyto
    df.fillna(-99999, inplace = True)
    #how many days to forecast for
    df['label'] = df[forecast_col].shift(-forecast_out)

    df = df [[currencyto,'label',]]

    x = np.array(df.drop(['label'],1))
    maxrate = x.max()

    x = preprocessing.scale(x)
    x = x[:-forecast_out]
    x_lately = x[-forecast_out:]
    df.dropna(inplace = True)
    y = np.array(df['label'])

    currency_file = 'linreg_' + currencyfrom + '_to_' + currencyto + '.pickle'
    #the model needs saving if the model for currency does not exist
    needs_saving = not os.path.isfile('./' + currency_file) or savemodel

    if needs_saving or retrain:
        #if retrain is triggered the minimum training = 10
        if retrain:
            train_a_lot = max(10, train_a_lot)
        scores = {}
        #train the classifier train_a_lot times (default = 1), and chose the optimal to be the model
        # for train in train_a_lot:
        if not silent:
            print('Training the model ' + str(train_a_lot) + ' time(s).')
        for i in range(train_a_lot):
            x_train, x_test, y_train, y_test = cross_validation.train_test_split(x,y, test_size=0.2, random_state=0)
            clf = LinearRegression(n_jobs= -1) #n_jobs makes it threaded -1 as many as possible
            clf.fit(x_train, y_train)
            #scores[( cross_validation.cross_val_score(clf, x, y, scoring='mean_squared_error', cv=loo,))] = clf
            scores [clf.score(x_test, y_test).mean()] = clf
        if not silent:
            print('The accuracies: ' + str(scores.keys()))
        score =  max(scores)
        model = max(scores, key=scores.get)
    else:
        if not silent:
            print('Loading model from file.')
        pickle_in = open(currency_file,'rb')
        model = pickle.load(pickle_in)

    #save the best model after training
    if needs_saving:
        with open(currency_file,'wb') as f:
            pickle.dump(model,f)
        if not silent:
            print('Model saved as : ' + currency_file)

    if not silent:
        print('Creating forecast.')
    forecast_set = clf.predict(x_lately)

    if not silent:
        print('Generating response.')

    lastknownrate = str(df.iloc[-1])
    dates = get_next_days(lastknownrate, forecast_out)
    forecasts, minday, maxday = create_plottable(dates, forecast_set)
    lastknownrate = df.iloc[-1]['label']
    accuracy = str(score)

    return {'maxrate' : maxrate,
            'lasknownrate' : lastknownrate,
            'accuracy' : accuracy,
            'forecasts' : forecasts,
            'tosell' : maxday,
            'tobuy' : minday
            }
def main():
    currencyfrom = 'GBP'
    currencyto = 'HUF'
    forecast_out = 5
    prediction = lin_reg_predict(currencyfrom, currencyto, forecast_out, save_ds=True, savemodel=True, silent=False, cache=True,
                    train_a_lot=1, retrain=False, refresh_interval=1)
    print(prediction)

if __name__ == "__main__":
    main()