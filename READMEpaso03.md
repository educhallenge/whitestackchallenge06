# CHALLENGE 06 PASO 3: ENVIAR LARGE HEADER REQUESTS

## 3.1 ANALISIS DEL POR QUÉ DEL ERROR

Ingresamos a la VM pivote. Recordemos que para usar el script de python debemos usar ***export*** para definir la environment variable INGRESS_HOSTNAME *(alternativamente se configura la environment variable en el archivo `.profile` para que se cargue automáticamente cada vez que ingresamos a la VM pivote)*
 
```
challenger-03@challenge-6-pivote:~$  export INGRESS_HOSTNAME="edu.challenger-03"
```

Ahora vamos a tener 2 sesiones abiertas en paralelo:
- A: Ejecución del script python usando el argumento ***--send_simple_request*** 
- B: Revisión de logs en el pod en tiempo real


A: Ejecución del script python usando el argumento ***--send_simple_request*** . Vemos que falla con un `response code 502` 

```
challenger-03@challenge-6-pivote:~$ python3 ~/ws-challenge-6/test-challenge6.py --send_simple_request
Response Headers:
{'Date': 'Fri, 04 Oct 2024 16:22:25 GMT', 'Content-Type': 'text/html', 'Content-Length': '150', 'Connection': 'keep-alive'}

Response Body:
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

B: Revisión de logs en el pod en tiempo real. Vemos un solo log indicando que se hizo un request al path `/random-code` y tuvo un `response code 200` 

```
challenger-03@challenge-6-pivote:~$ kubectl logs -l app=challenge-app -f
# output omitido por brevedad
2024-10-04 16:22:25,319 - 10.42.110.195 - - [04/Oct/2024 16:22:25] "GET /random-code HTTP/1.1" 200 -
```

De lo anterior vemos que la aplicación del pod tiene un `response code 200`  pero el ingress tiene un `response code 502` lo cual significa que la falla viene del ingress, no de la aplicación.


Esto lo comprobamos navegando directamente al servicio en vez de navegar al ingress. Para ello otra vez usamos 2 sesiones en paralelo:
- A: Ejecutar port-forward hacia el servicio
- B: Navegar hacia el servicio

A: Ejecutar port-forward hacia el servicio. Averiguamos que el servicio se llama "app-service" y hacemos port-forward del puerto 8000 del host hacia el puerto 80 del servicio.
```
challenger-03@challenge-6-pivote:~$ kubectl get svc
NAME          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
app-service   ClusterIP   10.43.46.150   <none>        80/TCP    7d22h

challenger-03@challenge-6-pivote:~$ kubectl port-forward svc/app-service 8000:80
Forwarding from 127.0.0.1:8000 -> 8080
Forwarding from [::1]:8000 -> 8080
Handling connection for 8000
```
B: En una sesión en paralelo navegamos hacia el servicio usando ***cURL***. Usamos la IP del localhost 127.0.0.1, el puerto 8000 (que usamos para hacer port-forwarding) y el path `random-code`.  Además también con el comando ***cURL*** usamos el argumento `-w '\n HEADERS SIZE %{size_header} BYTES'` que nos permite averiguar el tamaño de los headers.
```
challenger-03@challenge-6-pivote:~$ curl -v 127.0.0.1:8000/random-code -w '\n HEADERS SIZE %{size_header} BYTES'
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000
> GET /random-code HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/8.5.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: text/html; charset=utf-8
< Content-Length: 21
< X-Large-Header: 424e35aa9ede2240b215abe9cef3c1e807502bf706d9f1c5411854f1b03699cda67c3f2ffb4ad97bf352644891d45a57ebcfa2354cc1346c5073eca2e75cc496526a07db0b32b59afd1d3e980ef3abf4c311ec923462a5d56621a3315741d988dfb3b3c792ddd4011a34d53f514de83646f514d4eed54042accb929b084a42e2387ddb8a319e8d5a92786a2d6d22c44bb3098a35ae5716e9cbc3ec7b312d45417616348a7bdd0457c79c0c1ad24ae9b5748d8ee25fd04de7f93aa7514a6c641e7bde1e4332200545f1f0693a5679cd14114aa9024074afd5965e43462e4a98550396b8f83c60be3c8594b70cc757060f94b9aaa2ffd522bb1ec50ba4d6d67ce9c62cfbd135371e0cb9cfb7eb37505178e28efedbadadb364257e62046fb029d1e536125213ed9e16bd4f9903fa32c82d4e583d687fe62d913ce163ef80bfcbf56e2aa6f268f24ea8d7029b4f98b10d9730d6d810db6946fdc55b794f754c3dc54b7334d32176c80ec1baf909b1cc34235c7470c70d0b93a105d3187d950b142f50be26313742dddb785614bec6b2d32d5528ac6581daa2e7f3e88a88c1a9cb289f24181aecef38ba565f3d18afde09435e92640a4f64c53e673565048b71e0c4b8e807ed5a5e31fd5ab87b626751a2e9ca3ab8a0f728314af9ac013b00c32984837937fa1f96ce040304841b9fdcdc398bd7a4bed50703ef69ee9b53c092fe4c0745a0a95a41b0be30fca0e439682128de0183bfa3e6226267e76233a014a403361f482c8e542a990480b24e6b955c9fb1b2f26d2e240d2ec3f50763170e5586d5c3c823916954c4357c737d2677de1f206c9c5f8265c4cf7d369ada48fe6a96e53779f7f2bbd4c44d7b6094e1f727a3b778860f05b0509c7b8a8b19c25e78245a564a18a6ab6dc21a36d7fb20d1d429b7487e5bf53bd076f09ed611792cccab2becce7bb1afec153a6401569f6391c8b7321eb80a95c981a62e11bd750ac659ca229d698cee206350b8065707b80dd816f19a791df734fff5dc77bef9ad389dd509375df66fff053eaace16091319755217e384d8417e463f9d682f57f8d63959112961b528d43bd8a1c2133bcf2945fd203a3d6d92ad0791bf10e7bf446ef8fd251713c5bc6cdac75727e717ffdc96c1ef3f34dbb672141c04d1442927bca1b5b6bb349fe4538a6fccee80ea6fd81f8e1eb16632bdea1a090167feb4b1a56b8241ab8137e9c7254363ba289fff7ede4199ef7d6d30729b33f06fb747db56131371dbf23465ec2617f797be7e6c5ad8e68a28446650a2b83f0b645cf1fbe866e48d95610f78d49a631ad803ea63fac002b79af97a48dec6ac0f5560e13ede1fccfca1c423af18e73e8fc10ccd8bb4181cc1d5b5b20391318ad9e93a61f7fe934519102135a531a594607453babaf5d6c43e26547025a200278374ba0c5c1aedf9de44c7405c35a652d2ace964aaa73a8563c3f0bfac79b924124ec95203b7af78023a8b9daac9d0bc896c6012f9621b668142bdfc439270653f6afcba12c6ae61c9f9687ca86201afcc31cfee4f9b0ac3bb97a296f431ccab5a72fb2ea393abfd7eb571a3db324a7aa0b2f31fb23abb5f92ed2e6bafff26d196476c2250ef3d44a54d1deedae21c23fe6fbabf5fd21a0bd4d00dbfdef7199233cecdb1fdb9b300fc6ba024f1bed3c1ca6ff0e629b4939ae8ac33ac1332b22e964f7fb352e8d32143e122831989acbe30319ec16ffd775cde7ef5dca56660ba0fcbf17d58b5b19cddf3ad70255be422ea6a0c741f6794c378b876697af663240f59968fa0bb6cc5468076c199f8144b2313f39938fae1f28febed632304b1b77d43e809521fb8c9b1c36f465f8b0cc0f522312cb376105f5069eed15aeee3608d657fe3fe2bef396518854db450f9ca0b8b6247568a99df682e59d40a77148e868738fe12a88c8944b68feae70897ee6909f0db7caa148fc2a95bde5ea31f0afc71e8c6c13c7c7d0c061b95521b88fde7c1385a4f8990546d281e4d5b578e64ebd30ddab98e859fe5b61f3f3a138954049d1c5b768c39fa3683d263b33401cf5e2a5933ebfe9e400d2986d46121c1782804a14917a85cd1c02ae8ae5c313a6d5b2b805f238dfffc64c1c60091b166f4a3b449077bfb1d23167f24f4b18c34d9470708a28e4092fb1f9011c498b8800ed291b887e1398dfec79228af1fb55da0df9af12d6e1ae62b51a762ab5a668965f0994dd61ad975387edde329d942771cb259862ccaac8ee1bd8ce0f0271d824f073d98814580263a4dd5a5abcf218eda198e367c41187e95aa083082e6e062bad975b3ce9005567ea3b5bfced9c9e4b02af8881c033f0248d6bf70b2d562209705745feaccf7d1c4d5301c88e197fa187e99bb24c912397e24fabcc9be031dfbba01e1e407eb032a264dbeb664978fad0777e23e38a5261cbe99f4c3164f4257cb6882ca3d194054b940e9cb10bce60c1301ffd60da0cfbd1df25c8b628278f8c5a728fa88bde8404389b7c02ef7d564a22df6e82ae2fdad8ca8ec52fce2162e3670c191c66c2d3b6aea2f9e76446c3adad19a1f62b4a820a3c91bf963e4b094a660bc9f2e618a003c7d018bf75c353ec262a4de9b96283ba6a3fd35e19d29ead145bcf50da467bb4a958b38ded4b46bbedbf700d6273f9783905ec0e56bcc9492cdbb948b2604a52a40c387648be15aea6efa5c81e4c014b3b3c072d32a47eef5591515c89a153f7b4945fc8a3a9960f83762adfbee953b9520e71bd74ae1c0a90081c0e1f7f21d86e5aac1a7651c4b54dff92266172e70f6445b030a72a88901df9920179513
< Server: Werkzeug/2.0.3 Python/3.9.19
< Date: Fri, 04 Oct 2024 16:45:54 GMT
< 
* Closing connection
Received your request
 HEADERS SIZE 4172 BYTES
```
De la última línea del output anterior vemos que ***cURL*** calculó el tamaño de los headers `HEADERS SIZE 4172 BYTES` lo cual es muy grande. Si exploramos los headers vemos que `X-Large-Header` es el responsable de dicho tamaño grande. Todos los demás headers son pequeños.

Hemos revisado la documentación del ingress nginx https://github.com/kubernetes/ingress-nginx/blob/main/docs/user-guide/nginx-configuration/annotations.md#proxy-buffer-size 

Allí vemos que usa un tamaño de `proxy_buffer_size` con un valor por defecto de 4 kilobytes, lo cual es menor al tamaño total de los headers y justamente eso es el motivo de que el ingress nos da el error `response code 502`

Para solucionarlo debemos configurar un `annotation` para modificar el `proxy_buffer_size` del ingress.


## 3.2 SOLUCIÓN
    
Vamos a usar un `annotation` llamado `nginx.ingress.kubernetes.io/proxy-buffer-size` con el valor de "5k" para que el ingress pueda aceptar el tamaño de 4172 bytes de los headers que averiguamos en la sección anterior.

Copiamos el archivo `paso02-ingress.yaml` al archivo `paso03-ingress.yaml` y usamos el comando ***sed*** para agregar la ***annotation*** que acabamos de mencionar.

```
challenger-03@challenge-6-pivote:~$ cd ws-challenge-6/
challenger-03@challenge-6-pivote:~/ws-challenge-6$ cp paso02-ingress.yaml paso03-ingress.yaml
challenger-03@challenge-6-pivote:~/ws-challenge-6$ sed -i '/annotations:/a \    nginx.ingress.kubernetes.io/proxy-buffer-size: "5k"' paso03-ingress.yaml

challenger-03@challenge-6-pivote:~/ws-challenge-6$ more paso03-ingress.yaml 
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: challenge-app-ingress
  annotations:
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

Ahora aplicamos los cambios usando el archivo `paso03-ingress.yaml` y verificamos los cambios con el comando ***kubectl describe ingress***

```
challenger-03@challenge-6-pivote:~/ws-challenge-6$ kubectl apply -f paso03-ingress.yaml 
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
                     nginx.ingress.kubernetes.io/proxy-buffer-size: 5k
                     nginx.ingress.kubernetes.io/rewrite-target: /
Events:              <none>

```

Para probar la solución vamos a ejecutar el script python usando el argumento ***--send_simple_request***  Verificamos que ahora no hay ningún `response code 502` sino que la respuesta es exitosa y podemos ver todos los headers en la respuesta.

```
challenger-03@challenge-6-pivote:~$ python3 ~/ws-challenge-6/test-challenge6.py --send_simple_request
Response Headers:
{'Date': 'Sat, 05 Oct 2024 00:40:34 GMT', 'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '21', 'Connection': 'keep-alive', 'X-Large-Header': '45732817a11afb5210c57efb09616176ce9f2431eb6d4836351673da915b60f519c7f97679370b9b565b9384cab46ecdb99d3c22fcfb5b5d26a2689b28a5ec47f5d746eeb40d583a995ecbaa3b8072a86d299d7ceed24cb7485531f4af1e853c5bbb1d3087174659c7976f857838ddc09c8abf959a948cc8a7d7614f994cad21679b2e52888416fb849c6face918e4542de610ddf857264dbd32b90124ee091e2a9b6c31e4eff6fc562ebbd5255d564114595550822c9b3037cb739e0a8883808f3a2f42022597eb429d831ee73e3ddd79b36d030f5d11e68eae1f8cddc0647253902445abea9901c200b5ddb5acfe0e2c08d0378fe861ff2ffd4d22e41561649acd0f1adbe5adc0595f150e114d182f9795823d7be0c14776166864b3a6b957ef955b7847224a6a61c7dfc5dfaf115133c7a78058f21b5c3c4e073a1b57b316412a965481997f4a065f56337929c2668973150b8c876702913577e3bb2b24bf547065251117d0f15a7cb9304ac7872f9bc72ec1aa9ea71509fafcba32884b2cc274736ba00208e089e5ced1a5454886f564c014cbffb83c197a06934a2ea887aacb747186b5d72a4062b4b7bd407e8d21989db20a60e89707f8f26f850c6ca1eb09e76b1c63b1b4f0ff0c8b89d66ff482a5c38c8ad153a8428ea61692ddee82d1c49c696fe7f98d27920921f57780cdde5c4dfce3314670a37a7382e03c746d954441398fdb0214e4008c12d05cd26ab9e4e911614d4599e6c1dfe44f02dc1b35c405f9fb09534c55e0151217532926778cfb6d43c3240b14c0f3ea760dc36f77ab62b9bbd9f0400554dbc12c3a126575bbb5a51209b10f3b7ea83c765c856bb61766580c5068f27c952012ef4b2a2593e17a983f03d18d73feee5361ed1e8ed60f8e2e22f690d3399ec070146a413b3168b624a218a9f6a76fa8a2eae7480fc277660b688189156761055bfdbf93ce569397aaba74fb20698b4ee781a2518d4760c6afcf563022ec902e3526a54549b3bd81884dbda451d3dece2f1c3bd4bb24d4eebc343ecb01033fafdd9323401b1342080779ef4d52727be06b4496652e2609de0f59d82de8148e6cc027b318dfc0c91ec7e1f74c7a7ba8f46292015f6be2f0615caa40b30b4d5463be7a5564a1ea715cb607f9c796df9156d632c9579c68fac093ebe56d6ce6dc744f1578757ef62a314e83a01463bf3971aec116cba950f3d61232eca40a488ed2d11ed69cdd07b0a904df6f8a679bcbb12b75a774e7bfc52571a262738af71aabd2b0cad57a71a14d7f0070e0f0a574667f95a8406c600a5458fde6b4dfad58b3375f94a63aa76de6f0da851b7f58aed5804a8ef427766d4c1aa9d13ac7809b3aeff31db9367bc08b4711222ad1b59bc2374d372f061d1d0ecb79c33015175edf3b28db61ea66045497a53a3b4891cc1d30e633354f5a7809259b16b80fb3f56c2efb8a94167458b10add7ac1f2f68e6b571e91a312c8fede569e203dbedebc8cf2195c9722071751ae7678516c50de5223394489ce088bc5f4730def76bbb970f8ea0509127e051d9b1adc89949835ce6ef9d2768000ee046ed791f87e06f2e8ae1c5644375cd17c79c642a1de3db5e3045c72c13b3a1a2cda097991dc326978e43eb249d73c23d120d23273cf5254a68bae3fcac4f16a94f7b9fc629cba7c6eb9b0bbe2d68b97e618291f90034888d9e57f101bb27787c38c66d4d49102fb7a6fcfcca471d961455cdadf771418166725ad65bd20ad56bcf0d838b04864e142b4b86eb42dd2056ed87d83099ab0fe23bf4262b6e980c8bbc0c0f2d3c549efbc17e3086d658dd78a54ada28bdef58044ab3be4697eb23ec0b9531ce8a6612fccc541843becb394bdcaf3f53dfbdc2805fac2eb14cc8559013b6e5a9c66d8c45da5b02047a0c662aa13bd860d662bb3ad682dd982c64d18590ff0fab9d20d90af5b573536dd7d0a636f32f791ba36595a0827a124eb1d3164bd796535125d7cc7a94cc135b5f78b45709f9c7636e8d56240898a424386d0c03030d935f9c7d1337ebef7a50f15b361f70e98ce8ff57e6e84914b9e29be74a03aa253e6e26c668fb42d23d3f2a87477c46b492fb1c8e3a8ebd42c568e764795baa9321fcb810a90e6f43981a83edcac5b3b79ccd7d768428981e50b9e444289d131f8cf31ac423c9ce02c3f13fa02508f9942f0b86ceabe79575e4a1b55415e26d1ff5eb51339c0f56260b22517e65330b4380ecb4ebcd1a36b9c434ddba3a49f6fc664bb1855c2e7c1239b6db1e2d6b6c74c1f2b08b273fa8ca7ccad6378d6ea586be436b7ba2c02bee2564cede4c2916402e66908eaa3f83be2653dfb1f00c3231622185ae00770472d6a6f250d3b4cbe82f74cac790dbce8d550e899154bf99902ef2bb8ea7a5393b914719190916fd89875af7dceccd3a8638c3208c415d713f7d2fe69b05172e8206272fed35c3fc1df04d10652ea0b55e139f1a22e7f3781c03b92370418fc88a19be471eda26e8e2dd82d807f6bc167971768d2add184a59b1e055f0a1ddf03fd6b452a17265fdd93afb5964d33870558eaf8c9ab55545f462b9fbc263c47a5634a300c2ed534e7cb3c86064d30634fb8977a5448084cb86ae9ef9af8ac4376d3a4822c964977edf8b977c47cf958712810587d57c78a70cb798bfa8d8a5f75b129eef7ba210f74fc920c07b777f5044b3b3a0dc199d7fc7fdfd3c18cba53aa019249deb19a7b54e73dc92495a4817768ac6d90f6292080e5e34bbbd1425ac840afa8666c2de539da2c1038f6b5f999d191a47ccfef6fadaa7bb684b78fe28e2aceb3'}

Response Body:
Received your request
```

También podemos usar el argumento `tail` del comando ***kubectl logs*** y ver el último log de la aplicación el cual también se muestra exitoso con un `response code 200`

```
challenger-03@challenge-6-pivote:~$  kubectl logs -l app=challenge-app --tail=1
2024-10-05 00:40:34,339 - 10.42.110.195 - - [05/Oct/2024 00:40:34] "GET /random-code HTTP/1.1" 200 -
```
