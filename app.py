# app.py
import streamlit as st
import datetime
import base64
import io
import json
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="WhatsApp Clone",
    page_icon="💬",
    layout="wide"
)

# Initialize shared data in session state
if 'shared_data' not in st.session_state:
    st.session_state.shared_data = {
        'users': {},
        'messages': [],
        'contacts': {}
    }

def initialize_user():
    """Initialize user-specific session state"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.session_state.uploaded_files = {}

def get_shared_data():
    """Get the shared data that works across all sessions"""
    return st.session_state.shared_data

def save_shared_data():
    """Save to shared data (in production, this would be a database)"""
    # In Streamlit Cloud, this persists during the app's lifetime
    pass

def login_section():
    """User login/registration"""
    st.sidebar.header("🔐 Login / Register")
    
    shared_data = get_shared_data()
    
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username").strip()
        if st.button("Login", key="login_btn", use_container_width=True):
            if username:
                if username in shared_data['users']:
                    st.session_state.current_user = username
                    # Initialize user contacts if not exists
                    if username not in shared_data['contacts']:
                        shared_data['contacts'][username] = []
                    st.rerun()
                else:
                    st.error("User not found! Please register first.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username").strip()
        if st.button("Register", key="register_btn", use_container_width=True):
            if new_username:
                if new_username not in shared_data['users']:
                    # Register new user
                    shared_data['users'][new_username] = {
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    # Initialize contacts list for new user
                    shared_data['contacts'][new_username] = []
                    
                    st.session_state.current_user = new_username
                    st.success(f"Welcome {new_username}! You can now add contacts.")
                    save_shared_data()
                    st.rerun()
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please enter a username")

def contacts_section():
    """Manage contacts"""
    st.sidebar.header("👥 Contacts")
    
    shared_data = get_shared_data()
    current_user = st.session_state.current_user
    
    # Add contact section
    st.sidebar.subheader("Add Contact")
    new_contact = st.sidebar.text_input("Enter username:").strip()
    
    if st.sidebar.button("Add Contact", use_container_width=True):
        if new_contact:
            if new_contact == current_user:
                st.sidebar.error("You cannot add yourself!")
            elif new_contact in shared_data['users']:
                # Add to current user's contacts
                if new_contact not in shared_data['contacts'][current_user]:
                    shared_data['contacts'][current_user].append(new_contact)
                    st.sidebar.success(f"✅ Added {new_contact} to contacts!")
                    save_shared_data()
                    st.rerun()
                else:
                    st.sidebar.error("❌ Already in contacts!")
            else:
                st.sidebar.error("❌ User not found! Tell them to register first.")
    
    st.sidebar.markdown("---")
    
    # Display contacts
    st.sidebar.subheader("Your Contacts")
    user_contacts = shared_data['contacts'].get(current_user, [])
    
    if not user_contacts:
        st.sidebar.info("No contacts yet. Add someone to chat!")
    else:
        for contact in user_contacts:
            if st.sidebar.button(
                f"💬 {contact}", 
                key=f"chat_{contact}",
                use_container_width=True
            ):
                st.session_state.current_contact = contact
                st.rerun()

def display_message(message):
    """Display a chat message"""
    is_current_user = message["sender"] == st.session_state.current_user
    
    if message["type"] == "text":
        st.markdown(f"""
        <div style='
            background-color: {"#dcf8c6" if is_current_user else "white"};
            padding: 12px;
            border-radius: 8px;
            margin: 8px {"20% 0 0 0" if is_current_user else "0 20% 0 0"};
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        '>
            <div style='font-weight: bold; color: #128c7e; margin-bottom: 4px;'>
                {"You" if is_current_user else message["sender"]}
            </div>
            <div style='margin-bottom: 4px;'>{message["content"]}</div>
            <div style='font-size: 0.8em; color: #667781; text-align: right;'>
                {message["time"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif message["type"] == "image":
        st.markdown(f"""
        <div style='
            background-color: {"#dcf8c6" if is_current_user else "white"};
            padding: 12px;
            border-radius: 8px;
            margin: 8px {"20% 0 0 0" if is_current_user else "0 20% 0 0"};
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        '>
            <div style='font-weight: bold; color: #128c7e; margin-bottom: 4px;'>
                {"You" if is_current_user else message["sender"]}
            </div>
            <img src="{message['content']}" style="max-width: 300px; border-radius: 6px; margin-bottom: 4px;">
            <div style='font-size: 0.8em; color: #667781; text-align: right;'>
                {message["time"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

def chat_section():
    """Main chat interface"""
    if not st.session_state.current_contact:
        st.info("👈 Select a contact from the sidebar to start chatting!")
        return
    
    shared_data = get_shared_data()
    
    st.header(f"💬 Chat with {st.session_state.current_contact}")
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        # Get messages between current user and contact
        chat_messages = [
            msg for msg in shared_data['messages']
            if (msg["sender"] == st.session_state.current_user and msg["receiver"] == st.session_state.current_contact) or
               (msg["sender"] == st.session_state.current_contact and msg["receiver"] == st.session_state.current_user)
        ]
        
        # Sort by timestamp
        chat_messages.sort(key=lambda x: x["timestamp"])
        
        for message in chat_messages:
            display_message(message)
    
    st.markdown("---")
    
    # Text input
    text_input = st.chat_input(f"Message {st.session_state.current_contact}...")
    if text_input:
        new_message = {
            "type": "text",
            "sender": st.session_state.current_user,
            "receiver": st.session_state.current_contact,
            "content": text_input,
            "time": datetime.datetime.now().strftime("%H:%M"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        shared_data['messages'].append(new_message)
        save_shared_data()
        st.rerun()
    
    # Image upload
    st.subheader("📷 Share Image")
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        key=f"upload_{st.session_state.current_contact}"
    )
    
    if uploaded_file is not None:
        # Check if this is a new upload
        file_key = f"{st.session_state.current_user}_{st.session_state.current_contact}_{uploaded_file.name}"
        if file_key not in st.session_state.uploaded_files:
            # Process image
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data = f"data:image/png;base64,{img_str}"
            
            # Add image message
            new_message = {
                "type": "image",
                "sender": st.session_state.current_user,
                "receiver": st.session_state.current_contact,
                "content": image_data,
                "time": datetime.datetime.now().strftime("%H:%M"),
                "timestamp": datetime.datetime.now().isoformat()
            }
            shared_data['messages'].append(new_message)
            st.session_state.uploaded_files[file_key] = True
            save_shared_data()
            st.rerun()

def main():
    st.title("💬 WhatsApp Clone - Fixed Version")
    
    # Initialize user session
    initialize_user()
    
    # Show login if not logged in
    if not st.session_state.current_user:
        login_section()
        st.info("🔐 Please login or register to start chatting")
        return
    
    # Main app interface
    shared_data = get_shared_data()
    
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.rerun()
    
    contacts_section()
    chat_section()
    
    # Info panel
    with st.sidebar:
        st.markdown("---")
        st.header("ℹ️ App Info")
        st.write(f"**Total Users:** {len(shared_data['users'])}")
        st.write(f"**Your Contacts:** {len(shared_data['contacts'].get(st.session_state.current_user, []))}")
        st.write(f"**Total Messages:** {len(shared_data['messages'])}")
        
        # Show all registered users (for debugging)
        st.markdown("---")
        st.subheader("👤 All Registered Users")
        if shared_data['users']:
            for user in sorted(shared_data['users'].keys()):
                status = "✅ You" if user == st.session_state.current_user else "👤"
                st.write(f"{status} {user}")
        else:
            st.write("No users registered yet")

if __name__ == "__main__":
    main()
