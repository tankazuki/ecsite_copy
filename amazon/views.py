from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import dumps, loads, SignatureExpired, BadSignature
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView

from ecsite import settings
from .forms import LoginForm, SignUpForm
from .models import Product, User


class Lp(TemplateView):
    template_name = 'amazon/lp.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = Product.objects.all()
        context['items'] = items
        return context


class ItemList(ListView):
    model = Product
    template_name = 'amazon/item_list.html'

    def get_queryset(self):
        products = Product.objects.all()
        if 'q' in self.request.GET and self.request.GET['q'] is not None:
            q = self.request.GET['q']
            products = products.filter(name__icontains=q)
        return products


class ItemDetail(DetailView):
    model = Product
    template_name = 'amazon/item_detail.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'amazon/login.html'


class SignUp(CreateView):
    """ユーザ仮登録"""
    template_name = 'amazon/sign_up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        "仮登録と本登録メールの発行"
        # 仮登録の段階ではis_activeをFalseにしておく(レコードは保存しておく)

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': self.request.scheme,
            'domain': domain,
            'token': dumps(user.pk),
            'user': user,
        }
        subject_template = get_template('amazon/mail_template/sign_up/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('amazon/mail_template/sign_up/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        messages.success(self.request, '本登録用リンクを送付しました')
        return HttpResponseRedirect(reverse('amazon:signup'))


class SignUpDone(TemplateView):
    """メール内URLアクセス後のユーザ本登録"""

    template_name = 'amazon/sign_up_done.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60*60*24)

    def get(self, request, **kwargs):
        token = kwargs.get('token')

        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        except (SignatureExpired, BadSignature):
            return HttpResponseBadRequest()

        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    user.is_active = True
                    user.save()

                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()





