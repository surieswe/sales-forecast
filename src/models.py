# src/models.py
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class SalesForecaster:
    
    def __init__(self, df):
        """
        df: DataFrame with 'date' and 'sales' columns
        """
        self.df = df.copy()
        self.df['date'] = pd.to_datetime(self.df['date'])
        
    def train_test_split(self, test_size=90):
        """Split data into train and test"""
        split_idx = len(self.df) - test_size
        self.train = self.df.iloc[:split_idx]
        self.test = self.df.iloc[split_idx:]
        return self.train, self.test
    
    def arima_forecast(self, order=(5,1,2), periods=90):
        """
        ARIMA Model - Good for non-seasonal data
        order: (p, d, q)
            p: AR order (auto-regressive)
            d: differencing
            q: MA order (moving average)
        """
        print(f"Training ARIMA{order}...")
        model = ARIMA(self.train['sales'], order=order)
        fitted_model = model.fit()
        
        # Forecast
        forecast = fitted_model.forecast(steps=periods)
        
        # Get confidence intervals
        forecast_df = fitted_model.get_forecast(steps=periods)
        conf_int = forecast_df.conf_int()
        
        return fitted_model, forecast, conf_int
    
    def sarima_forecast(self, order=(1,1,1), seasonal_order=(1,1,1,12), periods=90):
        """
        SARIMA Model - Best for seasonal data
        seasonal_order: (P, D, Q, s)
            s: seasonal period (12 for monthly, 7 for weekly)
        """
        print(f"Training SARIMA{order}x{seasonal_order}...")
        model = SARIMAX(
            self.train['sales'], 
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        fitted_model = model.fit(disp=False)
        
        # Forecast
        forecast = fitted_model.forecast(steps=periods)
        
        # Get confidence intervals
        forecast_df = fitted_model.get_forecast(steps=periods)
        conf_int = forecast_df.conf_int()
        
        return fitted_model, forecast, conf_int
    
    def exponential_smoothing_forecast(self, periods=90, seasonal_periods=7):
        """
        Holt-Winters Exponential Smoothing
        Good for data with trend and seasonality
        """
        print("Training Exponential Smoothing...")
        
        model = ExponentialSmoothing(
            self.train['sales'],
            seasonal_periods=seasonal_periods,
            trend='add',
            seasonal='add',
            initialization_method="estimated"
        )
        fitted_model = model.fit()
        
        # Forecast
        forecast = fitted_model.forecast(steps=periods)
        
        return fitted_model, forecast
    
    def auto_arima_forecast(self, periods=90):
        """
        Simple Auto ARIMA - tries different parameters
        """
        best_aic = np.inf
        best_order = None
        best_model = None
        
        # Try different parameters
        p_values = [0, 1, 2, 5]
        d_values = [0, 1]
        q_values = [0, 1, 2]
        
        print("Finding best ARIMA parameters...")
        
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    try:
                        model = ARIMA(self.train['sales'], order=(p,d,q))
                        fitted = model.fit()
                        
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p,d,q)
                            best_model = fitted
                    except:
                        continue
        
        print(f"Best ARIMA order: {best_order} (AIC: {best_aic:.2f})")
        forecast = best_model.forecast(steps=periods)
        
        return best_model, forecast, best_order
    
    def calculate_metrics(self, actual, predicted):
        """Calculate forecast accuracy metrics"""
        # Handle array length mismatch
        min_len = min(len(actual), len(predicted))
        actual = actual[:min_len]
        predicted = predicted[:min_len]
        
        mape = mean_absolute_percentage_error(actual, predicted) * 100
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        mae = np.mean(np.abs(actual - predicted))
        
        return {
            'MAPE': round(mape, 2),
            'RMSE': round(rmse, 2),
            'MAE': round(mae, 2)
        }