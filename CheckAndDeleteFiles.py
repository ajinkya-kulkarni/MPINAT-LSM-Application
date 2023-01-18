import os

def check_and_delete(file_name):
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted old {file_name}")
