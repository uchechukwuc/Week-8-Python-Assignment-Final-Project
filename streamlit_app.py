# CORD-19 Streamlit Dashboard
# Run with: streamlit run streamlit_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="CORD-19 Analysis Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f4e79;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #b3d9ff;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """
    Load sample CORD-19 data for demonstration
    In real usage, this would load the actual metadata.csv file
    """
    # Create realistic sample data
    np.random.seed(42)
    
    titles = [
        'COVID-19 transmission dynamics in healthcare settings',
        'SARS-CoV-2 vaccine efficacy and safety analysis',
        'Respiratory complications in coronavirus patients',
        'Economic impact of pandemic control measures',
        'Mental health effects of social distancing policies',
        'Clinical characteristics of COVID-19 in elderly patients',
        'Diagnostic accuracy of rapid antigen tests',
        'Long COVID symptoms and patient outcomes',
        'Healthcare worker infection rates during pandemic',
        'Effectiveness of mask mandates in reducing transmission',
        'COVID-19 variants and immune escape mechanisms',
        'Pediatric COVID-19 clinical presentation',
        'Vaccine hesitancy and public health messaging',
        'Remote work productivity during lockdowns',
        'Supply chain disruptions in pharmaceutical industry',
        'COVID-19 impact on cancer screening programs',
        'Telemedicine adoption during pandemic',
        'School closure effects on student learning',
        'Food security challenges during COVID-19',
        'Environmental changes during lockdown periods'
    ]
    
    journals = [
        'Nature Medicine', 'The Lancet', 'New England Journal of Medicine',
        'Science', 'Cell', 'BMJ', 'JAMA', 'PNAS', 'Nature', 'PLoS ONE',
        'Journal of Virology', 'Clinical Infectious Diseases', 
        'Epidemiology', 'Public Health Reports', 'Vaccine'
    ]
    
    sources = ['PubMed', 'PMC', 'bioRxiv', 'medRxiv', 'arXiv']
    
    # Generate sample data
    n_papers = 5000
    data = []
    
    for i in range(n_papers):
        # Random publication date (weighted towards 2020-2022 for COVID-19)
        if np.random.random() < 0.7:  # 70% from 2020-2022
            year = np.random.choice([2020, 2021, 2022], p=[0.3, 0.4, 0.3])
            month = np.random.randint(1, 13)
            day = np.random.randint(1, 29)
        else:  # 30% from other years
            year = np.random.randint(2015, 2024)
            month = np.random.randint(1, 13)
            day = np.random.randint(1, 29)
        
        pub_date = f"{year}-{month:02d}-{day:02d}"
        
        # Generate abstract with realistic word count
        abstract_length = np.random.normal(150, 50)
        abstract_length = max(50, min(300, int(abstract_length)))
        
        data.append({
            'title': np.random.choice(titles),
            'abstract': f"Abstract with {abstract_length} words about COVID-19 research...",
            'publish_time': pub_date,
            'journal': np.random.choice(journals),
            'source_x': np.random.choice(sources),
            'authors': f"Author{i%100} et al.",
            'abstract_word_count': abstract_length
        })
    
    df = pd.DataFrame(data)
    df['publish_time'] = pd.to_datetime(df['publish_time'])
    df['publish_year'] = df['publish_time'].dt.year
    
    return df

@st.cache_data
def analyze_data(df):
    """
    Perform data analysis and return results
    """
    results = {}
    
    # Publications by year
    results['yearly_counts'] = df['publish_year'].value_counts().sort_index()
    
    # Top journals
    results['top_journals'] = df['journal'].value_counts().head(10)
    
    # Source distribution
    results['source_counts'] = df['source_x'].value_counts()
    
    # Word count statistics
    results['avg_abstract_length'] = df['abstract_word_count'].mean()
    results['median_abstract_length'] = df['abstract_word_count'].median()
    
    return results

def create_publication_timeline(df, year_range):
    """
    Create interactive timeline of publications
    """
    filtered_df = df[
        (df['publish_year'] >= year_range[0]) & 
        (df['publish_year'] <= year_range[1])
    ]
    
    yearly_counts = filtered_df['publish_year'].value_counts().sort_index()
    
    fig = px.line(
        x=yearly_counts.index, 
        y=yearly_counts.values,
        title=f'Publications by Year ({year_range[0]}-{year_range[1]})',
        labels={'x': 'Year', 'y': 'Number of Publications'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Publications",
        hovermode='x'
    )
    
    return fig

def create_journal_chart(df, top_n):
    """
    Create horizontal bar chart of top journals
    """
    top_journals = df['journal'].value_counts().head(top_n)
    
    fig = px.bar(
        x=top_journals.values,
        y=top_journals.index,
        orientation='h',
        title=f'Top {top_n} Publishing Journals',
        labels={'x': 'Number of Papers', 'y': 'Journal'}
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400 + (top_n * 20)
    )
    
    return fig

def create_source_pie_chart(df):
    """
    Create pie chart of source distribution
    """
    source_counts = df['source_x'].value_counts()
    
    fig = px.pie(
        values=source_counts.values,
        names=source_counts.index,
        title='Distribution of Papers by Source'
    )
    
    return fig

def main():
    """
    Main Streamlit application
    """
    # Header
    st.markdown('<h1 class="main-header">🦠 CORD-19 Research Analysis Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    This dashboard analyzes COVID-19 research papers from the CORD-19 dataset.
    Explore publication trends, top journals, and research patterns over time.
    """)
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Controls")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_sample_data()
        analysis_results = analyze_data(df)
    
    st.sidebar.success(f"✅ Loaded {len(df):,} papers")
    
    # Sidebar filters
    st.sidebar.subheader("🔧 Filters")
    
    # Year range slider
    min_year, max_year = int(df['publish_year'].min()), int(df['publish_year'].max())
    year_range = st.sidebar.slider(
        "Publication Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(2020, max_year),
        step=1
    )
    
    # Top N journals selector
    top_n_journals = st.sidebar.selectbox(
        "Number of Top Journals to Display",
        options=[5, 10, 15, 20],
        index=1
    )
    
    # Source filter
    available_sources = df['source_x'].unique().tolist()
    selected_sources = st.sidebar.multiselect(
        "Select Sources",
        options=available_sources,
        default=available_sources
    )
    
    # Filter data based on selections
    filtered_df = df[
        (df['publish_year'] >= year_range[0]) & 
        (df['publish_year'] <= year_range[1]) &
        (df['source_x'].isin(selected_sources))
    ]
    
    # Main dashboard
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Papers",
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        st.metric(
            "Unique Journals",
            f"{filtered_df['journal'].nunique():,}"
        )
    
    with col3:
        avg_length = filtered_df['abstract_word_count'].mean()
        st.metric(
            "Avg Abstract Length",
            f"{avg_length:.0f} words"
        )
    
    with col4:
        date_range = filtered_df['publish_year'].max() - filtered_df['publish_year'].min()
        st.metric(
            "Year Range",
            f"{date_range + 1} years"
        )
    
    st.divider()
    
    # Visualizations
    st.header("📈 Publication Trends")
    
    # Timeline chart
    timeline_fig = create_publication_timeline(filtered_df, year_range)
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # Two column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Top Publishing Journals")
        journal_fig = create_journal_chart(filtered_df, top_n_journals)
        st.plotly_chart(journal_fig, use_container_width=True)
    
    with col2:
        st.subheader("🔗 Source Distribution")
        source_fig = create_source_pie_chart(filtered_df)
        st.plotly_chart(source_fig, use_container_width=True)
    
    st.divider()
    
    # Data insights
    st.header("💡 Key Insights")
    
    # Most productive year
    yearly_counts = filtered_df['publish_year'].value_counts().sort_index()
    if len(yearly_counts) > 0:
        most_productive_year = yearly_counts.idxmax()
        max_papers = yearly_counts.max()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="insight-box">
                <h4>📅 Peak Publication Year</h4>
                <p><strong>{}</strong> was the most productive year with <strong>{:,} papers</strong></p>
            </div>
            """.format(most_productive_year, max_papers), unsafe_allow_html=True)
        
        with col2:
            top_journal = filtered_df['journal'].value_counts().index[0]
            top_journal_count = filtered_df['journal'].value_counts().iloc[0]
            st.markdown("""
            <div class="insight-box">
                <h4>🏆 Leading Journal</h4>
                <p><strong>{}</strong> published <strong>{:,} papers</strong></p>
            </div>
            """.format(top_journal, top_journal_count), unsafe_allow_html=True)
        
        with col3:
            covid_peak = yearly_counts[yearly_counts.index >= 2020].max() if any(yearly_counts.index >= 2020) else 0
            pre_covid = yearly_counts[yearly_counts.index < 2020].max() if any(yearly_counts.index < 2020) else 1
            increase = ((covid_peak - pre_covid) / pre_covid * 100) if pre_covid > 0 else 0
            st.markdown("""
            <div class="insight-box">
                <h4>📈 COVID-19 Impact</h4>
                <p><strong>{:.1f}%</strong> increase in publications since 2020</p>
            </div>
            """.format(increase), unsafe_allow_html=True)
    
    st.divider()
    
    # Abstract length analysis
    st.header("📝 Abstract Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Abstract length distribution
        fig_hist = px.histogram(
            filtered_df,
            x='abstract_word_count',
            nbins=30,
            title='Distribution of Abstract Word Counts',
            labels={'abstract_word_count': 'Word Count', 'count': 'Frequency'}
        )
        
        # Add mean line
        mean_length = filtered_df['abstract_word_count'].mean()
        fig_hist.add_vline(
            x=mean_length, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Mean: {mean_length:.0f} words"
        )
        
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Abstract length by year
        yearly_avg_length = filtered_df.groupby('publish_year')['abstract_word_count'].mean().reset_index()
        
        fig_trend = px.line(
            yearly_avg_length,
            x='publish_year',
            y='abstract_word_count',
            title='Average Abstract Length Over Time',
            labels={'publish_year': 'Year', 'abstract_word_count': 'Average Word Count'},
            markers=True
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    # Sample data table
    st.header("📋 Sample Data")
    
    # Search functionality
    search_term = st.text_input("🔍 Search in titles:", placeholder="Enter keywords to search...")
    
    # Filter by search term
    display_df = filtered_df.copy()
    if search_term:
        mask = display_df['title'].str.contains(search_term, case=False, na=False)
        display_df = display_df[mask]
        st.info(f"Found {len(display_df)} papers matching '{search_term}'")
    
    # Display options
    col1, col2, col3 = st.columns(3)
    with col1:
        rows_to_show = st.selectbox("Rows to display:", [10, 25, 50, 100], index=1)
    with col2:
        sort_column = st.selectbox("Sort by:", ['publish_time', 'journal', 'abstract_word_count'])
    with col3:
        sort_order = st.selectbox("Order:", ['Descending', 'Ascending'])
    
    # Sort and display data
    ascending = sort_order == 'Ascending'
    display_df_sorted = display_df.sort_values(sort_column, ascending=ascending)
    
    # Select columns to display
    columns_to_show = ['title', 'journal', 'publish_time', 'abstract_word_count', 'source_x']
    display_data = display_df_sorted[columns_to_show].head(rows_to_show)
    
    # Format the display
    display_data = display_data.copy()
    display_data['publish_time'] = display_data['publish_time'].dt.strftime('%Y-%m-%d')
    display_data.columns = ['Title', 'Journal', 'Publication Date', 'Abstract Words', 'Source']
    
    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Title': st.column_config.TextColumn(width='large'),
            'Journal': st.column_config.TextColumn(width='medium'),
            'Publication Date': st.column_config.DateColumn(),
            'Abstract Words': st.column_config.NumberColumn(format='%d'),
            'Source': st.column_config.TextColumn(width='small')
        }
    )
    
    st.divider()
    
    # Download section
    st.header("💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV download
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📄 Download Filtered Data (CSV)",
            data=csv_data,
            file_name=f"cord19_filtered_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download the current filtered dataset as CSV"
        )
    
    with col2:
        # Summary statistics download
        summary_stats = {
            'Total Papers': len(filtered_df),
            'Unique Journals': filtered_df['journal'].nunique(),
            'Date Range': f"{filtered_df['publish_year'].min()}-{filtered_df['publish_year'].max()}",
            'Avg Abstract Length': f"{filtered_df['abstract_word_count'].mean():.1f} words",
            'Most Productive Year': yearly_counts.idxmax() if len(yearly_counts) > 0 else 'N/A',
            'Top Journal': filtered_df['journal'].value_counts().index[0] if len(filtered_df) > 0 else 'N/A'
        }
        
        summary_df = pd.DataFrame(list(summary_stats.items()), columns=['Metric', 'Value'])
        summary_csv = summary_df.to_csv(index=False)
        
        st.download_button(
            label="📊 Download Summary Statistics",
            data=summary_csv,
            file_name=f"cord19_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download summary statistics of the analysis"
        )
    
    # Footer
    st.divider()
    
    with st.expander("ℹ️ About This Dashboard"):
        st.markdown("""
        ### CORD-19 Analysis Dashboard
        
        This interactive dashboard provides comprehensive analysis of COVID-19 research papers from the CORD-19 dataset.
        
        **Features:**
        - 📊 Interactive visualizations of publication trends
        - 🔍 Search and filter functionality  
        - 📈 Time-series analysis of research output
        - 📚 Journal and source distribution analysis
        - 📝 Abstract length statistics
        - 💾 Data export capabilities
        
        **Data Source:** CORD-19 Dataset (COVID-19 Open Research Dataset)
        
        **Note:** This dashboard uses sample data for demonstration. To use with real CORD-19 data, 
        replace the `load_sample_data()` function with code to load the actual metadata.csv file.
        
        **Created with:** Streamlit, Plotly, Pandas
        """)
    
    # Sidebar info
    st.sidebar.divider()
    st.sidebar.markdown("### 📈 Dashboard Stats")
    st.sidebar.metric("Filtered Papers", f"{len(filtered_df):,}")
    st.sidebar.metric("Original Dataset", f"{len(df):,}")
    st.sidebar.metric("Filter Efficiency", f"{len(filtered_df)/len(df)*100:.1f}%")

if __name__ == "__main__":
    main()