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

Procedemos a aplicar el deployment. Verificamos que se despliega un pod y un servicio llamado "app-service".

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

Revisamos el archivo `ingress.yaml` y vemos que dice "<<CHANGEME>>" en el campo host. Copiamos el archivo ingress.yaml a un nuevo archivo llamado `paso01-ingress.yaml` y allí reemplazamos el valor "<<CHANGEME>>" por el valor "edu.challenger-03" .

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

Con el comando "kubectl get nodes -owide" aprendemos la dirección IP de cada worker. Escogemos la IP 10.101.8.183 y solicitamos a los compañeros de Whitestack para que nos ayuden agregando la resolución de nombres en dicho archivo.

Debido a que no tenemos permisos de root no podemos editar el archivo "etc/hosts". Por tal motivo 

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get nodes -owide
Warning: Use tokens from the TokenRequest API or manually created secret-based tokens instead of auto-generated secret-based tokens.
NAME                                        STATUS   ROLES                       AGE    VERSION          INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
whitestackchallenge-master-ad607762-crl4g   Ready    control-plane,etcd,master   200d   v1.28.2+rke2r1   10.101.8.218   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-gbspf   Ready    worker                      190d   v1.28.2+rke2r1   10.101.8.122   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-kfbgg   Ready    worker                      200d   v1.28.2+rke2r1   10.101.8.182   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
whitestackchallenge-worker-f97ebc81-tnx7t   Ready    worker                      190d   v1.28.2+rke2r1   10.101.8.183   <none>        Ubuntu 20.04.2 LTS   5.4.0-65-generic   containerd://1.7.3-k3s1
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
