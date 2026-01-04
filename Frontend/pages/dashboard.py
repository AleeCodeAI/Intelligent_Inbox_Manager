import streamlit as st
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

class EmailAnalytics:
    def __init__(self, memory_path="D:\\Projects\\inbox-manager\\databases\\memory.jsonl"):
        self.memory_path = Path(memory_path)
        self.data = []
        self.df = None
        
    def load_data(self):
        self.data = []
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.data.append(json.loads(line))
            
            self.df = pd.DataFrame(self.data)
            self.df['timestamp'] = pd.to_datetime(self.df['time'])
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_of_week'] = self.df['timestamp'].dt.day_name()
            return True
        except FileNotFoundError:
            st.error(f"Memory file not found at: {self.memory_path}")
            return False
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def get_classification_distribution(self):
        if self.df is None or self.df.empty:
            return None
        
        classification_counts = self.df['classification'].value_counts()
        fig = px.pie(
            values=classification_counts.values,
            names=classification_counts.index,
            title="Email Classification Distribution",
            hole=0.4
        )
        fig.update_layout(
            font=dict(size=14, color='white'),
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_confidence_analysis(self):
        if self.df is None or self.df.empty:
            return None
        
        fig = px.box(
            self.df,
            x='classification',
            y='confidence',
            title="Classification Confidence Score Distribution",
            color='classification'
        )
        fig.update_layout(
            showlegend=False,
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_daily_email_volume(self):
        if self.df is None or self.df.empty:
            return None
        
        daily_counts = self.df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        fig = px.line(daily_counts, x='date', y='count', markers=True)
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_hourly_distribution(self):
        if self.df is None or self.df.empty:
            return None
        
        hourly_counts = self.df['hour'].value_counts().sort_index()
        fig = px.bar(x=hourly_counts.index, y=hourly_counts.values)
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_classification_by_day(self):
        if self.df is None or self.df.empty:
            return None
        
        day_class = pd.crosstab(self.df['day_of_week'], self.df['classification'])
        fig = px.bar(day_class, barmode='stack')
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_sender_analysis(self):
        if self.df is None or self.df.empty:
            return None
        
        sender_counts = self.df['from_name'].value_counts().head(10)
        fig = px.bar(
            x=sender_counts.values,
            y=sender_counts.index,
            orientation='h'
        )
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_priority_timeline(self):
        if self.df is None or self.df.empty:
            return None
        
        priority_df = self.df[self.df['classification'] == 'PRIORITY']
        if priority_df.empty:
            return None
        
        priority_daily = priority_df.groupby('date').size().reset_index(name='count')
        priority_daily['date'] = pd.to_datetime(priority_daily['date'])
        fig = px.area(priority_daily, x='date', y='count')
        fig.update_layout(
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    
    def get_stats_summary(self):
        if self.df is None or self.df.empty:
            return {}
        
        return {
            'total_emails': len(self.df),
            'avg_confidence': self.df['confidence'].mean(),
            'priority_count': len(self.df[self.df['classification'] == 'PRIORITY']),
            'unique_senders': self.df['from_email'].nunique(),
            'date_range': f"{self.df['date'].min()} to {self.df['date'].max()}"
        }


def main():
    st.set_page_config(
        page_title="Email Analytics Dashboard",
        page_icon=None,
        layout="wide"
    )
    
    # ------------------ ANIMATION-ONLY CSS ------------------
    st.markdown("""
    <style>

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(18px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slowGlow {
        0% { box-shadow: 0 0 0 rgba(160,32,240,0.0); }
        50% { box-shadow: 0 0 22px rgba(160,32,240,0.25); }
        100% { box-shadow: 0 0 0 rgba(160,32,240,0.0); }
    }

    .stApp {
        background: linear-gradient(270deg, #0f0518, #12081d, #0b0313);
        background-size: 400% 400%;
        animation: fadeUp 0.8s ease-out;
    }

    section[data-testid="stMetric"] {
        animation: fadeUp 0.8s ease-out;
        border-radius: 14px;
    }

    section[data-testid="stMetric"]:hover {
        animation: slowGlow 3s infinite;
        transform: translateY(-3px);
        transition: 0.3s ease;
    }

    div[data-testid="stPlotlyChart"] {
        animation: fadeUp 0.9s ease-out;
        transition: transform 0.3s ease;
    }

    div[data-testid="stPlotlyChart"]:hover {
        transform: translateY(-4px);
    }

    </style>
    """, unsafe_allow_html=True)

    st.title("Email Analytics Dashboard")
    st.markdown("### Comprehensive insights from your inbox management system")

    analytics = EmailAnalytics()

    with st.form("analytics_form"):
        if analytics.load_data():
            stats = analytics.get_stats_summary()
            
            metric_cols = st.columns(5)
            metric_cols[0].metric("Total Emails", stats['total_emails'])
            metric_cols[1].metric("Avg Confidence", f"{stats['avg_confidence']:.2%}")
            metric_cols[2].metric("Priority Emails", stats['priority_count'])
            metric_cols[3].metric("Unique Senders", stats['unique_senders'])
            metric_cols[4].metric("Start Date", stats['date_range'].split(' to ')[0])

            st.divider()

            col1, col2 = st.columns(2)
            col1.plotly_chart(analytics.get_classification_distribution(), use_container_width=True)
            col2.plotly_chart(analytics.get_confidence_analysis(), use_container_width=True)

            st.divider()
            st.plotly_chart(analytics.get_daily_email_volume(), use_container_width=True)

            st.divider()
            col3, col4 = st.columns(2)
            col3.plotly_chart(analytics.get_hourly_distribution(), use_container_width=True)
            col4.plotly_chart(analytics.get_classification_by_day(), use_container_width=True)

            st.divider()
            fig = analytics.get_priority_timeline()
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.plotly_chart(analytics.get_sender_analysis(), use_container_width=True)

            st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        submitted = st.form_submit_button("Refresh Dashboard", use_container_width=True)
        if submitted:
            st.rerun()


if __name__ == "__main__":
    main()
