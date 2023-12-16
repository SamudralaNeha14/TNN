import pickle
from pathlib import Path

import streamlit_authenticator as stauth

names = ["Samudrala Neha", " Perapa Tanuja","Basham Namrata"]
usernames = ["Sneha", "Ptanuja","Bnamrata"]
passwords = ["neha1402", "tanu1408","nammu504"]

hashed_passwords = stauth.Hasher(passwords).generate()

file_path = Path(__file__).parent / "hasher_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)