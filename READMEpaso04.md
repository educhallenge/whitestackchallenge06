# CHALLENGE 06 PASO 4: PROBAR UPLOAD DE UN ARCHIVO

## 4.1 ANALISIS DEL POR QUÉ DEL ERROR

Ingresamos a la VM pivote. Recordemos que para usar el script de python debemos usar ***export*** para definir la environment variable INGRESS_HOSTNAME *(alternativamente se configura la environment variable en el archivo `.profile` para que se cargue automáticamente cada vez que ingresamos a la VM pivote)*
 
```
challenger-03@challenge-6-pivote:~$  export INGRESS_HOSTNAME="edu.challenger-03"
```

Ahora vamos a ejecutar el script python usando el argumento ***--send_file file.bin*** . Vemos que falla con un `response code 413` 

```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6
challenger-03@challenge-6-pivote:~/ws-challenge-6$ python3 test-challenge6.py --send_file file.bin
An error occurred: 413 Client Error: Request Entity Too Large for url: http://edu.challenger-03/upload
```

Revisamos la siguiente documentación pública del ingress NGINX :
- https://github.com/kubernetes/ingress-nginx/blob/main/docs/user-guide/nginx-configuration/annotations.md#custom-max-body-size
- https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size

En dicha documentación encontramos que el error 413 se produce cuando se excede el máximo tamaño del ***request body*** el cual por defecto es 1 megabyte. Y el archivo que intentamos subir con el script python pesa 2 megabytes.

Podemos solucionar el problema usando un `annotation` en el ingress como se explica en la siguiente sección.

## 4.2 SOLUCIÓN

Vamos a usar un `annotation` llamado `nginx.ingress.kubernetes.io/proxy-body-size` con el valor de "3m" para que el ingress pueda aceptar subir el archivo `file.bin` que pesa 2 megabytes.

Copiamos el archivo `paso03-ingress.yaml` al archivo `paso04-ingress.yaml` y usamos el comando ***sed*** para agregar la ***annotation*** que acabamos de mencionar.

```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6/
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp paso03-ingress.yaml paso04-ingress.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/proxy-body-size: 3m' paso04-ingress.yaml

challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso04-ingress.yaml 
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: challenge-app-ingress
  annotations:
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
            name: app-service
            port:
              number: 80
```

Ahora aplicamos los cambios usando el archivo `paso04-ingress.yaml` y verificamos los cambios con el comando ***kubectl describe ingress***

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f paso04-ingress.yaml 
ingress.networking.k8s.io/challenge-app-ingress configured

challenger-03@challenge-6-pivote:~/ws-challenge-6$  kubectl describe ingress challenge-app-ingress
Name:             challenge-app-ingress
Labels:           <none>
Namespace:        challenger-03
Address:          10.43.114.145
Ingress Class:    nginx
Default backend:  <default>
Rules:
  Host               Path  Backends
  ----               ----  --------
  edu.challenger-03  
                     /   app-service:80 (10.42.110.251:8080)
Annotations:         field.cattle.io/publicEndpoints:
                       [{"addresses":["10.43.114.145"],"port":80,"protocol":"HTTP","serviceName":"challenger-03:app-service","ingressName":"challenger-03:challen...
                     nginx.ingress.kubernetes.io/limit-burst-multiplier: 1
                     nginx.ingress.kubernetes.io/limit-rpm: 175
                     nginx.ingress.kubernetes.io/proxy-body-size: 3m
                     nginx.ingress.kubernetes.io/proxy-buffer-size: 5k
                     nginx.ingress.kubernetes.io/rewrite-target: /
Events:
  Type    Reason  Age                  From                      Message
  ----    ------  ----                 ----                      -------
  Normal  Sync    13s (x10 over 4d2h)  nginx-ingress-controller  Scheduled for sync
  Normal  Sync    13s (x10 over 4d2h)  nginx-ingress-controller  Scheduled for sync
  Normal  Sync    13s (x10 over 4d2h)  nginx-ingress-controller  Scheduled for sync
```

Antes de probar la solución vamos a verificar que el directorio `uploads` está vacío en nuestro pod 

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$  kubectl exec -it challenge-app-6f79ff6b8d-fmzvc -- ls -hal /uploads
Warning: Use tokens from the TokenRequest API or manually created secret-based tokens instead of auto-generated secret-based tokens.
total 8.0K
drwxrwxrwx 2 root root 4.0K Oct  2 18:19 .
drwxr-xr-x 1 root root 4.0K Oct  4 00:04 ..
```

Ahora para probar la solución vamos a ejecutar el script python usando el argumento ***--send_file file.bin***  Verificamos que ahora no hay ningún `response code 413` sino que la respuesta es exitosa.

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ python3 test-challenge6.py --send_file file.bin
File uploaded successfully: 200
```

Volvemos a verificar el directorio `uploads` de nuestro pod y ahora vemos que está presente el archivo `file.bin` que acabamos de subir usando el script python.

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl exec -it challenge-app-6f79ff6b8d-fmzvc -- ls -hal /uploads
total 2.1M
drwxrwxrwx 2 root root 4.0K Oct  5 02:26 .
drwxr-xr-x 1 root root 4.0K Oct  4 00:04 ..
-rw-r--r-- 1 root root 2.0M Oct  5 02:26 file.bin
```

También podemos usar el argumento `tail` del comando ***kubectl logs*** y ver el último log de la aplicación de nuestro pod el cual muestra un POST exitoso con el path `/upload` y con un `response code 200`

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$  kubect logs -l app=challenge-app --tail=1
2024-10-05 02:26:59,878 - 10.42.110.195 - - [05/Oct/2024 02:26:59] "POST /upload HTTP/1.1" 200 -
```
