# :computer: Authentic

Authentic, é uma bibliotéca de authenticaçã para utilizar com django rest framework.



# :paperclip: Endpoints


O endpoint de autenticação "/entrar/" ao ser validado pelos dados corretos
via uma função de autentificação personalizada, adiciona automáticamente 
ao seu navegador, as chaves ["access","refresh"], o qual 
deve receber a autentificação das views com um Bearer token.


```js
# POST /entrar/
{
    "USERNAME_FIELD": str
    "password": str
}

# RETURNS
{
    "access": str,
    "refresh": str,
}
```


```js
# POST /verificar/
{
    "access": str,
}

# RETURNS
{
    bolean: True|False
}
```

```js
# POST /renovar/
{
    "refresh": str,
}

# RETURNS
{
    "access": str,
}
```
