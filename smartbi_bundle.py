# smartbi_bundle.py
"""
SmartBI - Comprehensive Business Intelligence and Data Analytics Application
A single-file bundle for easy deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import sqlite3
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Scientific computing and ML
try:
    from sklearn.impute import KNNImputer, SimpleImputer
    from sklearn.experimental import enable_iterative_imputer
    from sklearn.impute import IterativeImputer
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Time series forecasting
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

# OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# =============================================================================
# DATABASE LAYER - SQLite Persistence
# =============================================================================

class SmartBIDatabase:
    """Lightweight database for storing datasets and analysis history"""
    
    def __init__(self, db_path="smartbi.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                row_count INTEGER,
                column_count INTEGER,
                data_json TEXT NOT NULL
            )
        """)
        
        # Analysis history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER,
                analysis_type TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            )
        """)
        
        # Chat history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_dataset(self, name, df):
        """Save a dataset to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data_json = df.to_json(orient='split', date_format='iso')
        cursor.execute("""
            INSERT INTO datasets (name, row_count, column_count, data_json)
            VALUES (?, ?, ?, ?)
        """, (name, len(df), len(df.columns), data_json))
        
        dataset_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return dataset_id
    
    def load_dataset(self, dataset_id):
        """Load a dataset from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, data_json FROM datasets WHERE id = ?", (dataset_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            name, data_json = row
            df = pd.read_json(io.StringIO(data_json), orient='split')
            return name, df
        return None, None
    
    def list_datasets(self):
        """List all saved datasets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, uploaded_at, row_count, column_count 
            FROM datasets 
            ORDER BY uploaded_at DESC
        """)
        datasets = cursor.fetchall()
        conn.close()
        return datasets
    
    def save_chat_message(self, role, content):
        """Save a chat message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_history (role, content)
            VALUES (?, ?)
        """, (role, content))
        conn.commit()
        conn.close()
    
    def get_chat_history(self, limit=50):
        """Retrieve chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, created_at 
            FROM chat_history 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        history = cursor.fetchall()
        conn.close()
        return list(reversed(history))


# =============================================================================
# DATA CLEANING MODULE
# =============================================================================

class DataCleaner:
    """Advanced data cleaning with model-based imputation"""
    
    @staticmethod
    def analyze_missing_data(df):
        """Analyze missing data patterns"""
        missing_info = pd.DataFrame({
            'Column': df.columns,
            'Missing_Count': df.isnull().sum(),
            'Missing_Percentage': (df.isnull().sum() / len(df) * 100).round(2),
            'Data_Type': df.dtypes
        })
        missing_info = missing_info[missing_info['Missing_Count'] > 0]
        missing_info = missing_info.sort_values('Missing_Percentage', ascending=False)
        return missing_info
    
    @staticmethod
    def simple_imputation(df, strategy='mean'):
        """Simple imputation strategies"""
        df_cleaned = df.copy()
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        if SKLEARN_AVAILABLE:
            imputer = SimpleImputer(strategy=strategy)
            df_cleaned[numeric_cols] = imputer.fit_transform(df_cleaned[numeric_cols])
        else:
            if strategy == 'mean':
                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mean())
            elif strategy == 'median':
                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].median())
            elif strategy == 'most_frequent':
                df_cleaned[numeric_cols] = df_cleaned[numeric_cols].fillna(df_cleaned[numeric_cols].mode().iloc[0])
        
        return df_cleaned
    
    @staticmethod
    def knn_imputation(df, n_neighbors=5):
        """KNN-based imputation"""
        if not SKLEARN_AVAILABLE:
            st.warning("scikit-learn not available. Using simple mean imputation.")
            return DataCleaner.simple_imputation(df, strategy='mean')
        
        df_cleaned = df.copy()
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        imputer = KNNImputer(n_neighbors=n_neighbors)
        df_cleaned[numeric_cols] = imputer.fit_transform(df_cleaned[numeric_cols])
        
        return df_cleaned
    
    @staticmethod
    def iterative_imputation(df, max_iter=10):
        """Iterative model-based imputation (MICE)"""
        if not SKLEARN_AVAILABLE:
            st.warning("scikit-learn not available. Using simple mean imputation.")
            return DataCleaner.simple_imputation(df, strategy='mean')
        
        df_cleaned = df.copy()
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        imputer = IterativeImputer(
            estimator=RandomForestRegressor(n_estimators=10, random_state=42),
            max_iter=max_iter,
            random_state=42
        )
        df_cleaned[numeric_cols] = imputer.fit_transform(df_cleaned[numeric_cols])
        
        return df_cleaned
    
    @staticmethod
    def remove_duplicates(df):
        """Remove duplicate rows"""
        initial_count = len(df)
        df_cleaned = df.drop_duplicates()
        removed_count = initial_count - len(df_cleaned)
        return df_cleaned, removed_count
    
    @staticmethod
    def handle_outliers(df, method='iqr', threshold=1.5):
        """Handle outliers using IQR or Z-score method"""
        df_cleaned = df.copy()
        numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if method == 'iqr':
                Q1 = df_cleaned[col].quantile(0.25)
                Q3 = df_cleaned[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                df_cleaned[col] = df_cleaned[col].clip(lower_bound, upper_bound)
            elif method == 'zscore':
                mean = df_cleaned[col].mean()
                std = df_cleaned[col].std()
                df_cleaned[col] = df_cleaned[col].clip(
                    mean - threshold * std,
                    mean + threshold * std
                )
        
        return df_cleaned


# =============================================================================
# FEATURE EXTRACTION MODULE
# =============================================================================

# =============================================================================
# DATA PROFILING & ANALYSIS MODULE
# =============================================================================

class DataProfiler:
    """Comprehensive data profiling and quality analysis"""
    
    @staticmethod
    def generate_profile(df):
        """Generate comprehensive data profile"""
        profile = {
            'shape': {'rows': len(df), 'columns': len(df.columns)},
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
        }
        return profile
    
    @staticmethod
    def analyze_missing_values(df):
        """Detailed missing value analysis"""
        missing = pd.DataFrame({
            'Column': df.columns,
            'Missing_Count': df.isnull().sum(),
            'Missing_Percentage': (df.isnull().sum() / len(df) * 100).round(2),
            'Data_Type': df.dtypes
        })
        missing = missing[missing['Missing_Count'] > 0].sort_values('Missing_Percentage', ascending=False)
        return missing
    
    @staticmethod
    def detect_duplicates(df):
        """Detect duplicate rows"""
        total_duplicates = df.duplicated().sum()
        duplicate_cols = []
        for col in df.columns:
            dup_count = df[col].duplicated().sum()
            if dup_count > 0:
                duplicate_cols.append({'Column': col, 'Duplicates': dup_count})
        
        return {'total_duplicates': total_duplicates, 'by_column': duplicate_cols}
    
    @staticmethod
    def detect_data_types(df):
        """Detect and categorize data types"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        return {
            'numeric': numeric_cols,
            'categorical': categorical_cols,
            'datetime': datetime_cols
        }
    
    @staticmethod
    def identify_quality_issues(df):
        """Identify data quality issues"""
        issues = []
        
        # Check for high missing values
        missing = df.isnull().sum()
        for col, count in missing.items():
            pct = (count / len(df)) * 100
            if pct > 50:
                issues.append(f"⚠️ Column '{col}' has {pct:.1f}% missing values")
        
        # Check for constant columns
        for col in df.columns:
            if df[col].nunique() == 1:
                issues.append(f"⚠️ Column '{col}' has only one unique value")
        
        # Check for high cardinality categorical
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            if df[col].nunique() > len(df) * 0.5:
                issues.append(f"⚠️ Column '{col}' has very high cardinality ({df[col].nunique()} unique values)")
        
        # Check for potential outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = len(df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)])
            if outliers > 0:
                pct = (outliers / len(df)) * 100
                if pct > 5:
                    issues.append(f"📊 Column '{col}' contains {pct:.1f}% potential outliers")
        
        return issues if issues else ["✅ No major data quality issues detected"]
    
    @staticmethod
    def get_statistical_summary(df):
        """Generate statistical summary"""
        numeric_df = df.select_dtypes(include=[np.number])
        return numeric_df.describe().T


class InsightGenerator:
    """Generate automated insights and recommendations"""
    
    @staticmethod
    def analyze_features(df):
        """Analyze feature importance and characteristics"""
        insights = []
        
        # Numeric features analysis
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            variance = df[col].var()
            skewness = df[col].skew()
            
            if abs(skewness) > 1:
                insights.append(f"📈 {col}: Highly skewed distribution (skewness: {skewness:.2f})")
            
            if variance > df[col].mean() ** 2:
                insights.append(f"📊 {col}: High variability relative to mean")
        
        # Categorical features analysis
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            top_value_freq = df[col].value_counts().iloc[0] / len(df) if len(df[col].value_counts()) > 0 else 0
            if top_value_freq > 0.8:
                insights.append(f"🏷️ {col}: Dominated by one category ({top_value_freq*100:.1f}%)")
            else:
                insights.append(f"🏷️ {col}: {df[col].nunique()} distinct categories, well-distributed")
        
        return insights if insights else ["✅ Features appear well-balanced"]
    
    @staticmethod
    def analyze_correlations(df):
        """Analyze feature correlations"""
        insights = []
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return ["ℹ️ Need at least 2 numeric features for correlation analysis"]
        
        corr = numeric_df.corr()
        
        # Find strong correlations
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                corr_val = corr.iloc[i, j]
                if abs(corr_val) > 0.7:
                    direction = "positive" if corr_val > 0 else "negative"
                    insights.append(f"🔗 Strong {direction} correlation ({corr_val:.2f}) between {corr.columns[i]} and {corr.columns[j]}")
        
        return insights if insights else ["ℹ️ No strong correlations detected between features"]
    
    @staticmethod
    def generate_recommendations(df, issues):
        """Generate actionable recommendations"""
        recommendations = []
        
        # Missing value recommendations
        missing = df.isnull().sum()
        if missing.sum() > 0:
            recommendations.append("🔧 Data Cleaning: Use Data Cleaning page to handle missing values (Mean/Median/KNN imputation)")
        
        # Feature engineering recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            recommendations.append("⚙️ Feature Engineering: Create interaction features or polynomial features for better model performance")
        
        # Forecasting recommendation
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        numeric_with_date = [col for col in numeric_cols if 'date' in str(col).lower()]
        if len(datetime_cols) > 0 or len(numeric_with_date) > 0:
            recommendations.append("🔮 Time Series: Your data appears suitable for forecasting with the Forecasting page")
        
        # Data quality recommendations
        if len(issues) > 2:
            recommendations.append("📋 Quality Check: Consider reviewing and improving data quality before analysis")
        
        return recommendations if recommendations else ["✅ Data looks ready for analysis!"]
    
    @staticmethod
    def analyze_product_associations(df, transaction_column, separator=',', min_product_length=2):
        """Analyze which products are frequently bought together (Market Basket Analysis)"""
        try:
            # Parse transactions
            transactions = []
            for idx, value in df[transaction_column].items():
                if pd.isna(value):
                    continue
                # Split products and clean whitespace
                products = [p.strip() for p in str(value).split(separator)]
                products = [p for p in products if p]  # Remove empty strings
                if len(products) >= min_product_length:
                    transactions.append(products)
            
            if len(transactions) < 2:
                return {"error": "Not enough transactions for analysis"}
            
            # Calculate product pairs and their frequencies
            product_pairs = {}
            product_freq = {}
            triplets = {}
            
            for transaction in transactions:
                # Count individual products
                for product in transaction:
                    product_freq[product] = product_freq.get(product, 0) + 1
                
                # Count product pairs
                for i in range(len(transaction)):
                    for j in range(i + 1, len(transaction)):
                        pair = tuple(sorted([transaction[i], transaction[j]]))
                        product_pairs[pair] = product_pairs.get(pair, 0) + 1
                
                # Count triplets
                for i in range(len(transaction)):
                    for j in range(i + 1, len(transaction)):
                        for k in range(j + 1, len(transaction)):
                            triplet = tuple(sorted([transaction[i], transaction[j], transaction[k]]))
                            triplets[triplet] = triplets.get(triplet, 0) + 1
            
            # Calculate association metrics
            total_transactions = len(transactions)
            associations = []
            
            for (product_a, product_b), count in product_pairs.items():
                support = count / total_transactions
                confidence_ab = count / product_freq.get(product_a, 1)
                confidence_ba = count / product_freq.get(product_b, 1)
                lift = (count / total_transactions) / ((product_freq.get(product_a, 1) / total_transactions) * 
                                                        (product_freq.get(product_b, 1) / total_transactions))
                
                associations.append({
                    'Product A': product_a,
                    'Product B': product_b,
                    'Co-occurrence': count,
                    'Support': f"{support:.2%}",
                    'Confidence (A→B)': f"{confidence_ab:.2%}",
                    'Confidence (B→A)': f"{confidence_ba:.2%}",
                    'Lift': f"{lift:.2f}"
                })
            
            # Sort by co-occurrence count
            associations.sort(key=lambda x: x['Co-occurrence'], reverse=True)
            
            # Process triplets
            triplet_data = []
            for (prod_a, prod_b, prod_c), count in sorted(triplets.items(), key=lambda x: x[1], reverse=True)[:20]:
                support = count / total_transactions
                triplet_data.append({
                    'Products': f"{prod_a} + {prod_b} + {prod_c}",
                    'Co-occurrence': count,
                    'Support': f"{support:.2%}"
                })
            
            return {
                'associations': associations,
                'triplets': triplet_data,
                'product_freq': sorted(product_freq.items(), key=lambda x: x[1], reverse=True),
                'total_transactions': total_transactions,
                'unique_products': len(product_freq)
            }
        except Exception as e:
            return {"error": f"Error analyzing associations: {str(e)}"}
    
    @staticmethod
    def analyze_pos_data(df):
        """Comprehensive POS data analysis"""
        try:
            analysis = {}
            
            # Transaction metrics
            if 'Total_Amount' in df.columns or 'Total_Amount_JOD' in df.columns:
                amount_col = 'Total_Amount_JOD' if 'Total_Amount_JOD' in df.columns else 'Total_Amount'
                analysis['total_revenue'] = df[amount_col].sum()
                analysis['avg_transaction'] = df[amount_col].mean()
                analysis['max_transaction'] = df[amount_col].max()
                analysis['min_transaction'] = df[amount_col].min()
            
            # Customer analysis
            if 'Customer_ID' in df.columns:
                analysis['unique_customers'] = df['Customer_ID'].nunique()
                analysis['repeat_rate'] = (df.groupby('Customer_ID').size() > 1).sum() / analysis['unique_customers']
            
            # Payment method analysis
            if 'Payment_Method' in df.columns:
                analysis['payment_methods'] = df['Payment_Method'].value_counts().to_dict()
            
            # Customer status
            if 'Customer_Status' in df.columns:
                analysis['customer_status'] = df['Customer_Status'].value_counts().to_dict()
            
            # Category analysis
            if 'Primary_Item_Category' in df.columns:
                category_stats = df.groupby('Primary_Item_Category').agg({
                    'Transaction_ID': 'count',
                }).rename(columns={'Transaction_ID': 'count'})
                if 'Total_Amount_JOD' in df.columns:
                    category_stats['revenue'] = df.groupby('Primary_Item_Category')['Total_Amount_JOD'].sum()
                    category_stats['avg_price'] = df.groupby('Primary_Item_Category')['Total_Amount_JOD'].mean()
                analysis['categories'] = category_stats.to_dict()
            
            return analysis
        except Exception as e:
            return {"error": f"Error in POS analysis: {str(e)}"}


class FeatureExtractor:
    """Advanced feature extraction and engineering"""
    
    @staticmethod
    def create_polynomial_features(df, columns, degree=2):
        """Create polynomial features"""
        df_features = df.copy()
        numeric_cols = [c for c in columns if c in df.select_dtypes(include=[np.number]).columns]
        
        for col in numeric_cols:
            for d in range(2, degree + 1):
                df_features[f'{col}_power_{d}'] = df_features[col] ** d
        
        return df_features
    
    @staticmethod
    def create_interaction_features(df, columns):
        """Create interaction features between columns"""
        df_features = df.copy()
        numeric_cols = [c for c in columns if c in df.select_dtypes(include=[np.number]).columns]
        
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                col1, col2 = numeric_cols[i], numeric_cols[j]
                df_features[f'{col1}_x_{col2}'] = df_features[col1] * df_features[col2]
        
        return df_features
    
    @staticmethod
    def create_statistical_features(df, columns, window=7):
        """Create rolling statistical features"""
        df_features = df.copy()
        numeric_cols = [c for c in columns if c in df.select_dtypes(include=[np.number]).columns]
        
        for col in numeric_cols:
            df_features[f'{col}_rolling_mean_{window}'] = df_features[col].rolling(window=window, min_periods=1).mean()
            df_features[f'{col}_rolling_std_{window}'] = df_features[col].rolling(window=window, min_periods=1).std()
            df_features[f'{col}_lag_1'] = df_features[col].shift(1)
            df_features[f'{col}_lag_3'] = df_features[col].shift(3)
        
        return df_features
    
    @staticmethod
    def create_categorical_features(df, column):
        """One-hot encode categorical features"""
        df_features = df.copy()
        if column in df.columns:
            encoded = pd.get_dummies(df_features[column], prefix=column, drop_first=True)
            df_features = pd.concat([df_features, encoded], axis=1)
        
        return df_features
    
    @staticmethod
    def feature_importance_analysis(df, target_col):
        """Analyze feature importance using correlation"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if target_col not in numeric_df.columns:
            return None
        
        correlations = numeric_df.corr()[target_col].abs().sort_values(ascending=False)
        return correlations


# =============================================================================
# TIME SERIES FORECASTING MODULE
# =============================================================================

class TimeSeriesForecaster:
    """Advanced time series forecasting using Prophet"""
    
    @staticmethod
    def prepare_prophet_data(df, date_col, value_col):
        """Prepare data for Prophet format (ds, y)"""
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df[date_col]),
            'y': df[value_col]
        })
        return prophet_df
    
    @staticmethod
    def forecast_with_prophet(df, periods=30, yearly_seasonality=True, 
                             weekly_seasonality=True, daily_seasonality=False):
        """Generate forecast using Prophet"""
        if not PROPHET_AVAILABLE:
            st.error("Prophet not available. Please install it: pip install prophet")
            return None, None
        
        model = Prophet(
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=daily_seasonality
        )
        model.fit(df)
        
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        return model, forecast
    
    @staticmethod
    def calculate_accuracy_metrics(actual_df, forecast):
        """Calculate accuracy metrics for the forecast"""
        try:
            # Make copies to avoid modifying originals
            actual_copy = actual_df.copy()
            forecast_copy = forecast.copy()
            
            # Ensure ds is datetime
            actual_copy['ds'] = pd.to_datetime(actual_copy['ds'])
            forecast_copy['ds'] = pd.to_datetime(forecast_copy['ds'])
            
            # Normalize to date only (remove time component for matching)
            actual_copy['date'] = actual_copy['ds'].dt.date
            forecast_copy['date'] = forecast_copy['ds'].dt.date
            
            # Merge on date
            merge_df = forecast_copy[['date', 'yhat']].merge(
                actual_copy[['date', 'y']], 
                on='date', 
                how='inner'
            )
            
            if len(merge_df) == 0:
                return None
            
            actual = merge_df['y'].values
            predicted = merge_df['yhat'].values
            
            # Filter out NaN values
            mask = ~(np.isnan(actual) | np.isnan(predicted))
            actual = actual[mask]
            predicted = predicted[mask]
            
            if len(actual) == 0:
                return None
            
            # Calculate metrics
            mae = np.mean(np.abs(actual - predicted))
            rmse = np.sqrt(np.mean((actual - predicted) ** 2))
            mape = np.mean(np.abs((actual - predicted) / (np.abs(actual) + 1e-10))) * 100
            
            # Calculate R-squared
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r_squared = 1 - (ss_res / (ss_tot + 1e-10))
            
            return {
                'MAE': mae,
                'RMSE': rmse,
                'MAPE': mape,
                'R²': r_squared,
                'samples': len(actual)
            }
        except Exception as e:
            st.error(f"Error calculating metrics: {str(e)}")
            return None
    
    @staticmethod
    def plot_forecast(model, forecast, actual_df):
        """Create interactive forecast plot"""
        fig = go.Figure()
        
        # Actual data
        fig.add_trace(go.Scatter(
            x=actual_df['ds'],
            y=actual_df['y'],
            mode='lines',
            name='Actual',
            line=dict(color='blue')
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='red')
        ))
        
        # Confidence interval
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            mode='lines',
            name='Upper Bound',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            mode='lines',
            name='Lower Bound',
            fill='tonexty',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(width=0),
            showlegend=False
        ))
        
        fig.update_layout(
            title='Time Series Forecast',
            xaxis_title='Date',
            yaxis_title='Value',
            hovermode='x unified'
        )
        
        return fig


# =============================================================================
# CONVERSATIONAL AI MODULE
# =============================================================================

class AIAssistant:
    """Conversational AI agent with OpenAI integration"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.available = OPENAI_AVAILABLE and api_key
        
        if self.available:
            openai.api_key = api_key
    
    def chat(self, message, context="", model="gpt-3.5-turbo"):
        """Send a message to the AI assistant"""
        if not self.available:
            return self._fallback_response(message)
        
        try:
            system_prompt = """You are SmartBI Assistant, an expert in business intelligence, 
            data analytics, and data science. Help users understand their data, suggest analyses, 
            and provide insights. Be concise and practical."""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            messages.append({"role": "user", "content": message})
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error communicating with AI: {str(e)}"
    
    def _fallback_response(self, message):
        """Fallback responses when OpenAI is not available"""
        message_lower = message.lower()
        
        responses = {
            'help': "I can assist you with data cleaning, visualization, and forecasting. Upload your data to get started!",
            'clean': "For data cleaning, use the Data Cleaning page. You can handle missing values, remove duplicates, and handle outliers.",
            'forecast': "For forecasting, use the Forecasting page. Select your date and value columns, then choose forecast parameters.",
            'dashboard': "Create interactive dashboards on the Dashboard page. Choose chart types and customize visualizations.",
            'missing': "Handle missing data using simple imputation (mean/median), KNN imputation, or iterative imputation (MICE algorithm).",
        }
        
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        return ("OpenAI API key not configured. I'm running in fallback mode. "
                "I can provide basic help - try asking about 'clean', 'forecast', 'dashboard', or 'missing' data.")


# =============================================================================
# VISUALIZATION HELPERS
# =============================================================================

class Visualizer:
    """Create interactive visualizations"""
    
    @staticmethod
    def create_summary_stats(df):
        """Generate summary statistics"""
        return df.describe()
    
    @staticmethod
    def plot_correlation_matrix(df):
        """Plot correlation heatmap"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return None
        
        corr = numeric_df.corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Correlation Matrix"
        )
        return fig
    
    @staticmethod
    def plot_distribution(df, column):
        """Plot distribution of a column"""
        fig = px.histogram(
            df,
            x=column,
            title=f'Distribution of {column}',
            marginal='box'
        )
        return fig
    
    @staticmethod
    def plot_time_series(df, date_col, value_col):
        """Plot time series data"""
        fig = px.line(
            df,
            x=date_col,
            y=value_col,
            title=f'{value_col} over time'
        )
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text=value_col)
        return fig
    
    @staticmethod
    def plot_scatter(df, x_col, y_col, color_col=None):
        """Plot scatter plot"""
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f'{y_col} vs {x_col}'
        )
        return fig
    
    @staticmethod
    def plot_product_association_network(associations, top_n=15):
        """Visualize product associations as a network"""
        if not associations or len(associations) == 0:
            return None
        
        # Limit to top N associations
        top_associations = associations[:top_n]
        
        # Create nodes and edges
        products = set()
        edges = []
        edge_labels = []
        
        for assoc in top_associations:
            products.add(assoc['Product A'])
            products.add(assoc['Product B'])
            edges.append((assoc['Product A'], assoc['Product B'], assoc['Co-occurrence']))
            edge_labels.append(f"{assoc['Co-occurrence']}")
        
        # Create Plotly visualization
        nodes_list = list(products)
        node_x = []
        node_y = []
        
        # Simple circular layout
        import math
        circle_radius = 1
        for i, node in enumerate(nodes_list):
            angle = 2 * math.pi * i / len(nodes_list)
            node_x.append(circle_radius * math.cos(angle))
            node_y.append(circle_radius * math.sin(angle))
        
        # Create edges
        edge_x = []
        edge_y = []
        edge_weight = []
        
        node_indices = {node: i for i, node in enumerate(nodes_list)}
        
        for product_a, product_b, count in edges:
            idx_a = node_indices[product_a]
            idx_b = node_indices[product_b]
            edge_x.extend([node_x[idx_a], node_x[idx_b], None])
            edge_y.extend([node_y[idx_a], node_y[idx_b], None])
            edge_weight.append(count)
        
        # Create figure
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=20,
                color='#FF6B6B',
                line=dict(color='#C92A2A', width=2)
            ),
            text=nodes_list,
            textposition='top center',
            hovertext=nodes_list,
            hoverinfo='text',
            showlegend=False
        ))
        
        fig.update_layout(
            title="Product Association Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=50),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#f8f9fa',
            height=600
        )
        
        return fig
    
    @staticmethod
    def plot_product_frequency(product_freq, top_n=15):
        """Plot most frequently purchased products"""
        if not product_freq or len(product_freq) == 0:
            return None
        
        top_products = product_freq[:top_n]
        products = [p[0] for p in top_products]
        frequencies = [p[1] for p in top_products]
        
        fig = px.bar(
            x=frequencies,
            y=products,
            orientation='h',
            title='Most Frequently Purchased Products',
            labels={'x': 'Purchase Count', 'y': 'Product'},
            color=frequencies,
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(height=400, showlegend=False)
        return fig
    
    @staticmethod
    def plot_association_strength(associations, top_n=15):
        """Plot top product associations by strength"""
        if not associations or len(associations) == 0:
            return None
        
        top_assoc = associations[:top_n]
        
        df_assoc = pd.DataFrame({
            'Pair': [f"{a['Product A']} → {a['Product B']}" for a in top_assoc],
            'Co-occurrence': [a['Co-occurrence'] for a in top_assoc],
            'Lift': [float(a['Lift']) for a in top_assoc]
        })
        
        fig = go.Figure(data=[
            go.Bar(
                y=df_assoc['Pair'],
                x=df_assoc['Co-occurrence'],
                name='Co-occurrence',
                orientation='h',
                marker_color='#4ECDC4'
            )
        ])
        
        fig.update_layout(
            title='Top Product Associations',
            xaxis_title='Co-occurrence Count',
            yaxis_title='Product Pair',
            height=400,
            showlegend=False
        )
        
        return fig


# =============================================================================
# STREAMLIT APPLICATION
# =============================================================================

def init_session_state():
    """Initialize session state variables"""
    if 'db' not in st.session_state:
        st.session_state.db = SmartBIDatabase()
    
    if 'current_df' not in st.session_state:
        st.session_state.current_df = None
    
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'ai_assistant' not in st.session_state:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY", None)
        except:
            api_key = None
        st.session_state.ai_assistant = AIAssistant(api_key)
    
    if 'engineered_df' not in st.session_state:
        st.session_state.engineered_df = None
    
    # Forecast session state variables
    if 'forecast_result' not in st.session_state:
        st.session_state.forecast_result = None
    
    if 'forecast_model' not in st.session_state:
        st.session_state.forecast_model = None
    
    if 'forecast_prophet_df' not in st.session_state:
        st.session_state.forecast_prophet_df = None
    
    if 'forecast_periods' not in st.session_state:
        st.session_state.forecast_periods = None
    
    if 'forecast_value_col' not in st.session_state:
        st.session_state.forecast_value_col = None
    
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None


def home_page():
    """Home page with overview and quick start"""
    st.title("🎯 SmartBI - Business Intelligence & Analytics")
    st.markdown("### Intelligent Data Analytics for SMBs and Researchers")
    
    st.markdown("""
    Welcome to **SmartBI**, your comprehensive solution for data analytics and business intelligence.
    
    #### 🚀 Key Features:
    
    1. **🔬 Smart Data Profiling & Quality Analysis**
       - Comprehensive data profiling with automated insights
       - Real-time quality issue detection and severity assessment
       - Missing value analysis and correlation discovery
       - Actionable recommendations for data improvement
    
    2. **🧪 Intelligent Data Preparation & Cleansing**
       - Advanced imputation methods (KNN, iterative, statistical)
       - Duplicate and outlier detection and removal
       - Before/after comparison with quality metrics
       - Automated data type optimization
    
    3. **⚡ Powerful Feature Engineering**
       - Create polynomial and interaction features instantly
       - Generate statistical rolling window features and lags
       - Automatic categorical encoding and one-hot conversion
       - AI-powered feature importance ranking
    
    4. **� Market Basket Analysis**
       - Discover which products are frequently bought together
       - Calculate association metrics (Support, Confidence, Lift)
       - Visualize product relationships and networks
       - Generate business recommendations for bundling and cross-sell
    
    5. **📊 Interactive Business Intelligence Dashboards**
       - Real-time interactive visualizations powered by Plotly
       - Deep correlation analysis and relationship mapping
       - Distribution and trend analysis across dimensions
       - Export-ready custom charts and reports
    
    6. **🎯 Predictive Time Series Forecasting**
       - Prophet-based forecasting with trend and seasonality detection
       - Automatic confidence interval calculations
       - Long-term predictions with accuracy metrics
       - Seasonal decomposition and anomaly detection
    
    7. **🤖 AI-Powered Insights & Assistance**
       - Natural language interface with conversation history
       - Context-aware data analysis and recommendations
       - Smart insights generation from your data
       - Personalized guidance throughout your analysis journey
    
    #### 📋 Quick Start:
    
    1. **Upload Data**: Go to "Data Upload" and load your CSV file
    2. **Analyze**: Use "Data Analysis" to understand your dataset
    3. **Clean Data**: Use "Data Cleaning" to prepare your data
    4. **Analyze Relationships**: Use "Market Basket" to find product associations
    5. **Engineer Features**: Extract and create new features
    6. **Visualize**: Create dashboards with interactive charts
    7. **Forecast**: Predict future trends with time series analysis
    8. **Ask AI**: Get insights from our AI assistant
    """)
    
    # System status
    st.markdown("---")
    st.subheader("📦 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "✅ Available" if SKLEARN_AVAILABLE else "❌ Not Available"
        st.metric("scikit-learn", status)
    
    with col2:
        status = "✅ Available" if PROPHET_AVAILABLE else "❌ Not Available"
        st.metric("Prophet", status)
    
    with col3:
        status = "✅ Available" if OPENAI_AVAILABLE else "❌ Not Available"
        st.metric("OpenAI", status)
    
    # Sample data
    if st.button("📥 Load Sample Dataset"):
        sample_df = generate_sample_data()
        st.session_state.current_df = sample_df
        st.success("Sample dataset loaded! Go to 'Data Overview' to explore.")


def data_upload_page():
    """Data upload and management page"""
    st.title("📤 Data Upload & Management")
    
    tab1, tab2 = st.tabs(["Upload New Data", "Saved Datasets"])
    
    with tab1:
        st.subheader("Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Strip whitespace from column names
                df.columns = df.columns.str.strip()
                
                # Step 1: For columns with numeric keywords, aggressively convert
                numeric_keywords = ['amount', 'total', 'price', 'revenue', 'quantity', 'age', 'count', 'value', 'sales', 'year', 'month']
                datetime_keywords = ['date', 'time', 'timestamp', 'datetime']
                
                converted_numeric = []
                converted_datetime = []
                
                for col in df.columns:
                    col_lower = col.lower()
                    
                    # IMPORTANT: Try conversion for ALL columns with numeric keywords
                    if any(keyword in col_lower for keyword in numeric_keywords):
                        try:
                            # Method 1: Direct conversion (for already numeric)
                            temp = pd.to_numeric(df[col], errors='coerce')
                            
                            # If that doesn't work well, try stripping currency
                            if temp.isna().sum() > len(df) * 0.3:
                                temp = df[col].astype(str).str.strip()
                                temp = temp.str.replace(r'[A-Za-z\$€£¥\s]', '', regex=True)  # Remove letters and currency symbols
                                temp = temp.str.replace(',', '')  # Remove commas
                                temp = pd.to_numeric(temp, errors='coerce')
                            
                            # Use the converted version
                            if temp.notna().sum() > 0:
                                df[col] = temp
                                converted_numeric.append(col)
                        except Exception as e:
                            pass
                    
                    # Step 2: Try to convert datetime keywords (only if not already numeric)
                    elif any(keyword in col_lower for keyword in datetime_keywords):
                        try:
                            temp = pd.to_datetime(df[col], errors='coerce')
                            # Check if conversion was successful (at least 50% of values converted)
                            if temp.notna().sum() > len(df) * 0.5:
                                df[col] = temp
                                converted_datetime.append(col)
                        except Exception as e:
                            pass
                
                st.session_state.current_df = df
                
                # Count numeric columns
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                
                st.success(f"✅ File uploaded successfully! {len(df)} rows, {len(df.columns)} columns")
                st.info(f"📊 Detected: {len(numeric_cols)} numeric, {len(categorical_cols)} categorical, {len(datetime_cols)} datetime columns")
                
                # Show detailed conversion info
                if converted_numeric or converted_datetime:
                    with st.expander("🔄 Data Type Conversions Applied"):
                        if converted_numeric:
                            st.write(f"✅ Numeric conversions: {', '.join(converted_numeric)}")
                        if converted_datetime:
                            st.write(f"📅 DateTime conversions: {', '.join(converted_datetime)}")
                
                if numeric_cols:
                    st.write(f"**Numeric columns:** {', '.join(numeric_cols)}")
                if datetime_cols:
                    st.write(f"**DateTime columns:** {', '.join(datetime_cols)}")
                if categorical_cols:
                    st.write(f"**Categorical columns:** {', '.join(categorical_cols[:5])}{'...' if len(categorical_cols) > 5 else ''}")
                
                # Preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10))
                
                # Show column types
                with st.expander("📋 Column Types"):
                    col_types = pd.DataFrame({
                        'Column': df.columns,
                        'Type': df.dtypes.astype(str)
                    })
                    st.dataframe(col_types)
                
                # Save option
                dataset_name = st.text_input("Dataset Name (optional)", 
                                            value=uploaded_file.name.replace('.csv', ''))
                if st.button("💾 Save Dataset"):
                    dataset_id = st.session_state.db.save_dataset(dataset_name, df)
                    st.success(f"Dataset saved with ID: {dataset_id}")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with tab2:
        st.subheader("Saved Datasets")
        datasets = st.session_state.db.list_datasets()
        
        if datasets:
            for ds_id, name, uploaded_at, rows, cols in datasets:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                col1.write(f"**{name}**")
                col2.write(f"{rows} rows")
                col3.write(f"{cols} columns")
                if col4.button("Load", key=f"load_{ds_id}"):
                    _, df = st.session_state.db.load_dataset(ds_id)
                    st.session_state.current_df = df
                    st.success(f"Loaded dataset: {name}")
                    st.rerun()
        else:
            st.info("No saved datasets yet.")


def data_overview_page():
    """Data overview and basic statistics"""
    st.title("📊 Data Overview")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df
    
    # Basic info
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", len(df))
    col2.metric("Columns", len(df.columns))
    col3.metric("Missing Values", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())
    
    # Data types
    st.subheader("Column Information")
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes,
        'Non-Null Count': df.count(),
        'Null Count': df.isnull().sum(),
        'Unique Values': df.nunique()
    })
    st.dataframe(col_info)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    st.dataframe(df.describe())
    
    # Data preview
    st.subheader("Data Preview")
    st.dataframe(df.head(20))


def data_cleaning_page():
    """Data cleaning with advanced imputation"""
    st.title("🧹 Data Cleaning")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df.copy()
    
    st.subheader("Missing Data Analysis")
    missing_info = DataCleaner.analyze_missing_data(df)
    
    if len(missing_info) > 0:
        st.dataframe(missing_info)
        
        # Imputation options
        st.subheader("Handle Missing Values")
        
        method = st.selectbox(
            "Imputation Method",
            ["Simple (Mean)", "Simple (Median)", "KNN Imputation", "Iterative (MICE)"]
        )
        
        if method == "KNN Imputation":
            n_neighbors = st.slider("Number of Neighbors", 2, 10, 5)
        
        if st.button("🔧 Apply Imputation"):
            with st.spinner("Cleaning data..."):
                if method == "Simple (Mean)":
                    cleaned_df = DataCleaner.simple_imputation(df, strategy='mean')
                elif method == "Simple (Median)":
                    cleaned_df = DataCleaner.simple_imputation(df, strategy='median')
                elif method == "KNN Imputation":
                    cleaned_df = DataCleaner.knn_imputation(df, n_neighbors=n_neighbors)
                elif method == "Iterative (MICE)":
                    cleaned_df = DataCleaner.iterative_imputation(df)
                
                st.session_state.cleaned_df = cleaned_df
                st.success("✅ Data cleaned successfully!")
                
                # Show comparison
                col1, col2 = st.columns(2)
                col1.metric("Before - Missing Values", df.isnull().sum().sum())
                col2.metric("After - Missing Values", cleaned_df.isnull().sum().sum())
    else:
        st.success("✅ No missing values detected!")
    
    # Duplicate removal
    st.subheader("Remove Duplicates")
    if st.button("🗑️ Remove Duplicates"):
        cleaned_df, removed = DataCleaner.remove_duplicates(df)
        st.session_state.cleaned_df = cleaned_df
        st.success(f"✅ Removed {removed} duplicate rows")
    
    # Outlier handling
    st.subheader("Handle Outliers")
    col1, col2 = st.columns(2)
    
    with col1:
        outlier_method = st.selectbox("Method", ["IQR", "Z-Score"])
    
    with col2:
        threshold = st.slider("Threshold", 1.0, 3.0, 1.5, 0.1)
    
    if st.button("🎯 Handle Outliers"):
        cleaned_df = DataCleaner.handle_outliers(
            df, 
            method=outlier_method.lower(), 
            threshold=threshold
        )
        st.session_state.cleaned_df = cleaned_df
        st.success("✅ Outliers handled!")
    
    # Apply cleaned data
    if st.session_state.cleaned_df is not None:
        st.markdown("---")
        if st.button("✅ Apply Cleaned Data as Current Dataset"):
            st.session_state.current_df = st.session_state.cleaned_df
            st.session_state.cleaned_df = None
            st.success("Cleaned data applied!")
            st.rerun()


def dashboard_page():
    """Interactive dashboard creation"""
    st.title("📊 Dynamic Dashboard")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df
    
    # Chart type selector
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Correlation Matrix", "Distribution", "Box Plot", "Violin Plot", "Time Series", 
         "Scatter Plot", "Bar Chart", "Histogram", "Pie Chart", "Heatmap", "Sunburst (Categorical)"]
    )
    
    # Common chart styling
    chart_config = {"displayModeBar": True, "displaylogo": False}
    
    if chart_type == "Correlation Matrix":
        fig = Visualizer.plot_correlation_matrix(df)
        if fig:
            fig.update_layout(
                template="plotly_white",
                height=600,
                font=dict(size=11),
                title_font_size=14,
                coloraxis_colorbar=dict(title="Correlation")
            )
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("Need at least 2 numeric columns for correlation matrix")
    
    elif chart_type == "Distribution":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.caption(f"📊 Available numeric columns: {len(numeric_cols)}")
            column = st.selectbox("Select Column", numeric_cols, help="Only numeric columns are available for distribution analysis")
            fig = Visualizer.plot_distribution(df, column)
            fig.update_layout(
                template="plotly_white",
                height=500,
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("No numeric columns found")
    
    elif chart_type == "Box Plot":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            value_col = col1.selectbox("Value Column", numeric_cols)
            
            group_col = None
            if cat_cols:
                group_col = col2.selectbox("Group By (Optional)", ["None"] + cat_cols)
                if group_col == "None":
                    group_col = None
            
            fig = px.box(
                df,
                y=value_col,
                x=group_col if group_col else None,
                title=f"Box Plot of {value_col}",
                template="plotly_white"
            )
            fig.update_layout(height=500, hovermode="closest")
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("No numeric columns found")
    
    elif chart_type == "Violin Plot":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            value_col = col1.selectbox("Value Column", numeric_cols)
            
            group_col = None
            if cat_cols:
                group_col = col2.selectbox("Group By (Optional)", ["None"] + cat_cols)
                if group_col == "None":
                    group_col = None
            
            fig = px.violin(
                df,
                y=value_col,
                x=group_col if group_col else None,
                title=f"Violin Plot of {value_col}",
                template="plotly_white",
                points="outliers"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("No numeric columns found")
    
    elif chart_type == "Time Series":
        date_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if date_cols and numeric_cols:
            col1, col2 = st.columns(2)
            date_col = col1.selectbox("Date Column", date_cols)
            value_col = col2.selectbox("Value Column", numeric_cols)
            
            fig = Visualizer.plot_time_series(df, date_col, value_col)
            fig.update_layout(
                template="plotly_white",
                height=500,
                hovermode="x unified",
                title_font_size=14
            )
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("Need date and numeric columns")
    
    elif chart_type == "Scatter Plot":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            col1, col2, col3 = st.columns(3)
            x_col = col1.selectbox("X Axis", numeric_cols)
            y_col = col2.selectbox("Y Axis", [c for c in numeric_cols if c != x_col])
            
            color_col = None
            if cat_cols:
                color_col = col3.selectbox("Color By (Optional)", ["None"] + cat_cols)
                if color_col == "None":
                    color_col = None
            
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{y_col} vs {x_col}",
                template="plotly_white",
                hover_data={col: ":.2f" if df[col].dtype != 'object' else True for col in [x_col, y_col] + ([color_col] if color_col else [])}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("Need at least 2 numeric columns")
    
    elif chart_type == "Bar Chart":
        columns = df.columns.tolist()
        col1, col2 = st.columns(2)
        x_col = col1.selectbox("X Axis (Category)", columns)
        y_col = col2.selectbox("Y Axis (Value)", [c for c in columns if c != x_col])
        
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=f'{y_col} by {x_col}',
            template="plotly_white",
            color=y_col,
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=500, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True, config=chart_config)
    
    elif chart_type == "Histogram":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            value_col = col1.selectbox("Column", numeric_cols)
            nbins = col2.slider("Number of Bins", 10, 100, 30)
            
            fig = px.histogram(
                df,
                x=value_col,
                nbins=nbins,
                title=f"Histogram of {value_col}",
                template="plotly_white",
                color_discrete_sequence=["#636EFA"],
                marginal="box"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.warning("No numeric columns found")
    
    elif chart_type == "Pie Chart":
        columns = df.columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if cat_cols and numeric_cols:
            col1, col2 = st.columns(2)
            label_col = col1.selectbox("Category Column", cat_cols)
            value_col = col2.selectbox("Value Column", numeric_cols)
            
            # Aggregate by category
            pie_data = df.groupby(label_col)[value_col].sum().reset_index()
            
            fig = px.pie(
                pie_data,
                values=value_col,
                names=label_col,
                title=f"{value_col} Distribution by {label_col}",
                template="plotly_white",
                hover_data={value_col: ":.2f"}
            )
            fig.update_layout(
                height=500,
                font=dict(size=11)
            )
            st.plotly_chart(fig, use_container_width=True, config=chart_config)
        else:
            st.info("Need at least 1 categorical column and 1 numeric column for pie chart")
    
    elif chart_type == "Heatmap":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            # Select subset of columns for heatmap
            selected_cols = st.multiselect("Select columns for heatmap", numeric_cols, default=numeric_cols)
            
            if selected_cols:
                try:
                    # Remove rows with missing values in selected columns for correlation
                    corr_data = df[selected_cols].dropna()
                    
                    if len(corr_data) == 0:
                        st.error("❌ No valid data after removing missing values")
                    else:
                        corr_matrix = corr_data.corr()
                        fig = px.imshow(
                            corr_matrix,
                            text_auto=".2f",
                            aspect="auto",
                            color_continuous_scale="RdBu_r",
                            title="Correlation Heatmap",
                            labels=dict(color="Correlation")
                        )
                        fig.update_layout(height=600)
                        st.plotly_chart(fig, use_container_width=True, config=chart_config)
                except Exception as e:
                    st.error(f"❌ Error creating heatmap: {str(e)}")
                    st.info("💡 Tip: Make sure selected columns are numeric and have valid values")
        else:
            st.info(f"Need at least 2 numeric columns for heatmap. Found: {len(numeric_cols)} numeric columns")
    
    elif chart_type == "Sunburst (Categorical)":
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Show all numeric columns but suggest which ones are best for aggregation
        # Filter out only obvious ID columns that never make sense to aggregate
        id_keywords = ['_id', 'id_', 'transaction_id', 'customer_id']
        poor_agg_cols = [col for col in numeric_cols if any(kw in col.lower() for kw in id_keywords)]
        recommended_cols = [col for col in numeric_cols if col not in poor_agg_cols]
        
        if len(cat_cols) >= 2 and numeric_cols:
            col1, col2, col3 = st.columns(3)
            level1 = col1.selectbox("Level 1", cat_cols, help="First category level")
            level2 = col2.selectbox("Level 2", [c for c in cat_cols if c != level1], help="Second category level")
            
            # Show all numeric columns, but mark recommended ones
            value_options = []
            for col in numeric_cols:
                if col in recommended_cols:
                    value_options.append(f"✓ {col}")
                else:
                    value_options.append(f"⚠️ {col}")
            
            value_display = col3.selectbox(
                "Values", 
                value_options,
                help="✓ = Recommended for aggregation | ⚠️ = Use with caution (ID columns)"
            )
            
            # Extract actual column name
            value_col = value_display.replace("✓ ", "").replace("⚠️ ", "")
            
            try:
                # Create sunburst data with proper hierarchy
                sunburst_data = df.groupby([level1, level2])[value_col].sum().reset_index()
                
                # Rename columns for sunburst
                sunburst_data_clean = sunburst_data.copy()
                sunburst_data_clean['level1'] = sunburst_data_clean[level1]
                sunburst_data_clean['level2'] = sunburst_data_clean[level2]
                sunburst_data_clean['combined'] = sunburst_data_clean['level1'].astype(str) + ' - ' + sunburst_data_clean['level2'].astype(str)
                
                # Create hierarchical data structure
                # Root level
                root_df = pd.DataFrame({
                    'labels': ['Total'],
                    'parents': [''],
                    'values': [sunburst_data_clean[value_col].sum()]
                })
                
                # Level 1 aggregation
                level1_df = sunburst_data_clean.groupby('level1')[value_col].sum().reset_index()
                level1_df.columns = ['labels', 'values']
                level1_df['parents'] = 'Total'
                
                # Level 2 (leaf nodes)
                level2_df = sunburst_data_clean[['combined', 'level1', value_col]].copy()
                level2_df.columns = ['labels', 'parents', 'values']
                
                # Combine all levels
                final_data = pd.concat([
                    root_df,
                    level1_df,
                    level2_df
                ], ignore_index=True)
                
                # Create sunburst
                fig = px.sunburst(
                    final_data,
                    labels='labels',
                    parents='parents',
                    values='values',
                    title=f"Sunburst: {level1} → {level2} (Aggregated by {value_col})",
                    template="plotly_white"
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True, config=chart_config)
                
                # Show warning if using ID column
                if value_col in poor_agg_cols:
                    st.warning(f"⚠️ '{value_col}' appears to be an ID column. Results may not be meaningful.")
                    
            except Exception as e:
                st.error(f"❌ Error creating sunburst: {str(e)}")
                st.info("💡 **Tip:** For sunburst charts:")
                st.write("- **Level 1 & 2:** Categorical columns (text/categories)")
                st.write("- **Values:** Numeric column to aggregate (sum/count)")
                st.write(f"- **Best choices for Values:** {', '.join([c for c in recommended_cols if len(c) < 20])}")
        else:
            if len(cat_cols) < 2:
                st.info("Need at least 2 categorical columns for sunburst chart")
            else:
                st.info(f"Need numeric columns for Values. Found: {len(numeric_cols)} numeric columns")


def market_basket_page():
    """Market Basket Analysis - Find frequently bought items together"""
    st.title("🛒 Market Basket Analysis")
    st.markdown("Analyze which products are frequently purchased together and discover business opportunities")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Product Associations", "POS Overview", "Customer Insights", "Category Analysis", "Time Analysis"])
    
    with tab1:
        st.subheader("Product Association Analysis")
        st.markdown("Discover which products are frequently purchased together")
        
        # Column selection
        col1, col2 = st.columns(2)
        with col1:
            transaction_col = st.selectbox(
                "Transaction Column",
                df.columns.tolist(),
                help="Column containing products separated by delimiter"
            )
        
        with col2:
            delimiter = st.text_input("Product Separator", value="+", help="Character separating products")
        
        # Analysis parameters
        col1, col2, col3 = st.columns(3)
        min_support = col1.slider("Min Support (%)", 1, 100, 5)
        min_products = col2.slider("Min Products/Transaction", 1, 10, 2)
        show_triplets = col3.checkbox("Show Product Triplets", value=True)
        
        if st.button("🔍 Analyze Associations"):
            with st.spinner("Analyzing product associations..."):
                result = InsightGenerator.analyze_product_associations(
                    df, transaction_col, separator=delimiter, min_product_length=min_products
                )
                
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Transactions", result['total_transactions'])
                    col2.metric("Unique Products", result['unique_products'])
                    col3.metric("Product Pairs Found", len(result['associations']))
                    col4.metric("Avg Products/Transaction", f"{sum(len(t) for t in df[transaction_col].str.split(delimiter)) / len(df):.1f}")
                    
                    st.markdown("---")
                    
                    # Associations subtabs
                    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(
                        ["📊 Association Rules", "🕸️ Network", "📈 Product Frequency", "⭐ Strength"]
                    )
                    
                    with sub_tab1:
                        st.subheader("Top Product Associations")
                        
                        # Filter by minimum support
                        min_support_count = max(1, int(result['total_transactions'] * min_support / 100))
                        filtered_associations = [a for a in result['associations'] if a['Co-occurrence'] >= min_support_count]
                        
                        if filtered_associations:
                            display_assoc = []
                            for assoc in filtered_associations[:50]:
                                display_assoc.append({
                                    'Product A': assoc['Product A'],
                                    'Product B': assoc['Product B'],
                                    'Times Bought Together': assoc['Co-occurrence'],
                                    'Support %': float(assoc['Support'].rstrip('%')),
                                    'Confidence A→B': float(assoc['Confidence (A→B)'].rstrip('%')),
                                    'Confidence B→A': float(assoc['Confidence (B→A)'].rstrip('%')),
                                    'Lift': float(assoc['Lift'])
                                })
                            
                            st.dataframe(display_assoc, use_container_width=True)
                            
                            csv = pd.DataFrame(display_assoc).to_csv(index=False)
                            st.download_button("📥 Download CSV", csv, "associations.csv", "text/csv")
                        else:
                            st.info(f"No associations found with {min_support}% support. Lower the threshold.")
                    
                    with sub_tab2:
                        st.subheader("Product Association Network")
                        min_support_count = max(1, int(result['total_transactions'] * min_support / 100))
                        filtered_associations = [a for a in result['associations'] if a['Co-occurrence'] >= min_support_count]
                        
                        fig_network = Visualizer.plot_product_association_network(filtered_associations, top_n=20)
                        if fig_network:
                            st.plotly_chart(fig_network, use_container_width=True)
                        else:
                            st.info("Not enough data for network visualization")
                    
                    with sub_tab3:
                        st.subheader("Product Purchase Frequency")
                        fig_freq = Visualizer.plot_product_frequency(result['product_freq'], top_n=25)
                        if fig_freq:
                            st.plotly_chart(fig_freq, use_container_width=True)
                        
                        freq_df = pd.DataFrame(result['product_freq'], columns=['Product', 'Purchase Count'])
                        st.dataframe(freq_df, use_container_width=True)
                    
                    with sub_tab4:
                        st.subheader("Association Strength Ranking")
                        min_support_count = max(1, int(result['total_transactions'] * min_support / 100))
                        filtered_associations = [a for a in result['associations'] if a['Co-occurrence'] >= min_support_count]
                        
                        fig_strength = Visualizer.plot_association_strength(filtered_associations, top_n=20)
                        if fig_strength:
                            st.plotly_chart(fig_strength, use_container_width=True)
                    
                    # Insights
                    st.markdown("---")
                    st.subheader("💡 Insights & Recommendations")
                    if filtered_associations:
                        top_pair = filtered_associations[0]
                        insights = [
                            f"🏆 **Top Pair**: '{top_pair['Product A']}' + '{top_pair['Product B']}' (bought together {top_pair['Co-occurrence']}x)",
                            f"💡 **Bundle Opportunity**: Create a bundle with these products to increase sales",
                            f"📊 **Average Co-occurrence**: {sum(a['Co-occurrence'] for a in filtered_associations) / len(filtered_associations):.1f} times",
                        ]
                        for insight in insights:
                            st.info(insight)
    
    with tab2:
        st.subheader("📊 POS Transaction Overview")
        
        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Transactions", len(df))
        col2.metric("Date Range", f"{df['Date'].min() if 'Date' in df.columns else 'N/A'} to {df['Date'].max() if 'Date' in df.columns else 'N/A'}")
        
        if 'Total_Amount_JOD' in df.columns:
            col3.metric("Total Revenue", f"JOD {df['Total_Amount_JOD'].sum():,.2f}")
            col4.metric("Avg Transaction", f"JOD {df['Total_Amount_JOD'].mean():,.2f}")
        
        st.markdown("---")
        
        # Transaction amount distribution
        if 'Total_Amount_JOD' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_amount = px.histogram(
                    df, 
                    x='Total_Amount_JOD',
                    nbins=50,
                    title='Transaction Amount Distribution',
                    labels={'Total_Amount_JOD': 'Amount (JOD)'}
                )
                st.plotly_chart(fig_amount, use_container_width=True)
            
            with col2:
                fig_box = px.box(
                    df,
                    y='Total_Amount_JOD',
                    title='Transaction Amount Box Plot',
                    labels={'Total_Amount_JOD': 'Amount (JOD)'}
                )
                st.plotly_chart(fig_box, use_container_width=True)
    
    with tab3:
        st.subheader("👥 Customer Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Customer_Status' in df.columns:
                status_data = df['Customer_Status'].value_counts()
                fig_status = px.pie(
                    values=status_data.values,
                    names=status_data.index,
                    title='Customer Status Distribution'
                )
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            if 'Payment_Method' in df.columns:
                payment_data = df['Payment_Method'].value_counts()
                fig_payment = px.pie(
                    values=payment_data.values,
                    names=payment_data.index,
                    title='Payment Method Distribution'
                )
                st.plotly_chart(fig_payment, use_container_width=True)
        
        st.markdown("---")
        
        # Customer age analysis
        if 'Customer_Age' in df.columns:
            fig_age = px.histogram(
                df,
                x='Customer_Age',
                nbins=30,
                title='Customer Age Distribution',
                labels={'Customer_Age': 'Age'}
            )
            st.plotly_chart(fig_age, use_container_width=True)
        
        # Customer spending by status
        if 'Customer_Status' in df.columns and 'Total_Amount_JOD' in df.columns:
            spending_by_status = df.groupby('Customer_Status')['Total_Amount_JOD'].agg(['mean', 'sum', 'count'])
            st.subheader("Spending by Customer Status")
            st.dataframe(spending_by_status, use_container_width=True)
    
    with tab4:
        st.subheader("📦 Product Category Analysis")
        
        if 'Primary_Item_Category' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                category_counts = df['Primary_Item_Category'].value_counts()
                fig_cat = px.bar(
                    x=category_counts.values,
                    y=category_counts.index,
                    orientation='h',
                    title='Transactions by Category',
                    labels={'x': 'Count', 'y': 'Category'}
                )
                st.plotly_chart(fig_cat, use_container_width=True)
            
            with col2:
                if 'Total_Amount_JOD' in df.columns:
                    category_revenue = df.groupby('Primary_Item_Category')['Total_Amount_JOD'].sum().sort_values(ascending=False)
                    fig_rev = px.bar(
                        x=category_revenue.values,
                        y=category_revenue.index,
                        orientation='h',
                        title='Revenue by Category (JOD)',
                        labels={'x': 'Revenue', 'y': 'Category'}
                    )
                    st.plotly_chart(fig_rev, use_container_width=True)
            
            st.markdown("---")
            
            # Category detailed stats
            if 'Total_Amount_JOD' in df.columns:
                st.subheader("Category Performance Metrics")
                cat_stats = df.groupby('Primary_Item_Category').agg({
                    'Transaction_ID': 'count',
                    'Total_Amount_JOD': ['sum', 'mean', 'min', 'max']
                }).round(2)
                cat_stats.columns = ['Transactions', 'Total Revenue', 'Avg Amount', 'Min', 'Max']
                st.dataframe(cat_stats, use_container_width=True)
    
    with tab5:
        st.subheader("⏰ Time-based Analysis")
        
        if 'Day_of_Week' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_counts = df['Day_of_Week'].value_counts().reindex(day_order, fill_value=0)
                fig_day = px.bar(
                    x=day_counts.index,
                    y=day_counts.values,
                    title='Transactions by Day of Week',
                    labels={'x': 'Day', 'y': 'Transaction Count'}
                )
                st.plotly_chart(fig_day, use_container_width=True)
            
            with col2:
                if 'Total_Amount_JOD' in df.columns:
                    day_revenue = df.groupby('Day_of_Week')['Total_Amount_JOD'].sum().reindex(day_order, fill_value=0)
                    fig_day_rev = px.bar(
                        x=day_revenue.index,
                        y=day_revenue.values,
                        title='Revenue by Day of Week',
                        labels={'x': 'Day', 'y': 'Revenue (JOD)'}
                    )
                    st.plotly_chart(fig_day_rev, use_container_width=True)


def forecasting_page():
    """Time series forecasting with Prophet"""
    st.title("🔮 Time Series Forecasting")
    
    if not PROPHET_AVAILABLE:
        st.error("❌ Prophet is not installed. Please install it: pip install prophet")
        return
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df
    
    st.subheader("Configure Forecast")
    
    # Column selection
    date_cols = df.select_dtypes(include=['datetime64', 'object']).columns.tolist()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if not date_cols or not numeric_cols:
        st.warning("Need both date and numeric columns for forecasting")
        return
    
    col1, col2 = st.columns(2)
    date_col = col1.selectbox("Date Column", date_cols)
    value_col = col2.selectbox("Value Column", numeric_cols)
    
    # Forecast parameters
    st.subheader("Forecast Parameters")
    col1, col2 = st.columns(2)
    
    periods = col1.number_input("Forecast Periods", min_value=1, max_value=365, value=30)
    
    with col2:
        yearly_seasonality = st.checkbox("Yearly Seasonality", value=True)
        weekly_seasonality = st.checkbox("Weekly Seasonality", value=True)
        daily_seasonality = st.checkbox("Daily Seasonality", value=False)
    
    # Run forecast
    if st.button("🚀 Generate Forecast"):
        with st.spinner("Training model and generating forecast..."):
            try:
                # Prepare data
                prophet_df = TimeSeriesForecaster.prepare_prophet_data(df, date_col, value_col)
                
                # Train and forecast
                model, forecast = TimeSeriesForecaster.forecast_with_prophet(
                    prophet_df,
                    periods=periods,
                    yearly_seasonality=yearly_seasonality,
                    weekly_seasonality=weekly_seasonality,
                    daily_seasonality=daily_seasonality
                )
                
                if model and forecast is not None:
                    # Save to session state to persist across reruns
                    st.session_state.forecast_model = model
                    st.session_state.forecast_result = forecast
                    st.session_state.forecast_prophet_df = prophet_df
                    st.session_state.forecast_periods = periods
                    st.session_state.forecast_value_col = value_col
                    
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")
    
    # Display forecast results (from session state if available)
    if 'forecast_result' in st.session_state and st.session_state.forecast_result is not None:
        st.write("🔍 DEBUG: Forecast results found in session state")
        forecast = st.session_state.forecast_result
        model = st.session_state.forecast_model
        prophet_df = st.session_state.forecast_prophet_df
        periods = st.session_state.forecast_periods
        value_col = st.session_state.forecast_value_col
        
        st.success("✅ Forecast generated successfully!")
        
        # Plot
        fig = TimeSeriesForecaster.plot_forecast(model, forecast, prophet_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display accuracy metrics
        st.subheader("📊 Forecast Accuracy Metrics")
        
        metrics = TimeSeriesForecaster.calculate_accuracy_metrics(prophet_df, forecast)
        
        if metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("MAE (Mean Absolute Error)", f"{metrics['MAE']:.2f}")
                st.caption("Lower is better")
            
            with col2:
                st.metric("RMSE (Root Mean Square Error)", f"{metrics['RMSE']:.2f}")
                st.caption("Lower is better")
            
            with col3:
                st.metric("MAPE (%)", f"{metrics['MAPE']:.2f}%")
                st.caption("Lower is better")
            
            with col4:
                st.metric("R² (Coefficient)", f"{metrics['R²']:.4f}")
                st.caption("Closer to 1 is better")
            
            st.info(f"ℹ️ Metrics calculated on {metrics['samples']} historical data points")
            
            # Interpretation
            st.subheader("📈 Interpretation")
            if metrics['MAPE'] < 5:
                accuracy_level = "🟢 **Excellent** - Very reliable forecast"
            elif metrics['MAPE'] < 10:
                accuracy_level = "🟡 **Good** - Reliable forecast"
            elif metrics['MAPE'] < 20:
                accuracy_level = "🟠 **Fair** - Moderate accuracy"
            else:
                accuracy_level = "🔴 **Poor** - Consider more data or different approach"
            
            st.markdown(f"**Forecast Accuracy Level:** {accuracy_level}")
            
            if metrics['R²'] < 0:
                st.warning("⚠️ R² is negative, suggesting the forecast performs worse than a simple average. Consider adding more data or adjusting parameters.")
            elif metrics['R²'] < 0.3:
                st.warning("⚠️ Low R² (< 0.3) indicates weak model fit. More historical data might help.")
            elif metrics['R²'] < 0.7:
                st.info("✓ Moderate R² (0.3-0.7). Model captures some patterns but has room for improvement.")
            else:
                st.success("✅ Strong R² (≥ 0.7). Model captures most of the data variation.")
        else:
            st.warning("⚠️ Could not calculate accuracy metrics. Ensure you have sufficient historical data.")
        
        # Show forecast data
        st.subheader("Forecast Data")
        future_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        future_forecast.columns = ['Date', 'Forecast', 'Lower Bound', 'Upper Bound']
        st.dataframe(future_forecast)
        
        # Download forecast
        csv = future_forecast.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast",
            data=csv,
            file_name=f"forecast_{value_col}.csv",
            mime="text/csv"
        )


def data_analysis_page():
    """Comprehensive data analysis and profiling"""
    st.title("📊 Data Analysis & Insights")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df
    
    # Validate data
    if df.empty:
        st.error("❌ Dataset is empty. Please upload a valid dataset.")
        return
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.warning("⚠️ No numeric columns found. Some analysis features may be limited.")
    
    # Generate analysis
    profile = DataProfiler.generate_profile(df)
    data_types = DataProfiler.detect_data_types(df)
    missing_analysis = DataProfiler.analyze_missing_values(df)
    quality_issues = DataProfiler.identify_quality_issues(df)
    feature_insights = InsightGenerator.analyze_features(df)
    correlation_insights = InsightGenerator.analyze_correlations(df)
    recommendations = InsightGenerator.generate_recommendations(df, quality_issues)
    
    # =========================================================================
    # SECTION 1: DATA UNDERSTANDING
    # =========================================================================
    st.header("1️⃣ Data Understanding & Profiling")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📈 Rows", f"{profile['shape']['rows']:,}")
    col2.metric("📊 Columns", profile['shape']['columns'])
    col3.metric("💾 Memory", f"{profile['memory_usage']:.2f} MB")
    col4.metric("🚨 Issues Found", len(quality_issues) if isinstance(quality_issues, list) else 0)
    
    st.subheader("Data Types Distribution")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"📊 Numeric: {len(data_types['numeric'])} columns")
    with col2:
        st.info(f"🏷️ Categorical: {len(data_types['categorical'])} columns")
    with col3:
        st.info(f"📅 DateTime: {len(data_types['datetime'])} columns")
    
    # Detailed column information
    st.subheader("Column Details")
    col_info = pd.DataFrame({
        'Column': df.columns,
        'Type': df.dtypes.astype(str),
        'Non-Null': df.count(),
        'Null': df.isnull().sum(),
        'Unique Values': df.nunique()
    })
    st.dataframe(col_info, use_container_width=True)
    
    # =========================================================================
    # SECTION 2: DATA QUALITY & ISSUES
    # =========================================================================
    st.header("2️⃣ Data Quality Report")
    
    # Missing values
    st.subheader("Missing Values Analysis")
    if len(missing_analysis) > 0:
        st.dataframe(missing_analysis, use_container_width=True)
        st.warning(f"Found missing values in {len(missing_analysis)} column(s)")
    else:
        st.success("✅ No missing values detected!")
    
    # Duplicates
    st.subheader("Duplicate Analysis")
    dup_info = DataProfiler.detect_duplicates(df)
    col1, col2 = st.columns(2)
    col1.metric("Total Duplicated Rows", dup_info['total_duplicates'])
    col2.metric("Columns with Duplicates", len(dup_info['by_column']))
    
    if dup_info['by_column']:
        st.dataframe(pd.DataFrame(dup_info['by_column']), use_container_width=True)
    
    # Quality issues
    st.subheader("Data Quality Issues")
    for issue in quality_issues:
        st.write(issue)
    
    # =========================================================================
    # SECTION 3: FEATURE ANALYSIS
    # =========================================================================
    st.header("3️⃣ Feature Analysis")
    
    st.subheader("Statistical Summary")
    summary = DataProfiler.get_statistical_summary(df)
    st.dataframe(summary, use_container_width=True)
    
    st.subheader("Feature Insights")
    for insight in feature_insights:
        st.write(insight)
    
    # =========================================================================
    # SECTION 4: CORRELATION ANALYSIS
    # =========================================================================
    st.header("4️⃣ Correlation & Relationships")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 2:
        st.subheader("Correlation Analysis")
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='RdBu_r',
            title="Feature Correlation Matrix",
            labels=dict(color="Correlation")
        )
        fig.update_layout(
            height=600,
            font=dict(size=10),
            title_font_size=14,
            hovermode="closest"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation insights
        st.subheader("Relationship Insights")
        for insight in correlation_insights:
            st.write(insight)
        
        st.info("⚠️ **Important**: Correlation does not imply causation. Strong correlations may be coincidental or due to other factors.")
    else:
        st.info("Need at least 2 numeric columns for correlation analysis")
    
    # =========================================================================
    # SECTION 5: DISTRIBUTION ANALYSIS
    # =========================================================================
    st.header("5️⃣ Distribution Analysis")
    
    if numeric_cols:
        st.subheader("Numeric Feature Distributions")
        st.caption(f"📊 Available numeric columns: {len(numeric_cols)}")
        selected_col = st.selectbox("Select column to analyze", numeric_cols, help="Only numeric columns are available for distribution analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.histogram(
                df,
                x=selected_col,
                title=f"Distribution of {selected_col}",
                marginal="box",
                nbins=30,
                template="plotly_white"
            )
            fig.update_layout(
                height=450,
                hovermode="x unified",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Add box plot alternative
            fig_box = px.box(
                df,
                y=selected_col,
                title=f"Box Plot of {selected_col}",
                template="plotly_white"
            )
            fig_box.update_layout(height=450, showlegend=False)
            st.plotly_chart(fig_box, use_container_width=True)
        
        # Statistics in columns
        col1, col2, col3, col4 = st.columns(4)
        stats = df[selected_col].describe()
        col1.metric("Mean", f"{stats['mean']:.2f}")
        col2.metric("Median", f"{df[selected_col].median():.2f}")
        col3.metric("Std Dev", f"{stats['std']:.2f}")
        col4.metric("Skewness", f"{df[selected_col].skew():.2f}")
    
    # Categorical distributions
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    if cat_cols:
        st.subheader("Categorical Feature Distributions")
        selected_cat = st.selectbox("Select categorical column", cat_cols)
        
        value_counts = df[selected_cat].value_counts().head(20)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                x=value_counts.values,
                y=value_counts.index,
                orientation='h',
                title=f"Top Values in {selected_cat}",
                labels={'x': 'Count', 'y': 'Value'},
                template="plotly_white",
                color=value_counts.values,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig_pie = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=f"Distribution of {selected_cat}",
                template="plotly_white"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # =========================================================================
    # SECTION 6: RECOMMENDATIONS
    # =========================================================================
    st.header("6️⃣ Automated Recommendations")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # =========================================================================
    # SECTION 7: CLEANING REPORT (if data has been cleaned)
    # =========================================================================
    if st.session_state.cleaned_df is not None:
        st.header("7️⃣ Before & After Cleaning Comparison")
        
        original = st.session_state.current_df
        cleaned = st.session_state.cleaned_df
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Data")
            st.write(f"Rows: {len(original)}")
            st.write(f"Missing values: {original.isnull().sum().sum()}")
            st.write(f"Duplicates: {original.duplicated().sum()}")
        
        with col2:
            st.subheader("After Cleaning")
            st.write(f"Rows: {len(cleaned)}")
            st.write(f"Missing values: {cleaned.isnull().sum().sum()}")
            st.write(f"Duplicates: {cleaned.duplicated().sum()}")


def feature_engineering_page():
    """Feature extraction and engineering"""
    st.title("🔧 Feature Engineering")
    
    if st.session_state.current_df is None:
        st.warning("⚠️ No data loaded. Please upload data first.")
        return
    
    df = st.session_state.current_df.copy()
    
    # Validate data
    if df.empty:
        st.error("❌ Dataset is empty. Please upload a valid dataset.")
        return
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        st.warning("⚠️ No numeric columns available for feature engineering.")
        return
    
    # Feature engineering options
    st.subheader("Feature Engineering Tools")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Polynomial", "Interactions", "Statistical", "Categorical", "Importance"])
    
    with tab1:
        st.subheader("Polynomial Features")
        st.write("Create polynomial features (x², x³, etc.) to capture non-linear relationships.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        selected_cols = st.multiselect("Select columns for polynomial features", numeric_cols, default=numeric_cols if numeric_cols else [])
        degree = st.slider("Polynomial degree", 2, 4, 2)
        
        if st.button("🔧 Create Polynomial Features"):
            if not selected_cols:
                st.error("❌ Please select at least one column for polynomial features.")
            else:
                with st.spinner("Creating polynomial features..."):
                    engineered_df = FeatureExtractor.create_polynomial_features(df, selected_cols, degree=degree)
                    st.session_state.engineered_df = engineered_df
                    new_features = len(engineered_df.columns) - len(df.columns)
                    st.success(f"✅ Created {new_features} new polynomial features!")
                    st.dataframe(engineered_df.head())
    
    with tab2:
        st.subheader("Interaction Features")
        st.write("Create interaction features (x*y) to capture relationships between features.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        selected_cols = st.multiselect("Select columns for interactions", numeric_cols, key="interaction_cols", default=numeric_cols if numeric_cols else [])
        
        if st.button("🔧 Create Interaction Features"):
            if not selected_cols:
                st.error("❌ Please select at least one column for interaction features.")
            elif len(selected_cols) < 2:
                st.error("❌ Please select at least 2 columns to create interactions.")
            else:
                with st.spinner("Creating interaction features..."):
                    engineered_df = FeatureExtractor.create_interaction_features(df, selected_cols)
                    st.session_state.engineered_df = engineered_df
                    new_features = len(engineered_df.columns) - len(df.columns)
                    st.success(f"✅ Created {new_features} new interaction features!")
                    st.dataframe(engineered_df.head())
    
    with tab3:
        st.subheader("Statistical Rolling Features")
        st.write("Create rolling mean, std, and lag features for time series analysis.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        selected_cols = st.multiselect("Select columns for statistical features", numeric_cols, key="stat_cols", default=numeric_cols if numeric_cols else [])
        window = st.slider("Rolling window size", 3, 30, 7)
        
        if st.button("🔧 Create Statistical Features"):
            if not selected_cols:
                st.error("❌ Please select at least one column for statistical features.")
            else:
                with st.spinner("Creating statistical features..."):
                    engineered_df = FeatureExtractor.create_statistical_features(df, selected_cols, window=window)
                    st.session_state.engineered_df = engineered_df
                    new_features = len(engineered_df.columns) - len(df.columns)
                    st.success(f"✅ Created {new_features} new statistical features!")
                    st.dataframe(engineered_df.head())
    
    with tab4:
        st.subheader("Categorical Encoding")
        st.write("One-hot encode categorical variables for machine learning.")
        
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        if cat_cols:
            selected_col = st.selectbox("Select categorical column", cat_cols)
            
            if st.button("🔧 One-Hot Encode"):
                with st.spinner("Encoding categorical features..."):
                    engineered_df = FeatureExtractor.create_categorical_features(df, selected_col)
                    st.session_state.engineered_df = engineered_df
                    new_features = len(engineered_df.columns) - len(df.columns)
                    st.success(f"✅ Created {new_features} new encoded features!")
                    st.dataframe(engineered_df.head())
        else:
            st.info("No categorical columns found in the dataset.")
    
    with tab5:
        st.subheader("Feature Importance Analysis")
        st.write("Analyze correlations between variables.")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        all_cols = numeric_cols + cat_cols
        
        if numeric_cols or cat_cols:
            # Analysis mode selector
            analysis_mode = st.radio("Analysis Type", ["Compare 2 Variables", "Target Variable (All Features)"], horizontal=True)
            
            if analysis_mode == "Compare 2 Variables":
                st.caption("🔍 Calculate correlation between any 2 columns in your dataset")
                col1, col2 = st.columns(2)
                
                with col1:
                    col1_select = st.selectbox("Select First Variable", all_cols, key="col1_imp")
                with col2:
                    col2_select = st.selectbox("Select Second Variable", all_cols, key="col2_imp")
                
                if st.button("📊 Calculate Correlation"):
                    # Check if both columns are numeric
                    if col1_select in numeric_cols and col2_select in numeric_cols:
                        corr_value = df[col1_select].corr(df[col2_select])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Correlation Coefficient", f"{corr_value:.4f}")
                        with col2:
                            corr_strength = "Strong" if abs(corr_value) > 0.7 else "Moderate" if abs(corr_value) > 0.4 else "Weak"
                            st.metric("Strength", corr_strength)
                        with col3:
                            direction = "Positive" if corr_value > 0 else "Negative"
                            st.metric("Direction", direction)
                        
                        # Visualization
                        fig = px.scatter(
                            df,
                            x=col1_select,
                            y=col2_select,
                            title=f"Correlation between {col1_select} and {col2_select}",
                            trendline="ols",
                            labels={col1_select: col1_select, col2_select: col2_select}
                        )
                        fig.update_layout(height=500, hovermode="closest", template="plotly_white")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Interpretation
                        st.info(f"**Interpretation:** {col1_select} and {col2_select} have a {corr_strength.lower()} {direction.lower()} correlation (r={corr_value:.4f})")
                    
                    elif col1_select in numeric_cols and col2_select in cat_cols:
                        # Numeric vs Categorical
                        st.subheader(f"Analysis: {col1_select} by {col2_select}")
                        
                        # Create grouped statistics
                        grouped_stats = df.groupby(col2_select)[col1_select].agg(['mean', 'median', 'std', 'count'])
                        st.dataframe(grouped_stats)
                        
                        # Visualization
                        fig = px.box(
                            df,
                            x=col2_select,
                            y=col1_select,
                            title=f"{col1_select} Distribution by {col2_select}",
                            template="plotly_white"
                        )
                        fig.update_layout(height=500, hovermode="closest")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif col1_select in cat_cols and col2_select in numeric_cols:
                        # Categorical vs Numeric
                        st.subheader(f"Analysis: {col2_select} by {col1_select}")
                        
                        # Create grouped statistics
                        grouped_stats = df.groupby(col1_select)[col2_select].agg(['mean', 'median', 'std', 'count'])
                        st.dataframe(grouped_stats)
                        
                        # Visualization
                        fig = px.box(
                            df,
                            x=col1_select,
                            y=col2_select,
                            title=f"{col2_select} Distribution by {col1_select}",
                            template="plotly_white"
                        )
                        fig.update_layout(height=500, hovermode="closest")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    else:
                        st.warning("⚠️ Select at least one numeric column for analysis")
            
            else:
                # Original target variable analysis
                st.caption("📊 Correlations of all numeric features with a target variable")
                if numeric_cols:
                    target_col = st.selectbox("Select target column", numeric_cols)
                    
                    if st.button("📊 Analyze Feature Importance"):
                        importance = FeatureExtractor.feature_importance_analysis(df, target_col)
                        if importance is not None:
                            st.success("✅ Feature importance calculated!")
                            
                            # Display as dataframe
                            importance_df = pd.DataFrame({
                                'Feature': importance.index,
                                'Correlation_Strength': importance.values
                            })
                            st.dataframe(importance_df)
                            
                            # Visualize
                            fig = px.bar(
                                importance_df,
                                x='Correlation_Strength',
                                y='Feature',
                                orientation='h',
                                title=f'Feature Importance vs {target_col}'
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric columns found for importance analysis.")
        else:
            st.info("No numeric or categorical columns found for analysis.")
    
    # Apply engineered features
    if st.session_state.engineered_df is not None:
        st.markdown("---")
        st.subheader("Apply Engineered Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Use Engineered Data as Current Dataset"):
                st.session_state.current_df = st.session_state.engineered_df
                st.session_state.engineered_df = None
                st.success("✅ Engineered features applied!")
                st.rerun()
        
        with col2:
            csv = st.session_state.engineered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Engineered Dataset",
                data=csv,
                file_name="engineered_features.csv",
                mime="text/csv"
            )


def ai_assistant_page():
    """Conversational AI assistant"""
    st.title("🤖 AI Assistant")
    
    assistant = st.session_state.ai_assistant
    
    if not assistant.available:
        st.warning("⚠️ OpenAI API key not configured. Running in fallback mode with limited responses.")
        st.info("To enable full AI features, add your OpenAI API key in .streamlit/secrets.toml")
    
    # Chat interface
    st.subheader("Chat with SmartBI Assistant")
    
    # Display chat history
    for role, content, _ in st.session_state.db.get_chat_history():
        with st.chat_message(role):
            st.write(content)
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your data..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Save user message
        st.session_state.db.save_chat_message("user", prompt)
        
        # Generate context
        context = ""
        if st.session_state.current_df is not None:
            df = st.session_state.current_df
            context = f"Dataset: {len(df)} rows, {len(df.columns)} columns. Columns: {', '.join(df.columns[:10])}"
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = assistant.chat(prompt, context=context)
                st.write(response)
        
        # Save assistant message
        st.session_state.db.save_chat_message("assistant", response)
    
    # Quick actions
    st.subheader("Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    if col1.button("💡 Suggest Analysis"):
        st.session_state.quick_prompt = "What analysis would you suggest for this dataset?"
    
    if col2.button("📊 Explain Data"):
        st.session_state.quick_prompt = "Can you explain the key characteristics of this dataset?"
    
    if col3.button("🔍 Find Issues"):
        st.session_state.quick_prompt = "What data quality issues should I address?"


def generate_sample_data():
    """Generate sample dataset for demo"""
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)
    
    # Generate time series with trend and seasonality
    trend = np.linspace(100, 200, len(dates))
    seasonality = 20 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
    noise = np.random.normal(0, 10, len(dates))
    sales = trend + seasonality + noise
    
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'customers': np.random.poisson(50, len(dates)),
        'region': np.random.choice(['North', 'South', 'East', 'West'], len(dates)),
        'category': np.random.choice(['A', 'B', 'C'], len(dates))
    })
    
    # Add some missing values
    missing_indices = np.random.choice(df.index, size=50, replace=False)
    df.loc[missing_indices, 'sales'] = np.nan
    
    return df


def main():
    """Main application"""
    st.set_page_config(
        page_title="SmartBI - Business Intelligence",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🎯 SmartBI")
    st.sidebar.markdown("---")
    
    menu_options = ["🏠 Home", "📤 Data Upload", "📊 Data Overview", "🔬 Data Analysis", "🧹 Data Cleaning", 
                    "🔧 Feature Engineering", "📈 Dashboard", "🛒 Market Basket", "🔮 Forecasting", "🤖 AI Assistant"]
    
    page = st.sidebar.radio("Navigation", menu_options)
    
    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "📤 Data Upload":
        data_upload_page()
    elif page == "📊 Data Overview":
        data_overview_page()
    elif page == "🔬 Data Analysis":
        data_analysis_page()
    elif page == "🧹 Data Cleaning":
        data_cleaning_page()
    elif page == "🔧 Feature Engineering":
        feature_engineering_page()
    elif page == "📈 Dashboard":
        dashboard_page()
    elif page == "🛒 Market Basket":
        market_basket_page()
    elif page == "🔮 Forecasting":
        forecasting_page()
    elif page == "🤖 AI Assistant":
        ai_assistant_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**SmartBI v1.0**")
    st.sidebar.markdown("Business Intelligence & Analytics Platform")


if __name__ == "__main__":
    main()