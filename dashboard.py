import streamlit as st
import plotly.express as px
import pandas as pd
import subprocess
import time
import threading
from typing import List, Optional

from sqlalchemy.orm import sessionmaker
from app.db.db import engine
from app.models.models import Topic, IndicatorMeta, Country, IndicatorValue, ETLLog

# Database session
Session = sessionmaker(bind=engine)

class DatabaseService:
    
    def __init__(self):
        self.session = Session()
    
    def get_topics(self) -> List[Topic]:
        return self.session.query(Topic).order_by(Topic.name).all()
    
    def get_indicators_by_topic(self, topic_id: int) -> List[IndicatorMeta]:
        return self.session.query(IndicatorMeta).filter_by(topic_id=topic_id).all()
    
    def get_countries(self) -> List[Country]:
        return self.session.query(Country).order_by(Country.name).all()
    
    def get_indicator_data(self, indicator_id: int, country_ids: List[int], year_min: int, year_max: int) -> pd.DataFrame:
        rows = (
            self.session.query(IndicatorValue)
            .filter(IndicatorValue.indicator_id == indicator_id)
            .filter(IndicatorValue.country_id.in_(country_ids))
            .filter(IndicatorValue.date >= year_min)
            .filter(IndicatorValue.date <= year_max)
            .all()
        )
        return pd.DataFrame([{
            "country": r.country.name,
            "year": r.date,
            "value": r.value,
            "indicator_id": indicator_id
        } for r in rows])
    
    def get_latest_logs(self, limit: int = 50) -> pd.DataFrame:
        logs = (
            self.session.query(ETLLog)
            .order_by(ETLLog.timestamp.desc())
            .limit(limit)
            .all()
        )
        return pd.DataFrame([{
            "timestamp": log.timestamp,
            "level": log.level,
            "message": log.message
        } for log in logs])
    
    def close(self):
        self.session.close()

class ETLService:
    """Handle ETL operations"""
    
    @staticmethod
    def run_etl_pipeline() -> tuple[bool, str]:
        try:
            result = subprocess.run(
                ["python", "-m", "app.etl.pipeline"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.output

class VisualizationService:
    """Handle data visualisation"""
    
    @staticmethod
    def create_line_chart(df: pd.DataFrame, indicator_name: str):
        if df.empty:
            return None
        
        fig = px.line(
            df, 
            x="year", 
            y="value", 
            color="country", 
            markers=True, 
            title=f"{indicator_name} - Trends Over Time"
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Value",
            hovermode='x unified'
        )
        return fig
    
    @staticmethod
    def create_heatmap(df: pd.DataFrame, indicator_name: str):
        if df.empty:
            return None
            
        pivot_df = df.pivot_table(
            index="country", 
            columns="year", 
            values="value", 
            aggfunc="mean"
        )
        
        if pivot_df.empty:
            return None
            
        fig = px.imshow(
            pivot_df,
            text_auto=True,
            labels=dict(color="Value"),
            color_continuous_scale="YlGnBu",
            title=f"{indicator_name} - Country Comparison Heatmap"
        )
        return fig

def render_sidebar(db_service: DatabaseService):
    """Render sidebar with filters"""
    with st.sidebar:
        st.title("World Bank Dashboard")
        st.markdown("---")
        
        topic_list = db_service.get_topics()
        topic = st.selectbox("Select Topic", topic_list, format_func=lambda x: x.name)
        
        indicators = db_service.get_indicators_by_topic(topic.id)
        default_ids = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "SE.ADT.LITR.ZS"]
        selected_indicators = st.multiselect(
            "Choose Indicators",
            indicators,
            default=[i for i in indicators if i.code in default_ids],
            format_func=lambda x: x.name,
        )
        
        countries = db_service.get_countries()
        selected_countries = st.multiselect(
            "Select Countries", 
            countries, 
            default=countries[:5], 
            format_func=lambda x: x.name
        )
        
        year_range = st.slider(
            "Select Year Range", 
            min_value=2000, 
            max_value=2023, 
            value=(2010, 2023)
        )
        
        return topic, selected_indicators, selected_countries, year_range

def run_etl_in_background():
    """Run ETL pipeline in background thread"""
    success, output = ETLService.run_etl_pipeline()
    st.session_state.etl_running = False
    st.session_state.etl_success = success
    st.session_state.etl_output = output

def render_etl_section():
    """Render ETL management section"""
    with st.expander("ETL Pipeline Management", expanded=False):
        st.markdown("### Run ETL Pipeline")
        st.info("Click the button below to refresh data from World Bank API")
        
        if 'etl_running' not in st.session_state:
            st.session_state.etl_running = False
        
        if st.button("Run ETL Pipeline", type="primary", disabled=st.session_state.etl_running):
            st.session_state.etl_running = True
            st.session_state.etl_success = None
            st.session_state.etl_output = None
            
            etl_thread = threading.Thread(target=run_etl_in_background)
            etl_thread.daemon = True
            etl_thread.start()
        
        if hasattr(st.session_state, 'etl_success') and st.session_state.etl_success is not None:
            if st.session_state.etl_success:
                st.success("ETL pipeline completed successfully!")
                if st.button("Refresh Dashboard"):
                    st.rerun()
            else:
                st.error("ETL pipeline failed")
                with st.expander("Error Details"):
                    st.code(st.session_state.etl_output)

def render_logs_section(db_service: DatabaseService):
    """Render logs section with live updates"""
    with st.expander("ETL Logs", expanded=st.session_state.etl_running):
        st.markdown("### Recent ETL Activity")
        
        logs_df = db_service.get_latest_logs()
        
        if not logs_df.empty:
            def style_logs(df):
                def colour_level(val):
                    colours = {
                        'ERROR': 'background-color: #ffebee',
                        'WARNING': 'background-color: #fff3e0',
                        'INFO': 'background-color: #e8f5e8',
                        'DEBUG': 'background-color: #f3e5f5'
                    }
                    return colours.get(val, '')
                
                return df.style.applymap(colour_level, subset=['level'])
            
            st.dataframe(
                style_logs(logs_df),
                use_container_width=True,
                height=300
            )
        else:
            st.info("No logs available")

def render_dashboard(db_service: DatabaseService, selected_indicators, selected_countries, year_range):
    """Render main dashboard"""
    st.title("World Bank Indicators Dashboard")
    
    if not selected_indicators or not selected_countries:
        st.warning("Please select at least one indicator and one country from the sidebar to view data.")
        return
    
    country_ids = [c.id for c in selected_countries]
    all_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, indicator in enumerate(selected_indicators):
        status_text.text(f"Loading data for {indicator.name}...")
        
        df = db_service.get_indicator_data(
            indicator.id, 
            country_ids, 
            year_range[0], 
            year_range[1]
        )
        
        if not df.empty:
            df['indicator'] = indicator.name
            all_data.append(df)
        
        progress_bar.progress((i + 1) / len(selected_indicators))
    
    progress_bar.empty()
    status_text.empty()
    
    if not all_data:
        st.warning("No data available for the selected filters.")
        return
    
    combined_data = pd.concat(all_data, ignore_index=True)
    
    tab1, tab2, tab3 = st.tabs(["Trends", "Heatmaps", "Raw Data"])
    
    with tab1:
        st.header("Indicator Trends Over Time")
        for indicator in selected_indicators:
            indicator_data = combined_data[combined_data['indicator'] == indicator.name]
            
            if indicator_data.empty:
                st.warning(f"No data available for {indicator.name}")
                continue
            
            fig = VisualizationService.create_line_chart(indicator_data, indicator.name)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Country Comparison Heatmaps")
        for indicator in selected_indicators:
            indicator_data = combined_data[combined_data['indicator'] == indicator.name]
            
            if indicator_data.empty:
                continue
                
            fig = VisualizationService.create_heatmap(indicator_data, indicator.name)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Raw Data Table")
        st.dataframe(
            combined_data.sort_values(["indicator", "country", "year"]),
            use_container_width=True
        )

def main():
    """Main application function"""
    st.set_page_config(
        page_title="World Bank Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    db_service = DatabaseService()
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    current_time = time.time()
    refresh_interval = 1 if st.session_state.get('etl_running', False) else 5
    
    if current_time - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = current_time
        st.rerun()
    
    try:
        topic, selected_indicators, selected_countries, year_range = render_sidebar(db_service)
        
        render_etl_section()
        
        render_logs_section(db_service)
        
        render_dashboard(db_service, selected_indicators, selected_countries, year_range)
        
    finally:
        db_service.close()

if __name__ == "__main__":
    main()