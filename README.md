# waterdroplet_backend

#### в каждом роуте, использующем токен может вернуться ошибка 400 - token expired или bad token

### используемые модели:
- auth: username: str, password: str
- Token: token: str
- reg_user: username: str, password: str, email: str



## site_info
- delete('/delete-article/{article_id}' : принимает ...., возвращает успех или 

## user
- post("/register"): input: body: модель auth; query: user_type: str. output: код 200 / код 400 (в связи с занятым лицевым счетом)
- post("/login"): input: body: модель auth. output: код 200 / код 400 (неверный логин или пароль)
- put('/change_password'): input: body: Token ; query: new_password: str. output: код 200
- put('/change_email'): input: body: Token ; query: new_email: str. output: код 200
- post('/user_info'): input: body: Token. output: словарь со всей информацией о пользователе. поскольку в роуте
принимается и сотрудник, и физическое лицо, модели словарей разные. 
у сотрудника: id_sotrudnik, id_business, login,
у физ. лица: id_physic, login, full_name, email, address, id_business
- 