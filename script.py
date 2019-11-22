import subprocess


subprocess.run('git add .', shell=True)
subprocess.run('echo "58542376" | sudo -S git commit -m "Josue"', shell=True)
#subprocess.run('echo "uuriel12009u@gmail.com"')
subprocess.run('git push origin master', shell=True)
