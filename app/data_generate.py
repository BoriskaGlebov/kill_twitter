from itertools import combinations
from random import sample

import factory.fuzzy
import faker

# from app.medias.models import Media
# from app.tweets.models import Like, Tweet, TweetMedia
from app.users.models import Follow, User

faker = faker.Faker("ru_RU")


class UserFactory(factory.Factory):
    """Фабрика рандомных пользователей"""

    class Meta:
        model = User

    # id
    first_name = factory.Faker("first_name", locale="ru_Ru")
    last_name = factory.Faker("last_name", locale="ru_Ru")
    api_key = factory.Faker("word")


class FollowsFactory(factory.Factory):
    """Фабрика рандомных подписок и подписчиков"""

    class Meta:
        model = Follow

    # Генерируем неповторяющиеся комбинации
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Получаем все уникальные комбинации двух чисел от 1 до 20
        unique_combinations = list(combinations(range(1, 100), 2))

        # Случайным образом выбираем одну из комбинаций
        user_id, follower_id = sample(unique_combinations, 1)[0]

        # Создаем экземпляр модели Follow с выбранными id
        return model_class(user_id=user_id, follower_id=follower_id)


# class TweetFactory(factory.Factory):
#     class Meta:
#         model = Tweet
#
#     user_id = factory.LazyFunction(lambda: randint(1, 100))  # Случайное число от 1 до 100
#     tweet_data = factory.LazyFunction(lambda: faker.sentence())  # Случайный текст
#
#
# class LikeFactory(factory.Factory):
#     class Meta:
#         model = Like
#
#     # Генерируем неповторяющиеся комбинации
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         # Получаем все уникальные комбинации двух чисел от 1 до 20
#         unique_combinations = list(combinations(range(1, 100), 2))
#
#         # Случайным образом выбираем одну из комбинаций
#         user_id, tweet_id = sample(unique_combinations, 1)[0]
#
#         # Создаем экземпляр модели Follow с выбранными id
#         return model_class(user_id=user_id, tweet_id=tweet_id)
#
#
# class TweetMediaFactory(factory.Factory):
#     class Meta:
#         model = TweetMedia
#
#     # Генерируем неповторяющиеся комбинации
#     @classmethod
#     def _create(cls, model_class, *args, **kwargs):
#         # Получаем все уникальные комбинации двух чисел от 1 до 20
#         unique_combinations = list(combinations(range(1, 20), 2))
#
#         # Случайным образом выбираем одну из комбинаций
#         tweet_id, media_id = sample(unique_combinations, 1)[0]
#
#         # Создаем экземпляр модели Follow с выбранными id
#         return model_class(tweet_id=tweet_id, media_id=media_id)
#
#
# class MediaFactory(factory.Factory):
#     class Meta:
#         model = Media
#         exclude = ("_index",)  # Исключаем _index из аргументов конструктора
#
#     _index = factory.Sequence(lambda n: n + 1)
#     media_data = factory.LazyAttribute(lambda o: f"static/images/{o._index}.jpg")


def generate_users(num):
    out_set = set()  # Множество для хранения уникальных комбинаций
    out_instances = []

    while len(out_instances) < num:
        out_instance = UserFactory()
        combination = out_instance.api_key

        # Проверяем, есть ли такая комбинация уже в множестве
        if combination not in out_set:
            out_set.add(combination)  # Добавляем комбинацию в множество
            out_instances.append(out_instance)  # Добавляем экземпляр в список

    return out_instances


def generate_follow(num):
    out_set = set()  # Множество для хранения уникальных комбинаций
    out_instances = []

    while len(out_instances) < num:
        out_instance = FollowsFactory()
        combination = (out_instance.user_id, out_instance.follower_id)

        # Проверяем, есть ли такая комбинация уже в множестве
        if combination not in out_set:
            out_set.add(combination)  # Добавляем комбинацию в множество
            out_instances.append(out_instance)  # Добавляем экземпляр в список

    return out_instances


#
# def generate_likes(num):
#     out_set = set()  # Множество для хранения уникальных комбинаций
#     out_instances = []
#
#     while len(out_instances) < num:
#         out_instance = LikeFactory()
#         combination = (out_instance.user_id, out_instance.tweet_id)
#
#         # Проверяем, есть ли такая комбинация уже в множестве
#         if combination not in out_set:
#             out_set.add(combination)  # Добавляем комбинацию в множество
#             out_instances.append(out_instance)  # Добавляем экземпляр в список
#
#     return out_instances
#
#
# def generate_tweet_media(num):
#     out_set = set()  # Множество для хранения уникальных комбинаций
#     out_instances = []
#
#     while len(out_instances) < num:
#         out_instance = TweetMediaFactory()
#         combination = (out_instance.tweet_id, out_instance.media_id)
#
#         # Проверяем, есть ли такая комбинация уже в множестве
#         if combination not in out_set:
#             out_set.add(combination)  # Добавляем комбинацию в множество
#             out_instances.append(out_instance)  # Добавляем экземпляр в список
#
#     return out_instances


if __name__ == "__main__":
    pass
    # s = MediaFactory()
    # print(s.to_dict())
    # s = MediaFactory()
    # print(s.to_dict())
    # s = MediaFactory()
    # print(s.to_dict())
    # s = MediaFactory()
    # print(s.to_dict())
