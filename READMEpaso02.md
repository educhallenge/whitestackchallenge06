# CHALLENGE 06 PASO 2: ENVIAR ALTA CARGA DE REQUESTS

## 1. ANALISIS DEL POR QUÉ DEL ERROR

Ingresamos a la VM pivote. Recordemos que para usar el script de python debemos usar ***export*** para definir la environment variable INGRESS_HOSTNAME *(alternativamente se configura la environment variable en el archivo `.profile` para que se cargue automáticamente cada vez que ingresamos a la VM pivote)*

```
challenger-03@challenge-6-pivote:~$  export INGRESS_HOSTNAME="edu.challenger-03"
```

Ahora vamos a tener 3 sesiones abiertas en paralelo:
- A: Ejecución del script python usando el argumento ***--send_high_load*** 
- B: Ejecutar "kubectl get pods" con el argumento ***--watch*** para ver los cambios en el pod en tiempo real.
- C: Revisión de logs en el pod en tiempo real


A: Ejecución del script python usando el argumento ***--send_high_load*** . Vemos que los primeros 200 requests tienen un `response code 200` lo cual significa OK.  A partir del request 201 empieza a fallar a veces con un `response code 502` otra veces con `response code 503`.  A partir del request 1436 vuelve a aparecer el `response code 200` pero a partir del request 1654 vuelve a fallar hasta el final, es decir hasta el request 2000.

```
challenger-03@challenge-6-pivote:~$ python3 ws-challenge-6/test-challenge6.py --send_high_load
Request 1: 200
Request 2: 200
### output omitido por brevedad
Request 200: 200
Request 201: 502
Request 202: 502
### output omitido por brevedad
Request 1434: 503
Request 1435: 503
Request 1436: 200
Request 1437: 503
Request 1438: 200
Request 1439: 200
Request 1440: 200
### output omitido por brevedad
Request 1651: 200
Request 1652: 200
Request 1653: 200
Request 1654: 502
Request 1655: 502
Request 1656: 502
### output omitido por brevedad
Request 1996: 502
Request 1997: 502
Request 1998: 503
Request 1999: 503
Request 2000: 503
Completed 2000 requests.
challenger-03@challenge-6-pivote:~$ 
```

B: Ejecutar "kubectl get pods" con el argumento ***--watch*** para ver los cambios en el pod en tiempo real. Vemos que el pod se reinicia 2 veces

```
challenger-03@challenge-6-pivote:~$ kubectl get pods --watch
NAME                             READY   STATUS    RESTARTS      AGE
challenge-app-6f79ff6b8d-fmzvc   1/1     Running   0 (26m ago)   29h
challenge-app-6f79ff6b8d-fmzvc   0/1     Error     0 (26m ago)   29h
challenge-app-6f79ff6b8d-fmzvc   1/1     Running   1 (3s ago)    29h
challenge-app-6f79ff6b8d-fmzvc   0/1     Error     1 (7s ago)    29h
challenge-app-6f79ff6b8d-fmzvc   0/1     CrashLoopBackOff   1 (14s ago)   29h
challenge-app-6f79ff6b8d-fmzvc   1/1     Running            2 (16s ago)   29h

```

C: Revisión de logs en el pod en tiempo real. Vemos que los primeros 200 logs indican `response code 200` pero luego vemos el mensaje de error que se excedió un rate limit de 200 requests por minuto.

```
challenger-03@challenge-6-pivote:~$ kubectl logs challenge-app-6f79ff6b8d-fmzvc -f
# output omitido por brevedad
2024-10-03 23:37:09,822 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,832 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,840 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,848 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,857 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,864 - 10.42.110.195 - - [03/Oct/2024 23:37:09] "GET / HTTP/1.1" 200 -
2024-10-03 23:37:09,870 - ratelimit 200 per 1 minute (10.42.110.195) exceeded at endpoint: index
2024-10-03 23:37:09,871 - Rate limit exceeded. Exiting.
challenger-03@challenge-6-pivote:~$ 
```

Del análisis concluimos que el problema es que el número de requests excede el rate limit definido en la aplicación desplegada en el pod.

## 2. SOLUCIÓN

Vamos a usar rate limit a nivel del ingress para evitar exceder el rate limit de la aplicación. Para ello podemos usar las siguientes `annotations` :

- `nginx.ingress.kubernetes.io/limit-rpm` sirve para definir un número máximo de requests per minute desde una determinada IP. Para evitar superar el rate limit de la aplicación el `limit-rpm` debería ser menor a 200. Tras hacer varias pruebas hemos visto que hay bursts que hacen que el número de requests sea un poco mayor a `limit-rpm`. Por ejemplo al probar con el valor de 176 se suman algunos bursts y se excede el rate limit de 200 requests definidos por la aplicación. Es por ello que definimos el valor de `limit-rpm` con el valor 175. 
- `nginx.ingress.kubernetes.io/limit-burst-multiplier` es un multiplicador de `limit-rpm`. Por defecto el valor del `limit-burst-multiplier` es 5. Pero en este ejemplo vamos a usar el valor de 1.


Copiamos el archivo `paso01-ingress.yaml` al archivo `paso02-ingress.yaml` y usamos el comando ***sed*** para agregar las 2 ***annotations*** que acabamos de mencionar.

```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6/
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp paso01-ingress.yaml paso02-ingress.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/limit-burst-multiplier: "1"' paso02-ingress.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/limit-rpm: "175"' paso02-ingress.yaml

challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso02-ingress.yaml 
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: challenge-app-ingress
  annotations:
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

Ahora aplicamos los cambios usando el archivo `paso02-ingress.yaml` y verificamos los cambios con el comando ***kubectl describe ingress***

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f paso02-ingress.yaml 
ingress.networking.k8s.io/challenge-app-ingress configured

challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl describe ingress challenge-app-ingress
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
                     nginx.ingress.kubernetes.io/rewrite-target: /
Events:
  Type    Reason  Age                 From                      Message
  ----    ------  ----                ----                      -------
  Normal  Sync    11s (x7 over 3d4h)  nginx-ingress-controller  Scheduled for sync
  Normal  Sync    11s (x7 over 3d4h)  nginx-ingress-controller  Scheduled for sync
  Normal  Sync    11s (x7 over 3d4h)  nginx-ingress-controller  Scheduled for sync

```

Para probar la solución vamos a tener 3 sesiones abiertas en paralelo:
- A: Ejecución del script python usando el argumento ***--send_high_load*** 
- B: Ejecutar "kubectl get pods" con el argumento ***--watch*** para ver los cambios en el pod en tiempo real.
- C: Revisión de logs en el pod en tiempo real


A: Ejecución del script python usando el argumento ***--send_high_load***  Verificamos que ahora no hay ningún `response code 502`  De los 2000 requests vemos que hay 200 requests con `response code 200` y 1800 requests con `response code 503`.

```
challenger-03@challenge-6-pivote:~$ python3 ws-challenge-6/test-challenge6.py --send_high_load >> paso02result.txt

challenger-03@challenge-6-pivote:~$ grep -c ": 200" paso02result.txt
200

challenger-03@challenge-6-pivote:~$ grep -c ": 503" paso02result.txt
1800
```

B: Ejecutar "kubectl get pods" con el argumento ***--watch*** para ver los cambios en el pod en tiempo real. Verificamos que el pod no sufrió ningún reinicio adicional a los 2 restarts que ya se habían hecho antes.
```
challenger-03@challenge-6-pivote:~$ kubectl get pods --watch
NAME                             READY   STATUS    RESTARTS        AGE
challenge-app-6f79ff6b8d-fmzvc   1/1     Running   2 (5h19m ago)   35h
```

C: Revisión de logs en el pod en tiempo real. Vemos que todos los logs indican `response code 200` y que no hay ningún mensaje de error porque en ningún momento se excedió el rate limit a nivel de la aplicación de 200 requests 

```
challenger-03@challenge-6-pivote:~$ kubectl logs challenge-app-6f79ff6b8d-fmzvc -f
### output omitido por brevedad
2024-10-04 04:50:40,388 - 10.42.110.195 - - [04/Oct/2024 04:50:40] "GET / HTTP/1.1" 200 -
2024-10-04 04:50:40,407 - 10.42.110.195 - - [04/Oct/2024 04:50:40] "GET / HTTP/1.1" 200 -
### output omitido por brevedad
2024-10-04 04:50:47,939 - 10.42.110.195 - - [04/Oct/2024 04:50:47] "GET / HTTP/1.1" 200 -
2024-10-04 04:50:48,281 - 10.42.110.195 - - [04/Oct/2024 04:50:48] "GET / HTTP/1.1" 200 -
2024-10-04 04:50:48,624 - 10.42.110.195 - - [04/Oct/2024 04:50:48] "GET / HTTP/1.1" 200 -
```
