ТЗ "Перехват неудачных  смс с SMSС"

Описание: 
Необходимо перехватывать СМС , неотправленные приоритетным сервисом, и отправлять посредством резервного сервиса. 
Для сообщений в статусе "Недоступный номер" из журнала отправленных в smsc.ua, пересылать текст с помощью резервного сервиса sms-fly.ua. 
 
ИНСТРУКЦИИ API: 
1) https://smsc.ua/api/http/get_data/outbox/#menu  - основной сервис 
2) https://sms-fly.ua/public/api.v2.02.pdf  - резервный сервис 
 

 
 
ЗАДАНИЕ: 
 
1. ежеминутно даем запрос по АПИ smsc.ua - получаем все отправленные смс 
2. вносим в журнал перехваченных все смс 
3. вносим абонента в "Справочник абонентов" Имя нового абонента = пусто 
4. обрабатываем только смс в статусе "Недоступный номер" на smsc.ua - отправляем их получателю  через API fly-sms.ua . По результату задаем соответствующую запись в "жрунале перехваченных" 
 
СТРУКТУРА: 
1. БД перехваченных СМС.  
 
    1.1 "Журнал  перехваченных смс " 
         поля для журнала:  
              дата / время смс / номер телефона получателя / текст смс/ статус на smsc / статус на fly-sms: успех, проблема, в процессе 
Фильтры: поле поиска по тексту в заголовке каждой колонки отдельно - поиск по условию "содержит текст" 
 
     1.2 "Справочник абонентов". Поля: имя / телефон / время последнего успешного смс. Фильтры: поле поиска по тексту в заголовке каждой колонки отдельно - поиск по условию "содержит текст" 
 
     1.3. "Справочник пользователей службы" 
       
 
 
 2. кабинет пользователей : логин = электронная почта / пароль = мин 8 символов 
 
 3. инструменты управления :   
      3.1 Добавить / редактировать пользователей (редактировать пароль / удалить - добавить пользователя) 
      3.2 Редактировать справочник абонентов - прямо в ячейке таблицы. 
      3.3 Кнопка "Повторить последнее смс " в каждой строчке . Доступна всегда в журнале перехваченных смс  (в случае заминок на стороне резервного сервиса или просто для повторной отправки смс)
