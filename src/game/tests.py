from rest_framework.test import APISimpleTestCase, APITestCase, APIRequestFactory
from django.db.models import Q
from django.contrib.auth import get_user_model


# def register_view(request, *args, **kwargs):
#     form = CustomUserCreationForm()

#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home-page')
            
#     context = {
#         'form': form
#     }
#     return render(request, 'register.html', context)


# ----- CREATE REQUEST FACTORY CLIENT ---------

class GameManagerTest(APITestCase):
    username1 = 'mephis'
    username2 = 'trybalus'

    def setUp(self):
        self.User = get_user_model()

    def test_get_or_new(self, username1, username2):
        qlookup1 = Q(player1__username = username1) & Q(player2__username = username2)
        qlookup2 = Q(player1__username = username2) & Q(player2__username = username1)

        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() != 0:
            return qs[0]
        else:
            p1 = self.User.objects.get(username = username1)
            p2 = self.User.objects.get(username = username2)
            print(p1, p2)
            obj = self.model(player1 = p1, player2 = p2)
            obj.save()
            return obj