import json
from unittest import TestCase
from users_information import UsersInformation
from issue_editor import IssueEditor
from json_editor import JsonEditor


class GithubApiTests(TestCase):
    def setUp(self):
        user_data = UsersInformation()
        self.user_with_push_access = user_data.get_user_with_push_access()
        self.user_without_push_access = user_data.get_user_without_push_access()
        self.editor_with_push_access = IssueEditor(self.user_with_push_access['username'], self.user_with_push_access['password'])
        self.editor_without_push_access = IssueEditor(self.user_without_push_access['username'], self.user_without_push_access['password'])
        self.owner = user_data.get_owner_information()

        self.default_issue_content = {
            'title': 'Second Issue',
            'body': 'Hello! It\'s second default issue',
            'state': 'open',
            'milestone': 1,
            'labels': ['question', 'bug'],
            'assignees': [self.owner['ownername'], self.user_with_push_access['username']]
        }

        self.new_issue_content = {
            'title': 'Second but edited issue yet',
            'body': 'Thank you for editing issue!',
            'state': 'open',
            'milestone': 2,
            'labels': ['question'],
            'assignees': [self.user_with_push_access['username']]
        }

        self.default_issue_json = JsonEditor(self.default_issue_content).json
        self.new_issue_json = JsonEditor(self.new_issue_content).json

    def tearDown(self):
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', self.default_issue_json)

    def test_edit_existent_issue(self):
        """
        Тест редактирования существующей задачи.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер существующей задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        Ожидаемый результат:
        - Статус ответа на запрос = 200
        """
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', self.new_issue_json)
        self.assertEqual(request.status_code, 200, 'Can\'t edit issue #2\n' + json.dumps(request.json(), sort_keys=True, indent=4))

    def test_edit_nonexistent_issue(self):
        """
        Тест редактирования несуществующей задачи.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и номер задачи, которой нет в репозитории
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер несуществующей задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        Ожидаемый результат:
        - Статус ответа на запрос = 404 (искомая задача не найдена)
        """
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '3', self.new_issue_json)
        self.assertEqual(request.status_code, 404, 'Can edit nonexistent issue #3\n' + json.dumps(request.json(), sort_keys=True, indent=4))

    def test_edit_locked_issue(self):
        """
        Тест редактирования заблокированной задачи
        (пользователи с Push доступом могут редактировать задачу после блокировки)
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и номер задачи, которой нет в репозитории
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Заблокировать необходмую задачу,
        отправив PUT запрос га url https://api.github.com/repos/:owner/:repo/issues/:number/lock
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер блокируемой задачи
        - Если статус ответ = 204, отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер заблокированной ранее задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        - Иначе вызвать исключение о невозможности блокировки задачи
        Ожидаемый результат:
        - Статус ответа на запрос = 200
        """
        request = self.editor_with_push_access.lock_issue(self.owner['ownername'], self.owner['repo'], '2')
        if request.status_code == 204:
            request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', self.new_issue_json)
            self.assertEqual(request.status_code, 200, 'Can edit locked issue #1\n' + json.dumps(request.json(), sort_keys=True, indent=4))
            request = self.editor_with_push_access.unlock_issue(self.owner['ownername'], self.owner['repo'], '2')
        else:
            raise Exception('Can\t lock issue#2\n' + json.dumps(request.json(), sort_keys=True, indent=4))

    def test_edit_issue_for_user_with_no_push_access(self):
        """
        Тест редактирования существующей задачи пользователем, не имеющим Push доступа.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера, не имеющего Push доступа, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер несуществующей задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        Ожидаемый результат:
        - Статус ответа на запрос = 403 (пользователь должен иметь Admin права)
        """
        request = self.editor_without_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', self.new_issue_json)
        self.assertEqual(request.status_code, 403, 'User with no push access can edit issue #1\n' + json.dumps(request.json(), sort_keys=True, indent=4))

    def test_edit_nonexistent_issue_with_no_push_access(self):
        """
        Тест редактирования несуществующей задачи пользователем, не имеющим Push доступа.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и и номер несуществуюшей задачи
        - Создать сессию для юзера, не имеющего Push доступа, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер несуществующей задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        Ожидаемый результат:
        - Статус ответа за запрос = 404 (Отличие от предыдущего теста в том,
        что код ответа должен быть именно 404, так как задачи не существует)
        """
        request = self.editor_without_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '3', self.new_issue_json)
        self.assertEqual(request.status_code, 404, 'Can edit nonexistent issue #3 with no push access\n' + json.dumps(request.json(), sort_keys=True, indent=4))

    def test_edit_issue_with_invalid_content_type(self):
        """
        Тест редактирования существующей задачи c некорректно заполненным JSON.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер существующей задачи
            в качестве параметров запроса передается некорректно заполненный JSON
        Ожидаемый результат:
        - Статус ответа на запрос = 422
        """
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', json.dumps(2))
        request_content = json.dumps(request.json(), sort_keys=True, indent=4)
        self.assertEqual(request.status_code, 422)

    def test_edit_issue_with_incorrect_milestone(self):
        """
        Тест редактирования существующей задачи c номером milestone, которого нет в задаче.
        Данный тест выделяется от остальных тем, что поле milestone - единственное, значение которого выбирается из
        списка по номеру
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер существующей задачи
            в качестве параметров запроса передается JSON как для корректного редактирования задачи,
            но с измененным значением поля milestone на несуществующее
        Ожидаемый результат:
        - Статус ответа за запрос = 422
        """
        incorrect_issue_content = self.new_issue_content
        incorrect_issue_content['milestone'] = 50
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', json.dumps(incorrect_issue_content))
        self.assertEqual(request.status_code, 422)

    def test_edit_issue_without_authentication(self):
        """
        Тест редактирования существующей задачи без авторизации.
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера с пустым логином и паролем (авторизация отсутствует)
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер несуществующей задачи
            в качестве параметров запроса передается контент задачи в формате JSON
        Ожидаемый результат:
        - Статус ответа на запрос = 401 (Отсутствие полномочий на редактирование)
        """
        non_authorized_user = IssueEditor('', '')
        request = non_authorized_user.edit_issue(self.owner['ownername'], self.owner['repo'], '2', self.new_issue_json)
        self.assertEqual(request.status_code, 401)

    def test_edit_issue_with_empty_title(self):
        """
        Тест редактирования существующей задачи пустем установки пустого заголовка.
        Данный тест выделяется от остальных тем, что задача не может быть без заголовка
        Предусловие:
        Для выполнения теста необходимо наличие репозитория и созданная в этом репозитории задача
        - Создать сессию для юзера, используя логин и пароль
        Шаги воспроизведения:
        - Отправить POST запрос на url https://api.github.com/repos/:owner/:repo/issues/:number
            где:
            - :owner - логин владельца репозитория
            - :repo - название репозитория
            - :number - порядковый номер существующей задачи
            в качестве параметров запроса передается JSON как для корректного редактирования задачи,
            но с пустым значением поля title
        Ожидаемый результат:
        - Статус ответа за запрос = 422
        """
        incorrect_issue_content = self.new_issue_content
        incorrect_issue_content['title'] = ''
        request = self.editor_with_push_access.edit_issue(self.owner['ownername'], self.owner['repo'], '2', json.dumps(incorrect_issue_content))
        self.assertEqual(request.status_code, 422)
