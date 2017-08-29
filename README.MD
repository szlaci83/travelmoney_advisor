# Travel money advisor 

###### Using machine learning to predict currency exchange rate

## Problem definition
When I travel to my home country I always unsure what the best date is
to exchange my money to get the best possible rate. It is even more difficult
in case I need to exchange a larger amount. Other people might be in the same 
situation when they need to exchange money, so in order to make the decision easier 
I have created this Flask based API using machine learning, to find the best date in the near future, 
and created a web interface to access the API functionality, which can be checked [here.](http://laszloszoboszlai.me/travelmoney "Link to travelmoney webapp")
  

## Currently available rates:
* EUR -> BGN, GBP, HUF,PLN
* GBP -> HUF, PLN
* USD -> GBP, HUF, PLN

## API Endpoints:
### Available currencies to exchange from:
* GET /currencies   
* Returns the available currencies as a JSON 
* [Endpoint: http://laszloszoboszlai.me:5000/currencies](http://laszloszoboszlai.me:5000/currencies "Link to endpoint")

### Available currencies to exchange to:
* POST /tocurrencies   
* Returns the available currencies to translate from a specific curency
* request format : { "currency" : CURRENCY } 
* [Endpoint: http://laszloszoboszlai.me:5000/tocurrencies](http://laszloszoboszlai.me:5000/tocurrencies "Link to endpoint")

### Forecast a specific CURRENCY for X days:
* POST /forecast
	* expected JSON format : 
	* { 
	* "currencyfrom" : "CURRENCY",
	* "currencyto" : "CURRENCY",
    * "days": X
    * }
* Response:
	* {'lasknownrate' : last known exchange rate (date)
    * 'accuracy' : accuracy of the prediction (float)
    * 'forecasts' : forecasted exchange rates (array of dictionaries of date:rate pairs for easy plotting)
    * 'tosell' : the predicted day for selling the currency (date)
    * 'tobuy' : to predicted day for buying the currency (date)
    * }
	
* [Endpoint: http://laszloszoboszlai.me:5000/forecast](http://laszloszoboszlai.me:5000/forecast "Link to endpoint")
---
### Future plans
* My plan is to create another API for sentiment analysis of different financial websites to improve the 
  prediction accuracy from the gained knowledge.  
* Create a mobile application using the API.
* Move to microservice architecture.
# Demo video:
[![Demo video on youtube](http://img.youtube.com/vi/sl_guP8Hmt0/0.jpg)](http://www.youtube.com/watch?v=sl_guP8Hmt0)
