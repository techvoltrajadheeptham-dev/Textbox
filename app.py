# app.py
import streamlit as st
import datetime
import json
import os
from datetime import timezone

# Page configuration with better theme
st.set_page_config(
    page_title="WhatsApp Clone",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database file path
DB_FILE = "chat_database.json"

# Custom CSS for better UI colors with bold black text
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #128C7E 0%, #075E54 100%);
        color: white;
    }
    .stButton button {
        background-color: #25D366;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #128C7E;
        color: white;
    }
    .chat-header {
        background-color: #075E54;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #dcf8c6;
        padding: 12px;
        border-radius: 10px;
        margin: 10px 0 10px 20%;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border-bottom-right-radius: 5px;
    }
    .contact-message {
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        margin: 10px 20% 10px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        border-bottom-left-radius: 5px;
    }
    .message-sender {
        font-weight: bold;
        color: #128C7E;
        margin-bottom: 5px;
        font-size: 14px;
    }
    .message-text {
        font-weight: bold;
        color: #000000;
        font-size: 15px;
        line-height: 1.4;
    }
    .message-time {
        font-size: 0.7rem;
        color: #667781;
        text-align: right;
        margin-top: 5px;
    }
    .info-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-list {
        font-weight: bold;
        color: #000000;
    }
    .app-info-text {
        font-weight: bold;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

def get_current_time():
    """Get current time in proper format"""
    now = datetime.datetime.now()
    return now.strftime("%I:%M %p")

def get_current_date():
    """Get current date with time"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_current_timestamp():
    """Get timestamp for sorting"""
    return datetime.datetime.now().isoformat()

def load_database():
    """Load the shared database from file"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading database: {e}")
    
    # Return empty database structure
    return {
        "users": {},
        "messages": [],
        "contacts": {}
    }

def save_database(data):
    """Save the shared database to file"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Error saving database: {e}")
        return False

def initialize_session():
    """Initialize user session"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
        st.session_state.current_contact = None

def login_section():
    """User login/registration"""
    st.sidebar.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.sidebar.header("🔐 Login / Register")
    
    # Load current database
    db = load_database()
    
    tab1, tab2 = st.sidebar.tabs(["🚪 Login", "📝 Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username").strip()
        if st.button("Login", key="login_btn", use_container_width=True):
            if username:
                if username in db['users']:
                    st.session_state.current_user = username
                    # Initialize user contacts if not exists
                    if username not in db['contacts']:
                        db['contacts'][username] = []
                        save_database(db)
                    st.rerun()
                else:
                    st.error("User not found! Please register first.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username").strip()
        if st.button("Register", key="register_btn", use_container_width=True):
            if new_username:
                if new_username not in db['users']:
                    # Register new user
                    db['users'][new_username] = {
                        "created_at": get_current_date(),
                        "last_login": get_current_date()
                    }
                    # Initialize contacts list for new user
                    db['contacts'][new_username] = []
                    
                    # Save to database
                    if save_database(db):
                        st.session_state.current_user = new_username
                        st.success(f"🎉 Welcome {new_username}!")
                        st.rerun()
                    else:
                        st.error("Failed to save user registration.")
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please enter a username")
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

def contacts_section():
    """Manage contacts"""
    st.sidebar.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.sidebar.header("👥 Contacts")
    
    current_user = st.session_state.current_user
    db = load_database()
    
    # Add contact section
    st.sidebar.subheader("Add New Contact")
    new_contact = st.sidebar.text_input("Enter username:").strip()
    
    if st.sidebar.button("➕ Add Contact", use_container_width=True, type="primary"):
        if new_contact:
            if new_contact == current_user:
                st.sidebar.error("❌ You cannot add yourself!")
            elif new_contact in db['users']:
                # Add to current user's contacts
                if new_contact not in db['contacts'][current_user]:
                    db['contacts'][current_user].append(new_contact)
                    if save_database(db):
                        st.sidebar.success(f"✅ Added {new_contact}!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Failed to save contact.")
                else:
                    st.sidebar.error("❌ Already in contacts!")
            else:
                st.sidebar.error("❌ User not found!")
    
    st.sidebar.markdown("---")
    
    # Display contacts
    st.sidebar.subheader("Your Contacts")
    user_contacts = db['contacts'].get(current_user, [])
    
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
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

def display_message(message):
    """Display a chat message with bold black text"""
    is_current_user = message["sender"] == st.session_state.current_user
    
    if message["type"] == "text":
        if is_current_user:
            st.markdown(f"""
            <div class='user-message'>
                <div class='message-sender'>You</div>
                <div class='message-text'>{message["content"]}</div>
                <div class='message-time'>{message["time"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='contact-message'>
                <div class='message-sender'>{message["sender"]}</div>
                <div class='message-text'>{message["content"]}</div>
                <div class='message-time'>{message["time"]}</div>
            </div>
            """, unsafe_allow_html=True)

def chat_section():
    """Main chat interface"""
    if not st.session_state.current_contact:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div class='info-card' style='text-align: center;'>", unsafe_allow_html=True)
            st.info("👈 Select a contact from the sidebar to start chatting!")
            st.markdown("</div>", unsafe_allow_html=True)
        return
    
    db = load_database()
    
    # Chat header
    st.markdown(f"""
    <div class='chat-header'>
        <h3>💬 Chat with {st.session_state.current_contact}</h3>
        <p>Last seen: {get_current_time()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        # Get messages between current user and contact
        chat_messages = [
            msg for msg in db['messages']
            if (msg["sender"] == st.session_state.current_user and msg["receiver"] == st.session_state.current_contact) or
               (msg["sender"] == st.session_state.current_contact and msg["receiver"] == st.session_state.current_user)
        ]
        
        # Sort by timestamp
        chat_messages.sort(key=lambda x: x.get("timestamp", ""))
        
        for message in chat_messages:
            display_message(message)
        
        if not chat_messages:
            st.markdown("<div class='info-card' style='text-align: center;'>", unsafe_allow_html=True)
            st.info("No messages yet. Start the conversation! 👇")
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Text input only (no image upload)
    text_input = st.chat_input(f"💬 Type a message to {st.session_state.current_contact}...")
    if text_input:
        db = load_database()  # Reload to get latest messages
        new_message = {
            "type": "text",
            "sender": st.session_state.current_user,
            "receiver": st.session_state.current_contact,
            "content": text_input,
            "time": get_current_time(),
            "timestamp": get_current_timestamp()
        }
        db['messages'].append(new_message)
        if save_database(db):
            st.rerun()
        else:
            st.error("Failed to send message")

def info_section():
    """App information section"""
    st.sidebar.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.sidebar.header("📊 App Info")
    
    db = load_database()
    
    st.markdown(f'<div class="app-info-text">👤 Total Users: {len(db["users"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-info-text">💬 Your Contacts: {len(db["contacts"].get(st.session_state.current_user, []))}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-info-text">📨 Total Messages: {len(db["messages"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-info-text">🕐 Current Time: {get_current_time()}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="app-info-text">📅 Today\'s Date: {datetime.datetime.now().strftime("%B %d, %Y")}</div>', unsafe_allow_html=True)
    
    # Show all registered users
    st.markdown("---")
    st.subheader("👥 All Users")
    if db['users']:
        for user in sorted(db['users'].keys()):
            if user == st.session_state.current_user:
                st.markdown(f'<div class="user-list">✅ {user} (You)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-list">👤 {user}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="user-list">No users registered yet</div>', unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

def main():
    # App title with better styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #075E54;'>💬 WhatsApp Web Clone</h1>", unsafe_allow_html=True)
        st.markdown(f'<p style="text-align: center; color: #000000; font-weight: bold;">🕐 {get_current_time()} | 📅 {datetime.datetime.now().strftime("%B %d, %Y")}</p>', unsafe_allow_html=True)
    
    # Initialize user session
    initialize_session()
    
    # Show login if not logged in
    if not st.session_state.current_user:
        login_section()
        st.markdown("<div class='info-card' style='text-align: center;'>", unsafe_allow_html=True)
        st.info("🔐 Please login or register to start chatting")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Main app interface
    st.sidebar.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.sidebar.success(f"**Logged in as:** {st.session_state.current_user}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    contacts_section()
    info_section()
    chat_section()

if __name__ == "__main__":
    main()
