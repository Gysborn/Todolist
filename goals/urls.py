from django.urls import path

from goals import views

urlpatterns = [
    path("goal_category/create", views.GoalCategoryCreateView.as_view(), name='create-category'),
    path("goal_category/list", views.GoalCategoryListView.as_view(), name='list-category'),
    path("goal_category/<int:pk>", views.GoalCategoryView.as_view(), name='category'),
    path("goal/create", views.GoalCreateView.as_view(), name='goal-create'),
    path("goal/list", views.GoalListView.as_view(), name='goal-list'),
    path("goal/<int:pk>", views.GoalView.as_view(), name='goal'),

    path('goal_comment/create', views.GoalCommentCreateView.as_view(), name='create-comments'),
    path('goal_comment/list', views.GoalCommentListView.as_view(), name='list-comments'),
    path('goal_comment/<pk>', views.GoalCommentView.as_view(), name='comments'),
    path("board/create", views.BoardCreateView.as_view(), name='board-create'),
    path("board/list", views.BoardListView.as_view(), name='board-list'),
    path("board/<int:pk>", views.BoardView.as_view(), name='board'),

]
