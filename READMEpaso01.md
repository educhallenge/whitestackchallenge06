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

Procedemos a aplicar el deployment. Verificamos que se despliega exitosamente el pod "challenge-app" y un servicio llamado "app-service".

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f deployment.yaml 
deployment.apps/challenge-app created
service/app-service unchanged

challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get all
NAME                                 READY   STATUS    RESTARTS   AGE
pod/challenge-app-6f79ff6b8d-fmzvc   1/1     Running   0          4s

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/app-service   ClusterIP   10.43.46.150   <none>        80/TCP    6d

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/challenge-app   1/1     1            1           5s

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/challenge-app-6f79ff6b8d   1         1         1       4s
```

Revisamos el archivo `ingress.yaml` y vemos que dice "\<\<CHANGEME\>\>" en el campo host. Copiamos el archivo ingress.yaml a un nuevo archivo llamado `paso01-ingress.yaml` y allí reemplazamos el valor "\<\<CHANGEME\>\>" por el valor "edu.challenger-03" .

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ grep host ingress.yaml 
  # Change the hostname to a unique value
  - host: <<CHANGEME>>

challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp ingress.yaml paso01-ingress.yaml

challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/<<CHANGEME>>/edu.challenger-03/' paso01-ingress.yaml

challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso01-ingress.yaml 
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: challenge-app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  # Change the hostname to a unique value
  - host: edu.challenger-03
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

Aplicamos el archivo ingress y verificamos que levanta correctamente.
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$  kubectl apply -f paso01-ingress.yaml 
ingress.networking.k8s.io/challenge-app-ingress configured

challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get ingress
NAME                    CLASS   HOSTS               ADDRESS         PORTS   AGE
challenge-app-ingress   nginx   edu.challenger-03   10.43.114.145   80      42h
```

Con el comando "kubectl get nodes -owide" podemos saber la dirección IP de cada worker.

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get nodes -owide
NAME                                        STATUS   ROLES                       AGE    VERSION          INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
whitestackchallenge-master-ad607762-crl4g   Ready    control-plane,etcd,master   200d   v1.28.2+rke2r1   10.101.8.218   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-gbspf   Ready    worker                      190d   v1.28.2+rke2r1   10.101.8.122   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-kfbgg   Ready    worker                      200d   v1.28.2+rke2r1   10.101.8.182   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-tnx7t   Ready    worker                      190d   v1.28.2+rke2r1   10.101.8.183   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
```

Usamos el comando curl y usamos la función "resolve" para resolver el nombre "edu.challenger-03". Probamos exitosamente la resolución con la IP de cada worker.

Probamos exitosamente la resolución con la IP 10.101.8.122 de whitestackchallenge-worker-f97ebc81-gbspf
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ curl http://edu.challenger-03 --resolve edu.challenger-03:80:10.101.8.122
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitestack Challenge 6</title>
</head>
<body>
    <center><h1>Welcome to the Whitestack Challenge 6</h1> </center>
    <h2>Environment Variables:</h2>
    <p>Node Name: whitestackchallenge-worker-f97ebc81-tnx7t</p>
    <p>Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
    <h2>Upload a File</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>challenger-03@challenge-6-pivote:~/ws-challenge-6$
```

Ahora probamos exitosamente la resolución con la IP 10.101.8.182 de whitestackchallenge-worker-f97ebc81-kfbgg
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ curl http://edu.challenger-03 --resolve edu.challenger-03:80:10.101.8.182
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitestack Challenge 6</title>
</head>
<body>
    <center><h1>Welcome to the Whitestack Challenge 6</h1> </center>
    <h2>Environment Variables:</h2>
    <p>Node Name: whitestackchallenge-worker-f97ebc81-tnx7t</p>
    <p>Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
    <h2>Upload a File</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
```

Y también probamos exitosamente la resolución con la IP 10.101.8.183 de whitestackchallenge-worker-f97ebc81-tnx7t
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ curl http://edu.challenger-03 --resolve edu.challenger-03:80:10.101.8.183
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitestack Challenge 6</title>
</head>
<body>
    <center><h1>Welcome to the Whitestack Challenge 6</h1> </center>
    <h2>Environment Variables:</h2>
    <p>Node Name: whitestackchallenge-worker-f97ebc81-tnx7t</p>
    <p>Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
    <h2>Upload a File</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
</html>challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
```

Hemos comprobado que la resolución funciona con cualquiera de las IPs de los workers. Debido a que no tenemos permisos de root para editar el archivo "etc/hosts" le solicitamos a los compañeros de Whitestack para que nos ayuden agregando la resolución de nombres en dicho archivo. La resolución escogida es "10.101.8.183 edu.challenger-03" como vemos abajo

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cat /etc/hosts
127.0.0.1 localhost

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
10.101.8.183 edu.challenger-03
```

Ahora podemos usar curl sin la opción "resolve" ya que se usará la resolución del archivo "etc/hosts". Vemos que resuelve el nombre exitosamente.

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ curl http://edu.challenger-03
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitestack Challenge 6</title>
</head>
<body>
    <center><h1>Welcome to the Whitestack Challenge 6</h1> </center>
    <h2>Environment Variables:</h2>
    <p>Node Name: whitestackchallenge-worker-f97ebc81-tnx7t</p>
    <p>Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
    <h2>Upload a File</h2>
    <form method="post" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="Upload">
    </form>
</body>
```
 
Finalmente nos piden definir la environment variable llamada "INGRESS_HOSTNAME" con el valor que escogimos para nuestro hostname "edu.challenger-03". Dicha environment variable la usaremos en los pasos 2 , 3 , 4 y 5 para ejecutar el script python del archivo `test-challenge6.py`

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ more test-challenge6.py | grep getenv
INGRESS_HOSTNAME = os.getenv('INGRESS_HOSTNAME', 'default-hostname')

challenger-03@challenge-6-pivote:~/ws-challenge-6$  export INGRESS_HOSTNAME="edu.challenger-03"
```
