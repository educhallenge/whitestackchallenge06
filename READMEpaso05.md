# CHALLENGE 06 PASO 5: BALANCEAR LA CARGA DE LOS REQUESTS

## 1. ANALISIS DEL REQUERIMIENTO

El requerimiento es desplegar una nueva versión de la aplicación de forma gradual (70% de la app:v1 y 30%& de la app:v2) Esto corresponde a una técnica llamada ***canary deployment***

Para ejecutar dicha técnica en Kubernetes vamos a crear un nuevo deployment, un nuevo service y un nuevo ingress en paralelo al deployment, al service y al ingress que ya estaban en ejecución de antemano. Es decir los recursos originales de la app:v1 van a convivir con los nuevos recursos de la app:v2.

Además el nuevo ingress deberá usar las siguientes `annotations` para implementar el ***canary deployment***

- `nginx.ingress.kubernetes.io/canary` con el valor "true" para activar la funcionalidad
- `nginx.ingress.kubernetes.io/canary-weight` con el valor "30" para balancear el 30% de los request al nuevo ingress. El resto, o sea el 70% se balanceará al ingress original que ya estaba en ejecución de antemano.

## 2. CREACIÓN DEL NUEVO DEPLOYMENT Y SERVICE

En nuestra VM pivote vamos a copiar el archivo `deployment.yaml` (el que se usó para desplegar la app original, es decir la app:v1) y vamos a copiarlo a un nuevo archivo llamado `paso05-deployment.yaml`

```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6/
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp deployment.yaml paso05-deployment.yaml
```

En el nuevo archivo `paso05-deployment.yaml` vamos a modificar el nombre del deployment:
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/name: challenge-app/name: challenge-app-v2/' paso05-deployment.yaml
```

Luego vamos a modificar el label de la aplicación:
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/app: challenge-app/app: challenge-app-v2/' paso05-deployment.yaml
```

Luego vamos a modificar el nombre del servicio:
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/name: app-service/name: app-service-v2/' paso05-deployment.yaml
```

Y también a cambiar el nombre de la imagen que ya no va a ser app:v1 sino app:v2
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/app:v1/app:v2/' paso05-deployment.yaml
```

Revisamos el estado final del archivo `paso05-deployment.yaml`

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso05-deployment.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: challenge-app-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: challenge-app-v2
  template:
    metadata:
      labels:
        app: challenge-app-v2
    spec:
      containers:
      - name: frontend
        image: gcr.io/whitestack/challenge-6/app:v2
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: uploads
          mountPath: /uploads
        env:
          - name: NODE_NAME
            valueFrom:
              fieldRef:
                fieldPath: spec.nodeName
          - name: POD_NAME
            valueFrom:
              fieldRef:
                fieldPath: metadata.name
      volumes:
      - name: uploads
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: app-service-v2
spec:
  selector:
    app: challenge-app-v2
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
```

Aplicamos el nuevo archivo. Sin embargo cuando revisamos el status del nuevo pod vemos que constantemente se reinicia
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$  kubectl apply -f paso05-deployment.yaml 

challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get pods
NAME                                READY   STATUS             RESTARTS       AGE
challenge-app-6f79ff6b8d-fmzvc      1/1     Running            4 (2d3h ago)   3d8h
challenge-app-v2-749cf45bd6-9psrh   0/1     CrashLoopBackOff   5 (69s ago)    4m16s
```

Revisamos los logs y encontramos un traceback que nos indica un error con el módulo "Flask_Limiter"
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl logs challenge-app-v2-749cf45bd6-9psrh
Traceback (most recent call last):
  File "/app/app.py", line 3, in <module>
    from flask_limiter import Limiter
ModuleNotFoundError: No module named 'flask_limiter'
challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
```

Debido a los constantes reinicios no podemos ingresar al pod a realizar troubleshooting. Sin embargo vamos a nuestra máquina local y bajamos la imagen de la ***app:v2*** . Usaremos ***docker*** para hacer el troubleshooting:
```
ieee@linux:~$ sudo docker pull gcr.io/whitestack/challenge-6/app:v2
v2: Pulling from whitestack/challenge-6/app
e4fff0779e6d: Pull complete 
5be20a4ff277: Pull complete 
48174a2f2dd9: Pull complete 
0cb9f64d8db6: Pull complete 
c9140ff79093: Pull complete 
ed4f0a673788: Pull complete 
f5e57adfb11f: Pull complete 
c07f45de1838: Pull complete 
4f3c287706a7: Pull complete 
Digest: sha256:e1f4c853d5ed318d7ede955cc2c0892ea6f6ff3ebe629e4b4756ff8abeabfa6c
Status: Downloaded newer image for gcr.io/whitestack/challenge-6/app:v2
gcr.io/whitestack/challenge-6/app:v2
```

Ejecutamos el container y vemos que no se encuentra el módulo "Flask-Limiter" . Por eso procedemos a instalarlo.
```
ieee@linux:~$ sudo docker run -it gcr.io/whitestack/challenge-6/app:v2 bash

root@f865860ee746:/app# pip freeze | grep Flask-Limiter

root@f865860ee746:/app# pip install Flask-Limiter
Collecting Flask-Limiter
  Downloading Flask_Limiter-3.8.0-py3-none-any.whl (28 kB)
# output omitido por brevedad
Successfully installed Flask-Limiter-3.8.0 deprecated-1.2.14 importlib-resources-6.4.5 limits-3.13.0 markdown-it-py-3.0.0 mdurl-0.1.2 ordered-set-4.1.0 packaging-24.1 pygments-2.18.0 rich-13.9.2 typing-extensions-4.12.2 wrapt-1.16.0

root@f865860ee746:/app# pip freeze | grep Flask-Limiter
Flask-Limiter==3.8.0
root@f865860ee746:/app# exit
```

A partir de nuestro container modificado vamos a crear una nueva imagen y le asignaremos el nombre y tag ***edual/app:v2***
```
ieee@linux:~$ sudo docker ps -a
CONTAINER ID   IMAGE                                  COMMAND    CREATED          STATUS                     PORTS     NAMES
f865860ee746   gcr.io/whitestack/challenge-6/app:v2   "bash"     42 seconds ago   Exited (0) 4 seconds ago             upbeat_rhodes

ieee@linux:~$ sudo docker commit -a "edu" f865860ee746 edual/app:v2
sha256:2af9b1b32e116b3d452454c7bc6f7aea6dcc196e02db4c170d39cf4f17f80972

ieee@linux:~$ sudo docker images
REPOSITORY                          TAG       IMAGE ID       CREATED         SIZE
edual/app                           v2        2af9b1b32e11   47 seconds ago  150MB
gcr.io/whitestack/challenge-6/app   v2        97049df79ee2   6 weeks ago     137MB
```

Ahora vamos a subir la nueva imagen a Docker Hub
```
ieee@linux:~$ sudo docker login -u edual
Password: 
Login Succeeded

ieee@linux:~$ sudo docker push edual/app:v2
The push refers to repository [docker.io/edual/app]
9ba067c7e4d3: Layer already exists 
15a1cf09b607: Layer already exists 
b3865de0206e: Layer already exists 
cde66b870a07: Layer already exists 
a4836fd70a19: Layer already exists 
d24f9dbb0a3a: Layer already exists 
8657193c8651: Layer already exists 
0900caae955e: Layer already exists 
414698da489a: Layer already exists 
9853575bc4f9: Layer already exists 
v2: digest: sha256:ba998d877b52fe471e5e044a061d7b46baafe28fcc3060b366ed5723cf52f74d size: 2415
```

Volvemos a nuestra VM pivote y el archivo  `paso05-deployment.yaml` lo vamos a copiar a un nuevo archivo llamado  `paso05-deploy-edualv2.yaml`

En dicho nuevo archivo vamos a modificar el nombre de la imagen y también decirle a Kubernetes que ejecute el comando ***python*** con el argumento ***app.py***

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp paso05-deployment.yaml paso05-deploy-edualv2.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/gcr.io\/whitestack\/challenge-6\/app:v2/edual\/app:v2/' paso05-deploy-edualv2.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/app:v2/a \        command: [ "python" ]\n        args: [ "app.py" ]' paso05-deploy-edualv2.yaml
```

Verificamos el contenido del nuevo archivo
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso05-deploy-edualv2.yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: challenge-app-v2
spec:
  replicas: 1
  selector:
    matchLabels:
      app: challenge-app-v2
  template:
    metadata:
      labels:
        app: challenge-app-v2
    spec:
      containers:
      - name: frontend
        image: edual/app:v2
        command: [ "python" ]
        args: [ "app.py" ]
        imagePullPolicy: Always
# output omitido por brevedad
```

Ahora borramos los recursos del archivo `paso05-deployment.yaml` y creamos los recursos del archivo `paso05-deploy-edualv2.yaml`
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl delete -f paso05-deployment.yaml
deployment.apps "challenge-app-v2" deleted
service "app-service-v2" deleted

challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f paso05-deploy-edualv2.yaml
deployment.apps/challenge-app-v2 created
service/app-service-v2 created
```

Verificamos que los recursos de la app:v2 conviven con los recursos de la app:v1
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get all
NAME                                    READY   STATUS    RESTARTS       AGE
pod/challenge-app-6f79ff6b8d-fmzvc      1/1     Running   4 (2d9h ago)   3d14h
pod/challenge-app-v2-6b8464cddd-nnjmj   1/1     Running   0              2m9s

NAME                     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
service/app-service      ClusterIP   10.43.46.150   <none>        80/TCP    9d
service/app-service-v2   ClusterIP   10.43.148.20   <none>        80/TCP    2m10s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/challenge-app      1/1     1            1           3d14h
deployment.apps/challenge-app-v2   1/1     1            1           2m10s

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/challenge-app-6f79ff6b8d      1         1         1       3d14h
replicaset.apps/challenge-app-v2-6b8464cddd   1         1         1       2m10s

```

## 3. CREACIÓN DEL NUEVO INGRESS

En nuestra VM pivote vamos a copiar el archivo `paso04-ingress.yaml` a un nuevo archivo llamado `paso05-ingress.yaml`

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp paso04-ingress.yaml paso05-ingress.yaml
```

En el nuevo archivo vamos a cambiar el nombre del ingress
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/name: challenge-app-ingress/name: challenge-app-ingress-v2/' paso05-ingress.yaml
```

También vamos a cambiar el nombre del servicio que es llamado por el ingress
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i 's/name: app-service/name: app-service-v2/' paso05-ingress.yaml
```

Y finalmente vamos a agregar las `annotations` que explicamos al inicio de este readme.
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/canary: "true"' paso05-ingress.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/canary-weight: "30"' paso05-ingress.yaml
```

Verificamos como quedó nuestro archivo
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso05-ingress.yaml 
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: challenge-app-ingress-v2
  annotations:
    nginx.ingress.kubernetes.io/canary-weight: "30"
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: 3m
    nginx.ingress.kubernetes.io/proxy-buffer-size: "5k"
    nginx.ingress.kubernetes.io/limit-rpm: "175"
    nginx.ingress.kubernetes.io/limit-burst-multiplier: "1"
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
            name: app-service-v2
            port:
              number: 80
```

Aplicamos los cambios y vemos que el nuevo ingress levanta correctamente
```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f paso05-ingress.yaml 
ingress.networking.k8s.io/challenge-app-ingress-v2 created


challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get ingress
NAME                       CLASS   HOSTS               ADDRESS         PORTS   AGE
challenge-app-ingress      nginx   edu.challenger-03   10.43.114.145   80      5d9h
challenge-app-ingress-v2   nginx   edu.challenger-03   10.43.114.145   80      21s
```

## 4. VERIFICACIÓN DE LA SOLUCIÓN

Ahora vamos a ejecutar el script python usando el argumento ***--test_load_balance*** y el output lo guardamos en un archivo para su posterior análisis.

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ python3 test-challenge6.py --test_load_balance > paso05-output.txt

challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso05output.txt 
Resquest # 1
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 2
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 3
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 4
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 5
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 6
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 7
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 8
Pod Name: challenge-app-v2-6b8464cddd-nnjmj</p>

# output omitido por brevedad

Resquest # 96
Pod Name: challenge-app-v2-6b8464cddd-nnjmj</p>
Resquest # 97
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 98
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
Resquest # 99
Pod Name: challenge-app-6f79ff6b8d-fmzvc</p>
challenger-03@challenge-6-pivote:~/ws-challenge-6$ 
```

Vamos a usar el comando ***grep*** para contar los requests. Vemos que los requests que fueron a la ***app:v1***  se aproxima bastante al 70%  y los requests que fueron a la  ***app:v2***  se aproximan bastante al 30% con lo cual cumplimos con los requerimientos pedidos.


```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl get pods
NAME                                READY   STATUS    RESTARTS       AGE
challenge-app-6f79ff6b8d-fmzvc      1/1     Running   4 (2d9h ago)   3d15h
challenge-app-v2-6b8464cddd-nnjmj   1/1     Running   0              15m

challenger-03@challenge-6-pivote:~/ws-challenge-6$ grep -c "challenge-app-6f79ff6b8d-fmzvc" paso05-output.txt 
69

challenger-03@challenge-6-pivote:~/ws-challenge-6$ grep -c "challenge-app-v2-6b8464cddd-nnjmj" paso05-output.txt 
30
```
