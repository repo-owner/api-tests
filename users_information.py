class UsersInformation:
    __owner = 'repo-owner'
    __repo = 'api-tests'
    __user_without_push_access = 'user-without-push-access'
    __no_push_access_password = 'qUC7RqvMxd'
    __user_with_push_access = 'user-with-push-access'
    __push_access_password = 'qUC7RqvMxd'

    def get_owner_information(self):
        return {
            'ownername': self.__owner,
            'repo': self.__repo
        }

    def get_user_without_push_access(self):
        return {
            'username': self.__user_without_push_access,
            'password': self.__no_push_access_password
        }

    def get_user_with_push_access(self):
        return {
            'username': self.__user_with_push_access,
            'password': self.__push_access_password
        }
