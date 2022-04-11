from django.forms.widgets import Select


class SelectFriendWidget(Select):
    option_template_name = 'friendships/widgets/select_friend_option.html'