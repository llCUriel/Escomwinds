import subprocess


subprocess.run('git add .', shell=True)
subprocess.run('git commit -m "Josue"', shell=True)
subprocess.run('git push origin master', shell=True)
