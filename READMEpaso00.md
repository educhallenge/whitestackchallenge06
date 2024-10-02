# CHALLENGE 06 PASO 0: PROBAR ACCESOS

En nuestra máquina local llamada Lubuntu tenemos el archivo `challenger-03_id_ed25519` que contiene SSH keys y el archivo `whitestackchallenge.yaml` que sirve para conectarnos a un cluster remoto con Kubernetes.

También tenemos una máquina remota llamada "challenge-6-pivote" con IP 201.217.240.69 y puerto SSH tcp/3822.

Usamos el comando SCP y las ssh keys para copiar el archivo `whitestackchallenge.yaml` a la máquina remota

Usamos el comando SSH y las ssh keys para conectarnos a la máquina remota

```
ubuntu@lubuntu:~$ ls -hal
drwxr-xr-x 15 ubuntu ubuntu 4.0K Oct  1 19:44 .
drwxr-xr-x  4 root   root   4.0K Aug 31 21:47 ..
-rw-------  1 ubuntu ubuntu  432 Sep 14 19:06 challenger-03_id_ed25519
-rwx------  1 ubuntu ubuntu 2.5K Sep 14 19:06 whitestackchallenge.yaml

ubuntu@lubuntu:~$ scp -P 3822 -i ~/challenger-03_id_ed25519 whitestackchallenge.yaml  challenger-03@201.217.240.69:
whitestackchallenge.yaml                                                                   100% 2469    18.0KB/s   00:00

ubuntu@lubuntu:~$ ssh -p 3822  challenger-03@201.217.240.69  -i ~/challenger-03_id_ed25519
Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.8.0-31-generic x86_64)

challenger-03@challenge-6-pivote:~$
```

