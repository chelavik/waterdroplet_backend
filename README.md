# waterdroplet_backend

#### в каждом роуте, использующем токен может вернуться ошибка 400 - token expired или bad token

### используемые модели:
- auth: username: str, password: str
- Token: token: str
- reg_user: username: str, password: str, email: str
- AboutUs: about_text: str
- Article: article_name: str, article_text: str
- Service: service_name: str, price: str


## site_info
- get('/get-about-us'): output: описание сайта about_text
- put('/edit-about-us'): input: body: Token, AboutUs. output: код 200
- get('/get-all-articles'): output: список всех статей
- get('/get-article-by-id/{article_id}'): input: query: article_id: int. output: одна статья по введенному айди
- put('/edit-article/{article_id}'): input: body: Token; query: article_id: int, article_text: str, article_name: str / None. output: код 200 / код 400
- post('/post-article'): input: body: Token, Article. output: код 200
- delete('/delete-article/{article_id}': input: body: Token; query: article_id: int. output: код 200
- get('/get-all-services'): output: список всех сервисов
- put('/edit-service-by-id/{service_id}'): input: body: Token, Service; query: service_id: int. output: код 200
- post('/post-service'): input: body: Token, Service. output: код 200
- delete('/delete-service/{service_id}'): input: body: Token; query: service_id: int. output: код 200


## user
- post("/register"): input: body: модель auth; query: user_type: str. output: код 200 / код 400 (в связи с занятым лицевым счетом)
- post("/login"): input: body: модель auth. output: код 200 / код 400 (неверный логин или пароль)
- put('/change_password'): input: body: Token ; query: new_password: str. output: код 200
- put('/change_email'): input: body: Token ; query: new_email: str. output: код 200
- post('/user_info'): input: body: Token. output: словарь со всей информацией о пользователе. поскольку в роуте
принимается и сотрудник, и физическое лицо, модели словарей разные. 
у сотрудника: id_sotrudnik, id_business, login
у физ. лица: id_physic, login, full_name, email, address, id_business
- 1asdxzzzzzzz