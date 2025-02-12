from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
class M1(MiddlewareMixin):
    def process_request(self,request):
        if request.path == '/':
            return
        if 'blog' in request.path:
            if not request.session.get('identity'):
                return redirect('/')
            else:
                return
        if request.path == '/favicon.ico':
            return
        if 'ueditor' in request.path or 'avatar' in request.path or 'static' in request.path or 'article' in request.path or 'logout' in request.path:
            return
        if 'student' in request.path and request.session.get('identity') == '学生':
            return
        if 'teacher' in request.path and request.session.get('identity') == '教师':
            return
        if request.path.startswith('/media/upload/') and request.path.endswith('zip'):
            return
        if request.path.startswith('/media/dataShare/'):
            return
        if ('media' in request.path) and (request.session["identity"]=='教师'):
            return
        return redirect('/')