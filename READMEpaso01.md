# CHALLENGE 06 PASO 1: DESPLEGAR LA APLICACIÓN

Ingresamos a nuestra VM pivote y clonamos el repositorio que nos indicaron en el paso 1. 

```
challenger-03@challenge-6-pivote:~$ git clone https://github.com/whitestack/ws-challenge-6.git
Cloning into 'ws-challenge-6'...
remote: Enumerating objects: 6, done.
remote: Counting objects: 100% (6/6), done.
remote: Compressing objects: 100% (6/6), done.
remote: Total 6 (delta 0), reused 6 (delta 0), pack-reused 0 (from 0)
Receiving objects: 100% (6/6), done.
```

Verificamos listando los archivos del repositorio que clonamos
```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6/
challenger-03@challenge-6-pivote:~/ws-challenge-6$ ls -l
total 16
-rw-rw-r-- 1 challenger-03 challenger-03     939 Oct  2 18:01 deployment.yaml
-rw-rw-r-- 1 challenger-03 challenger-03 2097152 Oct  2 18:01 file.bin
-rw-rw-r-- 1 challenger-03 challenger-03     431 Oct  2 18:01 ingress.yaml
-rw-rw-r-- 1 challenger-03 challenger-03    2740 Oct  2 18:01 test-challenge6.py
```

