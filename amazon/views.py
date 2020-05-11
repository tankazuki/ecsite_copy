from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import dumps, loads, SignatureExpired, BadSignature
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.views.generic.edit import ModelFormMixin

from ecsite import settings
from .forms import LoginForm, SignUpForm, ReviewForm
from .models import Product, User, ShoppingCart, ShoppingCartItem


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


class ItemDetail(ModelFormMixin, DetailView):
    model = Product
    template_name = 'amazon/item_detail.html'
    form_class = ReviewForm

    def form_valid(self, form):
        review = form.save(commit=False)
        review.product = self.get_object()
        review.user = self.request.user
        review.save()
        return HttpResponseRedirect(self.request.path_info)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            self.object = self.get_object()
            return self.form_invalid(form)


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

                    cart = ShoppingCart()
                    cart.user = user
                    cart.save()

                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


class ShoppingCartDetail(LoginRequiredMixin, DetailView):
    model = ShoppingCart
    template_name = "amazon/shopping_cart.html"

    def post(self, request, *args, **kwargs):
        user = request.user
        product_pk = request.POST.get('product_pk')
        product = Product.objects.get(pk = product_pk)
        amount = request.POST.get('amount')

        exist = ShoppingCartItem.objects.filter(cart__user = user).filter(product = product)

        # すでにカートに存在する商品の場合は個数をインクリメント
        if len(exist) > 0:
            current_amount = exist[0].amount
            exist[0].amount = current_amount + int(amount)
            exist[0].save()
        else:
            new_cart_item = ShoppingCartItem()
            new_cart_item.cart = request.user.cart
            new_cart_item.product = product
            new_cart_item.amount = int(amount)
            new_cart_item.save()
        return HttpResponseRedirect(reverse('amazon:cart',  kwargs={'pk': self.get_object().pk}))


def update_cart_item(request):
    cart_item_pk = request.POST.get('cart_item_pk')
    new_amount = request.POST.get('amount')

    if cart_item_pk is None or new_amount is None:
        return JsonResponse({'error': 'invalid request'})
    if int(new_amount) <= 0:
        return JsonResponse({'error': 'amount must be getter than zero'})

    try:
        cart_item = ShoppingCartItem.objects.get(pk = cart_item_pk)
        cart_item.amount = int(new_amount)
        cart_item.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})


def delete_cart_item(request):
    cart_item_pk = request.POST.get('cart_item_pk')
    if cart_item_pk is None:
        return JsonResponse({'error': 'invalid parameter'})
    try:
        cart_item = ShoppingCartItem.objects.get(pk=cart_item_pk)
        cart_item.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e.args)})



