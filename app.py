import streamlit as st
import pickle
import pandas as pd

# ------------------------- 
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    
    .stTitle {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem !important;
        margin-bottom: 2rem;
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .metric-card {
        background:#0D1B2A;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    
    .match-header {
        background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .team-vs {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Load model
# -------------------------
@st.cache_resource
def load_model():
    try:
        return pickle.load(open('pipe.pkl','rb'))
    except FileNotFoundError:
        st.error("Model file 'pipe.pkl' not found. Please ensure the model is in the same directory.")
        st.stop()

pipe = load_model()

# -------------------------
# Teams & Cities
# -------------------------
teams = [
    'Sunrisers Hyderabad', 'Mumbai Indians', 'Royal Challengers Bangalore',
    'Kolkata Knight Riders', 'Kings XI Punjab', 'Chennai Super Kings',
    'Rajasthan Royals', 'Delhi Capitals'
]

cities = [
    'Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
    'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
    'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
    'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
    'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
    'Sharjah', 'Mohali', 'Bengaluru'
]

# Team colors for visualization
team_colors = {
    'Sunrisers Hyderabad': '#ff822a',
    'Mumbai Indians': '#004c91',
    'Royal Challengers Bangalore': '#d41948',
    'Kolkata Knight Riders': '#3a225d',
    'Kings XI Punjab': '#dd1f2d',
    'Chennai Super Kings': '#fdb913',
    'Rajasthan Royals': '#254aa5',
    'Delhi Capitals': '#17479e'
}

# -------------------------
# App Header
# -------------------------
st.title('🏏 IPL Win Predictor')
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-bottom: 2rem;'>
    Predict live match win probabilities using advanced machine learning
</div>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("""
    <div class='sidebar-header'>
        <h2>🎯 Match Setup</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Team Selection
    st.subheader("⚔️ Teams")
    batting_team = st.selectbox('🏏 Batting Team', sorted(teams), key='batting')
    bowling_team = st.selectbox('🥎 Bowling Team', sorted(teams), key='bowling')
    
    # Validation
    if batting_team == bowling_team:
        st.error("⚠️ Please select different teams!")
    
    st.subheader("🏟️ Match Details")
    selected_city = st.selectbox('📍 Host City', sorted(cities))
    target = st.number_input('🎯 Target Score', min_value=1, value=180, step=1)
    
    st.subheader("📊 Current Match State")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        score = st.number_input('💯 Current Score', min_value=0, value=120, step=1)
        wickets = st.number_input('❌ Wickets Lost', min_value=0, max_value=10, value=3, step=1)
    with col_s2:
        overs = st.number_input('⏱️ Overs Completed', min_value=0.0, max_value=20.0, value=12.0, step=0.1)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)

# -------------------------
# Main Content Area
# -------------------------
if batting_team != bowling_team:
    # Match Header
    st.markdown(f"""
    <div class='match-header'>
        <div class='team-vs'>{batting_team} vs {bowling_team}</div>
        <div style='margin-top: 0.5rem; color: #7f8c8d;'>📍 {selected_city}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    runs_left = target - score
    balls_left = 120 - int(overs * 6)
    wickets_left = 10 - wickets
    crr = score / overs if overs > 0 else 0
    rrr = (runs_left * 6 / balls_left) if balls_left > 0 else 0
    
    with col1:
        st.metric("🎯 Target", f"{target}", help="Total runs to chase")
    with col2:
        st.metric("💯 Current Score", f"{score}/{wickets}", help="Current score and wickets lost")
    with col3:
        st.metric("⏱️ Overs", f"{overs}/20", help="Overs completed")
    with col4:
        st.metric("🏃‍♂️ Runs Needed", f"{runs_left}", help="Runs required to win")
    
    # Prediction Section
    if st.button('🔮 Predict Win Probability', type="primary", use_container_width=True):
        
        # Handle end conditions
        if runs_left == 0 and balls_left == 0:
            st.warning("🤝 Match Tied! Both teams have the same score.")
        elif runs_left > 0 and balls_left == 0:
            st.error(f"❌ {bowling_team} wins! Batting side fell short.")
        elif runs_left <= 0:
            st.success(f"🎉 {batting_team} has already won!")
        else:
            # Prepare input
            input_df = pd.DataFrame({
                'batting_team': [batting_team],
                'bowling_team': [bowling_team],
                'city': [selected_city],
                'runs_left': [runs_left],
                'balls_left': [balls_left],
                'wickets': [wickets_left],
                'total_runs_x': [target],
                'crr': [crr],
                'rrr': [rrr]
            })
            
            # Predict
            with st.spinner('🤖 Analyzing match situation...'):
                result = pipe.predict_proba(input_df)
                loss = result[0][0]
                win = result[0][1]
            
            # Show win/loss probabilities
            st.markdown("### 🔮 Win Probability")
            colp1, colp2 = st.columns(2)
            with colp1:
                st.metric(f"🏏 {batting_team} Chance", f"{win*100:.2f} %")
            with colp2:
                st.metric(f"🥎 {bowling_team} Chance", f"{loss*100:.2f} %")
            
            # Detailed Match Analysis
            st.markdown("---")
            st.subheader("📈 Match Analysis")
            
            col_analysis1, col_analysis2 = st.columns(2)
            
            with col_analysis1:
                st.markdown(f"""
                <div class='metric-card'>
                    <h4>🎯 Required Run Rate</h4>
                    <h2 style='color: {'red' if rrr > 12 else 'orange' if rrr > 8 else 'green'};'>{rrr:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h4>📊 Current Run Rate</h4>
                    <h2 style='color: #1f77b4;'>{crr:.2f}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col_analysis2:
                overs_left = balls_left // 6
                balls_extra = balls_left % 6
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h4>⏰ Overs Remaining</h4>
                    <h2>{overs_left}.{balls_extra}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='metric-card'>
                    <h4>🏏 Wickets in Hand</h4>
                    <h2 style='color: {'red' if wickets_left <= 3 else 'orange' if wickets_left <= 5 else 'green'};'>{wickets_left}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Match Situation Summary
            st.markdown("---")
            if win*100 > 75:
                st.success(f"🔥 **Excellent position for {batting_team}!** They are heavy favorites to win this match.")
            elif win*100 > 60:
                st.info(f"👍 **{batting_team} are in a strong position** with a good chance of winning.")
            elif win*100 > 40:
                st.warning(f"⚖️ **Match is evenly poised!** Both teams have a realistic chance of winning.")
            elif win*100 > 25:
                st.warning(f"📉 **{bowling_team} have the upper hand** but {batting_team} can still pull this off.")
            else:
                st.error(f"🚨 **Very tough situation for {batting_team}!** They need something special to win from here.")
            
            # Fun Facts
            with st.expander("🎲 Match Insights"):
                st.write(f"• **Pressure Situation**: {'High' if rrr > 10 else 'Medium' if rrr > 7 else 'Low'}")
                st.write(f"• **Batting Powerplay**: {'Active' if overs < 6 else 'Completed'}")
                st.write(f"• **Death Overs**: {'Yes' if overs >= 15 else 'No'}")
                st.write(f"• **Required Strike Rate**: {rrr * 100/6:.1f}")
                
                if crr > rrr:
                    st.write("✅ Batting team is ahead of the required rate!")
                else:
                    st.write("⚠️ Batting team needs to accelerate!")

else:
    st.warning("⚠️ Please select different teams to proceed with prediction.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
   ⚡ Manan’s IPL Win Predictor | Where Cricket Meets ML 🤖
</div>
""", unsafe_allow_html=True)