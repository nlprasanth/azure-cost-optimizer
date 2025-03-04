import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class CostForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Forecast settings
        self.confidence_levels = [0.95, 0.80, 0.50]
        self.forecast_periods = 12  # months

    def generate_forecast(self, historical_data: List[Dict], analysis: Dict) -> Dict:
        """Generate cost forecasts based on historical data."""
        try:
            # Prepare data
            df = self._prepare_data(historical_data)
            if df.empty:
                return None

            # Generate features
            X, y = self._create_features(df)
            if len(X) == 0:
                return None

            # Train model
            self._train_model(X, y)

            # Generate forecasts
            forecasts = self._generate_predictions(df, analysis)

            return forecasts

        except Exception as e:
            logger.error(f"Error generating forecast: {str(e)}")
            return None

    def _prepare_data(self, historical_data: List[Dict]) -> pd.DataFrame:
        """Prepare historical data for forecasting."""
        try:
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Resample to monthly
            monthly = df.resample('M')['cost'].sum().reset_index()
            
            return monthly

        except Exception as e:
            logger.error(f"Error preparing data: {str(e)}")
            return pd.DataFrame()

    def _create_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Create features for the forecasting model."""
        try:
            features = []
            target = []
            
            for i in range(len(df) - 3):
                # Use last 3 months to predict next month
                feature_vector = [
                    df['cost'].iloc[i],
                    df['cost'].iloc[i+1],
                    df['cost'].iloc[i+2],
                    df['date'].iloc[i].month,  # month feature for seasonality
                    df['date'].iloc[i].quarter  # quarter feature for seasonality
                ]
                features.append(feature_vector)
                target.append(df['cost'].iloc[i+3])

            return np.array(features), np.array(target)

        except Exception as e:
            logger.error(f"Error creating features: {str(e)}")
            return np.array([]), np.array([])

    def _train_model(self, X: np.ndarray, y: np.ndarray) -> None:
        """Train the forecasting model."""
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model.fit(X_train, y_train)

        except Exception as e:
            logger.error(f"Error training model: {str(e)}")

    def _generate_predictions(self, df: pd.DataFrame, analysis: Dict) -> Dict:
        """Generate predictions and confidence intervals."""
        try:
            # Prepare last known data point
            last_date = df['date'].iloc[-1]
            last_costs = df['cost'].iloc[-3:].values
            
            forecasts = []
            confidence_intervals = {level: [] for level in self.confidence_levels}
            
            # Generate predictions for each future month
            for i in range(self.forecast_periods):
                next_date = last_date + pd.DateOffset(months=i+1)
                
                # Create feature vector
                feature_vector = np.array([
                    last_costs[0],
                    last_costs[1],
                    last_costs[2],
                    next_date.month,
                    next_date.quarter
                ]).reshape(1, -1)
                
                # Scale features
                feature_vector_scaled = self.scaler.transform(feature_vector)
                
                # Generate predictions
                predictions = []
                for _ in range(100):  # Bootstrap predictions
                    pred = self.model.predict(feature_vector_scaled)
                    predictions.append(pred[0])
                
                # Calculate mean prediction and confidence intervals
                mean_pred = np.mean(predictions)
                forecasts.append({
                    'date': next_date.strftime('%Y-%m-%d'),
                    'forecast': mean_pred
                })
                
                # Update last costs for next iteration
                last_costs = np.roll(last_costs, -1)
                last_costs[-1] = mean_pred
                
                # Calculate confidence intervals
                for level in self.confidence_levels:
                    interval = np.percentile(predictions, [(100-level*100)/2, 50+level*100/2])
                    confidence_intervals[level].append({
                        'date': next_date.strftime('%Y-%m-%d'),
                        'lower': interval[0],
                        'upper': interval[1]
                    })

            # Add seasonal adjustments
            self._apply_seasonal_adjustments(forecasts, analysis)

            # Calculate forecast metrics
            metrics = self._calculate_forecast_metrics(forecasts, confidence_intervals)

            return {
                'forecasts': forecasts,
                'confidence_intervals': confidence_intervals,
                'metrics': metrics
            }

        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            return None

    def _apply_seasonal_adjustments(self, forecasts: List[Dict], analysis: Dict) -> None:
        """Apply seasonal adjustments to forecasts."""
        try:
            if 'seasonality' in analysis:
                seasonal_patterns = analysis['seasonality']
                
                for forecast in forecasts:
                    date = datetime.strptime(forecast['date'], '%Y-%m-%d')
                    
                    # Apply monthly seasonality
                    if 'monthly' in seasonal_patterns:
                        month_pattern = seasonal_patterns['monthly']
                        if date.month in month_pattern:
                            forecast['forecast'] *= (1 + month_pattern[date.month])
                    
                    # Apply quarterly seasonality
                    if 'quarterly' in seasonal_patterns:
                        quarter_pattern = seasonal_patterns['quarterly']
                        if date.quarter in quarter_pattern:
                            forecast['forecast'] *= (1 + quarter_pattern[date.quarter])

        except Exception as e:
            logger.error(f"Error applying seasonal adjustments: {str(e)}")

    def _calculate_forecast_metrics(self, forecasts: List[Dict], confidence_intervals: Dict) -> Dict:
        """Calculate forecast metrics."""
        try:
            forecast_values = [f['forecast'] for f in forecasts]
            
            metrics = {
                'total_forecast': sum(forecast_values),
                'average_monthly_forecast': np.mean(forecast_values),
                'forecast_trend': 'increasing' if forecast_values[-1] > forecast_values[0] else 'decreasing',
                'forecast_growth': (forecast_values[-1] - forecast_values[0]) / forecast_values[0],
                'uncertainty_metrics': {}
            }
            
            # Calculate uncertainty metrics for each confidence level
            for level in self.confidence_levels:
                intervals = confidence_intervals[level]
                uncertainty_ranges = [i['upper'] - i['lower'] for i in intervals]
                
                metrics['uncertainty_metrics'][str(level)] = {
                    'average_range': np.mean(uncertainty_ranges),
                    'range_trend': 'increasing' if uncertainty_ranges[-1] > uncertainty_ranges[0] else 'decreasing',
                    'relative_uncertainty': np.mean(uncertainty_ranges) / np.mean(forecast_values)
                }

            return metrics

        except Exception as e:
            logger.error(f"Error calculating forecast metrics: {str(e)}")
            return {}
