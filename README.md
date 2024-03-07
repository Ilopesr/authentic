# :computer: Authentic

Authentic, é uma bibliotéca de authenticaçã para utilizar com django rest framework.



# :paperclip: Endpoints

### Autenticação



```js
# POST /entrar/
{
    "auth_user_username": str
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


### Criação

```js
# GET /contas/
{
    
}
