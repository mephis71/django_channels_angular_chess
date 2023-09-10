# from django.urls import reverse
# from game.models import GamePuzzle
# from rest_framework import status
# import factory

# class GamePuzzleFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = GamePuzzle

#     fen = '5B2/3r2P1/1pK5/8/k1Nb3p/2pnR2P/Pp6/5q2 w - - 0 1'

# class TestGamePuzzleViewSet:
#     def test_create(self, admin_client):
#         # given
#         data = {"fen": "2K5/P2P4/2p4p/4p3/k4P1p/BN6/Pp3q2/3Rn3 w - - 0 1"}

#         # when
#         response = admin_client.post(
#             reverse("gamepuzzle-list"),
#             data=data,
#         )

#         # then
#         assert response.status_code == status.HTTP_201_CREATED
#         assert "id" in response.data, "url" in response.data
#         assert GamePuzzle.objects.filter(id=response.data["id"]).exists()

#     def test_retrieve(self, admin_client):
#         # given
#         puzzle_obj = GamePuzzleFactory()
#         pk = puzzle_obj.pk
#         kwargs = {
#             'pk': pk
#         }

#         # when
#         response = admin_client.get(
#             reverse('gamepuzzle-detail', kwargs=kwargs),
#         )

#         # then
#         assert response.status_code == status.HTTP_200_OK
#         assert response.data['id'] == kwargs['pk']
#         assert response.data['fen'] == puzzle_obj.fen

# def test_url_property():
#     # given
#     puzzle_obj = GamePuzzleFactory()
#     id = puzzle_obj.id
#     url = f'/game/puzzle/{id}'

#     # when
#     obj_url = puzzle_obj.url

#     # then
#     assert url == obj_url
