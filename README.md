# waterdroplet_backend routes
ошибка 422 - неверный запрос: проверьте ожидаемое body/query.
#### в каждом роуте, использующем токен может вернуться ошибка 400 - token expired или bad token

### используемые модели:
- auth: username: str, password: str
- Token: token: str
- reg_user: username: str, password: str, email: str
- AboutUs: about_text: str
- Article: article_name: str, article_text: str
- Service: service_name: str, price: str


## site_info 
- post/put/delete запросы выполнятся лишь при токене от пользователя с ником admin
- get('/get-about-us'): OUT: описание сайта about_text
- put('/edit-about-us'): IN: body: Token, AboutUs. output: код 200
- get('/get-all-articles'): OUT: список словарей модели Article
- get('/get-article-by-id/{article_id}'): IN: query: article_id: int. OUT: одна статья по введенному айди
- put('/edit-article/{article_id}'): IN: body: Token; query: article_id: int, article_text: str, article_name: str / None. OUT: код 200 / код 400
- post('/post-article'): IN: body: Token, Article. OUT: код 200
- delete('/delete-article/{article_id}': IN: body: Token; query: article_id: int. OUT: код 200
- get('/get-all-services'): IN: список словарей модели Service
- put('/edit-service-by-id/{service_id}'): IN: body: Token, Service; query: service_id: int. OUT: код 200
- post('/post-service'): IN: body: Token, Service. OUT: код 200
- delete('/delete-service/{service_id}'): IN: body: Token; query: service_id: int. OUT: код 200


## user
- post("/register"): IN: body: модель auth; query: user_type: str. OUT: код 200 / код 400 (в связи с занятым лицевым счетом)
- post("/login"): IN: body: модель auth. OUT: {"access_token": str, "token_type": "bearer"}
- put('/change_password'): IN: body: Token ; query: new_password: str. OUT: код 200
- put('/change_email'): IN: body: Token ; query: new_email: str. OUT: код 200
- post('/user_info'): IN: body: Token. output: словарь со всей информацией о пользователе. поскольку в роуте
принимается и сотрудник, и физическое лицо, модели словарей разные. 
у сотрудника: id_sotrudnik, id_business, login
у физ. лица: id_physic, login, full_name, email, address, id_business
- post('/user_info_ipus') IN: body: Token. OUT: {"ipus": "ipu1"} / ошибка 400, если пользователь - не физическое лицо. пока так, поскольку неизвестно в каком виде хранятся счетчики в бд

## business
- post("/get_business"): IN: body: Token. OUT: id_business, login, email, apitoken, tariff словарем.

## transactions
- post("/add_transaction"): IN: body: Token; query: new_number: str, ipu: str. OUT: {'id_transaction': int, 'payment_sum': float}
- post("/trans_status"): IN: body: Token; query: trans_id: int, status: int. OUT: код 200.
транзакция имеет 3 статуса, записываемых в бд цифрой. 0 - отклонена, 1 - ожидание, 2 - успех.


# порты
- 3306 : mysql_db
- 5000: api_test 
- 5001: Backend (main)


# тестовые пользователи в бд
- админ и физическое лицо:
- {
  "username": "chelavik",
  "password": "amogus"
}
{
  "username": "admin",
  "password": "amogus"
}
- бизнес-аккаунт:
- {
  "username": "business_test",
  "password": "business"
}