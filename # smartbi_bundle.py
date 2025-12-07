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
            api_key = st.secrets["OPENAI_API_KEY"]
        except:
            api_key = None
        st.session_state.ai_assistant = AIAssistant(api_key)


def home_page():
    """Home page with overview and quick start"""
    st.title("🎯 SmartBI - Business Intelligence & Analytics")
    st.markdown("### Intelligent Data Analytics for SMBs and Researchers")
    
    st.markdown("""
    Welcome to **SmartBI**, your comprehensive solution for data analytics and business intelligence.
    
    #### 🚀 Key Features:
    
    1. **📊 Data Cleaning & Preparation**
       - Handle missing values with advanced imputation methods
       - Remove duplicates and outliers
       - Data quality analysis
    
    2. **📈 Dynamic Dashboards**
       - Interactive visualizations
       - Correlation analysis
       - Distribution plots
       - Custom charts
    
    3. **🔮 Time Series Forecasting**
       - Prophet-based forecasting
       - Seasonality detection
       - Confidence intervals
       - Long-term predictions
    
    4. **🤖 AI Assistant**
       - Conversational interface
       - Data insights
       - Analysis recommendations
       - Context-aware help
    
    #### 📋 Quick Start:
    
    1. **Upload Data**: Go to "Data Upload" and load your CSV file
    2. **Clean Data**: Use "Data Cleaning" to prepare your data
    3. **Visualize**: Create dashboards with interactive charts
    4. **Forecast**: Predict future trends with time series analysis
    5. **Ask AI**: Get insights from our AI assistant
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
                st.session_state.current_df = df
                
                st.success(f"✅ File uploaded successfully! {len(df)} rows, {len(df.columns)} columns")
                
                # Preview
                st.subheader("Data Preview")
                st.dataframe(df.head(10))
                
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
        ["Correlation Matrix", "Distribution", "Time Series", "Scatter Plot", "Bar Chart"]
    )
    
    if chart_type == "Correlation Matrix":
        fig = Visualizer.plot_correlation_matrix(df)
        if fig:
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Need at least 2 numeric columns for correlation matrix")
    
    elif chart_type == "Distribution":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            column = st.selectbox("Select Column", numeric_cols)
            fig = Visualizer.plot_distribution(df, column)
            st.plotly_chart(fig, width='stretch')
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
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Need date and numeric columns")
    
    elif chart_type == "Scatter Plot":
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            x_col = col1.selectbox("X Axis", numeric_cols)
            y_col = col2.selectbox("Y Axis", [c for c in numeric_cols if c != x_col])
            
            fig = Visualizer.plot_scatter(df, x_col, y_col)
            st.plotly_chart(fig, width='stretch')
        else:
            st.warning("Need at least 2 numeric columns")
    
    elif chart_type == "Bar Chart":
        columns = df.columns.tolist()
        col1, col2 = st.columns(2)
        x_col = col1.selectbox("X Axis (Category)", columns)
        y_col = col2.selectbox("Y Axis (Value)", [c for c in columns if c != x_col])
        
        fig = px.bar(df, x=x_col, y=y_col, title=f'{y_col} by {x_col}')
        st.plotly_chart(fig, width='stretch')


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
                    st.success("✅ Forecast generated successfully!")
                    
                    # Plot
                    fig = TimeSeriesForecaster.plot_forecast(model, forecast, prophet_df)
                    st.plotly_chart(fig, width='stretch')
                    
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
                
            except Exception as e:
                st.error(f"Error generating forecast: {str(e)}")


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
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "📤 Data Upload", "📊 Data Overview", "🧹 Data Cleaning", 
         "📈 Dashboard", "🔮 Forecasting", "🤖 AI Assistant"]
    )
    
    # Page routing
    if page == "🏠 Home":
        home_page()
    elif page == "📤 Data Upload":
        data_upload_page()
    elif page == "📊 Data Overview":
        data_overview_page()
    elif page == "🧹 Data Cleaning":
        data_cleaning_page()
    elif page == "📈 Dashboard":
        dashboard_page()
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