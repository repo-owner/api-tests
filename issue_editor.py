import requests


class IssueEditor:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.auth = (username, password)

    def create_issue(self, owner, repo, issue_content):
        url = 'https://api.github.com/repos/%s/%s/issues' % (owner, repo)
        request = self.session.post(url, issue_content)

        return request

    def edit_issue(self, owner, repo, issue_id, new_content):
        url = 'https://api.github.com/repos/%s/%s/issues/%s' % (owner, repo, issue_id)
        request = self.session.post(url, new_content)

        return request

    def lock_issue(self, owner, repo, issue_id):
        url = 'https://api.github.com/repos/%s/%s/issues/%s/lock' % (owner, repo, issue_id)
        headers = {'content-Length': '0'}
        request = self.session.put(url, headers=headers)

        return request

    def unlock_issue(self, owner, repo, issue_id):
        url = 'https://api.github.com/repos/%s/%s/issues/%s/lock' % (owner, repo, issue_id)
        request = self.session.delete(url)

        return request
