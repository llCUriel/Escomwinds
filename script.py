import subprocess

subprocess.run('git add .', shell=True)
subprocess.run('git commit -m "HolaJosue"')
subprocess.run('git push origin master')
