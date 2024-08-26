import streamlit as st

def creds_entered():
    if st.session_state["user"].strip() == "admin" and st.session_state["passwd"].strip() == "admin":
        st.session_state["authenticated"] = True
        st.experimental_rerun()  # Rerun the Streamlit app to reflect changes
    else:
        st.session_state["authenticated"] = False
        st.error("The username or password you have entered is invalid")

def authenticate_user():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.title("Welcome to Authentication Page")
        username = st.text_input(label="Username :", value="", key="user")
        password = st.text_input(label="Password :", value="", key="passwd", type="password", on_change=creds_entered)
        login_button = st.button("Login")
        if login_button:
            creds_entered()
    else:
        st.write("Redirecting to main page...")
        st.components.v1.html(
            """
            <script>
                setTimeout(function() {
                    window.location.href = '/main';  // Redirect to main page after 2 seconds
                }, 2000);
            </script>
            """
        )

def main():
    st.title("Main Page")
    if st.session_state.get("authenticated"):
        st.write("Logged in as admin")
        logout_button = st.button("Logout")
        if logout_button:
            st.session_state["authenticated"] = False
            st.experimental_rerun()  # Rerun the Streamlit app to reflect changes
    else:
        st.write("Redirecting to authentication page...")
        st.components.v1.html(
            """
            <script>
                setTimeout(function() {
                    window.location.href = '/auth';  // Redirect to authentication page after 2 seconds
                }, 2000);
            </script>
            """
        )


