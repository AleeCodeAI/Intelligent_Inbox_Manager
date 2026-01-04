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
        """Load and parse the memory.jsonl file"""
        self.data = []
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.data.append(json.loads(line))
            
            # Convert to DataFrame
            self.df = pd.DataFrame(self.data)
            
            # Parse datetime
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
        """Get email classification distribution"""
        if self.df is None or self.df.empty:
            return None
        
        classification_counts = self.df['classification'].value_counts()
        
        fig = px.pie(
            values=classification_counts.values,
            names=classification_counts.index,
            title="Email Classification Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=True,
            height=500,
            font=dict(size=14),
            paper_bgcolor='#1a0f2a',  # foam background color
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_confidence_analysis(self):
        """Analyze classification confidence scores"""
        if self.df is None or self.df.empty:
            return None
        
        fig = px.box(
            self.df,
            x='classification',
            y='confidence',
            title="Classification Confidence Score Distribution",
            color='classification',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            xaxis_title="Classification Type",
            yaxis_title="Confidence Score",
            showlegend=False,
            height=500,
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_daily_email_volume(self):
        """Get daily email volume trend"""
        if self.df is None or self.df.empty:
            return None
        
        daily_counts = self.df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = pd.to_datetime(daily_counts['date'])
        
        fig = px.line(
            daily_counts,
            x='date',
            y='count',
            title="Daily Email Volume Trend",
            markers=True
        )
        
        fig.update_traces(
            line_color='#8A2BE2',  # bright purple line
            line_width=3,
            marker=dict(size=8)
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Emails",
            hovermode='x unified',
            height=500,
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_hourly_distribution(self):
        """Get hourly email distribution"""
        if self.df is None or self.df.empty:
            return None
        
        hourly_counts = self.df['hour'].value_counts().sort_index()
        
        fig = px.bar(
            x=hourly_counts.index,
            y=hourly_counts.values,
            title="Email Volume by Hour of Day",
            labels={'x': 'Hour of Day', 'y': 'Number of Emails'},
            color=hourly_counts.values,
            color_continuous_scale='Purples'
        )
        
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            showlegend=False,
            height=500,
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_classification_by_day(self):
        """Get classification breakdown by day of week"""
        if self.df is None or self.df.empty:
            return None
        
        day_class = pd.crosstab(self.df['day_of_week'], self.df['classification'])
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_class = day_class.reindex([d for d in day_order if d in day_class.index])
        
        fig = px.bar(
            day_class,
            title="Email Classification by Day of Week",
            barmode='stack',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig.update_layout(
            xaxis_title="Day of Week",
            yaxis_title="Number of Emails",
            height=500,
            legend_title="Classification",
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_sender_analysis(self):
        """Analyze top senders"""
        if self.df is None or self.df.empty:
            return None
        
        sender_counts = self.df['from_name'].value_counts().head(10)
        
        fig = px.bar(
            x=sender_counts.values,
            y=sender_counts.index,
            orientation='h',
            title="Top 10 Email Senders",
            labels={'x': 'Number of Emails', 'y': 'Sender'},
            color=sender_counts.values,
            color_continuous_scale='Purples'
        )
        
        fig.update_layout(
            showlegend=False,
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_priority_timeline(self):
        """Show priority emails timeline"""
        if self.df is None or self.df.empty:
            return None
        
        priority_df = self.df[self.df['classification'] == 'PRIORITY'].copy()
        
        if priority_df.empty:
            return None
        
        priority_daily = priority_df.groupby('date').size().reset_index(name='count')
        priority_daily['date'] = pd.to_datetime(priority_daily['date'])
        
        fig = px.area(
            priority_daily,
            x='date',
            y='count',
            title="Priority Emails Timeline",
            color_discrete_sequence=['#FF00FF']  # bright purple
        )
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Priority Emails",
            height=400,
            paper_bgcolor='#1a0f2a',
            plot_bgcolor='#1a0f2a'
        )
        
        return fig
    
    def get_stats_summary(self):
        """Get summary statistics"""
        if self.df is None or self.df.empty:
            return {}
        
        return {
            'total_emails': len(self.df),
            'avg_confidence': self.df['confidence'].mean(),
            'priority_count': len(self.df[self.df['classification'] == 'PRIORITY']),
            'unique_senders': self.df['from_email'].nunique(),
            'date_range': f"{self.df['date'].min()} to {self.df['date'].max()}"
        }


# Streamlit App
def main():
    st.set_page_config(
        page_title="Email Analytics Dashboard",
        page_icon="📧",
        layout="wide"
    )
    
    # Custom CSS for dark purple theme
    st.markdown("""
        <style>
        /* Main background slightly lighter dark purple */
        .stApp {
            background-color: #2a1a3d;
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* Foam/cards background darker purple */
        div[data-testid="stForm"] {
            background-color: #1a0f2a;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }

        /* All text in white for contrast */
        h1, h2, h3, h4, h5, h6, p, span, div {
            color: white !important;
        }

        .stMetric label {
            color: white !important;
        }

        .stMetric .metric-value {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Email Analytics Dashboard")
    st.markdown("### Comprehensive insights from your inbox management system")
    
    # Initialize analytics
    analytics = EmailAnalytics()
    
    # Create form container
    with st.form("analytics_form"):
        # Load data
        if analytics.load_data():
            stats = analytics.get_stats_summary()
            
            # Display summary metrics
            st.markdown("#### System Overview")
            st.markdown("This dashboard provides real-time analytics on email classification performance, sender patterns, and operational insights.")
            
            metric_cols = st.columns(5)
            
            with metric_cols[0]:
                st.metric("Total Emails Processed", stats['total_emails'])
            
            with metric_cols[1]:
                st.metric("Average Confidence", f"{stats['avg_confidence']:.2%}")
            
            with metric_cols[2]:
                st.metric("Priority Emails", stats['priority_count'])
            
            with metric_cols[3]:
                st.metric("Unique Senders", stats['unique_senders'])
            
            with metric_cols[4]:
                st.metric("Data Period Start", stats['date_range'].split(' to ')[0])
            
            st.markdown("---")
            
            # Classification Distribution Section
            st.markdown("#### Email Classification Analysis")
            st.markdown("The classification system categorizes incoming emails into four distinct categories: BASIC (general inquiries), SCHEDULER (meeting requests), PRIORITY (urgent matters), and NON_BUSINESS (personal or spam). Understanding this distribution helps optimize response workflows and resource allocation.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = analytics.get_classification_distribution()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Key Insight:** The pie chart shows the proportional distribution of email types, helping identify which categories dominate your inbox.")
            
            with col2:
                fig = analytics.get_confidence_analysis()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Key Insight:** Higher confidence scores indicate more certain classifications. Low outliers may require manual review to improve accuracy.")
            
            st.markdown("---")
            
            # Volume Trends Section
            st.markdown("#### Email Volume Trends")
            st.markdown("Tracking email volume over time reveals patterns in communication frequency, helping predict workload and identify peak activity periods. This data is crucial for capacity planning and ensuring timely responses during high-traffic periods.")
            
            fig = analytics.get_daily_email_volume()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Key Insight:** Daily volume trends highlight business cycles, campaign impacts, and seasonal variations in email traffic.")
            
            st.markdown("---")
            
            # Time-Based Patterns Section
            st.markdown("#### Temporal Distribution Patterns")
            st.markdown("Understanding when emails arrive helps optimize monitoring schedules and automate responses during off-hours. These patterns reveal sender behavior and can inform business hour policies.")
            
            col3, col4 = st.columns(2)
            
            with col3:
                fig = analytics.get_hourly_distribution()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Key Insight:** Hourly distribution identifies peak times for incoming mail. Use this to schedule automated processing or allocate monitoring resources effectively.")
            
            with col4:
                fig = analytics.get_classification_by_day()
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("**Key Insight:** Weekly patterns show how email types vary by day. Notice if certain days receive more priority emails or scheduler requests.")
            
            st.markdown("---")
            
            # Priority Analysis Section
            st.markdown("#### Priority Email Monitoring")
            st.markdown("Priority emails require immediate attention and represent time-sensitive business matters such as urgent issues, appointment confirmations, or critical notifications. Tracking these over time helps assess system responsiveness and workload management.")
            
            fig = analytics.get_priority_timeline()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Key Insight:** Spikes in priority emails indicate critical periods requiring heightened attention. Use this timeline to evaluate response times and system performance during high-priority situations.")
            
            st.markdown("---")
            
            # Sender Analysis Section
            st.markdown("#### Sender Activity Analysis")
            st.markdown("Identifying frequent senders helps understand communication patterns, recognize key contacts, and detect potential spam sources. This analysis supports relationship management and helps prioritize important correspondences.")
            
            fig = analytics.get_sender_analysis()
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("**Key Insight:** High-frequency senders may be important clients, partners, or automated systems. Consider creating custom handling rules for top senders to improve efficiency.")
            
            st.markdown("---")
            
            # Footer
            st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Data Source:** memory.jsonl | **Total Records:** {len(analytics.df)}")
            
        else:
            st.warning("Unable to load data. Please check the file path and ensure memory.jsonl exists.")
        
        # Submit button (required for form but doesn't do anything special)
        submitted = st.form_submit_button("Refresh Dashboard", use_container_width=True)
        if submitted:
            st.rerun()


if __name__ == "__main__":
    main()
