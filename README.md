# waterdroplet_backend routes
ошибка 422 - неверный запрос: проверьте ожидаемое body/query.
#### в каждом роуте, использующем токен может вернуться ошибка 400 - token expired или bad token

### используемые модели:
- auth: username: str, password: str
- Token: access_token: str
- reg_user: username: str, password: str, email: str
- AboutUs: about_text: str
- Article: article_name: str, article_text: str
- Service: service_name: str, price: str
- Worker: login: str, full_name:str, phone: str, password: str
- Secret_key: key: str

## site_info 
- post/put/delete запросы выполнятся лишь при токене от пользователя с ником admin
- get('/get-about-us'): OUT: описание сайта about_text 
- put('/edit-about-us'): IN: body: Token, AboutUs. output: код 200
- get('/get-all-articles'): OUT: список словарей модели Article
- get('/get-article-by-id/{article_id}'): IN: query: article_id: int. OUT: одна статья по введенному айди
- put('/edit-article/{article_id}'): IN: body: Token; query: article_id: int, article_text: str, article_name: str / None. OUT: код 200 / код 400
- post('/post-article'): IN: body: Token, Article. OUT: код 200
- delete('/delete-article/{article_id}'): IN: body: Token; query: article_id: int. OUT: код 200
- get('/get-all-services'): IN: список словарей модели Service
- put('/edit-service-by-id/{service_id}'): IN: body: Token, Service; query: service_id: int. OUT: код 200
- post('/post-service'): IN: body: Token, Service. OUT: код 200
- delete('/delete-service/{service_id}'): IN: body: Token; query: service_id: int. OUT: код 200


## workers (работает только для бизнес-аккаунта)
### получаемые коды ответов: 
- 412 - запрос не от бизнеса, 
- 401 - неверный токен или срок его действия истек
- 404 - работник с этим id не существует или прикреплен к др. бизнесу 
- 402 - имя пользователя занято

- post('/workers/get_all_workers'): IN: body: Token. OUT: пример. {
  "workers": [
    {
      "id_sotrudnik": 3,
      "full_name": "PAVLOV H.A."
    },
    {
      "id_sotrudnik": 4,
      "login": "IVANOV I.I."
    }
  ]
} / 412 / 401 
- post('/workers/worker_info/{worker_id}'): IN: body: Token ; url: worker_id:int. 
OUT: {
  "worker": {
    "id_sotrudnik": 3,
    "id_business": 2,
    "login": "worker1",
    "phone": "+123",
    "hashed_password": "worker"
  }
} / 401 / 412 / 404
- delete('/workers/delete_worker/{worker_id}'): IN: body: Token ; url: worker_id:int.
 OUT: код 200 / 401 / 404 / 402
- post('/workers/create_worker'): IN: body: Token ; worker: Worker. OUT: 
 код 200 / 412 / 404 / 401 / 402
- put('/workers/edit_worker/{worker_id}'): IN: body: token: Token; query: worker_id: int, login: str, phone: str, password: str, full_name: str. OUT:
 код 200 / 412 - bad user_type - ожидается юр.лицо / 404 - не найден работник с таким id / 400 - проблема токена / 402 - такой логин занят


## user
- post("/register"): IN: body: модель auth; query: user_type: str. OUT: код 200 / код 400 (в связи с занятым лицевым счетом)
- post("/login"): IN: body: модель auth. OUT: {"access_token": str, "token_type": "bearer", "first_enter": bool, "user_type": str} / код 401. user_type: physic / business / sotrudnik
- put('/change_password'): IN: body: Token ; query: new_password: str. OUT: код 200 / код 402: не пройдена валидация пароля (min 8 символов, 2 цифры, 1 заглавная буква)
- put('/change_email'): IN: body: Token ; query: new_email: str. OUT: код 200
- post('/user_info'): IN: body: Token. output: словарь со всей информацией о пользователе / ошибка 400 если пользователь - не физик или работник. поскольку в роуте
принимается и сотрудник, и физическое лицо, модели словарей разные. (бизнес-токен не принимается)
у сотрудника: id_sotrudnik, id_business, login, full_name.
у физ. лица: id_physic, login, full_name, email, address, id_business
- post('/user_info_ipus') IN: body: Token. OUT: {
  "ipu1": "03/31/2023",
  "ipu2": "03/31/2023"
} / ошибка 400, если пользователь - не физическое лицо. пока так, поскольку неизвестно в каком виде хранятся счетчики в бд
- post('/send_form'): IN: query: name: str, phone: str, message: str. OUT: код 200 / код 500 - проблема бд.
- post('/get_user_by_address'): IN: body: token:Token; query: address: str. OUT: {
  "full_name": "IVANOV IVAN IVANOVICH",
  "login": "physic2"
  "email": "string"
} - login - номер договора  / 400 - пользователь - не сотрудник / 404 - не найден пользователь по адресу / 401 - плохой токен
## business
- post("/get_business"): IN: body: Token. OUT: id_business, login, email, apitoken, expiration_date словарем / ошибка 401, если пользователь - не бизнес
- post("/get_related_physics/{page_id}"): IN: body: Token; url: page_id: int. OUT: словарь до ста пользователей от n•100 до n•100+100
[
    {
      "id_physic": 4,
      "login": "physic1",
      "full_name": "string",
      "email": "string",
      "ipus": "ipu1",
      "address": null,
      "id_business": 2
    },
    {
      "id_physic": 5,
      "login": "physic2",
      "full_name": "string",
      "email": "string",
      "ipus": "ipu1 ipu2",
      "address": null,
      "id_business": 2
    }
  ] / 200 - success / 400 - bad user_type / 401 - проблема с токеном


## validations
- post("/suspicious_validations/{page_id}"): IN: body: Token; url: page_id: int. OUT: [
  {
    "id_physic": 5,
    "sotrudnik_photo_date": "2023-04-02 20:06:07"
  }
] / 400 - bad user_type /
401 - проблема с токеном
- post("/first_ipu_value"): IN: body: token: Token , key: Secret_key; query: number: str, ipu: str. OUT: 200 / 403 / 400/ 404

- post('/get_related_address/{page_id}'): IN: body: Token; url: page_id: int. OUT: [
  {
    "address": "улица abc d 123, kv 1"
  },
  {
    "address": "улица defc d 13, kv 55"
  }
] / 200 - success / 400 - bad user_type /
401 - проблема с токеном

- post('/get_all_related_addresses'): безлимитный вариант получения для предыдущей функции.
IN: body: Token. OUT: [
  {
    "address": "улица abc d 123, kv 1"
  },
  {
    "address": "улица defc d 13, kv 55"
  }
]


- post('/get_ipus_by_address'): IN: body: Token; query: address: str. OUT: {
  "ipu1": "04/14/2023",
  "ipu2": "None"
} / 200 - success / 400 - bad user_type /
401 - проблема с токеном

- post('/new_validation'): IN: body: Token; query: sotr_number: str, ipu: str, address: str. OUT: 200 - success / 400 - bad user_type /
401 - проблема с токеном
- post('/get_validation_logs'): IN: body: token: Token ; query: validation_id: int. OUT: 
{
  "sotrudnik_photo_date": "2023-04-02 20:05:51",
  "sotrudnik_number": "1010",
  "physic_photo_date": "2023-03-31 21:17:44",
  "physic_number": "1000",
  "verdict": 0,
  "physic_name": "string",
  "sotrudnik_name": "PAVLOV H.A."
} / 400 - проблема токена / 403 - bad user_type / 404 - не найдена валидация по id

## transactions
- post("/add_transaction"): IN: body:  token: Token , key: Secret_key; query: new_number: str, ipu: str. OUT: {'id_transaction': int, 'payment_sum': float} 
/ 403 - новое значение меньше предыдущего / 400 - проблема токена или секретного ключа / 404 - нет такого ipu / 401 - bad user_type (нужен физик)
- post("/trans_status"): IN: body: token: Token , key: Secret_key; query: trans_id: int, status: int. OUT: код 200.
транзакция имеет 3 статуса, записываемых в бд цифрой. 0 - отклонена, 1 - ожидание, 2 - успех.


# порты
- 3306 : mysql_db

- 5502: Backend (main)
- 5500: api (main)

- 5001: Backend_test
- 5000: api_test


# тестовые пользователи в бд
- админ и физическое лицо:
- {
  "username": "chelavik",
  "password": "Amogus12"
}
- {
  "username": "physic2",
  "password": "physic"
}
- {"username": "newbie",
  "password": "00000000"
}

{
  "username": "admin",
  "password": "Password11"
}
- бизнес-аккаунт:
{
  "username": "business_test",
  "password": "Business11"
}
- {"username": "new_business",
  "password": "00000000"




- работники
{
  "worker": {
    "login": "worker1",
    "password": "worker"
  }

  "worker": {
    "login": "worker2",
    "password": "worker"
  }