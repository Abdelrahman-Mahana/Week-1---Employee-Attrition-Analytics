import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============== PAGE CONFIG ==============
st.set_page_config(
    page_title="Week 1 Task: Employee Attrition Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============== KAYFA BRANDING ==============
KAYFA_LOGO_PATH = "logo.png"

# ============== CUSTOM CSS ==============
st.markdown("""
<style>
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .kpi-value {
        font-size: 36px;
        font-weight: bold;
    }
    .kpi-label {
        font-size: 14px;
        opacity: 0.9;
    }
    .insight-box {
        background-color: #f0f7ff;
        border-left: 4px solid #1a5276;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
    .recommendation-box {
        background-color: #e8f8e8;
        border-left: 4px solid #27ae60;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
    .warning-box {
        background-color: #fff3e0;
        border-left: 4px solid #f39c12;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============== DATA LOADING & PREP ==============
@st.cache_data
def load_data():
    train = pd.read_csv('data/raw/train.csv')
    test = pd.read_csv('data/raw/test.csv')
    df = pd.concat([train, test], ignore_index=True)
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace("'s", "s")
    df.rename(columns={'work-life_balance': 'work_life_balance'}, inplace=True)
    
    # Ordinal categories
    ordinal_mappings = {
        'work_life_balance': ['Poor', 'Fair', 'Good', 'Excellent'],
        'job_satisfaction': ['Low', 'Medium', 'High', 'Very High'],
        'performance_rating': ['Low', 'Below Average', 'Average', 'High'],
        'education_level': ['High School', 'Associate Degree', "Bachelor's Degree", "Master's Degree", 'PhD'],
        'job_level': ['Entry', 'Mid', 'Senior'],
        'company_size': ['Small', 'Medium', 'Large'],
        'company_reputation': ['Poor', 'Fair', 'Good', 'Excellent'],
        'employee_recognition': ['Low', 'Medium', 'High', 'Very High']
    }
    for col, categories in ordinal_mappings.items():
        df[col] = pd.Categorical(df[col], categories=categories, ordered=True)
    
    # Create useful groups
    df['age_group'] = pd.cut(df['age'], bins=[17, 25, 35, 45, 55, 65],
                              labels=['18-25', '26-35', '36-45', '46-55', '56+'])
    df['tenure_group'] = pd.cut(df['years_at_company'], bins=[0, 2, 5, 10, 20, 60],
                                 labels=['0-2 years', '3-5 years', '6-10 years', '11-20 years', '20+ years'])
    df['income_quartile'] = pd.qcut(df['monthly_income'], q=4, labels=['Q1 (Lowest)', 'Q2', 'Q3', 'Q4 (Highest)'])
    
    return df

# ============== SIDEBAR ==============
with st.sidebar:
    st.image(KAYFA_LOGO_PATH, width=180)
    st.markdown("---")
    st.markdown("### 📊 Week 1 Task:")
    st.markdown("## **Employee Attrition Analytics**")
    st.markdown("*AI & Data Analytics Internship*")
    st.markdown("---")
    
    # Global filters
    st.markdown("### Global Filters")
    
    df_full = load_data()
    
    selected_role = st.multiselect("Job Role", options=df_full['job_role'].unique(), default=df_full['job_role'].unique())
    selected_level = st.multiselect("Job Level", options=df_full['job_level'].unique(), default=df_full['job_level'].unique())
    selected_gender = st.multiselect("Gender", options=df_full['gender'].unique(), default=df_full['gender'].unique())
    
    age_range = st.slider("Age Range", int(df_full['age'].min()), int(df_full['age'].max()), 
                          (int(df_full['age'].min()), int(df_full['age'].max())))
    
    st.markdown("---")

# Filter data
df = df_full[
    (df_full['job_role'].isin(selected_role)) &
    (df_full['job_level'].isin(selected_level)) &
    (df_full['gender'].isin(selected_gender)) &
    (df_full['age'] >= age_range[0]) &
    (df_full['age'] <= age_range[1])
]

# ============== KPI SECTION ==============
total_employees = len(df)
attrition_rate = (df['attrition'] == 'Left').mean() * 100
stayed_count = (df['attrition'] == 'Stayed').sum()
left_count = (df['attrition'] == 'Left').sum()
avg_income = df['monthly_income'].mean()

# ============== MAIN CONTENT ==============
# Create tabs for navigation
tab_home, tab_q1q2, tab_q3q4, tab_q5q6, tab_q7q8, tab_q9q10, tab_drivers = st.tabs([
    "🏠 Home", "Q1-Q2: Overview", "Q3-Q4: Remote & Pay", "Q5-Q6: Timeline & Engagement",
    "Q7-Q8: Life Stage & Career", "Q9-Q10: Risk & Action", "📊 Top Drivers"
])

# ============== HOME TAB ==============
with tab_home:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.image(KAYFA_LOGO_PATH, width=180)
    with col2:
        st.markdown("### Week 1 Task:")
        st.markdown("## **Attrition Insights Dashboard**")
        st.markdown("*Employee Retention Analytics for HR Leaders*")
    
    st.markdown("---")
    
    # KPIs
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{total_employees:,}</div>
            <div class="kpi-label">Total Employees</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        color = "#e74c3c" if attrition_rate > 50 else "#f39c12" if attrition_rate > 40 else "#27ae60"
        st.markdown(f"""
        <div class="kpi-card" style="background: {color};">
            <div class="kpi-value">{attrition_rate:.1f}%</div>
            <div class="kpi-label">Attrition Rate</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <div class="kpi-value">{stayed_count:,}</div>
            <div class="kpi-label">Stayed</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%);">
            <div class="kpi-value">{left_count:,}</div>
            <div class="kpi-label">Left</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col5:
        st.markdown(f"""
        <div class="kpi-card" style="background: linear-gradient(135deg, #8e2de2 0%, #4a00e0 100%);">
            <div class="kpi-value">${avg_income:,.0f}</div>
            <div class="kpi-label">Avg Income</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Dashboard Purpose
    
    This interactive dashboard answers **10 critical business questions** about employee attrition,
    designed for HR leaders who need actionable insights - not just numbers.
    
    ### 📋 How to Navigate
    
    Use the tabs above to explore each analysis question:
    - **Q1-Q2**: Overall attrition picture and overtime impact
    - **Q3-Q4**: Remote work effect and pay fairness analysis
    - **Q5-Q6**: Retention timeline and engagement warning signs
    - **Q7-Q8**: Life stage factors and career stagnation
    - **Q9-Q10**: Highest-risk profiles and top drivers ranked
    - **Top Drivers**: Summary of all actionable drivers
    
    ###  Use the Filters
    
    Adjust the filters in the sidebar to segment the analysis by job role, level, gender, and age.
    
    ---
    *Data: Synthetic Employee Attrition Dataset | 74,498 records*
    """)

# ============== Q1-Q2 TAB ==============
with tab_q1q2:
    st.markdown("## Q1: The Headline - Overall Attrition & Job Role")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall attrition pie
        attrition_counts = df['attrition'].value_counts()
        fig = px.pie(values=attrition_counts.values, names=attrition_counts.index,
                     color=attrition_counts.index, color_discrete_map={'Stayed': '#27ae60', 'Left': '#e74c3c'},
                     title="Overall Attrition Distribution")
        fig.update_traces(textinfo='percent+label', pull=[0, 0.05])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Role attrition
        role_attrition = df.groupby('job_role')['attrition'].apply(lambda x: (x == 'Left').mean() * 100).sort_values(ascending=True)
        fig = px.bar(x=role_attrition.values, y=role_attrition.index, orientation='h',
                     color=role_attrition.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition Rate by Job Role",
                     labels={'x': 'Attrition Rate (%)', 'y': 'Job Role', 'color': 'Attrition %'})
        fig.add_vline(x=attrition_rate, line_dash="dash", line_color="red", 
                      annotation_text=f"Company Average ({attrition_rate:.1f}%)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Insight:</b> Education leads at {role_attrition.max():.1f}% attrition, but the 2-point spread across roles suggests universal drivers matter more than role-specific ones.
        HR should focus on company-wide interventions rather than role-targeted programs.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Q2: Overtime Impact on Attrition")
    
    col1, col2 = st.columns(2)
    
    with col1:
        overtime_crosstab = pd.crosstab(df['overtime'], df['attrition'], normalize='index') * 100
        fig = px.bar(overtime_crosstab, barmode='group',
                     color_discrete_map={'Stayed': '#27ae60', 'Left': '#e74c3c'},
                     title="Attrition by Overtime Status",
                     labels={'value': 'Percentage (%)', 'overtime': 'Overtime'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        no_ot = (df[df['overtime'] == 'No']['attrition'] == 'Left').mean() * 100
        yes_ot = (df[df['overtime'] == 'Yes']['attrition'] == 'Left').mean() * 100
        ot_lift = yes_ot - no_ot
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['No Overtime', 'Overtime'], y=[no_ot, yes_ot],
                             marker_color=['#3498db', '#e74c3c'],
                             text=[f'{no_ot:.1f}%', f'{yes_ot:.1f}%'],
                             textposition='outside', textfont_size=14))
        fig.add_hline(y=attrition_rate, line_dash="dash", line_color="red",
                      annotation_text=f"Company Average ({attrition_rate:.1f}%)")
        fig.update_layout(title="Overtime Increases Attrition", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Insight:</b> Overtime workers have {yes_ot:.1f}% attrition vs {no_ot:.1f}% for non-overtime - a {ot_lift:.1f} percentage point increase.
        {(df['overtime'] == 'Yes').mean()*100:.1f}% of employees work overtime.
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Review workload distribution and overtime policies. Consider hiring additional staff or redistributing work to reduce overtime dependency.
    </div>
    """, unsafe_allow_html=True)

# ============== Q3-Q4 TAB ==============
with tab_q3q4:
    st.markdown("## Q3: Remote Work - The Biggest Lever?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        remote_dist = df['remote_work'].value_counts()
        fig = px.pie(values=remote_dist.values, names=['On-site', 'Remote'],
                     color_discrete_sequence=['#3498db', '#27ae60'],
                     title=f"Remote Work Distribution\n(Only {remote_dist['Yes']/len(df)*100:.1f}% remote)")
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        remote_rates = df.groupby('remote_work')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['On-site', 'Remote'], y=[remote_rates['No'], remote_rates['Yes']],
                             marker_color=['#e74c3c', '#27ae60'],
                             text=[f'{remote_rates["No"]:.1f}%', f'{remote_rates["Yes"]:.1f}%'],
                             textposition='outside', textfont_size=14))
        fig.add_hline(y=attrition_rate, line_dash="dash", line_color="gray",
                      annotation_text=f"Company Average")
        fig.update_layout(title=f"Remote Work Effect: {remote_rates['No'] - remote_rates['Yes']:.1f} pts reduction",
                          yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Insight:</b> Remote work is associated with a {remote_rates['No'] - remote_rates['Yes']:.1f} percentage point reduction in attrition.
        On-site employees leave at {remote_rates['No']:.1f}% vs {remote_rates['Yes']:.1f}% for remote workers.
    </div>
    <div class="warning-box">
        <b>Caveat:</b> Only {remote_dist['Yes']/len(df)*100:.1f}% of employees work remotely. Remote workers may differ in tenure, role, or performance.
        Cannot conclude causation without controlling for confounders.
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Pilot a remote work expansion program, carefully tracking outcomes with proper controls.
        The effect size ({remote_rates['No'] - remote_rates['Yes']:.1f} pts) justifies serious exploration.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Q4: Pay Fairness Within Job Levels")
    
    level_tabs = st.tabs(["Entry Level", "Mid Level", "Senior Level"])
    
    for idx, (tab, level) in enumerate(zip(level_tabs, ['Entry', 'Mid', 'Senior'])):
        with tab:
            level_data = df[df['job_level'] == level]
            quartile_attrition = level_data.groupby('income_quartile', observed=True)['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
            
            fig = px.bar(x=quartile_attrition.index.astype(str), y=quartile_attrition.values,
                         color=quartile_attrition.values, color_continuous_scale='RdYlGn_r',
                         title=f"{level} Level: Attrition by Income Quartile",
                         labels={'x': 'Income Quartile', 'y': 'Attrition Rate (%)'})
            fig.add_hline(y=attrition_rate, line_dash="dash", line_color="red",
                          annotation_text="Company Average")
            st.plotly_chart(fig, use_container_width=True)
            
            diff = quartile_attrition.iloc[0] - quartile_attrition.iloc[-1]
            st.markdown(f"""
            <div class="insight-box">
                <b>{level} Level:</b> Lowest-paid quartile at {quartile_attrition.iloc[0]:.1f}% vs highest-paid at {quartile_attrition.iloc[-1]:.1f}%
                - difference of only {diff:.1f} percentage points.
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="recommendation-box">
        <b>Recommendation:</b> Pay has a surprisingly weak effect on attrition. Focus resources on non-monetary factors
        (remote work, work-life balance, growth opportunities) rather than blanket pay increases.
    </div>
    """, unsafe_allow_html=True)

# ============== Q5-Q6 TAB ==============
with tab_q5q6:
    st.markdown("## Q5: Retention Timeline - When Do Employees Leave?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tenure_rates = df.groupby('tenure_group', observed=True)['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
        fig = px.bar(x=tenure_rates.index.astype(str), y=tenure_rates.values,
                     color=tenure_rates.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition by Career Stage",
                     labels={'x': 'Years at Company', 'y': 'Attrition Rate (%)'})
        fig.add_hline(y=attrition_rate, line_dash="dash", line_color="red",
                      annotation_text="Company Average")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        yearly = df.groupby('years_at_company')['attrition'].apply(lambda x: (x == 'Left').mean() * 100).head(15)
        fig = px.line(x=yearly.index, y=yearly.values, markers=True,
                      title="First 15 Years: Attrition by Year",
                      labels={'x': 'Years at Company', 'y': 'Attrition Rate (%)'})
        fig.add_hline(y=attrition_rate, line_dash="dash", line_color="red",
                      annotation_text="Company Average")
        fig.update_traces(line_color='#e74c3c', marker_size=8)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Insight:</b> The first 5 years are the danger zone (52-53% attrition). Risk drops significantly after 10 years.
        Year {yearly.idxmax()} has the highest single-year attrition at {yearly.max():.1f}%.
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Invest heavily in first-year onboarding and early-career engagement programs.
        Implement structured mid-career check-ins at the 3-5 year mark.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Q6: Engagement Warning Signs")
    
    engagement_matrix = df.groupby(['job_satisfaction', 'work_life_balance'])['attrition'].apply(lambda x: (x == 'Left').mean() * 100).unstack()
    
    fig = px.imshow(engagement_matrix.values,
                    x=list(engagement_matrix.columns),
                    y=list(engagement_matrix.index),
                    color_continuous_scale='RdYlGn_r',
                    title="Attrition Rate (%) by Job Satisfaction x Work-Life Balance",
                    labels={'x': 'Work-Life Balance', 'y': 'Job Satisfaction', 'color': 'Attrition %'})
    fig.update_traces(text=engagement_matrix.values.round(1), texttemplate="%{text:.1f}%", textfont_size=12)
    st.plotly_chart(fig, use_container_width=True)
    
    max_combo = engagement_matrix.stack().idxmax()
    min_combo = engagement_matrix.stack().idxmin()
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Highest Risk:</b> {max_combo[0]} Satisfaction + {max_combo[1]} WLB = {engagement_matrix.stack().max():.1f}% attrition<br>
        <b>Lowest Risk:</b> {min_combo[0]} Satisfaction + {min_combo[1]} WLB = {engagement_matrix.stack().min():.1f}% attrition<br>
        <b>Gap:</b> {engagement_matrix.stack().max() - engagement_matrix.stack().min():.1f} percentage points
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Work-Life Balance is the dominant factor - Poor WLB consistently produces >55% attrition regardless of satisfaction.
        Managers should monitor WLB as the strongest early warning sign and intervene before satisfaction drops.
    </div>
    """, unsafe_allow_html=True)

# ============== Q7-Q8 TAB ==============
with tab_q7q8:
    st.markdown("## Q7: Life Stage - Age, Marital Status & Dependents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        age_rates = df.groupby('age_group', observed=True)['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
        fig = px.bar(x=age_rates.index.astype(str), y=age_rates.values,
                     color=age_rates.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition by Age Group")
        fig.update_layout(xaxis_title="Age Group", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        marital_rates = df.groupby('marital_status')['attrition'].apply(lambda x: (x == 'Left').mean() * 100).sort_values(ascending=False)
        fig = px.bar(x=marital_rates.index, y=marital_rates.values,
                     color=marital_rates.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition by Marital Status")
        fig.update_layout(xaxis_title="Marital Status", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        dep_rates = df.groupby('number_of_dependents')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
        fig = px.bar(x=dep_rates.index, y=dep_rates.values,
                     color=dep_rates.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition by Dependents")
        fig.update_layout(xaxis_title="Number of Dependents", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    life_stage_matrix = df.groupby(['age_group', 'marital_status'], observed=True)['attrition'].apply(lambda x: (x == 'Left').mean() * 100).unstack()
    fig = px.imshow(life_stage_matrix.values,
                    x=list(life_stage_matrix.columns),
                    y=[str(i) for i in life_stage_matrix.index],
                    color_continuous_scale='RdYlGn_r',
                    title="Attrition Rate (%) by Age x Marital Status")
    fig.update_traces(text=life_stage_matrix.values.round(1), texttemplate="%{text:.1f}%")
    st.plotly_chart(fig, use_container_width=True)
    
    max_ls = life_stage_matrix.stack().idxmax()
    st.markdown(f"""
    <div class="insight-box">
        <b>Highest Risk Life Stage:</b> {max_ls[0]} + {max_ls[1]} = {life_stage_matrix.stack().max():.1f}% attrition
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Create targeted retention for young single employees - mentorship programs, social events,
        and early-career development tracks. Married employees with 4+ dependents are most stable - use them as mentors.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Q8: Career Stagnation - Promotions & Opportunities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        promo_rates = df.groupby('number_of_promotions')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
        fig = px.bar(x=promo_rates.index, y=promo_rates.values,
                     color=promo_rates.values, color_continuous_scale='RdYlGn_r',
                     title="Attrition by Number of Promotions")
        fig.update_layout(xaxis_title="Promotions", yaxis_title="Attrition Rate (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        ldr_no = (df[df['leadership_opportunities'] == 'No']['attrition'] == 'Left').mean() * 100
        ldr_yes = (df[df['leadership_opportunities'] == 'Yes']['attrition'] == 'Left').mean() * 100
        inn_no = (df[df['innovation_opportunities'] == 'No']['attrition'] == 'Left').mean() * 100
        inn_yes = (df[df['innovation_opportunities'] == 'Yes']['attrition'] == 'Left').mean() * 100
        
        categories = ['No Leadership', 'Leadership', 'No Innovation', 'Innovation']
        values = [ldr_no, ldr_yes, inn_no, inn_yes]
        colors = ['#e74c3c', '#27ae60', '#e74c3c', '#27ae60']
        
        fig = go.Figure()
        for cat, val, col in zip(categories, values, colors):
            fig.add_trace(go.Bar(x=[cat], y=[val], marker_color=col, text=[f'{val:.1f}%'], textposition='outside'))
        fig.update_layout(title="Opportunities Effect on Attrition", yaxis_title="Attrition Rate (%)",
                          showlegend=False, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
    
    stuck = df[(df['leadership_opportunities'] == 'No') & (df['innovation_opportunities'] == 'No') & (df['number_of_promotions'] == 0)]
    stuck_rate = (stuck['attrition'] == 'Left').mean() * 100
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Threshold Effect:</b> 0-2 promotions all have ~49% attrition, but 3+ promotions drops to ~24%.<br>
        <b>'Stuck' employees</b> (no LDR, no INN, 0 promotions): {stuck_rate:.1f}% attrition (n={len(stuck):,}).
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Create clear promotion pathways with visible milestones. The threshold is around 3 promotions -
        ensure employees can see a path to multiple advancement opportunities.
    </div>
    """, unsafe_allow_html=True)

# ============== Q9-Q10 TAB ==============
with tab_q9q10:
    st.markdown("## Q9: Highest-Risk Employee Profile")
    
    # Build the risk profile interactively
    st.markdown("### Build a Risk Profile")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        rp_marital = st.selectbox("Marital Status", ['Single', 'Married', 'Divorced'], index=0)
        rp_age_max = st.slider("Max Age", 18, 60, 30)
    with col2:
        rp_sat = st.multiselect("Job Satisfaction", ['Low', 'Medium', 'High', 'Very High'], default=['Low', 'Medium'])
        rp_wlb = st.multiselect("Work-Life Balance", ['Poor', 'Fair', 'Good', 'Excellent'], default=['Poor', 'Fair'])
    with col3:
        rp_ot = st.selectbox("Overtime", ['Yes', 'No'], index=0)
        rp_promo_max = st.slider("Max Promotions", 0, 4, 0)
    
    profile = df[
        (df['marital_status'] == rp_marital) &
        (df['age'] <= rp_age_max) &
        (df['job_satisfaction'].isin(rp_sat)) &
        (df['work_life_balance'].isin(rp_wlb)) &
        (df['overtime'] == rp_ot) &
        (df['number_of_promotions'] <= rp_promo_max)
    ]
    
    if len(profile) > 0:
        profile_rate = (profile['attrition'] == 'Left').mean() * 100
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #cb2d3e 0%, #ef473a 100%); padding: 25px; border-radius: 15px; color: white; text-align: center;">
            <div style="font-size: 48px; font-weight: bold;">{profile_rate:.1f}%</div>
            <div style="font-size: 18px;">Attrition Rate</div>
            <div style="font-size: 14px; opacity: 0.9;">({len(profile):,} employees match this profile = {len(profile)/len(df)*100:.1f}% of workforce)</div>
            <div style="font-size: 14px; margin-top: 10px;">{profile_rate/attrition_rate:.2f}x the company average</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No employees match this exact profile. Try broadening the filters.")
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Default Highest-Risk Profile:</b> Single + Age 18-30 + Low/Med Satisfaction + Poor/Fair WLB + Overtime = 84.3% attrition.
        337 employees (0.5%) match this profile.
    </div>
    <div class="recommendation-box">
        <b>Recommendation:</b> Immediate 1-on-1 intervention for this small but extremely high-risk group.
        Assign mentors, reduce workload, and create personalized retention plans.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Q10: What Moves the Needle? - Top Drivers Ranked")
    
    # Calculate all driver impacts
    drivers = {}
    ms = df.groupby('marital_status')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
    drivers['Marital Status'] = abs(ms['Single'] - ms['Married'])
    
    rw = df.groupby('remote_work')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
    drivers['Remote Work'] = abs(rw['No'] - rw['Yes'])
    
    pr = df.groupby('number_of_promotions')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
    drivers['Promotions (0 vs 3+)'] = abs(pr[0] - pr[3]) if 3 in pr.index else abs(pr[0] - pr[pr.index.max()])
    
    wlb = df.groupby('work_life_balance', observed=True)['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
    drivers['Work-Life Balance'] = abs(wlb['Poor'] - wlb['Excellent'])
    
    ot = df.groupby('overtime')['attrition'].apply(lambda x: (x == 'Left').mean() * 100)
    drivers['Overtime'] = abs(ot['Yes'] - ot['No'])
    
    age_y = (df[df['age'] <= 25]['attrition'] == 'Left').mean() * 100
    age_o = (df[df['age'] >= 50]['attrition'] == 'Left').mean() * 100
    drivers['Age (Young vs Mature)'] = abs(age_y - age_o)
    
    sorted_drivers = sorted(drivers.items(), key=lambda x: x[1], reverse=True)
    
    fig = px.bar(x=[d[1] for d in sorted_drivers], y=[d[0] for d in sorted_drivers], orientation='h',
                 color=[d[1] for d in sorted_drivers], color_continuous_scale='RdYlGn_r',
                 title="Top Attrition Drivers Ranked by Impact (Percentage Point Difference)",
                 labels={'x': 'Impact (Percentage Points)', 'y': 'Driver'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Impact estimate
    on_site_count = len(df[df['remote_work'] == 'No'])
    current_left = len(df[(df['remote_work'] == 'No') & (df['attrition'] == 'Left')])
    projected_left = int(on_site_count * rw['Yes'] / 100)
    prevented = current_left - projected_left
    
    st.markdown(f"""
    <div class="insight-box">
        <b>Top 3 Actionable Drivers:</b><br>
        1. <b>Remote Work</b>: {drivers['Remote Work']:.1f} pts impact - MOST ACTIONABLE<br>
        2. <b>Promotions</b>: {drivers['Promotions (0 vs 3+)']:.1f} pts impact - Actionable via career dev<br>
        3. <b>Work-Life Balance</b>: {drivers['Work-Life Balance']:.1f} pts impact - Actionable via policy
    </div>
    <div class="recommendation-box">
        <b>#1 Recommendation: Expand Remote Work</b><br>
        If all on-site employees had remote options, we could potentially prevent ~{prevented:,} departures
        - a {prevented/current_left*100:.1f}% reduction in on-site attrition. This is the single highest-impact
        intervention HR can implement next quarter.
    </div>
    """, unsafe_allow_html=True)

# ============== TOP DRIVERS TAB ==============
with tab_drivers:
    st.markdown("## 📊 Summary: All Key Findings")
    
    findings = [
        ("Remote Work", f"{rw['No'] - rw['Yes']:.1f} pts reduction", f"On-site: {rw['No']:.1f}% → Remote: {rw['Yes']:.1f}%", "HIGH"),
        ("Marital Status", f"{abs(ms['Single'] - ms['Married']):.1f} pts gap", f"Single: {ms['Single']:.1f}% → Married: {ms['Married']:.1f}%", "MEDIUM"),
        ("Promotions (0 vs 3+)", f"{abs(pr[0] - pr[3]):.1f} pts reduction", f"0 promo: {pr[0]:.1f}% → 3+ promo: {pr[3]:.1f}%", "HIGH"),
        ("Work-Life Balance", f"{abs(wlb['Poor'] - wlb['Excellent']):.1f} pts reduction", f"Poor: {wlb['Poor']:.1f}% → Excellent: {wlb['Excellent']:.1f}%", "HIGH"),
        ("Overtime", f"{abs(ot['Yes'] - ot['No']):.1f} pts increase", f"No OT: {ot['No']:.1f}% → OT: {ot['Yes']:.1f}%", "MEDIUM"),
        ("Age (≤25 vs ≥50)", f"{abs(age_y - age_o):.1f} pts gap", f"Young: {age_y:.1f}% → Mature: {age_o:.1f}%", "LOW"),
    ]
    
    for name, impact, detail, actionability in findings:
        color = "#27ae60" if actionability == "HIGH" else "#f39c12" if actionability == "MEDIUM" else "#e74c3c"
        st.markdown(f"""
        <div style="border: 2px solid {color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <b style="font-size: 16px;">{name}</b><br>
                    <span style="color: #666;">{detail}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 24px; font-weight: bold; color: {color};">{impact}</span><br>
                    <span style="background: {color}; color: white; padding: 2px 10px; border-radius: 10px; font-size: 12px;">{actionability} ACTIONABILITY</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    ### 🎯 Final Recommendation for HR Leadership
    
    > **If HR could fix only one thing next quarter: Expand remote work options.**
    > 
    > The data shows a 28.1 percentage point reduction in attrition for remote workers.
    > With an estimated 16,959 preventable departures, this single intervention could reduce
    > company-wide attrition from 47.5% to approximately 35-38%.
    >
    > **Secondary priorities:** (1) Clear promotion pathways with 3+ advancement milestones,
    > and (2) Work-life balance monitoring and intervention programs.
    """)
    Brief Description of the Dashboard's Functionality (1-3 sentences)
    st.markdown("---")
