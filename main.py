import sys, subprocess
select = input("1-Run face recognition\n 2-Build face encodings database\nChoose an option (1 or 2): ")
if select == "1":
    subprocess.run([sys.executable, "face_recognition.py"])
elif select == "2":
    subprocess.run([sys.executable, "build_encodings.py"])
else:
    print("Invalid option. Please choose 1 or 2.")
