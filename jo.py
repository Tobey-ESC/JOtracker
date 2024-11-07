import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)

# Custom CSS to make it prettier
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📝 JoTRACII")
st.markdown("applications and progress")

# Initialize session state for editing
if 'editing' not in st.session_state:
    st.session_state.editing = False
    st.session_state.edit_index = None

# Function to load data
def load_data():
    if os.path.exists('job_applications.csv'):
        df = pd.read_csv('job_applications.csv')
        # Ensure 'Status History' column exists
        if 'Status History' not in df.columns:
            df['Status History'] = ""  # Initialize with empty strings if not present
        return df
    return pd.DataFrame(columns=['Date Applied', 'Company', 'Job Title', 'Description', 
                                 'Status', 'Status History', 'Next Steps', 'Notes', 'Last Updated'])

# Function to save data
def save_data(df):
    df.to_csv('job_applications.csv', index=False)

# Load existing data
df = load_data()

# Sidebar for adding/editing entries
with st.sidebar:
    st.header("Add/Edit Application")
    
    # Form for new entries
    with st.form("application_form", clear_on_submit=True):
        if st.session_state.editing and st.session_state.edit_index is not None and st.session_state.edit_index < len(df):
            # Populate form with existing data for editing
            row_to_edit = df.iloc[st.session_state.edit_index]
            company = st.text_input("Company Name", value=row_to_edit['Company'])
            job_title = st.text_input("Job Title", value=row_to_edit['Job Title'])
            description = st.text_area("Job Description", value=row_to_edit['Description'])
            status = st.selectbox("Application Status", 
                                ["Applied", "Assessment", "Phone Screen", 
                                 "Interview", "Offer", "Rejected", "Withdrawn"], 
                                index=["Applied", "Assessment", "Phone Screen", 
                                       "Interview", "Offer", "Rejected", "Withdrawn"].index(row_to_edit['Status']))
            next_steps = st.text_input("Next Steps", value=row_to_edit['Next Steps'])
            notes = st.text_area("Notes", value=row_to_edit['Notes'])
            submit_label = "Update Application"
        else:
            # New application form
            company = st.text_input("Company Name")
            job_title = st.text_input("Job Title")
            description = st.text_area("Job Description")
            status = st.selectbox("Application Status", 
                                ["Applied", "Assessment", "Phone Screen", 
                                 "Interview", "Offer", "Rejected", "Withdrawn"])
            next_steps = st.text_input("Next Steps")
            notes = st.text_area("Notes")
            submit_label = "Add Application"
        
        submitted = st.form_submit_button(submit_label)
        
        if submitted and company and job_title:
            new_row = {
                'Date Applied': datetime.now().strftime("%Y-%m-%d"),
                'Company': company,
                'Job Title': job_title,
                'Description': description,
                'Status': status,
                'Status History': status,  # Initialize status history with the current status
                'Next Steps': next_steps,
                'Notes': notes,
                'Last Updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            if st.session_state.editing and st.session_state.edit_index is not None:
                # Update existing row
                if len(df) > 0:  # Ensure DataFrame is not empty
                    # Update status history
                    current_status_history = df.at[st.session_state.edit_index, 'Status History']
                    new_status_history = f"{current_status_history} - {status}" if current_status_history else status
                    df.at[st.session_state.edit_index, 'Status'] = status
                    df.at[st.session_state.edit_index, 'Status History'] = new_status_history
                st.session_state.editing = False  # Reset editing state
            else:
                # Add new row
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)  # Save the updated DataFrame to CSV
            df = load_data()  # Reload data to reflect changes
            st.success("Application updated successfully!" if st.session_state.editing else "Application added successfully!")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Status metrics
    if not df.empty:
        total_applications = len(df)
        active_applications = len(df[df['Status'].isin(['Applied', 'Assessment', 'Phone Screen', 'Interview'])])
        offers = len(df[df['Status'] == 'Offer'])
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Total Applications", total_applications)
        metric_col2.metric("Active Applications", active_applications)
        metric_col3.metric("Offers", offers)

with col2:
    # Filter options
    status_filter = st.multiselect("Filter by Status", df['Status'].unique().tolist())
    
# Display applications
if not df.empty:
    filtered_df = df if not status_filter else df[df['Status'].isin(status_filter)]
    
    for idx, row in filtered_df.iterrows():
        with st.expander(f"{row['Company']} - {row['Job Title']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Applied:** {row['Date Applied']}")
                st.write(f"**Status:** {row['Status']}")
                st.write(f"**Status History:** {row['Status History']}")  # Display status history
                if row['Description']:
                    st.write("**Description:**")
                    st.write(row['Description'])
                if row['Next Steps']:
                    st.write("**Next Steps:**")
                    st.write(row['Next Steps'])
                if row['Notes']:
                    st.write("**Notes:**")
                    st.write(row['Notes'])
                
            with col2:
                if st.button("Delete", key=f"delete_{idx}"):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()
                    
                if st.button("Edit", key=f"edit_{idx}"):
                    st.session_state.editing = True
                    st.session_state.edit_index = idx
                    st.rerun()

else:
    st.info("No applications yet. Add your first application using the form in the sidebar!")
